# Pre-1.0 compatibility policy

IntentAtlas uses explicit compatibility classes before `1.0`. A versioned schema is not an
unbounded promise: the class below identifies what may change, how a breaking change is announced,
and whether migration support is required. Security and privacy corrections may shorten a
deprecation window, but the release notes must identify the correction and safe replacement.

## Contract matrix

| Contract | Class | Current boundary | Compatibility promise |
| --- | --- | --- | --- |
| Vault Markdown, supported frontmatter, and typed wikilinks | stable | documented fields and link meanings | Existing accepted notes remain readable; additions are optional; removals or meaning changes require deprecation and migration guidance. |
| Saved graph JSON | stable | graph schema 4, relation schema 5, and documented node/edge fields | Readers deterministically migrate schemas 1-3; unsupported versions fail with an actionable error. Breaking shapes use a new schema version and a documented regeneration or conversion path. |
| Supported CLI text | stable | documented commands, exit semantics, safety wording, and named metrics | Human-readable layout may gain sections, but commands, meanings, safeguards, and undefined-value wording do not silently change. |
| Supported CLI JSON | stable | each command's `schema_version`, documented fields, null semantics, and enum meanings | Additive fields are allowed; removal, type change, or semantic change requires a schema boundary and migration notes. |
| Change set, change analysis, change report, and review output | stable | their versioned schemas and fallback/full-suite meanings | `fallback` and `unknown` never become targeted-sufficiency claims; breaking changes require a version bump and migration notes. |
| Repository diagnostic output | stable | diagnostic schema 1, read-only/no-network semantics, capability and safe-next-action fields | Additive fields are allowed; it never silently writes state, claims evidence freshness, or weakens the Private boundary. |
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
