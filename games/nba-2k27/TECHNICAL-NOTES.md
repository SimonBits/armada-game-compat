# NBA 2K27 technical investigation notes

**Not playable — upstream pending. Investigated on AYN Odin 3.**
No playable configuration validated. This summarizes evidence collected by
2026-10-05; preparing this entry involved no new game runs. Public reports
and their evidence attachments are linked in [REFERENCES.md](REFERENCES.md).

## Captured environment

| Component | Recorded identity |
| --- | --- |
| Device / GPU | AYN Odin 3, ARM64 / Adreno 830 |
| OS / kernel | Armada `20260926.c2fd048` / Linux `7.2.6` aarch64 |
| Game | Steam App ID `4356430`, BuildID `25221291` |
| Proton | `experimental-11.0-20261001-arm64` |
| Stock translator | Bundled `libarm64ecfex.dll`, `FEX-2609-137-g0df84d3` |
| Experimental FEX base | `0df84d3844bcdb87bb7d3f5b8fb0959cd009c038` |
| VKD3D-Proton | `3.1.0`, commit `44cf7c2042168f3b8ee37249f0a53ac091e48fd9` |
| DXVK / DXGI | `v3.1.1-47-g685301564ea3486` |
| Turnip / Mesa | `26.2.3`; `mesa-vulkan-drivers-26.2.3-1.fc44.armada.aarch64` |
| Gamescope | `terra-gamescope-3.16.29^2-1.092414.fc44.armada.aarch64` |

The measured translator was the Wine/ARM64EC DLL, not the system
FEXInterpreter package. Exact Wine/Proton and downstream Mesa/Gamescope source
commits were not established; package identifiers must not be treated as
proof of unmodified upstream source. Binary hashes and fuller provenance are
in the upstream attachments. The experimental prefix retained earlier locale
changes; this was not a clean-prefix baseline.

NBA 2K27 game files were not modified. The experiment used isolated FEX
binaries and caches without replacing installed system components. All
game-level results here concern Offline mode. Online/EAC was intentionally
not tested with the experimental runtime and is not recommended: acceptance
of that modified compatibility environment is unknown.

## Startup: confirmed fault and experimental resolution

The original failure was at `NBA2K27.exe+0x4B30D20`. Runtime bytes
`0F 01 F9` confirmed RDTSCP; the resulting unhandled exception was
`STATUS_ILLEGAL_INSTRUCTION` / `0xC000001D`. The game process exited with
Linux exit code **84**. The later winedbg failure was secondary.

An independent guest probe measured the RDTSCP capability bit as **0**, then
reproduced `C000001D` by executing RDTSCP. Stock behavior was internally
consistent with CPUID; FEX was not falsely advertising RDTSCP. The game
executed the instruction, but its own CPUID decision logic was not traced,
so this does not establish that it ignores CPUID.

At the pinned FEX revision, the decoder recognized RDTSCP, but Wine/ARM64EC
disabled the TPIDRRO CPU-index path and the Windows ProcessorID JIT branch
lacked an API fallback. The instruction dispatch guards therefore rejected
RDTSCP/RDPID without an available CPU-ID path. Independent affinity tests
showed usable CPU-number APIs; this was not an inability to obtain CPU
numbers at all. Stock RDPID execution was not separately tested.

The isolated proof of concept added a checked, single-processor-group CPU-API
fallback for ProcessorID, updated capability exposure and dispatch together,
preserved guest state around the call, and retained the existing TSC path.
It is an experimental implementation for upstream discussion, not an
end-user workaround.

Standalone validation recorded:

- RDTSCP/RDPID capability bits became 1 and both instructions executed.
- CPU identification matched under fixed affinity across CPUs 0–5;
  multithread testing passed.
- RDTSCP checks covered registers, flags, output zero-extension, x87,
  XMM/YMM, and floating-point control state.
- Timestamp continuity/rate agreed with RDTSC/QPC; disabled, cold, and warm
  cache runs reported no failures.
- Forced-affinity tests observed approximately 1,700 AUX transitions per run
  without timestamp regression or out-of-range CPU IDs. This is not an exact
  count of kernel migrations or proof of atomic TSC/AUX association.

These checks do not cover every architectural, memory-ordering, topology, or
migration edge case. AUX was a single-group CPU index in this experiment.
The API fallback had measurable cost relative to RDTSC; probe loop timings
do not establish game performance overhead or production readiness.

