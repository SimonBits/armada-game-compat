# Batman: Arkham City GOTY on Armada OS

A small workaround for **Batman: Arkham City GOTY**, Steam App ID **200260**, using native Steam on Armada OS / ARM64. This is a public-review candidate, not an official Steam, Armada, or FEX fix.

Two separate startup problems were reproduced:

- Steam gets stuck installing **AMD Dual-Core Optimizer**. The script marks only this legacy prerequisite as completed.
- After that stage, `BatmanAC.exe` starts but shows a UE3 **Fatal Error**. The launch option below enables the full x87 precision this game needs.

Apply and rollback were independently validated on **AYN Odin 3** and **Retroid Pocket 6**, with separate installations/prefixes. Odin 3 gameplay was tested for approximately 30 minutes; RP6 startup was validated. This does not guarantee every device or fix unrelated launcher, rendering, or performance problems.

**This workaround addresses startup compatibility only. It is not a performance optimization.**

## Use

1. Install the game normally through **native Steam**.
2. Try a normal launch first. If it works, no workaround is needed.
3. If it hangs on AMD Dual-Core Optimizer, stop **Batman, its AMD installer, and the App 200260 Wine runtime**. Fully exiting Steam is recommended where practical. Native Steam/gamescope may remain running where Armada automatically keeps them open. If the game/installer runtime will not stop, reboot and **do not launch Batman again yet**. Do not launch games while the script runs.
4. Save `batman-amd-fix.py` in a convenient folder. Open a terminal in that folder and run as your normal user, **without sudo**:

   ```bash
   python3 batman-amd-fix.py
   ```

   The script uses Python 3 already present on the tested systems; it installs nothing. Wait for the verified AMD change, or confirmation that AMD is already set. If it prints `STOP`, resolve the reported condition before proceeding; do not bypass its checks.
5. Reopen Steam if you closed it.
6. Open **Batman: Arkham City GOTY → Properties → General → Launch Options**, save your previous text, then use:

   ```text
   FEX_X87REDUCEDPRECISION=0 /usr/libexec/armada/armada-game-launch %command%
   ```

   **Preserve custom launch options.** If the Armada wrapper already exists, add only `FEX_X87REDUCEDPRECISION=0` before it. Do not duplicate the wrapper. If that variable is already present, set it to `0` instead of adding a conflicting assignment. Keep unrelated arguments; complex custom wrappers need individual review.
7. Start the game.

## Undo

Stop Batman, its AMD installer, and the App 200260 Wine runtime again. Run the **exact rollback command printed by the script**. Keep the script and the printed backup directory. Rollback restores only the previous AMD value, preserving later unrelated registry changes. Do not copy the old whole `system.reg` over the current one.

To undo the launch-option change, restore the text you saved. The script never edits Steam launch options.

## Limits and further information

The script requires an existing initialized Proton prefix and a recognized registry layout. Missing/ambiguous prefixes, redirected/shared layouts, and unsupported formats are refused; it never falls back to `~/.wine`. Flatpak Steam is outside the validated scope. It does not delete prefixes, repair the AMD installer, change game files, or stop services.

See [technical notes and validation](TECHNICAL-NOTES.md) and [upstream references and attribution](REFERENCES.md). Original code and tests use the repository's [MIT License](../../LICENSE); original documentation uses [CC BY 4.0](../../LICENSE-DOCS).
