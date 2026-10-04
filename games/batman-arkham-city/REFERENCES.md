# References and attribution

These are upstream references used to check the investigation's interpretation. Upstream documentation and issue reports are distinct from the tester's Armada observations. Links were reviewed during package preparation; live pages and source branches may change.

## Existing FEX community knowledge

- [FEX-Emu compatibility entry: Batman: Arkham City GOTY](https://wiki.fex-emu.com/index.php/Batman:_Arkham_City_GOTY) — documents the game's need for full x87 precision. The reviewed content is also available as [wiki revision 1660](https://wiki.fex-emu.com/index.php?title=Batman:_Arkham_City_GOTY&oldid=1660). This requirement predates this package; credit belongs to the FEX community contributors.
- [FEX issue #5827: X87ReducedPrecision breaks FILD m64int → FISTP m64int roundtrip](https://github.com/FEX-Emu/FEX/issues/5827) — the original reporter provides a small integer-conversion reproducer, including runs without Wine/Proton. It concerns another program and supports the precision explanation; it does not prove the AMD installer hang's root cause or every step of Batman's crash.
- [FEX configuration definitions](https://github.com/FEX-Emu/FEX/blob/main/FEXCore/Source/Interface/Config/Config.json.in) — upstream context for FEX options. The setting used here is `FEX_X87REDUCEDPRECISION=0`; this package does not copy or replace a global FEX configuration.

## Steam and Proton

- [Valve Steamworks: Creating and using InstallScripts](https://partner.steamgames.com/doc/sdk/installscripts) — authoritative description of `Run Process`, `HasRunKey`, DWORD completion state and registry redirection. The game's own inspected configuration establishes the particular App 200260 `AMD` marker; the documentation is general behavior, not a claim that Valve recommends this bypass.
- [Steam Support: Setting Game Launch Options](https://help.steampowered.com/en/faqs/view/7D01-D2DD-D75E-2955) — supported user interface for saving launch options. The script does not automate configuration-file writes.
- [ValveSoftware Proton launcher source, proton_11.0 branch](https://github.com/ValveSoftware/Proton/blob/proton_11.0/proton) — context for prefix selection and initialization. The installed Armada launcher was also inspected during the earlier investigation. A source branch alone does not certify a host-side invocation for every installed Proton build.

## Wine registry behavior

- [Wine reg.exe implementation](https://github.com/wine-mirror/wine/blob/master/programs/reg/reg.c) and [reg add implementation](https://github.com/wine-mirror/wine/blob/master/programs/reg/add.c) — normal registry-tool interfaces, including registry-view selection. The utility deliberately does not run them.
- [Wine server registry implementation](https://github.com/wine-mirror/wine/blob/master/server/registry.c) — text-hive parsing and persistence background. The utility accepts a limited recognized layout and refuses unsupported forms; this reference does not make offline editing an official Valve interface.

## Armada findings and independent validation

The AMD prerequisite hang, observed process/custom-action state, App 200260 registry state, Armada launch-wrapper integration, and apply/rollback outcomes on Odin 3 and RP6 come from the investigation and tester's reports described in [TECHNICAL-NOTES.md](TECHNICAL-NOTES.md). They are not attributed to the upstream issue authors. No public issue, benchmark, or raw validation archive is invented as a citation.

The package's contribution is a scoped utility and the Armada reproduction/integration/validation record. Full-x87 precision as a game requirement is existing FEX community knowledge. Upstream code, documentation, issue text, and game assets remain subject to their respective rights and licenses; only links and concise summaries are included here.

## Project license

- [Open Source Initiative: MIT License](https://opensource.org/license/mit) — reference for the license for this utility's original code and tests. The supplied notice is Copyright (c) 2026 SimonBits; see the repository's [LICENSE](../../LICENSE). Original documentation uses [CC BY 4.0](../../LICENSE-DOCS). Upstream material retains its own ownership and licenses.