Game-level hardware execution evidence mapped to the following guest RET
at `+0x4B30D25`, beyond RDTSCP and `MOV EAX,ECX`. The original unhandled
startup fault did not recur, and shader compilation/later graphics stages
were reached. This is not a claim that every later `C000001D` log entry
disappeared or that the game became playable.

## Rendering: confirmed symptoms and evidence limits

The confirmed path was **D3D12 → VKD3D-Proton → Wine Vulkan →
Turnip/Adreno → Gamescope**. DXVK supplied DXGI; that does not establish a
D3D11 rendering path. The native presentation path included the Gamescope
WSI XWayland-bypass layer, with XWayland still used for window management.

Multiple Offline runs showed severe persistent flicker: agreement UI or
background, an earlier complete copyright page, and black content repeatedly
appeared after shader compilation progressed/finished. Early text was stable
before its disappearance and flicker onset, but no specific graphics-state
transition has been tied to that observation.

### Queue profiler: ongoing progress during confirmed flicker

In an 84-second late window with directly observed severe flicker, the
profiler recorded 19,821 submissions, 19,819 completion notifications and
4,955 Present markers (about 59/s). The two remaining recorded submissions
completed after the window; no sustained growth of the observed backlog was
found. A persistent global queue/submission stall is therefore lower priority.

This does not prove correct pixels or exclude synchronization/visibility
errors. Completion lanes were host observations, not GPU timestamps;
never-completed or unemitted work cannot be ruled out. Parsed-event integrity
was checked, but the profiler has no comprehensive loss counter and the
shutdown tail lacked two present-wait records. Profiling can perturb timing.
The conclusion applies to the late window, not every startup stage.

### Invalid VBO / NULL VA: confirmed anomaly, causality unproven

Numerous invalid-VBO warnings occurred. Bounded runtime sampling directly
confirmed two nonzero GPU VAs returning NULL from `vkd3d_va_map_deref()`.
Successful lookups on the same command list / slot 0 followed approximately
18.333 and 38.332 microseconds later. These CPU observation intervals include
tool overhead; they are not measured GPU durations or NULL-state lifetimes.

Neither consumption of the NULL state by a Draw nor a chain from that state
to submission and incorrect pixels was established. Warning volume and NULL
lookups alone do not make VBO binding the rendering root cause.

### Image identity: valid sample with a critical coverage gap

A separate 17.423-second hardware sample produced **3,072 events / 1,024
complete CPU-side identity chains**, with no `LOST` / `LOST_SAMPLES`.
Thread/process identity, event pairing, and installation-lifecycle checks
passed. Backbuffer/resource → VkImage/index mapping rotated consistently;
Present sequences and valid IDs **42–1065** were continuous, all recorded
results were `VK_SUCCESS`, and all used the blit path.

WSI logs distinguished separate swapchain lifecycles despite reuse of the
same numeric handle. The sampling points did not directly capture numeric
`VkSwapchainKHR`, so that handle was not unambiguously joined to the CPU
chains. No complete compositor/scanout content chain was obtained.

**This window did not reliably cover the severe flicker or the transition
from stable text to flicker.** It cannot exclude presentation/image-selection
faults. Screenshots roughly 2.1 seconds apart were not per-Present ground
truth. Three visible content classes do not establish triple-buffer rotation
or a fixed image-to-content relationship.

### Other observations and unresolved attribution

ROV shader capability rejection, occasional presentation-related errors,
and early sleep/resume records were observed without a demonstrated causal
link to flicker. Optional Proton DLL-copy errors were not the captured direct
cause of the original Offline termination or an established rendering cause.
An earlier run was manually terminated with SIGTERM; later bounded runs
exited with code 0 after requested closure. Neither establishes gameplay
stability, and manual termination must not be presented as a spontaneous crash.

High-confidence observations establish the startup fault, experimental
crossing, reproducible flicker, and the bounded measurements above. The
rendering root cause remains unresolved. Current evidence cannot assign it
to Armada, VKD3D-Proton, Wine/WSI, Turnip, Gamescope, the game, or another
component, and does not establish that the experimental FEX change caused it.
The two submitted reports seek upstream investigation, not endorsement of a
diagnosis or a promise of a fix. **No playable configuration validated.**

Original documentation is covered by [CC BY 4.0](../../LICENSE-DOCS).
Referenced third-party material retains its respective rights and licenses.
