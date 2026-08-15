# Phase 09 — Delete `PointArithmetic` facade, expose methods on `Point`

## Goal
Replace the `PointArithmetic` facade (a 7-method class with all-forwarding methods) with direct methods on the `Point` value type. Add operator overloading for `+`, `-`, `*`, and unary `-`.

## Context
Depends on Phase 19 (which handles the `__x`/`__y`/`__infinity` slot rename). For this phase to be testable, Phase 19 must complete first. After this phase, `point.negate()`, `point + other`, `k * point` etc. are all first-class.

## Tasks

### Task 09.1 — Delete `PointArithmetic` class
**Acceptance Criteria:**
- `grep -rn 'PointArithmetic' btx/ tests/ --include='*.py'` returns no matches
- `btx/curve/point.py` no longer defines `PointArithmetic`

**Steps:**
1. Read `btx/curve/point.py` lines 34-115
2. Delete the entire `PointArithmetic` class

### Task 09.2 — Add `Point.negate()` method
**Acceptance Criteria:**
- `point.negate()` returns the additive inverse of `point`
- For the generator, `GENERATOR_POINT.negate() + GENERATOR_POINT == Point(infinity=True)`
- Lazy-import inside the method to avoid circular import

**Steps:**
1. Add method to `Point` class
2. Inside, `from btx.curve.operations import negate; return negate(self)`

### Task 09.3 — Add `Point.add(other)` method
**Acceptance Criteria:**
- `p1.add(p2)` returns the sum
- `GENERATOR_POINT.add(GENERATOR_POINT) == double(GENERATOR_POINT)`

**Steps:**
1. Add method
2. Lazy-import `from btx.curve.operations import add; return add(self, other)`

### Task 09.4 — Add `Point.double()` method
**Acceptance Criteria:**
- `point.double()` returns `2 * point`

**Steps:**
1. Add method
2. Lazy-import `from btx.curve.operations import double; return double(self)`

### Task 09.5 — Add `Point.multiply(scalar)` method
**Acceptance Criteria:**
- `GENERATOR_POINT.multiply(2) == double(GENERATOR_POINT)`
- `GENERATOR_POINT.multiply(0) == INFINITY_POINT`
- `GENERATOR_POINT.multiply(-1)` raises `ValueError`

**Steps:**
1. Add method with `Raises: ValueError` if `scalar < 0`

### Task 09.6 — Add `Point.is_on_curve()` method
**Acceptance Criteria:**
- `GENERATOR_POINT.is_on_curve()` returns `True`
- A manually-constructed off-curve point returns `False`

**Steps:**
1. Add method
2. Lazy-import `from btx.curve.operations import is_on_curve; return is_on_curve(self)`

### Task 09.7 — Delete `Point.arithmetic` property
**Acceptance Criteria:**
- `grep -rn 'arithmetic' btx/ --include='*.py'` returns no matches
- `point.arithmetic` raises `AttributeError`

**Steps:**
1. Delete `btx/curve/point.py:182-189` (the `Point.arithmetic` property)

### Task 09.8 — Add operator overloading (per opportunity F8)
**Acceptance Criteria:**
- `p1 + p2 == p1.add(p2)`
- `p1 - p2 == p1.add(p2.negate())`
- `k * point == point.multiply(k)`
- `-point == point.negate()`

**Steps:**
1. Add `__add__(self, other)` returning `self.add(other)`
2. Add `__sub__(self, other)` returning `self.add(other.negate())`
3. Add `__mul__(self, scalar)` returning `self.multiply(scalar)` (only for int scalars; raise `TypeError` otherwise)
4. Add `__neg__(self)` returning `self.negate()`

### Task 09.9 — Add `Point.serialize(compressed=True)` convenience (per opportunity F9)
**Acceptance Criteria:**
- `point.serialize()` returns 33-byte compressed SEC by default
- `point.serialize(compressed=False)` returns 65-byte uncompressed SEC

**Steps:**
1. Add method that delegates to `to_sec_compressed()` or `to_sec_uncompressed()` based on `compressed`

### Task 09.10 — Update all `Point.arithmetic` call sites
**Acceptance Criteria:**
- `grep -rn 'point.arithmetic\|p.arithmetic\|\.arithmetic' btx/ tests/ --include='*.py'` returns no matches
- All curve tests pass

**Steps:**
1. Find every `point.arithmetic.negate()` etc. pattern
2. Replace with `point.negate()` etc.

## End-of-Phase Verification
- `python -c "from btx.curve import GENERATOR_POINT; p = GENERATOR_POINT; print(p + p, p * 3, -p)"` succeeds
- All curve-related tests pass
- `Point` has no `arithmetic` property

## Notes
- The lazy-imports inside each method preserve the original `PointArithmetic` pattern; they avoid circular imports at module load time.
- Operator overloading makes the value type behave like a number, which is the Pythonic expectation for a mathematical object.