# References and attribution

## Submitted upstream investigation reports

- [Armada #628: NBA 2K27 Offline rendering flicker](https://github.com/armada-os/armada/issues/628) records the unresolved rendering investigation on Odin 3, the experimental FEX prerequisite, and the request for cross-stack triage. Its sanitized evidence attachment contains environment/hashes, selected logs, queue and image-identity summaries, and representative screenshots. It supports the observed flicker and documented measurement limits; it does not establish a responsible component, a playable configuration, or an image-to-visible-content mapping.

- [FEX #6009: Wine/ARM64EC ProcessorID fallback for RDTSCP/RDPID](https://github.com/FEX-Emu/FEX/issues/6009) records the separate capability gap, measured stock CPUID behavior, standalone fault reproduction, isolated proof of concept, semantic-validation results, and game-level execution past the original instruction fault. Its attachment contains probe sources/results, experimental diff, provenance, and limitations. It supports experimental startup progress, not full game compatibility, exhaustive architectural correctness, production readiness, or a rendering fix.

A FEX maintainer later clarified that the intended upstream direction is Linux
kernel support for exposing the core index through `TPIDRRO_EL0`, followed by
FEX integration. The API-backed ProcessorID implementation from this
investigation should therefore be treated as a proof of concept rather than
the intended upstream fix. See the
[maintainer response](https://github.com/FEX-Emu/FEX/issues/6009#issuecomment-5998624708).

Both reports were submitted by SimonBits and reviewed for this entry on
2026-10-05. They publish this investigation's findings; they are not
independent confirmations by upstream maintainers. Submission does not imply
that maintainers have confirmed the diagnosis, accepted the experimental
patch, or committed to a fix. Detailed evidence remains with the upstream
reports instead of being duplicated here.

## Repository contribution and scope

This entry is an **Original investigation** record, summarizing the supplied
Armada/FEX investigation and its limits. The [user-facing entry](README.md)
states the current compatibility result; [technical notes](TECHNICAL-NOTES.md)
separate confirmed observations from unresolved causal explanations.

The experimental FEX implementation is prerequisite context for reaching the
rendering stage, not a recommended end-user workaround. Investigation on
AYN Odin 3 does not establish playable-device validation. Online/EAC was
intentionally not tested with that runtime; its acceptance is unknown.

Original documentation is covered by [CC BY 4.0](../../LICENSE-DOCS).
Upstream software, patches, documentation, game assets, and other referenced
material retain their respective rights and licenses; this entry does not
relicense them.
