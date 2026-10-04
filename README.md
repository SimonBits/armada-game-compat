# Armada Game Compatibility

Real-device tested game compatibility notes, startup fixes, and workarounds for **Armada OS on ARM64 handhelds**.

Each entry documents the observed issue, tested workaround, validation devices, and known limitations. Results are based on actual testing and do not guarantee identical behavior across all devices or Armada OS versions.

## Games

| Game | Steam App ID | Status | Validated Devices |
| --- | ---: | --- | --- |
| Batman: Arkham City GOTY | 200260 | Workaround available | AYN Odin 3, Retroid Pocket 6 |

## Repository Structure

Each game has its own directory under `games/`.

For example:

`games/batman-arkham-city/`

Individual game directories may contain:

- User-facing workaround instructions
- Helper scripts when required
- Technical investigation notes
- Upstream references
- Validation information

## Scope

This repository focuses on game compatibility with **native Steam / Proton / FEX on Armada OS**.

A listed workaround means it was tested on the devices shown in the table. It does not guarantee identical behavior on every ARM64 device or future Armada OS release.

Performance optimization is outside the scope unless explicitly documented for a specific game.

## License

Original utilities and documentation in this repository are released under the MIT License unless otherwise noted.
