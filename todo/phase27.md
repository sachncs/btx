# Phase 27 — CHANGELOG entry

## Goal
Add a new top-level entry to `CHANGELOG.md` documenting the 0.5.0 release.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- Historical CHANGELOG entries are immutable; do not retroactively edit. The 0.4.0 content is unchanged.
- The committed `## 0.5.0 — Package renamed to btx` entry differs slightly from the template: it adds the CLI static→instance extractor change and the `BatchResult` field renames as breaking changes, and drops the dead-code claim for `Record.vin`/`Record.sig` to "kept as canonical names". The actual `Record` alias removal is still pending (Phase 07.7).
