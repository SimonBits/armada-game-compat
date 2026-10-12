# Stellar Blade on Armada OS

Steam App ID: **3489700**. Startup and short-session gameplay were validated
on **AYN Odin 3** with the workaround below. LSFG 2× was used successfully
in the earlier test, but later frame-generation tests showed ghosting,
jitter, and black screens. **Long-term LSFG stability is Not verified.**

This is a startup compatibility workaround, not a general performance
optimization or a claim of full compatibility.

## Game information and tested environment

| Field | Recorded environment |
| --- | --- |
| Game | Stellar Blade |
| Steam App ID | 3489700 |
| Platform / device | Armada OS / ARM64, AYN Odin 3 |
| Earlier startup test | 2026-09-30 UTC |
| Armada image in that test | 20260926.c2fd048 (Fedora 44), kernel 7.2.6 |
| GPU / driver in that test | Adreno 830 / Mesa Turnip 26.2.3 |
| Proton in that test | experimental-11.0-20260924-cache-arm64 |
| Renderer in that test | D3D12 / vkd3d-proton 3.1.0 |
| Steam build in that test | 24463856; separate game version label: Not recorded |
| Earlier LSFG setup | razoomnik LSFG-VK 2 ARM64, existing 2× profile |
| FPS / exact displayed frame-generation ratio | Not verified; no benchmark is claimed |

These versions belong to the September 30 record. The October 8 black-screen
investigation recorded the same Armada image but Proton
`experimental-11.0-20261001-arm64` and a different local LSFG setup.
October 8–9 diagnostic tests used experimental Phase 2E/2F/2G builds.
Their results must not be combined into one unchanged test environment.
The game used Proton's bundled ARM64EC FEX components; the system FEX
package version is not a verified version for those runtime components.

## Observed startup problem

In the September 30 comparison, the game started with LSFG disabled.
Enabling the existing LSFG 2× launch chain caused a startup crash, reproduced
twice. Both Proton logs recorded:

```text
err:vulkan:vkGetPastPresentationTimingEXT Exception 0xc0000005 in Unix call.
```

Adding `VKD3D_DISABLE_EXTENSIONS=VK_EXT_present_timing` to that LSFG launch
chain allowed entry into gameplay. The successful log confirmed that the
extension was disabled, the LSFG layer was loaded, and its existing 2×
profile was selected. The tester reported working gameplay with apparent
2× frame generation. This supports the tested startup workaround; it does
not prove every generated frame was displayed or establish a unique faulty
component in the presentation-timing path.

## Workaround

1. In Steam, open **Stellar Blade → Properties → General → Launch Options**.
2. Save the existing text, then use this base Armada launch option:

   ```text
   FEX_X87REDUCEDPRECISION=0 VKD3D_DISABLE_EXTENSIONS=VK_EXT_present_timing /usr/libexec/armada/armada-game-launch %command%
   ```

3. Start the game and check startup separately from LSFG behavior.

Preserve existing custom options. If the Armada wrapper is already present,
add or update the two variable assignments before it without duplicating
the wrapper. Preserve other entries in an existing
`VKD3D_DISABLE_EXTENSIONS` list. Apply these settings only to this game.

The command above does not install or enable LSFG. The successful LSFG
test also used its existing LSFG launcher and profile; later tests used
different integration. This entry does not prescribe an LSFG installation.

