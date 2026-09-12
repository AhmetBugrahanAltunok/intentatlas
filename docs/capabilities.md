# Capabilities in detail

What each adapter, importer and query actually covers, and where each one abstains. The
[README](../README.md) carries the short version; [architecture](architecture.md) explains
the design behind it.

IntentAtlas is an early working prototype. Python, TypeScript/JavaScript, and Go analysis share a
language-neutral built-in adapter contract. The TypeScript/JavaScript adapter covers `.ts`, `.tsx`,
`.js`, and `.jsx` files with conservative symbol, local-import, re-export, and test relationships.
The Go adapter covers `.go` files, `go.mod` module boundaries, named types, functions, methods,
module-local package imports, and tests. Same-directory tests gain structural evidence only for
referenced exported declarations owned by one production file; ambiguous names remain unlinked and
filename matching stays a weak fallback. Both adapters publish an `end_line` only when their
dependency-free structural parsers can prove a balanced declaration boundary; ambiguous or
malformed declarations remain spanless. Neither adapter runs a language runtime or project code.

Adapter conformance contract version 1 turns the shared boundary into an executable check. Fresh
and cached fragments must satisfy the same bounded symbol, relation, endpoint, evidence, ordering,
and determinism rules before graph merge. Built-in adapters pass one fixture-driven helper; this is
not an external plugin loader. See [language adapter conformance](adapter-conformance.md).

Configured Cobertura and JUnit reports now create generated coverage and test-result evidence in
the graph. Graph diff schema 1 provides stable node and relationship changes for CI without a
generation timestamp.

Explicit local delivery snapshots connect requirements and decisions to issues, pull requests,
changed files, and known commits without credentials or provider API access.

Recent Git history also records direct `modifies` relationships for Python classes, functions, and
methods, plus conservatively balanced JavaScript/TypeScript and Go declarations, when changed
new-side lines intersect their validated spans and the current file still matches the analyzed
commit blob. File-level `changes` links stay available for stale files, deletions, module-level
edits, unsupported or ambiguous spans, and uncertain cases.

`recommend-tests` consumes those validated graph relationships and ranks test-file candidates as
high, medium, or low confidence. Python tests can target exact imported symbols through bounded
package re-exports; nested changes can use a focused owning-symbol test when its test name agrees.
For a markerless root `src/` layout, both conventional imports such as `from auth import ...` and
namespace-style imports such as `from src.auth import ...` resolve when they identify one local
module. A `pyproject.toml` with setuptools, Hatch, or Flit source-root metadata takes precedence.
Ambiguous module or symbol identities remain deliberately unlinked; run `scan`, then `diagnose`,
to check whether the saved graph contains exact Python symbol-test links.
JavaScript/TypeScript records exact named and default static imports, and follows at most one exact
symbol-dependent source file to a directly linked test. For a selected file or symbol, tests from
the artifact's most recent analyzed narrow co-change provide separate low-confidence evidence;
commits wider than 20 artifacts abstain. A filename-only second hop remains low. Python files are
direct runnable targets only when bounded pytest filename patterns and safely read `python_files`
or `testpaths` declarations prove that role; `conftest.py`, package markers, typing fixtures, files
outside declared test roots, and unmatched support
files remain graph artifacts but are not commands to run. JavaScript/TypeScript and Go retain their
existing adapter behavior.

Low is exploratory discovery mode: weak filename, fallback, and co-change signals can produce high
fan-out and low precision. Use medium or higher for automated CI selection; the default and guided
flows remain medium. An exact static direct reference is intentionally `80/medium`; high is
reserved for stronger evidence such as a test directly present in the changed set. The query never
performs unrestricted transitive traversal.

`evaluate-recommendations` reuses that production query unchanged and compares it with strict,
closed-world local labels. Its timestamp-free schema-1 output makes threshold tradeoffs and
ranking regressions visible while keeping undefined metrics explicit.

`evaluate-corpus` applies the same query to multiple saved graphs and reports low, medium, and high
confidence side by side. It fails the complete corpus when any graph or label is invalid, so stale
or malformed projects cannot silently improve aggregate metrics.

Impact and recommendation queries share a lazy deterministic adjacency index. Repeated local
lookups inspect only matching incoming or outgoing buckets; adding an edge invalidates and safely
rebuilds the in-memory index.

The local viewer also derives a bounded set of shortest structural paths from the selected node to
tests, evidence, coverage, test results, commits, and pull requests. These paths make the
intent-to-proof story easier to follow; they explain graph connectivity and do not claim causality,
completeness, freshness, or test necessity. `intentatlas demo` opens the same production viewer on
an original twelve-node same-file counterexample and removes its temporary graph when the viewer
stops. `intentatlas demo --report text` and `--report json` render the same bounded evidence story
without starting a listener.

For large repositories, the viewer retains the complete graph for local navigation but renders a
deterministic window of at most 240 nodes and 900 edges. The default overview balances graph layers;
global search, report links, and relationship links can open a bounded two-hop neighborhood around
any hidden node. Total and rendered counts remain visible, and relationship details explicitly
report omitted items instead of creating unbounded browser DOM.

The real-world evaluator adds a provenance gate around the same scanner and corpus evaluator. A
strict manifest binds each local checkout to an exact GitHub origin, commit, SPDX identifier,
license-file hash, and reviewed labels. The included 18 cases across Python, JavaScript, and Go
are useful validation evidence for those pinned changes only; they are not a general accuracy
claim.

Ongoing work and completion status are tracked in the
[Product Roadmap](https://github.com/AhmetBugrahanAltunok/IntentAtlas/blob/main/atlas/Brain/Product%20Roadmap.md). The root `ROADMAP.md` is retained only as
an explicitly archived snapshot of the original 0.1–0.3 technical plan.


## Inspiration

The vault-first memory model is inspired by
[breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind), while IntentAtlas
adds a code-and-delivery intent graph. No third-party source code is bundled.

MIT licensed. See [CONTRIBUTING.md](../CONTRIBUTING.md) before opening a pull request.
