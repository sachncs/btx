# Phase 05 — Rename `BitcoinError` → `BtxError`

## Goal
Rename the package's base exception class from `BitcoinError` to `BtxError` for naming consistency with the package `btx`.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- This is a public API break. Anyone catching `BitcoinError` must update to `BtxError`.
- The CHANGELOG.md historical entry (Phase 05.9) deliberately preserves the old name — historical CHANGELOG entries are immutable records of what was shipped, not living documentation.
