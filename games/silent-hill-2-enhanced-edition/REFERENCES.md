# References and attribution

## Upstream/project documentation

- [Silent Hill 2 Enhanced Edition — official project site](https://enhanced.townofsilenthill.com/SH2/) — background on the community enhancement project for the PC game. Credit for the enhancements belongs to the project contributors; this link is not a source for the original game.
- [Wine manual: WINEDLLOVERRIDES](https://manpages.debian.org/bookworm/wine/wine.1.en.html) — Wine's manual, hosted by Debian, documents DLL load-order overrides: `n` means native Windows DLL, `b` means Wine builtin, and `n,b` tries native first with builtin fallback. This explains the notation, not why any particular override was necessary in this test.

These references describe the project and Wine behavior. They do not certify
the Armada configuration or establish an Armada/FEX bug fix.

## Armada validation and demonstration

- [Silent Hill 2 Enhanced Edition on Armada OS | Add & Run Non-Steam Games](https://www.youtube.com/watch?v=QQsrFA3wG7Y) — the tester-supplied real-device setup/gameplay demonstration for the working AYN Odin 3 configuration recorded in the [game entry](README.md).

The Armada-specific contribution is a record of the tested native Steam
Non-Steam setup, Armada wrapper, and DLL override combination. No original
upstream bug/fix discovery, specific technical cause, or validation on other
devices is claimed.

The project site and Wine manual were checked during this review. The
YouTube page could not be retrieved by the review tool; the clean URL,
title, and demonstration context are supplied by the tester.

No game files, preconfigured packages, redistributed assets, or game-download
links are included. The repository's original documentation uses the
[MIT License](../../LICENSE); the game, enhancement project, video, and
upstream documentation retain their respective rights and licenses.
