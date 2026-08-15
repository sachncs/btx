# Phase 13 — Unify `MutableInput` / `MutableOutput` with `PsbtInput` / `PsbtOutput` (revised per Issue C4)

## Goal
Eliminate the mutable shadow dataclasses by using `dataclasses.replace()` for in-place edits within `PsbtEditor`, while keeping `PsbtInput` / `PsbtOutput` frozen.

## Context
Depends on Phase 03. The revision (per Issue C4) preserves the immutability contract of `PsbtInput`/`PsbtOutput` rather than removing `frozen=True`.

## Tasks

### Task 13.1 — Delete `MutableInput`
**Acceptance Criteria:**
- `grep -rn 'MutableInput' btx/ tests/ --include='*.py'` returns no matches

**Steps:**
1. Read `btx/psbt/editor.py:38`
2. Delete the dataclass

### Task 13.2 — Delete `MutableOutput`
**Acceptance Criteria:**
- `grep -rn 'MutableOutput' btx/ tests/ --include='*.py'` returns no matches

**Steps:**
1. Read `btx/psbt/editor.py:53`
2. Delete the dataclass

### Task 13.3 — Confirm `PsbtInput` / `PsbtOutput` remain frozen
**Acceptance Criteria:**
- `btx/psbt/models.py:36` and `:77` retain `@dataclass(frozen=True, slots=True)`
- `psbt_input.field = value` raises `FrozenInstanceError`

**Steps:**
1. Read the model file
2. Confirm `frozen=True` is still in the decorator

### Task 13.4 — Update `PsbtEditor` to use `dataclasses.replace()`
**Acceptance Criteria:**
- `PsbtEditor.set_field(input_index=0, key=b"\\x07", value=...)` replaces the input at index 0 with a new frozen `PsbtInput`
- After `replace()`, the original `PsbtInput` is unchanged

**Steps:**
1. Read `btx/psbt/editor.py:__init__` and the editing methods
2. Replace each `self.inputs[i].field = value` with `self.inputs = (*self.inputs[:i], dataclasses.replace(self.inputs[i], field=value), *self.inputs[i+1:])`
3. Or use `self.inputs = tuple(dataclasses.replace(inp, field=value) if j == i else inp for j, inp in enumerate(self.inputs))`

### Task 13.5 — `PsbtEditor.build()` produces the immutable `Psbt`
**Acceptance Criteria:**
- After all edits, `editor.build()` returns a `Psbt` whose `inputs` is a tuple of frozen `PsbtInput` instances

**Steps:**
1. Confirm `build()` constructs `Psbt(*)` from the stored tuple

## End-of-Phase Verification
- No `MutableInput` / `MutableOutput` exist
- `PsbtEditor` editing operations work via `dataclasses.replace`
- All PSBT editor tests pass
- `PsbtInput` and `PsbtOutput` remain frozen

## Notes
- The revision preserves hashability (Issue C4). If a user relied on `MutableInput` mutation, they must migrate to `PsbtEditor` API.
- Performance: `replace()` is O(1) per field (it copies the frozen dataclass once). Replacing in a tuple is O(n) but PSBTs rarely have more than a few hundred inputs.