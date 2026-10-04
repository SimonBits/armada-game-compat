"""Local synthetic tests only. No connection to Armada, Steam or Wine."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('fix', Path(__file__).with_name('batman-amd-fix.py'))
fix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fix)
BASE = (b'WINE REGISTRY Version 2\n;; All keys relative to REGISTRY\\Machine\n\n#arch=win64\n\n['
        + fix.KEY + b'] 0\n#time=0\n'
        b'"directx"=dword:00000001\n"InstallDescription"="AMD Dual-Core Optimizer"\n'
        b'"vcredist"=dword:00000001\n\n[Software\\\\Other]\n"AMD"=dword:00000000\n')


class FixTests(unittest.TestCase):
    def setUp(self):
        runner_uid = os.getuid()
        self.tmp = tempfile.TemporaryDirectory(prefix='batman-fixture-')
        self.home = Path(self.tmp.name)
        self.root = self.home / '.local/share/Steam'
        self.lib = self.home / 'SD Card' / 'Steam Library'
        (self.root / 'steamapps').mkdir(parents=True)
        self.folders = self.root / 'steamapps/libraryfolders.vdf'
        self.folders.write_text('"libraryfolders" { "0" { "path" "' + str(self.root) +
                                '" } "1" { "path" "' + str(self.lib) + '" } }')
        self.pfx = self.lib / 'steamapps/compatdata/200260/pfx'
        (self.pfx / 'drive_c/windows').mkdir(parents=True)
        for name in ('system.reg', 'user.reg', 'userdef.reg'):
            (self.pfx / name).write_bytes(BASE)
        for name in ('version', 'config_info', 'pfx.lock'):
            (self.pfx.parent / name).write_text('fixture')
        self.manifest = self.lib / 'steamapps/appmanifest_200260.acf'
        self.manifest.write_text('"AppState" { "appid" "200260" "installdir" "Batman Arkham City GOTY" }')
        exe = self.lib / 'steamapps/common/Batman Arkham City GOTY/Binaries/Win32/BatmanAC.exe'
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b'SYNTHETIC - not an executable')
        self.default = self.home / '.wine/system.reg'
        self.default.parent.mkdir()
        self.default.write_bytes(b'DEFAULT MUST NEVER CHANGE')
        self.reg = self.pfx / 'system.reg'
        self.env = patch.dict(os.environ, {'HOME': str(self.home), 'XDG_DATA_HOME': str(self.home / '.local/share')})
        self.env.start()
        # Model one ordinary Steam user regardless of the actual CI runner UID.
        # Map only fixture ownership; retain real mode, links, inode and timestamps.
        original_stat = Path.stat
        def fixture_stat(path, *args, **kwargs):
            result = original_stat(path, *args, **kwargs)
            if (path == self.home or self.home in path.parents) and result.st_uid == runner_uid:
                fields = {name: getattr(result, name) for name in dir(result) if name.startswith('st_')}
                fields['st_uid'] = 1000
                return SimpleNamespace(**fields)
            return result
        for mocked in (patch.object(fix.os, 'getuid', return_value=1000),
                       patch.object(Path, 'stat', fixture_stat)):
            mocked.start()
            self.addCleanup(mocked.stop)

    def tearDown(self):
        self.assertEqual(self.default.read_bytes(), b'DEFAULT MUST NEVER CHANGE')
        self.env.stop()
        self.tmp.cleanup()

    def run_cli(self, *args):
        output = io.StringIO()
        with patch.object(fix.sys, 'argv', ['batman-amd-fix.py', *args]), \
                patch.object(fix, 'quiet'), contextlib.redirect_stdout(output):
            fix.main()
        return output.getvalue()

    def backups(self):
        return sorted(self.home.glob('batman-200260-backup-*'))

    def test_external_library_spaces(self):
        self.assertEqual(fix.discover(self.home)[2], self.pfx)

    def test_default_library(self):
        oldroot = self.root
        # Move only the synthetic library fixture into the default Steam root.
        self.lib.rename(self.home / 'moved')
        oldroot.rename(self.home / 'unused')
        (self.home / 'moved').rename(oldroot)
        (oldroot / 'steamapps/libraryfolders.vdf').write_text(
            '"libraryfolders" { "0" { "path" "' + str(oldroot) + '" } }')
        self.assertEqual(fix.discover(self.home)[2], oldroot / 'steamapps/compatdata/200260/pfx')

    def test_alias_roots_are_deduplicated(self):
        (self.home / '.steam').mkdir()
        (self.home / '.steam/steam').symlink_to(self.root)
        self.assertEqual(fix.discover(self.home)[0], self.root)

    def test_missing_prefix(self):
        self.pfx.rename(self.pfx.with_name('missing'))
        with self.assertRaisesRegex(RuntimeError, 'Missing'):
            fix.discover(self.home)

    def test_wrong_appid(self):
        self.manifest.write_text('"AppState" { "appid" "200261" }')
        with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
            fix.discover(self.home)

    def test_missing_game_executable(self):
        for p in self.lib.rglob('BatmanAC.exe'):
            p.unlink()
        with self.assertRaisesRegex(RuntimeError, 'BatmanAC.exe'):
            fix.discover(self.home)

    def test_prefix_lock_busy(self):
        with (self.pfx.parent / 'pfx.lock').open('rb') as lock:
            fix.fcntl.flock(lock, fix.fcntl.LOCK_EX | fix.fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                self.run_cli()
        self.assertEqual(self.reg.read_bytes(), BASE)

    def test_ambiguous_prefix(self):
        (self.root / 'steamapps/compatdata/200260/pfx').mkdir(parents=True)
        with self.assertRaisesRegex(RuntimeError, 'ambiguous'):
            fix.discover(self.home)

    def test_linked_prefix(self):
        moved = self.home / 'elsewhere'
        self.pfx.rename(moved)
        self.pfx.symlink_to(moved)
        with self.assertRaisesRegex(RuntimeError, 'Linked'):
            fix.discover(self.home)

    def test_hardlinked_hive(self):
        os.link(self.reg, self.home / 'alias.reg')
        with self.assertRaisesRegex(RuntimeError, 'hardlinks'):
            fix.discover(self.home)

    def test_symlinked_hive(self):
        self.reg.unlink()
        self.reg.symlink_to(self.default)
        with self.assertRaisesRegex(RuntimeError, 'symlinks'):
            fix.discover(self.home)

    def test_vdf_malformed_or_duplicate(self):
        for data in ['"a" {', '"a" "b" "a" "c"', 'unquoted value', '"a" "bad\\q"']:
            with self.subTest(data=data), self.assertRaises(RuntimeError):
                fix.vdf(data)

    def test_vdf_escaped_paths(self):
        self.assertEqual(fix.vdf(r'"x" "a\\b\"c" // comment'), {'x': 'a\\b"c'})

    def test_unsupported_registry(self):
        for data in [BASE.replace(b'#arch=win64', b'#arch=win32'), BASE + b'x',
                     BASE.replace(fix.KEY, b'OtherKey'), BASE.replace(b'\n', b'\r\n'),
                     BASE + b'[' + fix.KEY + b']\n']:
            with self.subTest(data=data[:30]), self.assertRaises(RuntimeError):
                fix.registry(data)

    def test_duplicate_amd_or_wrong_type(self):
        for line in [b'"AMD"="1"\n', fix.MARKER + fix.MARKER.lower()]:
            with self.assertRaises(RuntimeError):
                fix.registry(fix.change(BASE, line))

    def test_check_no_writes(self):
        self.assertIn('CHECK ONLY', self.run_cli('--check'))
        self.assertEqual(self.reg.read_bytes(), BASE)
        self.assertEqual(self.backups(), [])

    def test_apply_backup_idempotency_and_only_one_value(self):
        self.reg.chmod(0o640)
        before_other = (self.pfx / 'user.reg').read_bytes()
        output = self.run_cli()
        self.assertIn('absent -> 1', output)
        self.assertEqual(fix.change(self.reg.read_bytes(), None), BASE)
        self.assertEqual((self.pfx / 'user.reg').read_bytes(), before_other)
        self.assertEqual(self.reg.stat().st_mode & 0o777, 0o640)
        backup, = self.backups()
        self.assertEqual((backup / 'system.reg.before').read_bytes(), BASE)
        inode = self.reg.stat().st_ino
        self.assertIn('No change', self.run_cli())
        self.assertEqual(self.backups(), [backup])
        self.assertEqual(self.reg.stat().st_ino, inode)

    def test_existing_one_is_noop(self):
        data = fix.change(BASE, b'"amd"=dword:00000001\n')
        self.reg.write_bytes(data)
        self.run_cli()
        self.assertEqual(self.reg.read_bytes(), data)
        self.assertEqual(self.backups(), [])

    def test_unexpected_amd_dword_refused(self):
        data = fix.change(BASE, b'"AMD"=dword:00000002\n')
        self.reg.write_bytes(data)
        with self.assertRaisesRegex(RuntimeError, 'Unexpected AMD'):
            self.run_cli()
        self.assertEqual(self.reg.read_bytes(), data)

    def test_rollback_preserves_later_prerequisite(self):
        self.run_cli()
        backup, = self.backups()
        later = self.reg.read_bytes().replace(b'"directx"=dword:00000001', b'"directx"=dword:00000002')
        self.reg.write_bytes(later)
        self.run_cli('--rollback', str(backup))
        expected = BASE.replace(b'"directx"=dword:00000001', b'"directx"=dword:00000002')
        self.assertEqual(self.reg.read_bytes(), expected)
        count = len(self.backups())
        self.run_cli('--rollback', str(backup))
        self.assertEqual(len(self.backups()), count)

    def test_rollback_restores_zero(self):
        old = fix.change(BASE, b'"aMd"=dword:00000000\n')
        self.reg.write_bytes(old)
        self.run_cli()
        backup, = self.backups()
        self.run_cli('--rollback', str(backup))
        self.assertEqual(self.reg.read_bytes(), old)

    def test_printed_rollback_preserves_custom_steam_root(self):
        custom = self.home / 'Custom Steam'
        self.root.rename(custom)
        output = self.run_cli('--steam-root', str(custom))
        command = next(line for line in output.splitlines() if line.startswith('python3 '))
        argv = shlex.split(command)
        self.assertIn('--steam-root', argv)
        self.run_cli(*argv[2:])
        self.assertEqual(self.reg.read_bytes(), BASE)

    def test_rollback_rejects_changed_amd(self):
        self.run_cli()
        backup, = self.backups()
        self.reg.write_bytes(fix.change(BASE, b'"AMD"=dword:00000002\n'))
        with self.assertRaisesRegex(RuntimeError, 'AMD changed'):
            self.run_cli('--rollback', str(backup))

    def test_rollback_rejects_wrong_prefix_record(self):
        self.run_cli()
        backup, = self.backups()
        path = backup / 'record.json'
        record = json.loads(path.read_text())
        record['pfx_identity'][1] += 1
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(RuntimeError, 'identity/hash mismatch'):
            self.run_cli('--rollback', str(backup))

    def test_rollback_rejects_corrupt_backup(self):
        self.run_cli()
        backup, = self.backups()
        (backup / 'system.reg.before').write_bytes(b'bad')
        with self.assertRaisesRegex(RuntimeError, 'identity/hash mismatch'):
            self.run_cli('--rollback', str(backup))

    def test_backup_failure_leaves_original(self):
        with patch.object(fix, 'durable', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.run_cli()
        self.assertEqual(self.reg.read_bytes(), BASE)

    def test_concurrent_registry_change_refused(self):
        count = 0
        def race(_):
            nonlocal count
            count += 1
            if count == 2:
                self.reg.write_bytes(BASE + b'\n')
        with patch.object(fix.sys, 'argv', ['fix']), patch.object(fix, 'quiet', side_effect=race), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'changed'):
            fix.main()
        self.assertEqual(self.reg.read_bytes(), BASE + b'\n')

    def test_busy_processes_refused_without_kill(self):
        proc = self.home / 'proc'
        item = proc / '123456789'
        item.mkdir(parents=True)
        for comm, env in [(b'steam.exe', b''), (b'wineserver', b''), (b'FEX:DiskCache', b''),
                          (b'unknown', os.fsencode('WINEPREFIX=' + str(self.pfx)))]:
            (item / 'comm').write_bytes(comm)
            (item / 'cmdline').write_bytes(comm + b'\0')
            (item / 'environ').write_bytes(env)
            with self.subTest(comm=comm), self.assertRaisesRegex(RuntimeError, 'Still running'):
                fix.quiet(self.pfx, proc)

    def simple_process(self, name, args=None, env=b''):
        proc = self.home / 'proc'
        item = proc / '123456789'
        item.mkdir(parents=True, exist_ok=True)
        (item / 'comm').write_bytes(name)
        (item / 'cmdline').write_bytes(b'\0'.join(args or [name]) + b'\0')
        (item / 'environ').write_bytes(env)
        return proc, item

    def test_native_steam_and_gamescope_allowed(self):
        for name in (b'steam', b'steamwebhelper', b'steam-runtime-l', b'gamescope'):
            proc, _ = self.simple_process(name)
            fix.quiet(self.pfx, proc)

    def test_native_steam_with_target_env_still_blocks(self):
        proc, _ = self.simple_process(b'steam', env=b'SteamAppId=200260\0')
        with self.assertRaisesRegex(RuntimeError, 'Still running'):
            fix.quiet(self.pfx, proc)

    def test_prerequisite_wrapper_without_env_blocks(self):
        for args in ([b'reaper', b'SteamLaunch', b'AppId=200260', b'Install=1'],
                     [b'wrapper', b'legacycompat\\evaluatorscript_200260.vdf'],
                     [b'wrapper', os.fsencode(str(self.pfx / 'system.reg'))]):
            proc, _ = self.simple_process(b'wrapper', args)
            with self.subTest(args=args), self.assertRaisesRegex(RuntimeError, 'Still running'):
                fix.quiet(self.pfx, proc)

    def test_windows_steamservice_without_env_blocks(self):
        proc, _ = self.simple_process(b'SteamService.ex', [
            b'Z:\\steam\\legacycompat\\SteamService.exe',
            b'/installscript'])
        with self.assertRaisesRegex(RuntimeError, 'Still running'):
            fix.quiet(self.pfx, proc)

    def test_similarly_numbered_app_not_mistaken_for_target(self):
        proc, _ = self.simple_process(b'reaper', [b'reaper', b'AppId=2002600'])
        fix.quiet(self.pfx, proc)

    def plugin_fixture(self):
        proc = self.home / 'proc'
        child = proc / '123456789'
        parent = proc / '123456788'
        command = (b'/usr/bin/FEX\0' + os.fsencode(str(self.home / 'homebrew/services/PluginLoader')) +
                   b'\0' + os.fsencode(str(self.home / 'homebrew/services/PluginLoader')) + b'\0')
        for directory, comm in ((child, b'LSFG-VK 2 ARM64'), (parent, b'Decky Loader')):
            directory.mkdir(parents=True)
            (directory / 'comm').write_bytes(comm + b'\n')
            (directory / 'cmdline').write_bytes(command)
            (directory / 'cgroup').write_bytes(b'0::/system.slice/plugin_loader.service\n')
        (child / 'status').write_bytes(b'PPid:\t123456788\n')
        (parent / 'status').write_bytes(b'Uid:\t0\t0\t0\t0\n')
        return proc, child, parent

    def test_verified_decky_plugin_unreadable_env_allowed(self):
        proc, child, parent = self.plugin_fixture()
        original = Path.read_bytes
        original_stat = Path.stat
        def read(path):
            if path == child / 'environ':
                raise PermissionError('non-dumpable plugin')
            return original(path)
        def proc_stat(path, *args, **kwargs):
            st = original_stat(path, *args, **kwargs)
            if path == parent:
                return SimpleNamespace(**{**vars(st), 'st_uid': 0})
            return st
        with patch.object(Path, 'read_bytes', read), patch.object(Path, 'stat', proc_stat):
            fix.quiet(self.pfx, proc)

    def test_decky_exception_requires_all_identity_checks(self):
        proc, child, parent = self.plugin_fixture()
        comm = (child / 'comm').read_bytes().strip()
        args = (child / 'cmdline').read_bytes().split(b'\0')
        self.assertTrue(fix.known_decky_lsfg(child, comm, args, proc))
        self.assertFalse(fix.known_decky_lsfg(child, b'BatmanAC.exe', args, proc))
        self.assertFalse(fix.known_decky_lsfg(child, comm, [b'/usr/bin/FEX', b'wine', b''], proc))
        for path, invalid in [(child / 'cgroup', b'0::/user.slice/other.service\n'),
                              (parent / 'cgroup', b'0::/system.slice/other.service\n'),
                              (parent / 'status', b'Uid:\t1000\t1000\t1000\t1000\n'),
                              (parent / 'comm', b'unknown\n'),
                              (parent / 'cmdline', b'/usr/bin/FEX\0wine\0')]:
            old = path.read_bytes()
            path.write_bytes(invalid)
            self.assertFalse(fix.known_decky_lsfg(child, comm, args, proc), str(path))
            path.write_bytes(old)

    def test_decky_target_prefix_env_still_blocks(self):
        proc, child, parent = self.plugin_fixture()
        (child / 'environ').write_bytes(os.fsencode('WINEPREFIX=' + str(self.pfx)) + b'\0')
        # Remove the parent from iteration, retaining its identity files for lookup.
        with patch.object(Path, 'iterdir', return_value=iter([child])), \
                self.assertRaisesRegex(RuntimeError, 'Still running'):
            fix.quiet(self.pfx, proc)

    def test_unknown_fex_unreadable_env_still_blocks(self):
        proc, child, _ = self.plugin_fixture()
        (child / 'cgroup').write_bytes(b'0::/user.slice/unknown\n')
        original = Path.read_bytes
        def read(path):
            if path == child / 'environ':
                raise PermissionError('unknown process')
            return original(path)
        with patch.object(Path, 'read_bytes', read), \
                patch.object(Path, 'iterdir', return_value=iter([child])), \
                self.assertRaisesRegex(RuntimeError, 'Cannot inspect'):
            fix.quiet(self.pfx, proc)

    def test_root_refused(self):
        with patch.object(fix.os, 'getuid', return_value=0), patch.object(fix, 'discover') as discover:
            with self.assertRaisesRegex(RuntimeError, 'root'):
                self.run_cli()
            discover.assert_not_called()
        self.assertEqual(self.reg.read_bytes(), BASE)


if __name__ == '__main__':
    unittest.main(verbosity=2)
