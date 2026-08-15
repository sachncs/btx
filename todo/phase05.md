# Phase 05 — Rename `BitcoinError` → `BtxError`

## Goal
Rename the package's base exception class from `BitcoinError` to `BtxError` for naming consistency with the package `btx`.

## Context
Depends on Phase 03 (which renamed module references) and Phase 04 (which renamed runtime strings). After this phase, the only exception class named after the package is `BtxError`.

## Tasks

### Task 05.1 — Update `__all__` in `btx/exceptions.py`
**Acceptance Criteria:**
- `btx/exceptions.py:25-31` contains `"BtxError"` (not `"BitcoinError"`)
- The list still contains `"UnsupportedScriptPathError"`

**Steps:**
1. Read `btx/exceptions.py` lines 25-31
2. Replace `"BitcoinError"` with `"BtxError"`

### Task 05.2 — Rename class definition
**Acceptance Criteria:**
- `btx/exceptions.py:34` reads `class BtxError(ValueError):`
- No `class BitcoinError` exists in the codebase

**Steps:**
1. Read line 34
2. Replace `BitcoinError` with `BtxError`

### Task 05.3 — Update class docstring
**Acceptance Criteria:**
- `btx/exceptions.py:35` reads `"""Base exception for all btx package errors."""`

**Steps:**
1. Read line 35
2. Replace `bitcoin package` with `btx package`

### Task 05.4 — Update subclass base classes
**Acceptance Criteria:**
- `btx/exceptions.py:38, 42, 46, 50` all use `BtxError` as the base class
- All four subclasses (`NotInvertible`, `PointError`, `ParsingError`, `UnsupportedScriptPathError`) inherit from `BtxError`

**Steps:**
1. Read lines 38, 42, 46, 50
2. Replace `BitcoinError` with `BtxError` in each base-class position

### Task 05.5 — Update top-level re-export
**Acceptance Criteria:**
- `btx/__init__.py` imports `BtxError` from `btx.exceptions`
- `btx/__init__.py:__all__` contains `"BtxError"` (not `"BitcoinError"`)
- `btx.BtxError is btx.exceptions.BtxError` is True at runtime

**Steps:**
1. Read `btx/__init__.py` around lines 115-121 and 264
2. Replace `BitcoinError` with `BtxError`

### Task 05.6 — Update exception usage in `btx/signature/attack.py`
**Acceptance Criteria:**
- `btx/signature/attack.py:54, 62` reference `BtxError`
- `btx/signature/attack.py` no longer references `BitcoinError`

**Steps:**
1. Read lines 54 and 62
2. Replace `BitcoinError` with `BtxError`

### Task 05.7 — Update docs/API.md exception reference
**Acceptance Criteria:**
- `docs/API.md:21` (or the equivalent line after prior renames) uses `:exc:`BtxError``
- The Sphinx cross-reference renders correctly when docs are built

**Steps:**
1. Search `docs/API.md` for `BitcoinError`
2. Replace with `BtxError`

### Task 05.8 — Update docs/MODULES.md exception section
**Acceptance Criteria:**
- The exception section header in `docs/MODULES.md:243-252` (after prior renames) refers to `BtxError`
- All inline references use the new name

**Steps:**
1. Read the section
2. Replace every `BitcoinError` with `BtxError`

### Task 05.9 — CHANGELOG historical entry is left untouched
**Acceptance Criteria:**
- `CHANGELOG.md:157` (or wherever the historical `BitcoinError(ValueError)` mention lives) remains as-is
- The historical note is a record of past API; it is not retroactively edited

**Steps:**
1. Read line 157
2. Confirm no change is made

## End-of-Phase Verification
- `grep -rn 'BitcoinError' btx/ tests/ --include='*.py'` returns no matches
- `grep -rn 'BitcoinError' docs/ CHANGELOG.md README.md CONTRIBUTING.md` returns no matches in forward-looking docs (historical CHANGELOG entry may remain)
- `python -c "import btx; print(btx.BtxError)"` works
- All tests still pass

## Notes
- This is a public API break. Anyone catching `BitcoinError` must update to `BtxError`.
- The CHANGELOG.md historical entry (Phase 05.9) deliberately preserves the old name — historical CHANGELOG entries are immutable records of what was shipped, not living documentation.