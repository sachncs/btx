# Phase 15 — Add `BaseExtractor` ABC (revised per Issue C9)

## Goal
Collapse the 5 parallel extractor classes (`LegacyExtractor`, `P2WPKHExtractor`, `P2WSHExtractor`, `P2SHSegWitExtractor`, `TaprootExtractor`) into subclasses of a new `BaseExtractor` ABC. Convert their staticmethods into instance methods.

## Context
Depends on Phase 03 and Phase 07 (deleted dead `ExtractorPlugin` Protocol). The revision (per Issue C9) acknowledges that the static→instance change is a public-API break; tests must be updated accordingly.

## Tasks

### Task 15.1 — Define `BaseExtractor` ABC
**Acceptance Criteria:**
- `btx/signature/extraction/engine.py` defines:
  ```python
  class BaseExtractor(ABC):
      name: ClassVar[str]
      @abstractmethod
      def can_handle(self, script_type: str, is_segwit: bool) -> bool: ...
      @abstractmethod
      def extract(self, tx, vin, txin, script_pubkey, value) -> list[Record]: ...
  ```
- `BaseExtractor` cannot be instantiated directly (`TypeError`)

**Steps:**
1. Add the imports: `from abc import ABC, abstractmethod` (if not already), `from typing import ClassVar`
2. Add the class

### Task 15.2 — Document the call-site convention change
**Acceptance Criteria:**
- The `BaseExtractor` docstring states: "Subclasses implement instance methods. The legacy static-method convention is removed."

**Steps:**
1. Add the note to the class docstring

### Task 15.3 — Convert `LegacyExtractor` to subclass
**Acceptance Criteria:**
- `LegacyExtractor` extends `BaseExtractor`
- Its `can_handle` and `extract` are instance methods (no `@staticmethod`)
- It defines `name: ClassVar[str] = "legacy"`

**Steps:**
1. Read `btx/signature/extraction/engine.py:78-100`
2. Remove `@staticmethod` from both methods
3. Add `BaseExtractor` as base
4. Add the `name` class variable

### Task 15.4 — Convert remaining four extractors
**Acceptance Criteria:**
- `P2WPKHExtractor`, `P2WSHExtractor`, `P2SHSegWitExtractor`, `TaprootExtractor` all extend `BaseExtractor`
- All four have instance-method `can_handle` and `extract`
- All four define `name`

**Steps:**
1. Apply the same transformation to each of the four remaining classes

### Task 15.5 — Update `BUILTIN_EXTRACTOR_CLASSES` registration
**Acceptance Criteria:**
- The registry now contains instances, not classes:
  ```python
  BUILTIN_EXTRACTOR_INSTANCES: tuple[BaseExtractor, ...] = (
      LegacyExtractor(),
      P2WPKHExtractor(),
      P2WSHExtractor(),
      P2SHSegWitExtractor(),
      TaprootExtractor(),
  )
  ```
- Registration loop iterates over instances and calls `.can_handle(...)` directly

**Steps:**
1. Replace `BUILTIN_EXTRACTOR_CLASSES` with the instance tuple
2. Update the registration loop in `register_builtin_extractors()`

### Task 15.6 — Update tests to use instances
**Acceptance Criteria:**
- Tests that did `LegacyExtractor.can_handle(...)` now do `LegacyExtractor().can_handle(...)`
- `grep -rn 'LegacyExtractor\.\(can_handle\|extract\)\b' tests/'` returns no matches

**Steps:**
1. `grep -rn '[A-Z][A-Za-z]*Extractor\.\(can_handle\|extract\)' tests/`
2. Update each call site

### Task 15.7 — Update `tests/test_extraction.py`, `tests/test_extraction_coverage.py`
**Acceptance Criteria:**
- All extraction tests pass
- New tests exist (added in Phase 26.8 if needed) for the instance-method convention

**Steps:**
1. Run `uv run pytest tests/test_extraction.py tests/test_extraction_coverage.py -v`
2. Fix any failures

## End-of-Phase Verification
- 5 extractors share a common base class
- All extraction tests pass
- The `register_builtin_extractors()` call still works

## Notes
- This is a public API break: callers using the old static-method convention must instantiate.
- The benefit is a uniform interface and the ability to add state to extractors later (e.g. caching).