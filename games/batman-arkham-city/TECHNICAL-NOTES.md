# Technical notes

## Scope and evidence

This package addresses two independent startup blockers in Batman: Arkham City GOTY, Steam App ID 200260, on the tested Armada OS / ARM64 handhelds. Its script is based on the independently device-tested `batman-amd-fix-v3.py`.

The investigation findings below come from the earlier Armada investigation. Device results are reported by the tester who performed the independent validations. Package preparation used local source review and synthetic tests only: no further device access, deployment, game launch, or device testing was performed.

## Issue 1: AMD Dual-Core Optimizer prerequisite

The observed execution chain was:

```text
Steam prerequisite evaluator
  → AMD_DCOptSetup.exe /S /v/qn
  → MSIEXEC.EXE /i .../Dual-Core Optimizer.msi /qn
  → installer custom action
  → process chain does not complete normally in the observed ARM64/FEX environment
  → Steam never records AMD prerequisite completion
```

The inspected game supplied `Setup/AMD_DCOptSetup.exe`; the extracted MSI identified the legacy Dual-Core Optimizer package. The custom-action path was investigated through process/thread state and installer artifacts. An exited process leader with a surviving FEX disk-cache thread and waiting installer parents strongly implicated the FEX/Wine process-exit lifecycle. This is a **strong hypothesis**, not proof of a specific defect in a particular FEX function. The investigation did not establish a normal final installer exit code reaching Steam, nor that the optimizer had installed successfully but Steam alone lost the completion record.

AMD Dual-Core Optimizer was intended for old AMD x86 dual-core systems. It has no corresponding hardware purpose on the tested ARM64 handhelds. Skipping it here is a platform-specific compatibility workaround, not a recommendation to bypass arbitrary prerequisites.

Steam's [InstallScript documentation](https://partner.steamgames.com/doc/sdk/installscripts) describes a per-process DWORD under `HasRunKey`: an absent/zero value requests execution, and successful completion records a value of one. The inspected game's `AMD` prerequisite uses that mechanism through the 32-bit registry view. Its physical machine-hive location is:

```text
HKLM\Software\Wow6432Node\Valve\Steam\Apps\200260
AMD = DWORD 1
```

The script **does not install or repair AMD Dual-Core Optimizer**. It records only this prerequisite as completed so Steam can continue. It preserves `vcredist`, `dotnet`, `directx`, and every other prerequisite value, and leaves partial AMD installer remnants intact. No `installscript.vdf` or `runasadmin.vdf` is edited.

## Issue 2: BatmanAC.exe UE3 Fatal Error

Once the AMD prerequisite was bypassed, `BatmanAC.exe` genuinely started. The tested reduced-x87-precision configuration then produced a UE3 Fatal Error. The stack's `filename not found` wording was treated as symbol/module resolution output, not evidence of a missing game asset.

The investigation observed x87 integer-conversion instructions, including a 64-bit integer load/store sequence (`FILD m64int` and `FISTP m64int`), in the running executable's relevant path. This correlated with reduced-precision integer round-trip problems. It does not by itself establish every intermediate corrupted value or explain all possible UE3 crashes.

