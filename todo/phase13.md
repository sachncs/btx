# Phase 13 — Unify `MutableInput` / `MutableOutput` with `PsbtInput` / `PsbtOutput` (revised per Issue C4)

## Goal
Eliminate the mutable shadow dataclasses by using `dataclasses.replace()` for in-place edits within `PsbtEditor`, while keeping `PsbtInput` / `PsbtOutput` frozen.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The revision preserves hashability (Issue C4). If a user relied on `MutableInput` mutation, they must migrate to `PsbtEditor` API.
- Performance: `replace()` is O(1) per field (it copies the frozen dataclass once). Replacing in a tuple is O(n) but PSBTs rarely have more than a few hundred inputs.
