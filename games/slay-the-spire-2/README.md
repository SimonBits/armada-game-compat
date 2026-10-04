# Slay the Spire 2 on Armada OS

Steam App ID: **2868840**. A startup workaround was independently validated
on **AYN Odin 3** and **Retroid Pocket 6** running Armada OS.

## Observed problem

The native Linux x86_64 build launched through SteamLinuxRuntime sniper and
FEX on Armada, with no Wine/Proton prefix involved. Startup failed with an
unhandled Godot/.NET finalizer exception followed by SIGABRT. Vulkan and FMOD
had initialized successfully in the observed logs.

## Workaround

1. In Steam, open **Slay the Spire 2 → Properties → General → Launch Options**.
2. Set:

   ```text
   DOTNET_EnableWriteXorExecute=0 /usr/libexec/armada/armada-game-launch %command%
   ```

3. Start the game.

Preserve any existing custom launch options. If the Armada wrapper is already
present, add only `DOTNET_EnableWriteXorExecute=0` before it; do not duplicate
the wrapper. Save your previous launch options so you can restore them.

**Apply this variable only to this game, not globally.** No helper script,
prefix changes, or prerequisite installation is required.

To undo the workaround, remove only `DOTNET_EnableWriteXorExecute=0` from this
game's launch options, preserving the Armada wrapper and other options.

## Evidence and interpretation

`DOTNET_EnableWriteXorExecute=0` was tested as a single-variable workaround.
Changing CoreCLR executable-memory behavior avoided the observed startup
failure on both tested devices. The evidence is consistent with a CoreCLR/FEX
compatibility problem; the underlying defect has not been conclusively
identified. Successful Vulkan and FMOD initialization does not rule out all
later graphics or audio problems.

Upstream reports document Slay the Spire 2 / CoreCLR problems under FEX and,
separately, a partial mitigation using this variable in Barotrauma. They do
not document this exact Slay the Spire 2 workaround. Our Armada-specific
step was to test the existing setting against the observed failure and
validate successful startup on Odin 3 and RP6. Credit for the prior reports
and variable-use precedent remains with their contributors; see
[references and attribution](REFERENCES.md) for source details and limits.

## Validation and limitations

| Device | Reported validation |
| --- | --- |
| AYN Odin 3 | Startup workaround validated successfully |
| Retroid Pocket 6 | Startup workaround independently validated successfully |

These results are the testers' reported observations, not new device tests
performed while preparing this entry. No gameplay duration, benchmark, or
specific Armada/FEX/game build versions are recorded here.

This addresses startup compatibility only and is not a performance
optimization. It does not guarantee compatibility on every device or fix
unrelated rendering, audio, or gameplay issues. The documented path is the
native Linux build; no Windows/Proton workaround is established by these tests.
