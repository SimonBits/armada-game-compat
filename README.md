# Armada Game Compatibility

Real-device tested game compatibility notes, startup fixes, and workarounds
for Armada OS on ARM64 handhelds.

Entries cover both original project investigations and existing upstream or
community workarounds independently validated on Armada, with attribution to
the original sources.

Each game entry records:

- The observed compatibility problem.
- Any tested workaround, or the remaining unresolved blockers.
- The validation devices, or explicitly identified investigation-only devices.
- Known limitations.

## Games

| Game | Steam App ID | Issue | Status | Validated Devices | Source |
| --- | ---: | --- | --- | --- | --- |
| [Batman: Arkham City GOTY](games/batman-arkham-city/) | 200260 | AMD prerequisite hang + x87 startup crash | Workaround available | AYN Odin 3, Retroid Pocket 6 | Investigation + upstream |
| [Slay the Spire 2](games/slay-the-spire-2/) | 2868840 | Native Linux/CoreCLR startup crash under FEX | Workaround available | AYN Odin 3, Retroid Pocket 6, Retroid Pocket Nova (user report) | Investigation + upstream |
| [Silent Hill 2 Enhanced Edition](games/silent-hill-2-enhanced-edition/) | Non-Steam | Non-Steam launch / DLL override configuration | Working configuration | AYN Odin 3 | Armada validation |
| [NBA 2K27](games/nba-2k27/) | 4356430 | RDTSCP startup blocker experimentally resolved; severe rendering flicker unresolved | Not playable — upstream pending | No playable configuration validated; investigated on AYN Odin 3 | Original investigation |

**Not playable — upstream pending** identifies an evidence-backed unresolved
investigation with submitted upstream reports and no validated playable
configuration. It does not imply upstream acceptance of a diagnosis or fix.
Investigation-only devices in the table are not validated playable devices.

The **Source** field distinguishes:

- **Original investigation**: original evidence-backed investigation; the problem may remain unresolved and no working workaround is implied.
- **Investigation + upstream**: the Armada-specific problem was investigated and the workaround integrated here; relevant existing upstream knowledge is credited in the game entry.
- **Upstream/community workaround, Armada validated**: the workaround already existed elsewhere; this repository records independent real-device validation on Armada OS and credits the original source.
- **Armada validation**: a working configuration independently tested on Armada; no original upstream bug/fix discovery is claimed.

## Repository Structure

Game directories under `games/` may contain user-facing instructions,
validation results, technical investigation notes, upstream/community
references, and helper scripts where required. Contents vary by game entry.
Licensing is divided between original software/code and original documentation;
see [License](#license).

## Scope

- Native Steam / Proton / FEX on Armada OS.
- Real-device testing on ARM64 handhelds, with the tested devices and limits documented.
- No universal compatibility guarantee.
- Performance optimization is not implied unless explicitly documented.

Read the relevant game entry before applying a workaround. Upstream knowledge
and project-specific findings are attributed separately in each entry.

## License

- Original software/code in this repository is licensed under the [MIT License](LICENSE) — Copyright (c) 2026 SimonBits.
- Original documentation authored for this repository is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DOCS).

These categories apply to current and future original repository material.
Third-party/upstream software, documentation, game assets, trademarks, names,
and referenced or quoted materials remain subject to their respective rights
and licenses; this licensing structure does not relicense them.

Earlier public revisions remain available under the license terms under which
they were originally released. This change does not revoke or remove rights
already granted under MIT for those revisions.
