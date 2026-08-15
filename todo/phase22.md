# Phase 22 — In-scope new features for `Tx`

## Goal
Add small API improvements that integrate naturally with Phase 10's `Tx` method additions.

## Context
Depends on Phase 10 (Tx method surface established). After this phase, `Tx` has a richer Python interface.

## Tasks

### Task 22.1 — Add `Tx.__len__` returning input+output count (per F1)
**Acceptance Criteria:**
- `len(tx)` returns `len(tx.inputs) + len(tx.outputs)`
- `len(empty_tx)` returns 0 (raises `ValueError` on access since empty tx is invalid, so probably only tested with non-empty)

**Steps:**
1. Add `__len__` method to `Tx`

### Task 22.2 — Add `Tx.__iter__` yielding `TxIn` (per F2)
**Acceptance Criteria:**
- `for txin in tx: ...` iterates over `tx.inputs`
- Iteration yields `TxIn` instances in order

**Steps:**
1. Add `__iter__` method

### Task 22.3 — Add `Tx.to_dict()` method (per F10)
**Acceptance Criteria:**
- `tx.to_dict()` returns a dict that round-trips through `tx_from_dict()`:
  ```python
  {
      "version": int,
      "inputs": [{"txid": bytes, "vout": int, "script_sig": bytes, "sequence": int, "witness": tuple[bytes, ...]}],
      "outputs": [{"value": int, "script_pubkey": bytes}],
      "lock_time": int,
  }
  ```
- `tx_from_dict(tx.to_dict()) == tx` (value-equality)

**Steps:**
1. Add the method

### Task 22.4 — `Tx.total_output_value()` (per F3, also Phase 10.6)
**Acceptance Criteria:**
- `tx.total_output_value()` returns the sum of output values
- The free function `total_output_value(tx)` is removed from `btx/__init__.py:__all__`

## End-of-Phase Verification
- All four features work as specified
- Tests for new methods pass

## Notes
- `tx.to_dict()` enables JSON serialization via existing `tx_to_json()` helper.