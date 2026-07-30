# Changelog

All notable changes will be documented in this file.

The format is based on Keep a Changelog and the project follows Semantic Versioning.

## [Unreleased]

### Added

- Initial local intent graph scanner.
- Obsidian-compatible project brain and generated graph notes.
- Local interactive viewer, impact tracing, and health status commands.
- Phase-based delivery protocol with evidence and review completion gates.
- Phase 2 typed relation catalog, inverse relationship labels, issue notes, and explicit
  `relation:: [[target]]` Markdown links.

### Changed

- Repository discovery now prunes excluded directories before descent and never walks the vault.
- Graph and vault generation reject identity collisions and escape untrusted Markdown content.
- The Product Roadmap is now the clearly identified active plan; the original version-oriented
  roadmap remains available as an explicitly archived historical snapshot.
- Phase 1 now has complete local, browser, dependency-audit, and packaged-wheel acceptance
  evidence recorded in the Obsidian vault.
- Graph caches use schema 2 while retaining read compatibility with schema 1, and impact output
  explains relation direction, category, and provenance.

### Fixed

- Restored reliable pointer, click, and keyboard activation for graph nodes in the local viewer.
