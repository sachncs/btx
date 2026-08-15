# Phase 07 — Delete dead code

## Goal
Remove symbols that are defined but never used, and parameters that are accepted but documented as no-ops.

## Context
Depends on Phase 05 (BitcoinError → BtxError already done; this phase deletes other unused exception classes that inherit from it). After this phase, every named export is reachable.

## Tasks

### Task 07.1 — Delete `NotInvertible` exception
**Acceptance Criteria:**
- `grep -rn 'NotInvertible' btx/ tests/ --include='*.py'` returns no matches
- `btx/exceptions.py:__all__` no longer contains `"NotInvertible"`

**Steps:**
1. Read `btx/exceptions.py:38`
2. Delete the class definition
3. Remove `"NotInvertible"` from `__all__`

### Task 07.2 — Delete `PointError` exception
**Acceptance Criteria:**
- `grep -rn 'PointError' btx/ tests/ --include='*.py'` returns no matches
- `btx/exceptions.py:__all__` no longer contains `"PointError"`

**Steps:**
1. Read `btx/exceptions.py:42`
2. Delete the class definition
3. Remove `"PointError"` from `__all__`

### Task 07.3 — Delete `ParsingError` exception
**Acceptance Criteria:**
- `grep -rn 'ParsingError' btx/ tests/ --include='*.py'` returns no matches
- `btx/exceptions.py:__all__` no longer contains `"ParsingError"`

**Steps:**
1. Read `btx/exceptions.py:46`
2. Delete the class definition
3. Remove `"ParsingError"` from `__all__`

### Task 07.4 — Final shape of `btx/exceptions.py`
**Acceptance Criteria:**
- `btx/exceptions.py:__all__` reads `["BtxError", "UnsupportedScriptPathError"]`
- Only two classes remain in the file: `BtxError` and `UnsupportedScriptPathError`

**Steps:**
1. Read the file
2. Confirm only two classes remain
3. Verify `__all__` is correct

### Task 07.5 — Delete `NoNonceReuseError` exception
**Acceptance Criteria:**
- `grep -rn 'NoNonceReuseError' btx/ tests/ --include='*.py'` returns no matches
- `btx/signature/attack.py` no longer defines `NoNonceReuseError`

**Steps:**
1. Read `btx/signature/attack.py:70`
2. Delete the class

### Task 07.6 — Drop unused parameters from `collect_info`
**Acceptance Criteria:**
- `btx/descriptor/analyzer.py:97` (the `collect_info` function) accepts only `(node, keys)` — no `has_timelock` or `has_hash_lock`
- The single caller in `analyze_descriptor` (line 85) calls `collect_info(node, keys)` without the dropped parameters
- All descriptor tests pass

**Steps:**
1. Read `btx/descriptor/analyzer.py` to identify the `collect_info` function and its caller
2. Remove the two parameters from the signature
3. Remove the two arguments from the call site
4. Update the docstring to remove the "Accepted for API symmetry; not modified" prose

### Task 07.7 — Delete `Record.vin` and `Record.sig` alias properties
**Acceptance Criteria:**
- `btx/signature/record.py:58-67` no longer defines `vin` or `sig` properties
- `Record.input_index` and `Record.signature` remain as the canonical attributes
- No tests reference `record.vin` or `record.sig`

**Steps:**
1. Read `btx/signature/record.py` lines 58-67
2. Delete both `@property` definitions
3. Search for `.vin` and `.sig` usages on `Record` instances and update them to use the canonical names

### Task 07.8 — Delete dead `BlockchainProvider(Protocol)`
**Acceptance Criteria:**
- `grep -rn 'BlockchainProvider' btx/ --include='*.py'` returns no matches
- `btx/services/blockchain.py` no longer defines the Protocol

**Steps:**
1. Read `btx/services/blockchain.py:68`
2. Delete the class definition and its `@runtime_checkable` decorator

### Task 07.9 — Delete dead `ExtractorPlugin(Protocol)`
**Acceptance Criteria:**
- `grep -rn 'ExtractorPlugin' btx/ --include='*.py'` returns no matches
- `btx/signature/extraction/plugins.py:31` no longer defines the Protocol

**Steps:**
1. Read the file
2. Delete the class definition and its `@runtime_checkable` decorator

## End-of-Phase Verification
- `grep -rn 'NotInvertible\|PointError\|ParsingError\|NoNonceReuseError\|BlockchainProvider\|ExtractorPlugin' btx/ tests/ --include='*.py'` returns no matches
- `collect_info` has only `(node, keys)` parameters
- `Record` has no `vin` or `sig` alias properties
- All tests pass

## Notes
- The two Protocols were never subclassed; deleting them removes documentation-only dead weight.
- The three deleted exceptions (`NotInvertible`, `PointError`, `ParsingError`) were defined but `raise`'d nowhere — pure no-ops. Callers that need them can re-introduce with a real call site.