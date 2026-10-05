# NBA 2K27 on Armada OS

Steam App ID: **4356430**.

**Status: Not playable — upstream pending.**

**Investigated on AYN Odin 3.** No playable configuration validated.
This entry records an unresolved investigation, not an end-user workaround.

## Tested environment

The recorded 2026-10-05 investigation used AYN Odin 3 / Adreno 830,
Armada `20260926.c2fd048`, Linux `7.2.6` aarch64, and Proton
`experimental-11.0-20261001-arm64`. Rendering observations required an
isolated experimental FEX runtime. The graphics path was D3D12 →
VKD3D-Proton → Wine Vulkan → Turnip/Adreno → Gamescope.

These results describe that captured environment, not newer builds or other
devices. Component versions and evidence limits are in the
[technical notes](TECHNICAL-NOTES.md).

## Startup blocker

With the recorded stock FEX runtime, `NBA2K27.exe` terminated on RDTSCP with
`STATUS_ILLEGAL_INSTRUCTION` / `0xC000001D`.

The startup blocker was **experimentally resolved with an isolated FEX proof
of concept**. Standalone probes and game-level evidence showed execution past
the original fault and progress into shader compilation and later graphics
stages. The installed Armada FEX was not replaced. This establishes startup
progress only; the proof of concept is not an end-user workaround or a
production-ready fix.

## Rendering blocker and symptoms

Severe persistent flicker remained after shader compilation progressed or
finished. The agreement screen/background, an earlier complete copyright
page, and black content repeatedly appeared, preventing normal interaction
and play. Early text was observed to be stable; flicker began when it
disappeared. The corresponding graphics transition is unresolved.

The rendering root cause remains unassigned. The evidence does not establish
that the experimental FEX change caused the flicker.

## Current recommendation

Treat this game as not playable on the investigated setup and follow the
upstream reports for further investigation. There is no validated playable
configuration to recommend. This entry provides no experimental FEX
installation instructions.

## Upstream tracking

- [Armada rendering investigation #628](https://github.com/armada-os/armada/issues/628): cross-stack triage of the unresolved flicker.
- [FEX ProcessorID / RDTSCP / RDPID investigation #6009](https://github.com/FEX-Emu/FEX/issues/6009): the separate startup capability gap and experimental implementation.

These are submitted upstream investigation reports. Their submission does
not establish maintainer confirmation of the diagnosis, acceptance of the
patch, or commitment to a fix. See [references and attribution](REFERENCES.md).

## Offline / Online / EAC scope

**Offline only. NBA 2K27 game files were not modified.** The experiment
modified the isolated FEX compatibility runtime. Online/EAC was intentionally
not tested with that runtime; anti-cheat acceptance is unknown. Experimental
FEX is not recommended for Online/EAC use.

Original documentation is covered by [CC BY 4.0](../../LICENSE-DOCS).
Referenced third-party material retains its respective rights and licenses.
