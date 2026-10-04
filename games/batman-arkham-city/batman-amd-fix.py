#!/usr/bin/env python3
"""Offline AMD prerequisite marker fix for Batman: Arkham City GOTY (App 200260).

No Wine invocation, default-prefix fallback, downloads or Steam config writes.
Steam/gamescope may stay open. Stop Batman and its installer first; do not
launch Batman or other Wine/FEX applications during this run.
This is a narrowly validated Wine registry-file edit, not an official Valve API.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import sys
import tempfile

APP = "200260"
KEY = rb"Software\\Wow6432Node\\Valve\\Steam\\Apps\\200260"
MARKER = b'"AMD"=dword:00000001\n'
LAUNCH = "FEX_X87REDUCEDPRECISION=0 /usr/libexec/armada/armada-game-launch %command%"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def vdf(text):
    """Read the quoted textual KeyValues subset; reject unsupported syntax.

    Used ONLY for libraryfolders.vdf and appmanifest_200260.acf. Never serialize VDF.
    """
    token = re.compile(r'\s+|//[^\n]*|"(?:\\.|[^"\\])*"|[{}]')
    tokens, pos = [], 0
    while pos < len(text):
        m = token.match(text, pos)
        require(m is not None, "Unsupported Steam metadata syntax; no changes.")
        raw = m.group()
        pos = m.end()
        if raw.isspace() or raw.startswith('//'):
            continue
        if raw.startswith('"'):
            value = raw[1:-1]
            require(re.fullmatch(r'(?:[^\\]|\\[\\"])*', value) is not None, "Unsupported VDF escape.")
            tokens.append(("s", re.sub(r'\\([\\"])', r'\1', value)))
        else:
            tokens.append((raw, raw))
    index = 0

    def obj(nested=False):
        nonlocal index
        out = {}
        while index < len(tokens):
            kind, key = tokens[index]
            index += 1
            if kind == "}" and nested:
                return out
            require(kind == "s" and index < len(tokens), "Malformed Steam metadata.")
            kind, value = tokens[index]
            index += 1
            if kind == "{":
                value = obj(True)
            else:
                require(kind == "s", "Malformed Steam metadata value.")
            key = key.lower()
            require(key not in out, "Duplicate Steam metadata key; refusing ambiguity.")
            out[key] = value
        require(not nested, "Unclosed Steam metadata block.")
        return out
    return obj()


def discover(home, steam_override=None):
    roots = [Path(steam_override).expanduser()] if steam_override else [
        home / '.steam/steam', home / '.steam/root', home / '.local/share/Steam',
        Path(os.environ.get('XDG_DATA_HOME', str(home / '.local/share'))) / 'Steam']
    roots = {p.resolve() for p in roots if (p / 'steamapps/libraryfolders.vdf').is_file()}
    require(len(roots) == 1, "Cannot identify one native Steam installation. Use --steam-root PATH.")
    root = roots.pop()
    folders = vdf((root / 'steamapps/libraryfolders.vdf').read_text()).get('libraryfolders')
    require(isinstance(folders, dict), "Invalid libraryfolders.vdf.")
    libraries = {root}
    for number, entry in folders.items():
        if number.isdigit():
            path = entry.get('path') if isinstance(entry, dict) else entry
            require(isinstance(path, str) and Path(path).is_absolute(), "Invalid Steam library path.")
            libraries.add(Path(path).resolve())
    installed, prefixes = [], []
    for library in sorted(libraries):
        manifest = library / 'steamapps/appmanifest_200260.acf'
        if manifest.exists():
            state = vdf(manifest.read_text()).get('appstate', {})
            require(isinstance(state, dict) and state.get('appid') == APP,
                    "App manifest identity mismatch; no changes.")
            name = state.get('installdir', '')
            require(isinstance(name, str) and name not in ('', '.', '..') and '/' not in name,
                    "Invalid game installation directory.")
            require((library / 'steamapps/common' / name / 'Binaries/Win32/BatmanAC.exe').is_file(),
                    "Manifest exists but BatmanAC.exe was not found; no changes.")
            installed.append((library, manifest))
        if (library / 'steamapps/compatdata/200260/pfx').exists():
            prefixes.append(library)
    require(len(installed) == 1, "Expected exactly one installed App 200260; no changes.")
    library, manifest = installed[0]
    require(prefixes == [library], "Missing, relocated or ambiguous App 200260 prefix; no changes.")
    compat = library / 'steamapps/compatdata/200260'
    pfx = compat / 'pfx'
    for p in (library / 'steamapps', compat.parent, compat, pfx):
        require(p.is_dir() and not p.is_symlink(), "Linked prefix/layout is unsupported; no changes.")
    require(pfx.resolve() != (home / '.wine').resolve(), "Default Wine prefix is forbidden.")
    for rel in ('system.reg', 'user.reg', 'userdef.reg'):
        check_file(pfx / rel)
    for rel in ('version', 'config_info', 'pfx.lock'):
        check_file(compat / rel)
    require((pfx / 'drive_c/windows').is_dir(), "Prefix is not initialized.")
    require(pfx.stat().st_uid == os.getuid(), "Prefix is not owned by this user.")
    return root, manifest, pfx


def check_file(path):
    st = path.lstat()
    require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_uid == os.getuid(),
            f"Expected an ordinary file owned by you (no symlinks/hardlinks): {path}")
    return st


def registry(data):
    require(data.startswith(b'WINE REGISTRY Version 2\n') and b'\n#arch=win64\n' in data[:1024],
            "Unsupported Wine registry header/architecture.")
    require(b'\r' not in data and data.endswith(b'\n'), "Unexpected registry line format.")
    sections = list(re.finditer(rb'(?m)^\[([^\n]*)\][^\n]*\n', data))
    matches = [(i, m) for i, m in enumerate(sections) if m[1].lower() == KEY.lower()]
    require(len(matches) == 1, "Expected one existing 32-bit Steam App 200260 key; no changes.")
    i, header = matches[0]
    end = sections[i+1].start() if i+1 < len(sections) else len(data)
    body = data[header.end():end]
    # This Steam prerequisite key contains DWORDs, single-line strings and Wine metadata.
    # Refuse escaped names, multiline values, duplicate names or future formats.
    seen, value_span = set(), None
    offset = header.end()
    for line in body.splitlines(keepends=True):
        if line.strip() and not line.startswith((b'#', b';')):
            m = re.fullmatch(rb'"([^"\\]+)"=(dword:[0-9a-fA-F]{8}|"(?:\\.|[^"\\])*")\n', line)
            require(m is not None, "Unexpected prerequisite key contents; no changes.")
            name = m[1].lower()
            require(name not in seen, "Duplicate prerequisite marker; no changes.")
            seen.add(name)
            if name == b'amd':
                require(m[2].startswith(b'dword:'), "AMD is not a DWORD; no changes.")
                value_span = (offset, offset + len(line), int(m[2][6:], 16))
        offset += len(line)
    return header.end(), value_span


def change(data, desired):
    insert, span = registry(data)
    if span:
        start, end, _ = span
        return data[:start] + (desired or b'') + data[end:]
    return data[:insert] + (desired or b'') + data[insert:]


def known_decky_lsfg(proc, comm, args, proc_root):
    """Recognize the observed unrelated, non-dumpable Armada LSFG plugin.

    A name or PID alone is insufficient. Require the exact native PluginLoader
    command, system-service cgroup and root-owned Decky parent identity. Unknown
    layouts fail closed. A readable target-prefix environment still takes priority.
    """
    if comm != b'LSFG-VK 2 ARM64':
        return False
    loader = os.fsencode(str(Path.home().resolve() / 'homebrew/services/PluginLoader'))
    expected = [b'/usr/bin/FEX', loader, loader]
    if args != expected + [b'']:
        return False
    try:
        group = b'0::/system.slice/plugin_loader.service\n'
        if (proc / 'cgroup').read_bytes() != group:
            return False
        parent_match = re.search(rb'(?m)^PPid:\s*(\d+)\s*$', (proc / 'status').read_bytes())
        if parent_match is None:
            return False
        parent = proc_root / parent_match[1].decode()
        return ((parent / 'comm').read_bytes().strip() == b'Decky Loader' and
                (parent / 'cmdline').read_bytes().split(b'\0') == expected + [b''] and
                (parent / 'cgroup').read_bytes() == group and
                re.search(rb'(?m)^Uid:\s*0\s+0\s+0\s+0\s*$',
                          (parent / 'status').read_bytes()) is not None)
    except OSError:
        return False


def quiet(pfx, proc_root=Path('/proc')):
    require(proc_root.is_dir(), "Cannot inspect processes; no changes.")
    busy = []
    # Native Steam/gamescope do not own Wine's registry. Windows SteamService.exe
    # and steam.exe do belong to the prerequisite runtime and must still block.
    suspect = re.compile(rb'(?i)^(steam(?:service)?\.exe|wineserver.*|wine(?:64|boot|preloader)?|proton|fex.*|batmanac\.exe|msiexec\.exe|iscriptevaluator\.exe|amd_dcoptsetup\.exe)$')
    for proc in proc_root.iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            comm = (proc / 'comm').read_bytes().strip()
            args = (proc / 'cmdline').read_bytes().split(b'\0')
            names = [comm] + [a.replace(b'\\', b'/').rsplit(b'/', 1)[-1] for a in args[:2]]
            relevant = any(suspect.fullmatch(n) for n in names)
            if relevant and known_decky_lsfg(proc, comm, args, proc_root):
                relevant = False
            # Catch Steam's launcher/install-script wrappers before Wine starts,
            # including when the target environment is unavailable or not yet set.
            for arg in args:
                normalized = arg.replace(b'\\', b'/')
                base = normalized.rsplit(b'/', 1)[-1].lower()
                if arg.lower() in (b'appid=200260', b'steamappid=200260', b'steamgameid=200260'):
                    relevant = True
                if base in (b'evaluatorscript_200260.vdf', b'appmanifest_200260.acf'):
                    relevant = True
                if arg.startswith(b'/'):
                    path = Path(os.fsdecode(arg)).resolve()
                    if path == pfx.parent or pfx.parent in path.parents:
                        relevant = True
            try:
                env = (proc / 'environ').read_bytes().split(b'\0')
            except PermissionError:
                require(not relevant, f"Cannot inspect possible game process PID {proc.name}.")
                env = []
            for item in env:
                key, _, value = item.partition(b'=')
                if key in (b'WINEPREFIX', b'STEAM_COMPAT_DATA_PATH') and value:
                    relevant |= Path(os.fsdecode(value)).resolve() in (pfx, pfx.parent)
                if key in (b'SteamAppId', b'SteamGameId') and value == b'200260':
                    relevant = True
            if relevant:
                busy.append(proc.name)
        except (FileNotFoundError, ProcessLookupError):
            continue
    require(not busy, "Stop Batman and its prerequisite installer; close any remaining Wine/FEX applications. "
            "Steam/gamescope may stay open. Do not launch Batman during this script. "
            "Still running PIDs: " + ', '.join(busy) + ". Nothing was killed.")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def durable(path, data):
    with path.open('xb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def commit(pfx, old, new, home, mode, steam_root=None):
    reg = pfx / 'system.reg'
    before = check_file(reg)
    # Full original hive plus a scoped rollback record, stored outside the prefix.
    # Use a private new directory in HOME: no extra package or XDG state-path dependency.
    backup = Path(tempfile.mkdtemp(prefix='batman-200260-backup-', dir=home))
    durable(backup / 'system.reg.before', old)
    _, after_span = registry(new)
    _, before_span = registry(old)
    after_value = after_span[2] if after_span else None
    before_value = before_span[2] if before_span else None
    record = {'app_id': APP, 'pfx': str(pfx), 'pfx_identity': [pfx.stat().st_dev, pfx.stat().st_ino],
              'before_sha256': digest(old), 'after_sha256': digest(new), 'amd_after': after_value, 'mode': mode}
    durable(backup / 'record.json', json.dumps(record, indent=2).encode())
    sync_dir(backup)
    sync_dir(home)
    require((backup / 'system.reg.before').read_bytes() == old, "Backup verification failed.")
    print(f"Verified backup: {backup}", flush=True)
    fd, temp = tempfile.mkstemp(prefix='.batman-amd-', dir=pfx)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(new)
            f.flush()
            os.fsync(f.fileno())
        shutil.copystat(reg, temp)
        quiet(pfx)
        now = check_file(reg)
        require((before.st_dev, before.st_ino, before.st_mtime_ns) ==
                (now.st_dev, now.st_ino, now.st_mtime_ns) and reg.read_bytes() == old,
                "Registry changed while preparing backup; no write performed.")
        os.replace(temp, reg)
        sync_dir(pfx)
        require(reg.read_bytes() == new, "Post-write verification failed; preserve the printed backup.")
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    print("Verified: only the AMD value in HKLM\\Software\\Wow6432Node\\Valve\\Steam\\Apps\\200260 changed.")
    print(f"AMD: {before_value if before_value is not None else 'absent'} -> "
          f"{after_value if after_value is not None else 'absent'} (numeric values are DWORDs).")
    argv = ['python3', str(Path(__file__).resolve()), '--rollback', str(backup)]
    if steam_root is not None:
        argv += ['--steam-root', str(Path(steam_root).expanduser().resolve())]
    command = shlex.join(argv)
    print("Undo this registry change (with Batman and its Wine/installer processes stopped):\n" + command)
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steam-root', help='Native Steam client directory, only if autodetection fails')
    parser.add_argument('--check', action='store_true', help='Read-only discovery and proposed change; no backup/write')
    parser.add_argument('--rollback', metavar='BACKUP_DIRECTORY', help='Restore ONLY the previous AMD value')
    args = parser.parse_args()
    require(os.getuid() != 0, "Run as your ordinary Steam user; never use sudo/root.")
    home = Path.home().resolve()
    _, _, pfx = discover(home, args.steam_root)
    print(f"Verified Steam App {APP}, prefix: {pfx}")
    # Existing Proton lock serializes cooperating launchers. Process checks are also
    # required because an established wineserver need not hold this lock.
    with (pfx.parent / 'pfx.lock').open('rb') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        quiet(pfx)
        data = (pfx / 'system.reg').read_bytes()
        _, span = registry(data)
        if args.rollback:
            backup = Path(args.rollback).expanduser().resolve()
            record = json.loads((backup / 'record.json').read_text())
            prior = (backup / 'system.reg.before').read_bytes()
            require(isinstance(record, dict) and record.get('app_id') == APP and record.get('pfx') == str(pfx) and
                    record.get('pfx_identity') == [pfx.stat().st_dev, pfx.stat().st_ino] and
                    record.get('before_sha256') == digest(prior), "Backup identity/hash mismatch.")
            _, previous_span = registry(prior)
            desired = prior[previous_span[0]:previous_span[1]] if previous_span else None
            old_value = previous_span[2] if previous_span else None
            value = span[2] if span else None
            require('amd_after' in record and value in (record['amd_after'], old_value),
                    "AMD changed since the fix; refusing rollback.")
            new = data if value == old_value else change(data, desired)
        else:
            require(span is None or span[2] in (0, 1), "Unexpected AMD DWORD; refusing overwrite.")
            new = data if span and span[2] == 1 else change(data, MARKER)
        if new == data:
            print("No change: AMD is already in the requested state. No new backup needed.")
        elif args.check:
            print("CHECK ONLY: would back up system.reg and " +
                  ("restore its previous AMD value." if args.rollback else "set AMD = DWORD 1."))
        else:
            os.umask(0o077)
            commit(pfx, data, new, home, 'rollback' if args.rollback else 'apply', args.steam_root)
    if not args.rollback:
        print("\nSteam > Batman: Arkham City GOTY > Properties > General > Launch Options:\n" + LAUNCH)
        print("Save your old launch options first. If the Armada wrapper is already there, add only "
              "FEX_X87REDUCEDPRECISION=0 at the beginning. Preserve custom options; do not duplicate the wrapper.")
    print("Steam launch options were not edited. The game was not started.")


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, RecursionError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
