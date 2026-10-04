# Silent Hill 2 Enhanced Edition on Armada OS

This entry documents a working Non-Steam configuration tested on
**AYN Odin 3**, running **Armada OS on ARM64**. Silent Hill 2 Enhanced
Edition is a community enhancement project. The tested installation was
added to native Steam as a Non-Steam game and launched through Armada's
game wrapper.

## Setup

1. Prepare your own legitimate, working Silent Hill 2 Enhanced Edition installation.
2. Add the appropriate game executable to native Steam as a **Non-Steam game**.
3. Open its **Steam Properties → General → Launch Options**.
4. Use:

   ```text
   WINEDLLOVERRIDES="d3d8=n,b;dinput8.dll=n,b;d3dx=n,b" /usr/libexec/armada/armada-game-launch %command%
   ```

5. Launch through Steam.

Preserve any existing custom launch options and avoid duplicating the Armada
wrapper. Keep these overrides in this game's launch options.

The DLL overrides are part of the validated working configuration. In Wine's
load-order notation, `n` prefers a native Windows DLL and `b` provides a
builtin fallback. This record does not establish a specific Wine/FEX defect
or prove that each override is individually required. See
[references](REFERENCES.md) for the Wine documentation and project information.

## Validation

**AYN Odin 3 — working configuration validated.** No other device or
gameplay duration is claimed in this entry.

## Video

[Silent Hill 2 Enhanced Edition on Armada OS | Add & Run Non-Steam Games](https://www.youtube.com/watch?v=QQsrFA3wG7Y)

The video demonstrates the tested setup and result on the real device.

## Limitations

- This is a Non-Steam configuration record, not an official Armada, Valve, FEX, Silent Hill 2, or Enhanced Edition fix.
- This entry provides no original game or copyrighted assets. Users must supply their own legitimate game installation.
- Results may differ across Armada/FEX versions and devices.
- This entry documents compatibility/startup configuration, not performance optimization.
