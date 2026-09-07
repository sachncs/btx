# Phase 06 — Rename `GENERATOR` / `INFINITY` constants

## Goal
Rename the two module-level constants that violate PEP 8 by using PascalCase: `GENERATOR` → `GENERATOR_POINT` and `INFINITY` → `INFINITY_POINT`.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The math-notation `R`, `G`, `Q` locals remain under per-file `N806` ignores (intentional cryptographic convention).
- `GENERATOR_POINT` and `INFINITY_POINT` are immutable singletons used as group identity and generator in secp256k1 arithmetic.
