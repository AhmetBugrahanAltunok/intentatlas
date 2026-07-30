---
id: EVD-002
type: evidence
status: verified
phase: 1
verified_on: 2026-07-30
---
# Phase 1 foundation verification

This evidence verifies [[Requirements/REQ-002 - Harden trust boundaries]] and
[[Decisions/ADR-002 - Pruned trust-boundary traversal]] under the
[[Brain/Phase Completion Protocol]].

## Change inventory

- Added the product roadmap, phase completion protocol, Phase 1 requirement, and traversal ADR.
- Established the Product Roadmap as the canonical active plan and labeled the original 0.1–0.3
  technical roadmap as an archived snapshot, with README and vault navigation updated accordingly.
- Replaced post-recursion filtering with deterministic top-down directory pruning.
- Excluded the configured vault from repository discovery and added root `.obsidian` scanner and
  Git-ignore boundaries without excluding the real `atlas/.obsidian/` vault configuration.
- Prevented traversal through directory symlinks and Windows junctions.
- Rejected project-root output paths, unsafe/reserved user IDs, and graph identity collisions.
- Limited user note IDs to frontmatter instead of matching arbitrary body text.
- Escaped untrusted Markdown display text, metadata, and wikilink components.
- Made generated filename collision handling deterministic and resistant to repeat collisions.
- Prevented generated-note cleanup from reading symlink targets.
- Preserved pointer selection while restoring standard click and keyboard activation in the viewer.
- Updated architecture, security, contribution, and agent guidance.

## Focused regression verification

- Command: `python -m pytest tests/test_config.py tests/test_graph.py tests/test_scanner.py tests/test_vault.py tests/test_viewer.py`
- Result: 20 passed.
- Private-boundary tests replace `os.scandir` with a guard that fails immediately if
  `atlas/Private/` or a configured nested exclusion is enumerated.
- Reserved IDs, body-only IDs, identity collisions, Markdown injection shapes, and viewer
  activation wiring have dedicated regressions.

## Complete quality suite

- `python -m pytest`: 26 passed.
- `python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80`:
  26 passed, 85.96% branch-aware coverage.
- `python -m ruff check .`: all checks passed.
- `python -m bandit -q -r src`: no findings.
- `python -m pip check`: no broken requirements.
- `node --check src/intentatlas/web/app.js`: JavaScript syntax passed on Node 20.12.0.
- `git diff --check`: passed after normalizing the repository config to LF.

## Repository and CLI acceptance

- Final repository scan: 175 nodes, 242 relationships, 163 generated notes.
- Graph health: 0 orphaned durable notes.
- Git layer: 1 commit node is present and linked to changed files.
- `intentatlas impact REQ-002 --depth 2` connects the requirement to ADR-002, the roadmap,
  the phase protocol, the prior requirement, and scanner implementation evidence.
- The generated graph contains no `Private/` references and does not include the repository-root
  `.obsidian/` folder.

## Browser acceptance

- The local loopback viewer rendered the 173-node, 231-relationship pre-evidence graph; the final
  scan adds this Evidence note and its Review note without changing viewer code.
- A real pointer click selected REQ-002 and opened 6 relationship details.
- Keyboard activation selected REQ-001 and opened 9 relationship details.
- Searching for `REQ-002` produced exactly 1 visible and 172 dimmed nodes.
- The final 175-node, 241-relationship graph also loaded successfully; searching for
  `Product Roadmap` found exactly one matching accessible node, and keyboard activation opened
  its detail panel with 9 relationships.
- No browser console warnings or errors were reported in either run.

## Packaging and dependency verification

- The project owner explicitly approved the required network access on 2026-07-30.
- Installed the declared `hatchling>=1.25` build backend; the resolved version was 1.31.0.
- `python -m pip_audit`: no known dependency vulnerabilities found. The unpublished local
  `intentatlas 0.1.0` distribution was reported as not present on PyPI and therefore skipped.
- `python -m pip wheel . --no-deps --no-build-isolation`: built
  `intentatlas-0.1.0-py3-none-any.whl` successfully.
- Wheel SHA-256: `a4ec6a45e977142f41664b55cae7e24b4a1072cf1d77065fa1b43af11f91e72f`.
- All required viewer assets, package metadata, and CLI entry points were present among 21 wheel
  entries.
- Installing that wheel into a clean virtual environment and running `init`, `scan`, and `status`
  succeeded with 6 nodes, 9 relationships, and 0 durable orphans.

## Remaining risks

- Large-graph performance and richer viewer interaction tests belong to Phase 4.
- Special-character wikilink resolution is safely escaped but is not yet tested against every
  Obsidian platform build.
