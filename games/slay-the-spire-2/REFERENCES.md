# References and attribution

## Upstream/community knowledge

- [FEX compatibility entry: Slay the Spire 2](https://wiki.fex-emu.com/index.php/Slay_the_Spire_2) — the page returned during this review ([revision 1545](https://wiki.fex-emu.com/index.php?title=Slay_the_Spire_2&oldid=1545)) records an early startup failure involving embedded CoreCLR and labels the game unplayable. It does not list the launch-variable workaround. That upstream record is distinct from the successful Armada validation reported here.
- [FEX issue #5991](https://github.com/FEX-Emu/FEX/issues/5991) — reports Slay the Spire 2's native Linux build crashing during main-menu asset preload on Retroid Pocket 6 / Armada OS after successful Vulkan initialization. It reports several managed exceptions ending in an access violation, rather than establishing the finalizer-exception path observed in our investigation. The report proposes a JIT/concurrency hypothesis; it does not prove the cause or mention `DOTNET_EnableWriteXorExecute=0`.
- [FEX issue #5766](https://github.com/FEX-Emu/FEX/issues/5766) — concerns Barotrauma's native Linux build with .NET 8 / CoreCLR under FEX. The reporter says `DOTNET_EnableWriteXorExecute=0` avoids an earlier internal runtime failure and allows content loading to proceed, but later crashes remain. This is precedent for a partial mitigation using the executable-memory setting in another CoreCLR application under translation, not a documented Slay the Spire 2 fix or proof of the underlying mechanism.
- [Comment on #5766](https://github.com/FEX-Emu/FEX/issues/5766#issuecomment-5007068525) — identifies CoreCLR problems under FEX as also affecting Slay the Spire 2. It does not report testing the variable in that game.

Both issue bodies and all available comments were reviewed on 2026-10-04
(#5991: no comments; #5766: one comment). Neither report documents this exact
Slay the Spire 2 workaround or establishes an identical crash or a
conclusively identified CoreCLR/FEX defect. The reports support the reason
to test the variable, not a claim that every CoreCLR failure shares a cause.

Credit for existing upstream reports and workaround knowledge belongs to
their original contributors. This repository does not claim those
discoveries as its own.

## Armada investigation and validation

The [game entry](README.md) records the supplied Armada investigation and
tester reports: native Linux x86_64 execution through SteamLinuxRuntime
sniper and FEX, successful Vulkan/FMOD initialization, an unhandled
Godot/.NET finalizer exception followed by SIGABRT, and successful testing
of the launch variable on AYN Odin 3 and Retroid Pocket 6.

The Armada-specific contribution is testing this existing CoreCLR setting
as a single-variable workaround against the observed Slay the Spire 2
failure and validating successful startup on both devices. Those results
support the compatibility interpretation in this entry; they are not
results reported by the upstream issue authors. No raw logs or private
validation artifacts are included.

The repository's original documentation is covered by the [MIT License](../../LICENSE).
Upstream software, documentation, and game assets retain their respective
rights and licenses.
