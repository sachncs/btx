# Phase 18 — Replace `SignatureCollection.sort_records(key: str)` with callable

## Goal
Replace the string-key parameter with a proper callable, removing the `hasattr`-based dispatch and the fragile operator-precedence trick.

## Context
Depends on Phase 03. After this phase, type checkers can validate the sort key.

## Tasks

### Task 18.1 — Change parameter type
**Acceptance Criteria:**
- `btx/signature/collection.py:47-63` `sort_records` signature is:
  ```python
  def sort_records(self, key: Callable[[Record], Any]) -> Self:
  ```
- The parameter is `Callable`, not `str`

**Steps:**
1. Read the method
2. Update the annotation
3. Add `from collections.abc import Callable` if not present

### Task 18.2 — Remove the `hasattr` trick
**Acceptance Criteria:**
- The body of `sort_records` no longer contains `if not hasattr(...) if self.records else False`
- The body simply calls `sorted(self.records, key=key)`

**Steps:**
1. Replace the entire body with `return type(self)(records=tuple(sorted(self.records, key=key)))`

### Task 18.3 — Update tests
**Acceptance Criteria:**
- Tests that did `collection.sort_records("input_index")` now do `collection.sort_records(attrgetter("input_index"))`
- Tests pass

**Steps:**
1. `grep -rn 'sort_records("' tests/`
2. Update each call site

## End-of-Phase Verification
- `sort_records` accepts a callable
- Tests pass

## Notes
- The old `key: str` API was fragile and un-typecheckable; the new API is standard Python.