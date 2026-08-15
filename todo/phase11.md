# Phase 11 — Refactor `JSONFormatter` (revised per Issue C3)

## Goal
Split the `JSONFormatter` class into a free function for the formatting logic and a minimal subclass of `logging.Formatter` that delegates to it. This satisfies the constraint that `logging.Formatter()` expects a format string, not a callable.

## Context
Depends on Phase 03. After this phase, the JSON formatting logic lives in a free function but the `logging.Formatter` subclass that `setFormatter()` requires is preserved (4 lines, not 1).

## Tasks

### Task 11.1 — Add free `format_json(record)` function
**Acceptance Criteria:**
- `btx/cli/app.py` defines a module-level `def format_json(record: logging.LogRecord) -> str`
- The function returns the same JSON string the old `JSONFormatter.format()` method returned

**Steps:**
1. Read `btx/cli/app.py:56-71` (the old `JSONFormatter` class)
2. Extract the body of the `format` method into a top-level function
3. Add a Google-style docstring with `Args:` and `Returns:`

### Task 11.2 — Reduce `JSONFormatter` to a thin delegating subclass
**Acceptance Criteria:**
- `JSONFormatter` (or `JsonFormatter`, PEP 8) is a 4-line class:
  ```python
  class JsonFormatter(logging.Formatter):
      def format(self, record: logging.LogRecord) -> str:
          return format_json(record)
  ```
- The class has a docstring referencing `format_json`

**Steps:**
1. Rename `JSONFormatter` to `JsonFormatter` (PEP 8)
2. Reduce the class body to the delegation shown above

### Task 11.3 — Update `configure_logging()`
**Acceptance Criteria:**
- `configure_logging()` uses `JsonFormatter` (not the deleted `JSONFormatter`)
- `BTX_LOG_LEVEL=DEBUG btx health` emits JSON-formatted log lines

**Steps:**
1. Read `btx/cli/app.py` `configure_logging()`
2. Confirm it instantiates `JsonFormatter()`

### Task 11.4 — Update tests importing `JSONFormatter`
**Acceptance Criteria:**
- Any test that imported `JSONFormatter` now imports `JsonFormatter`
- Tests pass

**Steps:**
1. `grep -rn 'JSONFormatter' btx/ tests/ --include='*.py'`
2. Update each import to `JsonFormatter`

## End-of-Phase Verification
- `grep -rn 'JSONFormatter' btx/ tests/ --include='*.py'` returns no matches (renamed)
- `BTX_LOG_LEVEL=DEBUG btx health | head` produces JSON-formatted log lines
- All CLI tests pass

## Notes
- This was identified as Issue C3 in the plan: pure free function alone won't work because `logging.Formatter(fmt=...)` expects a format *string*. The minimal subclass is the correct solution.