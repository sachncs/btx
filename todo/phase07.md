# Phase 07 — Delete dead code

## Goal
Remove symbols that are defined but never used, and parameters that are accepted but documented as no-ops.

## Context
The three exception classes (`NotInvertible`, `PointError`, `ParsingError`) and the `ExtractorPlugin` Protocol have been deleted; raise sites now use `ValueError`. The `Record.vin`/`Record.sig` aliases were audited (commit b08f3ff) and are intentionally kept as canonical names — no deletion.

## Resolved by Decision
### Task 07.7 — `Record.vin` and `Record.sig` alias properties — KEPT (no change)
The audit (commit b08f3ff) determined the `vin`/`sig` aliases are the canonical names for the fields; they are kept as convenience properties pointing at `input_index`/`signature`.

**State:**
- `btx/signature/record.py:58-66` defines both `@property` aliases and documents them in the module docstring — this is the intended end-state
- Tests reference them intentionally: `tests/test_extraction_coverage.py:450` (`records[0].sig`), `tests/test_signature_new.py:24,88` (`rec.vin`), `tests/test_mainnet_vectors.py`, `tests/test_stateful.py:62-63`, `tests/test_psbt_parser.py:366,423`
- `CHANGELOG.md` notes them as "kept as canonical names"

## End-of-Phase Verification
- All dead code deletions from Phase 07 are complete; the `Record` aliases remain by design.

## Notes
- The two Protocols were never subclassed; deleting them removes documentation-only dead weight. `ExtractorPlugin` is deleted.
- The three deleted exceptions (`NotInvertible`, `PointError`, `ParsingError`) are gone from `btx/exceptions.py` (classes + `__all__`); their former raise sites in `btx/field/modular.py`, `btx/field/sqrt.py`, and `btx/transaction/parser.py` now raise plain `ValueError`, which is still caught by `except BtxError` since `BtxError` subclasses `ValueError`.
