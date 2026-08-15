# Phase 17 — Unify `BatchResult` ↔ `PsbtBatchResult`

## Goal
Collapse the two near-identical batch-result dataclasses into a single generic `BatchResult[T]`.

## Context
Depends on Phase 03. After this phase, both pipelines use one type.

## Tasks

### Task 17.1 — Convert `BatchResult` to a generic
**Acceptance Criteria:**
- `btx/signature/pipeline.py:121` defines:
  ```python
  @dataclass(frozen=True, slots=True)
  class BatchResult(Generic[T]):
      items: tuple[T, ...]
      errors: tuple[tuple[str, str], ...]
      @property
      def total(self) -> int: return len(self.items) + len(self.errors)
      @property
      def successful(self) -> int: return len(self.items)
      @property
      def failed(self) -> int: return len(self.errors)
  ```
- `BatchResult[Record]`, `BatchResult[Psbt]` etc. work

**Steps:**
1. Add `from typing import Generic, TypeVar` with `T = TypeVar("T")`
2. Rewrite the class

### Task 17.2 — Delete `PsbtBatchResult`
**Acceptance Criteria:**
- `grep -rn 'PsbtBatchResult' btx/ tests/ --include='*.py'` returns no matches
- `btx/psbt/pipeline.py:35` no longer defines the class

**Steps:**
1. Read the file
2. Delete the class

### Task 17.3 — PSBT pipeline uses `BatchResult[Psbt]`
**Acceptance Criteria:**
- `btx/psbt/pipeline.py` constructs `BatchResult[Psbt]` instead of `PsbtBatchResult`

**Steps:**
1. Update the type annotation and instantiation

### Task 17.4 — Signature pipeline uses `BatchResult[Record]`
**Acceptance Criteria:**
- `btx/signature/pipeline.py` constructs `BatchResult[Record]`

**Steps:**
1. Update the type annotation and instantiation

### Task 17.5 — Update callers and tests
**Acceptance Criteria:**
- All callers (in `btx/`, `tests/`, `docs/`) use `BatchResult[T]` 
- Tests pass

**Steps:**
1. `grep -rn 'PsbtBatchResult' btx/ tests/ docs/ --include='*.py' --include='*.md'`
2. Update each site
3. Run `uv run pytest tests/test_pipeline.py tests/test_psbt_new.py -v`

## End-of-Phase Verification
- Only one batch-result type exists
- Both pipelines produce `BatchResult[T]` instances
- All tests pass

## Notes
- The original `BatchResult` had `records` (and `PsbtBatchResult` had `psbts`); both are now uniformly called `items`. This is a minor API break for anyone using the old `records` field name.