# Phase 22 — In-scope new features for `Tx`

## Goal
Add small API improvements that integrate naturally with Phase 10's `Tx` method additions.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- `tx.to_dict()` enables JSON serialization via existing `tx_to_json()` helper.
- `total_output_value` remains a supported module-level operation in
  `btx.transaction.ops` and is re-exported from `btx.transaction`; the
  current transaction model intentionally keeps domain operations outside the
  frozen data carrier.
