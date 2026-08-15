# Phase 20 — Duplicated `HASH_BYTE_LENGTH`

## Goal
Eliminate the duplicate `HASH_BYTE_LENGTH = 32` constant that appears in both `btx/signature/check.py` and `btx/signature/signer.py`.

## Context
Depends on Phase 03. After this phase, only one definition exists.

## Tasks

### Task 20.1 — Keep the definition in `btx/signature/check.py`
**Acceptance Criteria:**
- `btx/signature/check.py:48` still defines `HASH_BYTE_LENGTH = 32`
- The constant is module-level and `UPPER_SNAKE_CASE`

**Steps:**
1. Read the line
2. Confirm it remains

### Task 20.2 — Remove the duplicate in `btx/signature/signer.py`
**Acceptance Criteria:**
- `btx/signature/signer.py:41` no longer defines `HASH_BYTE_LENGTH`
- `btx/signature/signer.py` imports `HASH_BYTE_LENGTH` from `btx.signature.check`
- All signer tests pass

**Steps:**
1. Read `btx/signature/signer.py`
2. Delete the `HASH_BYTE_LENGTH = 32` line
3. Add `from btx.signature.check import HASH_BYTE_LENGTH` at the top

## End-of-Phase Verification
- `grep -rn 'HASH_BYTE_LENGTH' btx/ --include='*.py'` shows exactly one definition and multiple usages
- Tests pass

## Notes
- Alternative: move `HASH_BYTE_LENGTH` to `btx/encoding/hasher.py` (where the hash functions live). This is more discoverable. Pick whichever fits the codebase organization better — the constant `32` is the byte length of a SHA-256 hash.