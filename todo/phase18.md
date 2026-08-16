# Phase 18 — Replace `SignatureCollection.sort_records(key: str)` with callable

## Goal
Replace the string-key parameter with a proper callable, removing the `hasattr`-based dispatch and the fragile operator-precedence trick.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The old `key: str` API was fragile and un-typecheckable; the new API is standard Python.
