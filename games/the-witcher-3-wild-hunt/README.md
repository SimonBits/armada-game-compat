# The Witcher 3: Wild Hunt on Armada OS

A DX12 startup workaround was validated by the author on **Retroid Pocket 6**.
A later **AYN Odin 3** user report describes a similar problem resolved with
the same setting; that report is separate from the author's own testing.

**This entry covers startup compatibility only. It is not a performance
optimization or a guarantee that all DX12 problems are resolved.**

## Game information

| Field | Details |
| --- | --- |
| Game | The Witcher 3: Wild Hunt |
| Steam App ID | [292030](https://store.steampowered.com/app/292030/) |
| Platform | Armada OS / ARM64 |
| Launch path | Steam, retaining the Armada game-launch wrapper |
| Renderer covered | DX12 renderer; Next-Gen Update / DX12 context, not a separate game release |
| Exact game version / Steam build or branch | Not recorded |

## Tested environment / devices

| Field | Retroid Pocket 6 | AYN Odin 3 |
| --- | --- | --- |
| Evidence type | Author's earlier hands-on test, described by the author | Later third-party user feedback, relayed by the author |
| Platform | Armada OS / ARM64 | Armada OS / ARM64 |
| Armada OS version / image | Not recorded | Not recorded |
| Proton / vkd3d-proton / FEX versions | Not recorded | Not recorded |
| GPU driver version | Not recorded | Not recorded |
| Test date | Not recorded | Not recorded |
| Exact error text / code | Not recorded | Not recorded |
| Gameplay duration / FPS | Not recorded | Not recorded |

No new device test was performed while preparing this entry. The exact
device/software combinations cannot be reconstructed from the supplied
reports. Other devices and version combinations are **Not verified**.

## Problem description

On some ARM64 devices running Armada OS, starting the game's DX12 renderer
may fail or produce a startup error. The author previously reproduced this
on Retroid Pocket 6 and successfully used the setting below. A later user
reported a similar DX12 startup problem on AYN Odin 3 and reported that the
same setting resolved it.

The exact error messages and underlying cause are **Not recorded** and
**Not verified**, respectively. Similar symptoms and successful use of the
same setting do not establish that both devices encountered the same defect.

## Workaround

1. If DX12 startup already works, no workaround is needed for this issue.
2. Stop the game. In Steam, open **The Witcher 3: Wild Hunt → Properties →
   General → Launch Options**, and save the existing text.
3. Use the following launch options, retaining Armada's wrapper:

   ```text
   VKD3D_FEATURE_LEVEL=12_1 /usr/libexec/armada/armada-game-launch %command%
   ```

4. Start the game using its DX12 renderer and check whether the original
   startup failure is resolved.

Preserve custom launch options. If the Armada wrapper is already present,
add only `VKD3D_FEATURE_LEVEL=12_1` before it; do not duplicate the wrapper.
If this variable is already present, change its value to `12_1` rather than
adding a conflicting assignment. Keep unrelated arguments; complex custom
wrappers require individual review.

**Apply this setting only to this game, not globally.** The workaround
requires no helper script, game-file edit, driver replacement, or system
configuration change.

### What the setting does

In the reviewed [vkd3d-proton implementation](https://github.com/HansKristian-Work/vkd3d-proton/blob/44cf7c2042168f3/libs/vkd3d/device.c),
`VKD3D_FEATURE_LEVEL=12_1` overrides the maximum Direct3D feature level
reported to the application to `12_1` and adjusts some reported capability
fields. This changes capability reporting in the D3D12-to-Vulkan layer.
The reviewed revision is technical background, not an identified version
from either successful device test.

A [feature level is distinct from a Direct3D API version](https://learn.microsoft.com/en-us/windows/win32/direct3d12/hardware-feature-levels).
This variable does not select or force the game's DX12 renderer, repair a
GPU driver, or add missing hardware capabilities. The successful startup
results do not establish which capability check caused the original failure.

### Undo

Stop the game and restore the saved launch options. If the variable was
newly added, remove only `VKD3D_FEATURE_LEVEL=12_1`, preserving the Armada
wrapper and other options. If it replaced an existing value, restore that
value. Undo behavior was **Not verified** in the supplied test reports.

## Validation results

**Workaround status: Confirmed working in reported cases (3 user reports)**

The author reports feedback from **3 users** that `VKD3D_FEATURE_LEVEL=12_1`
resolved DX12 startup problems on Armada OS. This counts users, not three
different devices or three independent test environments. A complete
per-user device, OS version, and test-date breakdown is **Not recorded**.
The known device-specific evidence remains as follows:

| Device | Before the workaround | After the workaround | Evidence / scope |
| --- | --- | --- | --- |
| Retroid Pocket 6 | DX12 startup problem reproduced by the author | Startup problem resolved in the author's earlier test | First-hand author validation, supplied as an account of prior testing; no paired raw logs available for this entry |
| AYN Odin 3 | Similar DX12 startup problem reported by another user | User reported that the same setting resolved startup | Third-party report relayed by the author; not independently retested by the author |

The Retroid Pocket 6 result supports a **validated startup workaround in
that tested environment**. The Odin 3 report adds a successful user-reported
case, not another author-performed test or a verified version matrix.
These results do not establish sustained gameplay stability or rendering
correctness. Evidence provenance is recorded in [REFERENCES.md](REFERENCES.md).

## Known limitations

- Exact OS, game, Proton, vkd3d-proton, FEX, and driver versions are
  **Not recorded**. Current or other version combinations are **Not verified**.
- Public links and paired before/after logs for the device results were
  not supplied. The third-party reports have not been independently reproduced
  for this entry.
- DX11, other launch paths or storefronts, ray tracing, graphics settings,
  long-session stability, and performance are **Not verified** by these results.
- Overriding reported capabilities does not ensure that every advertised
  feature works on the underlying GPU/driver. Later rendering errors or
  crashes remain possible; this is not a general DX12 compatibility fix.
- vkd3d-proton environment variables can change between versions; see the
  [upstream guidance and attribution](REFERENCES.md).

## References and license

See [references and attribution](REFERENCES.md) for technical sources and
the distinction between upstream behavior, author testing, and user reports.
Original documentation uses the repository's [CC BY 4.0](../../LICENSE-DOCS).
Third-party software, documentation, game names, trademarks, and assets
retain their respective rights and licenses.
