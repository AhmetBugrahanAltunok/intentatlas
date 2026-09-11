# Pre-1.0 compatibility policy

IntentAtlas uses explicit compatibility classes before `1.0`. A versioned schema is not an
unbounded promise: the class below identifies what may change, how a breaking change is announced,
and whether migration support is required. Security and privacy corrections may shorten a
deprecation window, but the release notes must identify the correction and safe replacement.

## Change-range correctness correction

ChangeSet schema 1 retains the existing integer `start` and `count` fields. A valid deletion-only
hunk in a surviving file is now preserved with `count: 0`, including `start: 0` when Git removes
leading lines. Previously these hunks were silently omitted, which could incorrectly make a
mixed edit/deletion look fully analyzed. Consumers must preserve zero-count ranges as uncertainty;
they are not source lines and must not be mapped to a current symbol. Positive ranges keep their
existing meaning. Whole-file deletions retain their existing deleted-file/unknown analysis.
Reports can consequently change from targeted-only to a full-suite fallback without any scoring
or threshold change. Re-run analysis to regenerate saved reports; do not treat old reports as
evidence of complete change coverage.

## Contract matrix

| Contract | Class | Current boundary | Compatibility promise |
| --- | --- | --- | --- |
| Vault Markdown, supported frontmatter, and typed wikilinks | stable | documented fields and link meanings | Existing accepted notes remain readable; additions are optional; removals or meaning changes require deprecation and migration guidance. |
| Saved graph JSON | stable | graph schema 4, relation schema 5, and documented node/edge fields | Readers deterministically migrate schemas 1-3; unsupported versions fail with an actionable error. Breaking shapes use a new schema version and a documented regeneration or conversion path. |
| Supported CLI text | stable | documented commands, exit semantics, safety wording, and named metrics | Human-readable layout may gain sections, but commands, meanings, safeguards, and undefined-value wording do not silently change. |
| Supported CLI JSON | stable | each command's `schema_version`, documented fields, null semantics, and enum meanings | Additive fields are allowed; removal, type change, or semantic change requires a schema boundary and migration notes. |
| Change set, change analysis, change report, and review output | stable | their versioned schemas and fallback/full-suite meanings | `fallback` and `unknown` never become targeted-sufficiency claims; breaking changes require a version bump and migration notes. |
| Repository diagnostic output | stable | diagnostic schema 1, read-only/no-network semantics, capability and safe-next-action fields | Additive fields are allowed; it never silently writes state, claims evidence freshness, or weakens the Private boundary. |
| Guided CLI human interaction | stable | empty argv TTY gate, `guide [SOURCE]`, TTY-only one-URL shorthand, conservative scope order, explicit remote consent, no-write analysis boundary, and Change Report trust meanings | Non-TTY empty/URL argv retains argparse stderr/exit 2 with no prompt/network/cache. Additive prompts are allowed, but source consent, scope, omission, fallback, advisory, and explicit-browser meanings do not silently weaken. |
| Managed public-repository cache | experimental | strict GitHub HTTPS URL identity, exact revision, schema-1 metadata, shallow/resource bounds, atomic entry lifecycle, and exact-target list/info/clear | Cache entries are rebuildable and do not imply remote freshness. Identity, privacy, authentication refusal, and traversal/link protections cannot silently weaken; incompatible metadata may be reacquired. |
| Longitudinal pilot manifest, labels, classifications, and result JSON | stable | schema 1, frozen partition hashes, canonical error-set hashes | Existing frozen inputs remain verifiable; breaking changes use a new version and retain a documented way to reproduce the prior baseline. |
| Evidence import formats and external report adapters | experimental | explicitly supported schema versions and bounded parsers | Changes require a version boundary and release-note migration guidance, but may omit a full deprecation cycle before `1.0`. |
| Language adapters and adapter conformance protocol | experimental | documented adapter protocol and current structural evidence | New evidence or parser corrections may change graphs; incompatible protocol changes are versioned and documented. |
| Workspace ownership projection | experimental | workspace schema 1; repository/project/package/source-root nodes and `contains`/`declares`/`owns` relations | Only supported bounded metadata is interpreted. Ambiguous or unsupported ownership abstains; incompatible projection changes require a graph-schema boundary. |
| Loopback viewer query JSON | experimental | query schema 1; snapshot, total/returned/omitted counts, and bounded overview/search/neighborhood/path responses | Additive fields are allowed; incompatible response meanings require a query schema change. The initial window never depends on the complete graph payload. |
| Incremental scan cache | internal | rebuildable adapter-and-workspace partitions under `.intentatlas` | No compatibility promise; any release may invalidate and rebuild it without migration. |
| Viewer bundles, in-memory indexes, and implementation helpers | internal | rebuildable implementation details behind the bounded query contract | No compatibility promise; they may change without notice when query output remains within its contract. |

