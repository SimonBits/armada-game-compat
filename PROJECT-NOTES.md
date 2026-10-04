# Project Notes

## Purpose

`armada-game-compat` is SimonBits' real-device compatibility knowledge base
for PC games running on Armada OS / ARM64 handhelds.

The repository is the source of truth for validated results.
Do not rely on chat history or memory when repository information is available.

## Maintainer

SimonBits

## Project workflow

For a new game:

1. Reproduce the problem on a real device.
2. Preserve the original failure state where practical.
3. Investigate before changing multiple variables.
4. Prefer single-variable, reversible tests.
5. Distinguish confirmed observations from hypotheses.
6. Validate the workaround on real hardware.
7. Test a second device when practical.
8. Check existing upstream/community reports before claiming a new discovery.
9. Submit useful findings upstream/community where appropriate.
10. Add the validated result to this repository.

## Evidence rules

Only list a device under `Validated Devices` if the workaround/configuration
was actually tested on that device.

Planned testing does not count as validation.

When useful, distinguish validation levels:

- Startup validated
- Main menu validated
- Gameplay validated
- Extended gameplay validated

Never infer an unrecorded device, version, test duration, or result.

Do not claim a root cause when only a workaround or correlation is established.

Do not claim existing upstream/community knowledge as an original discovery.

## Source classifications

- `Original investigation`
- `Investigation + upstream`
- `Upstream/community workaround, Armada validated`
- `Armada validation`

Use the narrowest accurate description.

## Scope

Primary scope:

- Armada OS
- ARM64 handhelds
- Native Steam
- Proton / FEX
- Non-Steam PC games where relevant

Startup compatibility and working configurations belong here.

Performance optimization is separate unless explicitly investigated and validated.

Do not include copyrighted game files, redistributed game assets, ROMs,
preconfigured commercial-game packages, or other material that should not be
redistributed.

## Current repository conventions

Each game lives under:

`games/<game-name>/`

Entries may contain:

- `README.md`
- `TECHNICAL-NOTES.md`
- `REFERENCES.md`
- helper scripts
- synthetic tests

Not every game needs every file.

The root README is the public index.

## Automation / AI assistants

Before continuing existing work, read this file, the root `README.md`, and the relevant game entry.

Repository records are the source of truth for previously validated results and take precedence over recalled session or chat context.

When assisting with this project:

1. Read the relevant game directory before making claims about previous testing or results.
2. Do not infer validation from planned or intended tests. Only record devices, versions, results, or test durations that were actually verified.
3. Do not change validated scripts merely for style or refactoring.
4. Preserve evidence boundaries: distinguish confirmed observations, working hypotheses, and unverified explanations.
5. Preserve upstream/community attribution and do not present existing knowledge as an original discovery.
6. Do not add, commit, push, publish, or submit upstream changes unless explicitly authorized.
7. Prefer small, reversible, single-variable tests when investigating compatibility problems.
8. If repository records conflict with new information from the maintainer, stop and clarify which information is current before changing the record.

## Publication workflow

Preferred order for substantial new technical findings:

1. Validate locally.
2. Contribute/report to the relevant upstream or community when useful.
3. Update this repository.
4. YouTube.
5. Bilibili.

Small documentation-only updates do not need to follow this sequence mechanically.

## Licensing

Apply the following categories to current and future original repository
material:

- **Software/code: [MIT License](LICENSE).** This includes Python utilities,
  helper scripts, synthetic tests, and future original source code. Preserve
  the notice: Copyright (c) 2026 SimonBits.
- **Documentation: [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DOCS).**
  This includes README files, PROJECT-NOTES.md, TECHNICAL-NOTES.md,
  REFERENCES.md, compatibility records, and original investigation/validation
  documentation authored for this repository.

Maintainers and AI/automation sessions must preserve this distinction: do not
apply MIT to all documentation or CC BY 4.0 to source code. Use CC BY 4.0
without adding NonCommercial or NoDerivatives restrictions.

These licenses apply only to this repository's original material. They do not
relicense FEX, Wine, Proton, Steam/Valve, Armada, or Silent Hill 2 Enhanced
Edition project material; game software/assets; or quoted or referenced
third-party material. Preserve upstream attribution and existing notices.
Third-party software, documentation, game assets, trademarks, names, and
referenced materials retain their respective rights and licenses.

Earlier public revisions remain available under the license terms under which
they were originally released. This change does not revoke or remove rights
already granted under MIT for those revisions.
