# Phase 10 — Delete `TxSerializer` / `TxRbf` / `TxSighash` facades (priority)

## Goal
Remove the three facade classes that wrap `Tx` and forward to module-level functions. Promote the wrapped operations into direct methods on `Tx`.

## Context
Depends on Phase 03. After this phase, `tx.serialize()`, `tx.is_opt_in_rbf()`, `tx.sighash_legacy(...)` are direct method calls. The `tx_services.py` file is deleted entirely.

## Tasks

### Task 10.1 — Delete `tx_services.py`
**Acceptance Criteria:**
- `ls btx/transaction/tx_services.py` fails
- `grep -rn 'tx_services\|TxSerializer\|TxRbf\|TxSighash' btx/ --include='*.py'` returns no matches

**Steps:**
1. `rm btx/transaction/tx_services.py`

### Task 10.2 — Delete `Tx.serializer`, `Tx.rbf`, `Tx.sighash` properties
**Acceptance Criteria:**
- `btx/transaction/models.py` no longer defines those properties
- `grep -rn 'tx.serializer\|tx.rbf\|tx.sighash' btx/ tests/ --include='*.py'` returns no matches after Phase 10.7

**Steps:**
1. Read `btx/transaction/models.py:131-162`
2. Delete the three `@property` definitions

### Task 10.3 — Add `Tx.serialize()` and `Tx.serialize_legacy()` methods (per F4)
**Acceptance Criteria:**
- `tx.serialize()` returns the full wire-format bytes (with witness if segwit)
- `tx.serialize_legacy()` returns the non-witness bytes
- For a non-segwit tx, both return the same bytes

**Steps:**
1. Add `Tx.serialize(self) -> bytes` method that calls the existing `serialize_tx` function
2. Add `Tx.serialize_legacy(self) -> bytes` method that calls `serialize_legacy_tx`

### Task 10.4 — Add `Tx.is_opt_in_rbf()` method (per F5)
**Acceptance Criteria:**
- `tx.is_opt_in_rbf()` returns `True`/`False` based on the tx's input sequences

**Steps:**
1. Add method that calls the existing `is_opt_in_rbf` function with `self`

### Task 10.5 — Add `Tx.sighash_legacy/segwit/taproot()` methods (per F6)
**Acceptance Criteria:**
- `tx.sighash_legacy(vin, script_code, sighash_type=SIGHASH_ALL)` returns the legacy sighash bytes
- Same shape for segwit and taproot variants

**Steps:**
1. Add three methods, each calling the corresponding module-level function
2. Use `SIGHASH_ALL` as default

### Task 10.6 — Add `Tx.total_output_value()` method (per F3)
**Acceptance Criteria:**
- `tx.total_output_value()` returns `sum(out.value for out in tx.outputs)`
- The existing module-level `total_output_value(tx)` function is removed (now only available as method)

**Steps:**
1. Add method
2. Remove `total_output_value` from `btx/__init__.py:__all__`
3. Update any callers of the free function

### Task 10.7 — Update facade call sites
**Acceptance Criteria:**
- `grep -rn '\.serializer\.\|\.rbf\.\|\.sighash\.' btx/ tests/ --include='*.py'` returns no matches
- All tests pass

**Steps:**
1. Find every `tx.serializer.serialize_tx(...)`, `tx.rbf.is_opt_in_rbf()`, `tx.sighash.legacy(...)` call site
2. Replace with `tx.serialize()`, `tx.is_opt_in_rbf()`, `tx.sighash_legacy(...)`

### Task 10.8 — Update tests that referenced the facade classes
**Acceptance Criteria:**
- `tests/test_serialization.py`, `tests/test_parse_tx.py` etc. import the new methods, not the deleted classes
- Tests pass

**Steps:**
1. Search for `from btx.transaction.tx_services import` or similar
2. Update each test file

## End-of-Phase Verification
- `ls btx/transaction/tx_services.py` fails
- `tx.serialize()`, `tx.serialize_legacy()`, `tx.is_opt_in_rbf()`, `tx.sighash_legacy(...)` all work
- All transaction-related tests pass

## Notes
- This phase is marked priority per your direct feedback: these three facades are the clearest examples of unnecessary wrapper classes.
- The deleted file contained ~200 lines; the net LOC delta is heavily negative.