`VKD3D_DISABLE_EXTENSIONS` tells vkd3d-proton not to use the named extension,
as described in its [environment-variable documentation](https://github.com/HansKristian-Work/vkd3d-proton#environment-variables).
`FEX_X87REDUCEDPRECISION=0` disables FEX's reduced-precision x87 mode; see
the [FEX configuration definitions](https://github.com/FEX-Emu/FEX/blob/main/FEXCore/Source/Interface/Config/Config.json.in).
The x87 setting was retained throughout the earlier comparison, so that
comparison does not independently establish its necessity for this game.
Neither setting is evidence of a general FPS improvement or a driver fix.

To undo, stop the game and restore the saved launch options. No game-file
or global system-configuration changes are required by this workaround.

## LSFG validation and unresolved issues

| Evidence | Result and scope |
| --- | --- |
| 2026-09-30 startup comparison | No-LSFG baseline started; existing LSFG 2× chain failed twice; disabling the extension allowed gameplay with LSFG 2× enabled. Short-session validation only. |
| Later tester observations | Ghosting, jitter, and black screens occurred during LSFG testing. Disabling LSFG restored the picture during reported black-screen cases. Exact timestamps for every visible symptom: Not recorded. |
| 2026-10-08 Phase 2E diagnostics | Repeated swapchain/context recreation and frame-history resets were logged. Diagnostic output budgets were exhausted before the full black-screen window was covered. |
| 2026-10-09 Phase 2F diagnostics | Repeated recreation and frame-history resets were again observed; they are diagnostic findings, not proof of the sole black-screen cause. |
| 2026-10-09 Phase 2G follow-up | Limited sessions with a candidate fix showed less repeated recreation and no tester-observed black screen. These different-build results do not certify the earlier setup or long-term stability. |

The recorded present-related budget exhaustion concerns **diagnostic log
output**, not established exhaustion of GPU presentation resources. Once
a logging budget is exhausted, missing events cannot be treated as proof
that no errors occurred.

Recovery after disabling LSFG implicates its additional processing or its
interaction with the surrounding graphics stack, but does not isolate a
single algorithm, driver, Proton, FEX, or synchronization defect. Startup
success and LSFG image quality/stability remain separate conclusions.

## Known limitations

- The unique root cause of the LSFG black screens is **Not verified**.
- Long-session stability, every launch/restart path, and all display or
  frame-generation settings are **Not verified**.
- Other devices and OS/Proton/driver combinations are **Not verified**.
- The launch option does not guarantee resolution of later LSFG artifacts,
  black screens, or unrelated D3D12 failures.
- The earlier test did not independently capture each generated frame's
  display identity. Configuration and layer loading alone are not proof
  of an exact output multiplier or consistently correct frame pacing.

## Evidence and attribution

This entry summarizes prior device tests, local logs, and the tester's
observations. No new game launch or device test was performed while writing
it. Local records reviewed under `stellar-blade-lsfg-test-20260930` include:

- `REPORT.txt`, `environment.json`, and `steam-details.json`: September 30
  test account, recorded system/runtime versions, and Steam build identity.
  `device/lsfg2x/steam-3489700.log`,
  `device/lsfg2x-repro/steam-3489700.log`, and
  `device/lsfg2x-no-present-timing/steam-3489700.log` contain the startup
  failure/reproduction and successful extension-disable evidence.
- `ab-20261003T012847Z/PREFLIGHT-REPORT.txt` records user-observed ghosting;
  its staged alternative had not yet been run. The October 8
  `stellar-blade-lsfg-black-screen-20261008/ENVIRONMENT.md` and
  `phase2e/REPORT.md` distinguish the later environment and reported
  recovery after disabling LSFG.
- `phase2e/test-analysis-20261008T153741Z/REPORT.md` and its
  `evidence/user-journal.txt` record repeated recreation and
  `budget_last=1`. The Phase 2F report in
  `phase2f/test-analysis-20261009T023629Z` and Phase 2G reports in
  `phase2g/stability-analysis-20261009T044206Z` and
  `phase2g/1080p-analysis-20261009T053037Z` record the later diagnostic
  findings and limited candidate-fix observations.

These are local archive identifiers, not public links or files distributed
with this entry. Jitter and the visible recovery behavior are attributed
to tester reports rather than inferred from API logs. Upstream references
above explain the settings; they do not independently validate this device.

Original documentation uses the repository's [CC BY 4.0](../../LICENSE-DOCS).
Upstream software, documentation, game assets, names, and trademarks retain
their respective rights and licenses.
