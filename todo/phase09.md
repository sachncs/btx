# Phase 09 — Delete `PointArithmetic` facade, expose methods on `Point`

## Goal
Replace the `PointArithmetic` facade (a 7-method class with all-forwarding methods) with direct methods on the `Point` value type. Add operator overloading for `+`, `-`, `*`, and unary `-`.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The lazy-imports inside each method preserve the original `PointArithmetic` pattern; they avoid circular imports at module load time.
- Operator overloading makes the value type behave like a number, which is the Pythonic expectation for a mathematical object.
