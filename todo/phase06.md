# Phase 06 — Rename `GENERATOR` / `INFINITY` constants

## Goal
Rename the two module-level constants that violate PEP 8 by using PascalCase: `GENERATOR` → `GENERATOR_POINT` and `INFINITY` → `INFINITY_POINT`.

## Context
Depends on Phase 03 (which renamed module references but did not touch identifiers). After this phase, no module-level constant uses PascalCase except for class names and type aliases (which PEP 8 explicitly endorses).

## Tasks

### Task 06.1 — Rename `GENERATOR` in `btx/curve/__init__.py`
**Acceptance Criteria:**
- `btx/curve/__init__.py:75` defines `GENERATOR_POINT` (not `GENERATOR`)
- `GENERATOR_POINT` is a `Point` instance with `x=GENERATOR_X, y=GENERATOR_Y`
- `python -c "from btx.curve import GENERATOR_POINT; print(GENERATOR_POINT)"` succeeds

**Steps:**
1. Read line 75
2. Replace `GENERATOR` with `GENERATOR_POINT`

### Task 06.2 — Rename `INFINITY` in `btx/curve/__init__.py`
**Acceptance Criteria:**
- `btx/curve/__init__.py:76` defines `INFINITY_POINT` (not `INFINITY`)
- `INFINITY_POINT` is a `Point` instance with `infinity=True`

**Steps:**
1. Read line 76
2. Replace `INFINITY` with `INFINITY_POINT`

### Task 06.3 — Update `__all__` in `btx/curve/__init__.py`
**Acceptance Criteria:**
- The `__all__` list contains `"GENERATOR_POINT"` and `"INFINITY_POINT"` (not the PascalCase originals)

**Steps:**
1. Read `btx/curve/__init__.py` `__all__` (around lines 84, 87)
2. Replace `"GENERATOR"` with `"GENERATOR_POINT"`
3. Replace `"INFINITY"` with `"INFINITY_POINT"`

### Task 06.4 — Rename `INFINITY` in `btx/curve/batch.py`
**Acceptance Criteria:**
- `btx/curve/batch.py:33` defines `INFINITY_POINT` (not `INFINITY`)
- `from btx.curve.batch import INFINITY_POINT` succeeds

**Steps:**
1. Read line 33
2. Replace `INFINITY` with `INFINITY_POINT`

### Task 06.5 — Update top-level re-export
**Acceptance Criteria:**
- `btx/__init__.py` imports and re-exports `GENERATOR_POINT` and `INFINITY_POINT`
- `btx/__init__.py:__all__` contains the new names (not the old PascalCase ones)

**Steps:**
1. Read `btx/__init__.py` around lines 278, 282
2. Update the imports and `__all__`

### Task 06.6 — Update health.py import
**Acceptance Criteria:**
- `btx/health.py:86` imports `GENERATOR_POINT` (not `GENERATOR`)
- `btx health` runs successfully

**Steps:**
1. Read line 86
2. Update the import

### Task 06.7 — Update all call sites
**Acceptance Criteria:**
- `grep -rE '\bGENERATOR\b' btx/ tests/ docs/ --include='*.py' --include='*.md' --include='*.rst'` returns no matches except possibly in docstrings referencing historical context
- `grep -rE '\bINFINITY\b' btx/ tests/ docs/ --include='*.py' --include='*.md' --include='*.rst'` returns no matches except in places where the word `INFINITY` appears in error messages or unrelated contexts (e.g. `math.inf` references)
- All curve tests pass

**Steps:**
1. Find all call sites in source: `grep -rln 'GENERATOR\b\|INFINITY\b' btx/ tests/`
2. Replace each with the new name
3. Run `uv run pytest tests/test_curve.py tests/test_imports.py tests/test_mainnet.py -q` and confirm green

## End-of-Phase Verification
- Only `GENERATOR_X`, `GENERATOR_Y`, `GENERATOR_POINT`, `INFINITY_POINT` exist in the codebase
- All curve-related tests pass
- `python -c "import btx; print(btx.GENERATOR_POINT, btx.INFINITY_POINT)"` succeeds

## Notes
- The math-notation `R`, `G`, `Q` locals remain under per-file `N806` ignores (intentional cryptographic convention).
- `GENERATOR_POINT` and `INFINITY_POINT` are immutable singletons used as group identity and generator in secp256k1 arithmetic.