**The full-x87 requirement was already documented by the FEX community.** The [FEX compatibility entry for this game](https://wiki.fex-emu.com/index.php/Batman:_Arkham_City_GOTY) identifies full x87 precision as necessary to avoid startup crashes. [FEX issue #5827](https://github.com/FEX-Emu/FEX/issues/5827) supplies related integer round-trip evidence from a different program, including a reproducer independent of Wine/Proton. That issue is supporting mechanism evidence, not a Batman-specific or AMD-optimizer-specific bug report.

Setting `FEX_X87REDUCEDPRECISION=0` resolved the startup failure on the tested devices. The recommended command retains Armada's existing launch wrapper:

```text
FEX_X87REDUCEDPRECISION=0 /usr/libexec/armada/armada-game-launch %command%
```

This work contributes Armada reproduction, diagnosis, integration, a scoped prerequisite-marker utility, and real-device validation. It does **not** claim discovery of the x87 requirement. No broader Proton/FEX profile change is required by this workflow.

## Validation record

| Environment | Reported result |
| --- | --- |
| AYN Odin 3 / Armada OS | AMD hang reproduced; v3 apply bypassed it; full-x87 launch option resolved the subsequent fatal error; approximately 30 minutes of actual gameplay tested. Rollback restored the original AMD marker state and the prerequisite problem reproduced again. |
| Retroid Pocket 6 / Armada OS | Independent installation/prefix; AMD issue reproduced; v3 apply bypassed it; x87 startup path validated. Independent rollback restored the original behavior. |

Odin 3 native performance varied significantly by scene. No performance optimization or frame-rate guarantee is claimed. On RP6, a first-run launcher UI alignment anomaly was observed once; its cause was not established, and it is separate from the validated apply/rollback and startup workarounds.

These observations do not establish universal compatibility, identical behavior across Armada devices, or fixes for unrelated launcher, rendering, and performance issues. Exact per-device OS/Proton/FEX version matrices were not supplied for both independent validations, so none are inferred here.

## Implementation and safety review

The utility uses Python's standard library and edits a recognized Wine text registry file offline. It is **not an official Valve API**. Wine's normal [registry tool](https://github.com/wine-mirror/wine/blob/master/programs/reg/reg.c) was considered, but starting a Proton/Wine runtime can initialize or synchronize additional state. This utility starts neither Wine nor Proton. The [Wine persistence implementation](https://github.com/wine-mirror/wine/blob/master/server/registry.c) is background for the recognized format, not a promise of a stable external editing API.

| Safeguard | Candidate behavior |
| --- | --- |
| Fixed scope | App ID 200260 is fixed; no arbitrary App ID or prefix option. |
| Library discovery | Reads native Steam's `libraryfolders.vdf`; checks installed manifests across listed libraries. No investigator-specific library path is embedded. |
| Installation identity | Requires matching App ID, installed `BatmanAC.exe`, and exactly one initialized `steamapps/compatdata/200260/pfx` in the game's library, with expected Proton metadata. |
| Unsupported targets | Rejects ambiguity, relevant directory symlinks, symlinked/hardlinked registry hives, unexpected ownership, and unsupported registry syntax. Never falls back to `~/.wine`. |
| Registry scope | Requires the existing physical 32-bit key in a `WINE REGISTRY Version 2` hive with a `win64` format header. Recognizes a limited set of DWORD/string entries and rejects duplicates or unexpected AMD types/values. |
| Idempotency | Absent AMD or DWORD 0 becomes DWORD 1; existing DWORD 1 is a no-op. Other values are refused. |
| Quiescence | Takes the existing Proton prefix lock and checks current-user process names, arguments and prefix/App ID environments. Rechecks before replacement and rejects a changed registry. |
| Background services | Native Steam/gamescope may remain open. Windows `steam.exe`/`SteamService.exe` and target prerequisite wrappers still block. A narrow LSFG/Decky exception verifies command, system-service cgroup and root Decky parent identity; it is not a PID-only or name-only exemption. Unknown relevant FEX processes may cause conservative refusal. No services are stopped or modified. |
| Backup and write | Creates a private new `~/batman-200260-backup-…/` directory, writes and verifies the original machine hive plus metadata, then performs an atomic replacement containing only the calculated AMD edit. Verifies the complete resulting file against those expected bytes. |
| Rollback | Validates backup hash and prefix identity, restores only the prior AMD value, preserves newer unrelated registry values, and backs up before changing anything. A moved/recreated prefix or conflicting AMD change causes refusal. |
| No other actions | No root/sudo, downloads, game-file edits, launch-option edits, prefix deletion/recreation, AMD-remnant cleanup, or process termination. |

The supported assumptions are native Linux Steam, Python 3, a user-owned initialized Proton prefix, and a filesystem supporting the locking, atomic rename and flush operations used. Flatpak/container Steam, manually redirected/shared prefixes and unrecognized registry formats are outside scope. A first Steam launch must have created the prefix; the utility does not create a missing prefix.

The process check and advisory lock are not a guarantee against a user or noncooperating program launching Wine at exactly the wrong instant. **Do not launch Batman or other Wine/FEX applications during apply or rollback.** Exiting Steam where practical reduces accidental launches, but native Steam's automatic startup is not itself a reason to stop the utility. No Steam configuration file is being edited.

Backups contain the user's own registry and local paths. They are for local recovery and should not be posted wholesale in a public issue. This package contains no actual backup or prefix data.

## Changes from device-tested v3

- Renamed the public candidate to `batman-amd-fix.py` and replaced the investigation-era opening description.
- Fixed a demonstrated defect in the **printed rollback command**: an apply using `--steam-root` now prints that argument with an absolute path for rollback. The new synthetic regression test failed on unchanged v3 and passed after the fix.
- Preserved registry apply/rollback transformations, backup format, discovery checks, process rules and the existing Decky exception. No new workaround or device feature was added.
- Generalized the existing synthetic tests' embedded example home path and registry timestamps; no real device artifacts are shipped.

The final candidate passed all 37 existing tests plus the new rollback-command regression test (38 total), along with local syntax/static checks. Device validation applies to v3's core behavior; the small public-candidate change was tested locally and was **not** deployed or retested on either handheld.

Final release review changed only synthetic test identity handling and documentation/license material. Normal CLI tests explicitly mock a representative non-root UID and matching fixture ownership; a dedicated test mocks UID 0 and verifies refusal before Steam discovery. The suite is designed to be root-runner-independent through this mocked UID behavior. An actual UID-0 test-runner environment was not available on this host, and no real root/container execution is claimed or required for this release review. The production script is byte-for-byte unchanged from the preceding public-review candidate.
