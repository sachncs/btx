# Phase 22 — In-scope new features for `Tx`

## Goal
Add small API improvements that integrate naturally with Phase 10's `Tx` method additions.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- `tx.to_dict()` enables JSON serialization via existing `tx_to_json()` helper.
- The free function `total_output_value` is removed from `btx/transaction/fee.py` and from the `btx/transaction` and `btx` re-exports; only the method `Tx.total_output_value()` at `btx/transaction/models.py` remains.
