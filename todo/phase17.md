# Phase 17 — Unify `BatchResult` ↔ `PsbtBatchResult`

## Goal
Collapse the two near-identical batch-result dataclasses into a single generic `BatchResult[T]`.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The original `BatchResult` had `records` (and `PsbtBatchResult` had `psbts`); both are now uniformly called `items`. This is a minor API break for anyone using the old `records` field name.
- `BatchResult` is `@dataclass(frozen=True, slots=True) class BatchResult(Generic[T])` with `items`/`errors` fields and `total`/`successful`/`failed` read-only properties.
