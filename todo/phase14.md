# Phase 14 — Convert `ScriptChunk` (revised per Issue C6)

## Goal
Either convert `ScriptChunk` to a `NamedTuple` (immutable) or keep it as a dataclass, depending on whether external code mutates it.

## Context
Depends on Phase 03. The mutation contract must be determined before deciding which path to take.

## Tasks

### Task 14.1 — Determine the mutation contract
**Acceptance Criteria:**
- A decision is documented: keep as dataclass (mutable) or convert to `NamedTuple` (immutable)
- The decision is based on whether any caller assigns to `chunk.opcode` or `chunk.data` after construction

**Steps:**
1. `grep -rn 'chunk\.\(opcode\|data\)\s*=' btx/ tests/ --include='*.py'`
2. If hits exist, keep as dataclass (mutable)
3. If no hits, convert to `NamedTuple` (immutable, simpler)

### Task 14.2 — Apply the chosen transformation
**Acceptance Criteria:**
- `ScriptChunk` is either a `@dataclass` or a `NamedTuple` with consistent field names
- Redundant `__slots__` is removed (both `@dataclass` and `NamedTuple` already provide it)
- The `is_push` accessor still works

**Steps:**
1. Based on Task 14.1's decision:
   - If `NamedTuple`: rewrite the class declaration; keep all field names; replace `@property is_push` with a method or computed value
   - If dataclass: only remove the redundant `__slots__ = (...)` line

### Task 14.3 — Verify callers continue to work
**Acceptance Criteria:**
- All `ScriptChunk(...)` constructions across the codebase still type-check
- If converted to `NamedTuple`, no caller attempts mutation
- All script-related tests pass

**Steps:**
1. Run `uv run pytest tests/test_script.py tests/test_classifier.py -q` (or whatever covers script parsing)
2. Run `uv run mypy btx/`

## End-of-Phase Verification
- `ScriptChunk` is either a `NamedTuple` or a stripped-down dataclass (no redundant `__slots__`)
- All callers continue to compile and run
- The decision is recorded in the phase notes below

## Notes
- The audit initially suggested converting to `NamedTuple`; the revision (per Issue C6) defers the decision to the actual mutation audit.
- If kept as dataclass, the redundant `__slots__ = (...)` line is the only cleanup.