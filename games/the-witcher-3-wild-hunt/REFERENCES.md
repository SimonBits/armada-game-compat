# References and attribution

## Technical references

- [vkd3d-proton device implementation, revision 44cf7c2042168f3](https://github.com/HansKristian-Work/vkd3d-proton/blob/44cf7c2042168f3/libs/vkd3d/device.c) — `d3d12_device_caps_override` reads `VKD3D_FEATURE_LEVEL`, recognizes `12_1`, changes some capability fields, and assigns the maximum reported feature level. This supports the variable explanation, not a diagnosis of either device's startup failure. This revision is not claimed as the version installed during testing.
- [vkd3d-proton README: Environment variables](https://github.com/HansKristian-Work/vkd3d-proton#environment-variables) — upstream notes that these variables are primarily debugging controls and may change or be removed. This is general version-scope guidance, not a Witcher 3 compatibility guarantee.
- [Microsoft: Hardware Feature Levels](https://learn.microsoft.com/en-us/windows/win32/direct3d12/hardware-feature-levels) — distinguishes feature levels from API versions and documents the associated capability groups. Setting a reported feature level does not supply missing hardware or driver functionality.
- [Steam store: App 292030](https://store.steampowered.com/app/292030/) — game/store identity reference only. Store metadata does not identify the build used in the reported tests or validate Armada compatibility. This entry uses **The Witcher 3: Wild Hunt** as the game name and treats update/renderer labels within that entry, not as a separate game release.

Technical sources were reviewed while preparing this entry. Mutable pages
may change. Upstream implementation and documentation remain the work of
their respective contributors; this repository does not claim discovery
of the environment variable.

## Author's earlier Armada validation

The author supplied an account of earlier hands-on testing on Retroid
Pocket 6: a DX12 startup problem was reproduced and
`VKD3D_FEATURE_LEVEL=12_1` resolved it. The [game entry](README.md) records
that result as first-hand author validation. It is not a new test performed
during documentation preparation.

The author specified the complete Armada launch option documented in the
entry, including `/usr/libexec/armada/armada-game-launch %command%`.
No exact test date, software version matrix, error text, benchmark, or
paired before/after log set was supplied, so none is inferred.

## Later third-party user feedback

The author's updated account records **3 users** reporting that
`VKD3D_FEATURE_LEVEL=12_1` resolved DX12 startup problems on Armada OS.
The feedback channels are **Not recorded**; the reports are not assumed
to come from Steam reviews or ProtonDB. The evidence source for the count
is the author's account of user feedback, not a Steam or ProtonDB record.
A complete per-user device, OS version, and test-date breakdown is
**Not recorded**. Three user reports do not establish three distinct
devices or three independent test environments.

The known AYN Odin 3 third-party report, relayed by the author, states that
a similar DX12 startup problem was resolved using the same setting.
This is attributed to the third-party user and is not described as an
author-performed test. A public report URL, reporter identity, exact test
date, version matrix, and raw logs were **Not recorded** in the supplied
account. Independent reproduction by the author is **Not verified**.

No public issue, quotation, or raw validation archive is invented as a
citation for either device result. Upstream references above explain the
setting; they do not corroborate these device-specific outcomes.

## Local evidence review

Local investigation material was checked before drafting this entry.
Steam compatibility-tool mappings and process-tracking records referencing
App ID 292030 were found among captures made for other investigations.
They do not establish the selected renderer, the effective workaround
value, or a successful before/after comparison for the reported cases.
No matching paired validation logs were located in the reviewed material.

Those incidental records are not used to assign test dates, Proton/OS
versions, error messages, or gameplay results to either device report.
Private capture files and machine-specific paths are not included in this
public documentation.

## License

Original documentation is covered by the repository's
[CC BY 4.0](../../LICENSE-DOCS). Referenced upstream software and
documentation, and game software, assets, names, and trademarks retain
their respective rights and licenses. Links and concise summaries do not
relicense third-party material.