## SCIP exact-evidence capability matrix

SCIP protobuf-JSON remains experimental. Source-free fallback observations accept bounded documents,
but exact semantic edges require schema `0.3.0`, a full 40-character revision equal to repository
HEAD, Git-aligned artifact bytes, one workspace owner, a valid range, and role `0` (reference) or
`1` (definition). The exact producer allowlist is `scip-python`, `scip-typescript`, and `scip-go`;
other producer/schema pairs remain fallback. IntentAtlas never invokes or downloads an indexer.

## Migration and deprecation rules

Stable contracts follow these rules:

1. Additive optional fields may ship in the current schema. Consumers must ignore documented
   additive fields they do not need.
2. A removed field, changed type, changed enum meaning, changed null meaning, or weakened safety
   semantic is breaking and requires a new schema or command boundary.
3. A stable breaking change is announced for at least one minor release before removal. The old
   reader or command remains available during that window unless retaining it would violate a
   security or privacy boundary.
4. Persistent user-owned material receives a converter or exact manual migration steps. Rebuildable
   graph material may use deterministic regeneration as its migration path.
5. Deprecation warnings identify the affected contract, replacement, first deprecated version, and
   planned removal version. Warnings go to stderr and do not corrupt JSON stdout.

Experimental contracts use an explicit schema or protocol version and release-note migration
guidance, but may change at the next minor release without a prior warning cycle. Internal
contracts carry no migration or deprecation promise. Moving a contract to a stronger class is an
architectural decision; moving it to a weaker class is a breaking change and follows the stable
rules.

## Longitudinal baseline boundary

The Phase 11B evaluator calls the unchanged production recommendation and change-report paths. Its
manifest freezes exact revisions, license reviews, thresholds, exclusions, and partition hashes.
Evaluation is offline and does not acquire repositories, execute third-party code, or persist
third-party source. Duration and savings stay unknown unless separate aligned execution evidence
is supplied. Confidence intervals are descriptive uncertainty for the reviewed cohort, not a
population or general-accuracy claim.

Phase 17 corrects recommendation schema-1 values to the already documented ADR-009 confidence
bands: high `85+`, medium `65-84`, low `0-64`. Threshold filtering and omission counters apply to
requirements and tests before result limiting or strategy selection. This is a semantic bug fix,
not a schema change. Experimental Python workspace projection recognizes bounded setuptools,
Hatchling, Flit, and unique conventional src layouts; ambiguous root/src identities abstain.

Phase 17F keeps Change Report schema 1 and graph schema 4. Change Report items add optional
`primary_reason` and `reason_details` fields that bind each score to one signal, path, and evidence
set; omission records additionally expose `selection_reason`. Existing `reasons`, `paths`,
`evidence`, and omission `reason` fields remain readable aggregate or selection fields and are
deprecated for consumers that need a linked ranking explanation. Python test nodes may add
`test_role`, `test_runner`, and discovery-evidence metadata. Bounded pytest `python_files` and
`testpaths` declarations refine runnable-target
eligibility without removing the node or its graph edges. Graphs without role metadata, and
non-Python adapters, retain their prior recommendation behavior. These are additive fields under
the existing schema boundaries and require no stored-data migration.

Change Report schema 1 may also include additive `analysis_coverage` metadata. It separates result
limits from artifact and test-signal analysis limits, records how many candidates were analyzed or
omitted by each bound, and marks whether published requirement/test totals are complete or lower
bounds. Existing selection fields and `analysis_coverage_complete` remain present; strict consumers
that reject unknown fields must allow this additive object.

Change Analysis schema 1 narrows one evidence label. `vault-frontmatter-id` previously appeared for
every durable vault note, including notes whose identity the scanner derived from their path
because no `id:` frontmatter existed. It now appears only when the declared identity is real, and
the new `vault-path-identity` label covers the derived case. This narrows an inaccurate claim
rather than weakening a safety semantic: state, freshness, confidence, and artifact identity are
unchanged, and `durable-intent-artifact` still accompanies both. A consumer detecting durable vault
notes must key off `durable-intent-artifact`; one that keyed off `vault-frontmatter-id` was relying
on a signal that did not mean what it said. User-owned vault nodes carry a corresponding additive
`metadata["identity"]` of `frontmatter` or `path`; a graph without it resolves to the conservative
`vault-path-identity`.
