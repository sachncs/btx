# Phase 08 — Replace `Settings` with frozen dataclass

## Goal
Convert the hand-rolled `Settings` class (with `__slots__`, internal lock, and 3 property/setter pairs) into a frozen dataclass with a single validated field.

## Context
Depends on Phase 07 (dead settings fields `strict_mode` and `max_extraction_inputs` are deleted; the validation logic moves into `__post_init__`). After this phase, `Settings` is a 10-line frozen dataclass.

## Tasks

### Task 08.1 — Delete `strict_mode` property/setter/slot
**Acceptance Criteria:**
- `btx/settings.py` no longer has `__strict_mode` slot, `strict_mode` property, or `strict_mode` setter
- `grep -rn 'strict_mode' btx/ tests/ --include='*.py'` returns no matches (confirming the field is unused anywhere)

**Steps:**
1. Read `btx/settings.py` lines 50-59
2. Delete the property, setter, and `__slots__` entry for `__strict_mode`

### Task 08.2 — Delete `max_extraction_inputs` property/setter/slot
**Acceptance Criteria:**
- `btx/settings.py` no longer has `__max_extraction_inputs` slot, property, or setter
- `grep -rn 'max_extraction_inputs' btx/ tests/ --include='*.py'` returns no matches

**Steps:**
1. Read `btx/settings.py` lines 75-86
2. Delete the property, setter, and `__slots__` entry

### Task 08.3 — Convert `Settings` to a frozen dataclass
**Acceptance Criteria:**
- `btx/settings.py:26` reads:
  ```python
  @dataclass(frozen=True, slots=True)
  class Settings:
      default_backend: str | None = None
  ```
- `Settings()` instantiates with `default_backend=None`
- Attempting to set `settings.default_backend = "native"` raises `FrozenInstanceError`

**Steps:**
1. Read `btx/settings.py`
2. Replace the entire class with the dataclass above
3. Add `from dataclasses import dataclass` if not already imported
4. Delete the manual `__init__`, the `__repr__`, the lock, and the validation setter logic

### Task 08.4 — Add `__post_init__` validation
**Acceptance Criteria:**
- `Settings(default_backend="invalid")` raises `ValueError("default_backend must be one of (None, 'native', 'libsecp').")`
- `Settings(default_backend=None)`, `Settings(default_backend="native")`, `Settings(default_backend="libsecp")` all succeed

**Steps:**
1. Add `def __post_init__(self) -> None:` to the class
2. Inside, validate `self.default_backend in (None, "native", "libsecp")`; raise `ValueError` otherwise
3. Test by importing and instantiating with each value

### Task 08.5 — Module-level singleton
**Acceptance Criteria:**
- `btx/settings.py:97` reads `settings = Settings()`
- `btx.settings.settings.default_backend is None`
- `btx.settings` re-exports `settings` from `btx/__init__.py`

**Steps:**
1. Keep the `settings = Settings()` line at module scope
2. Confirm the re-export is intact

### Task 08.6 — Document the thread-safety trade-off (per Issue M2)
**Acceptance Criteria:**
- `btx/settings.py` module docstring includes a note that mutation via `dataclasses.replace()` is atomic at the Python level but not safe across concurrent threads, and that callers requiring thread-safe mutation should wrap the `replace()` call in an external lock

**Steps:**
1. Read the module docstring
2. Add the trade-off paragraph

### Task 08.7 — Drop the threading lock
**Acceptance Criteria:**
- `grep -n 'threading\|Lock\|__lock' btx/settings.py` returns no matches
- No `import threading` remains in `btx/settings.py`

**Steps:**
1. Remove `import threading`
2. Remove the `__lock` slot
3. Remove `self.__lock = threading.Lock()` from the old `__init__`

## End-of-Phase Verification
- `btx/settings.py` is approximately 25 lines (was 97)
- `python -c "import btx; s = btx.settings; print(s.default_backend)"` succeeds
- Tests that touch settings still pass

## Notes
- The frozen dataclass gives us immutability + value semantics for free. The trade-off (no built-in thread-safety) is acceptable because `Settings` is read-mostly; the only mutation path is `dataclasses.replace()`.
- If future thread-safety becomes a requirement, wrap `replace()` calls in a `threading.Lock` at the call site.