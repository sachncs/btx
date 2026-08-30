# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Tests for the new curve/ package (Point, operations, backends)."""

import pytest

from btx.curve import (
    CURVE_ORDER,
    FIELD_PRIME,
    GENERATOR_POINT,
    INFINITY_POINT,
    NativeBackend,
    Point,
    add,
    double,
    get_backend,
    is_on_curve,
    multiply,
    negate,
    set_backend,
)


class TestPoint:
    def test_creation(self) -> None:
        p = Point(x=1, y=2)
        assert p.x == 1
        assert p.y == 2
        assert not p.infinity

    def test_infinity(self) -> None:
        p = Point(infinity=True)
        assert p.infinity
        assert p.x is None
        assert p.y is None

    def test_equality(self) -> None:
        a = Point(x=1, y=2)
        b = Point(x=1, y=2)
        c = Point(x=1, y=3)
        assert a == b
        assert a != c
        assert INFINITY_POINT == Point(infinity=True)

    def test_hash(self) -> None:
        a = Point(x=1, y=2)
        b = Point(x=1, y=2)
        assert hash(a) == hash(b)

    def test_generator_on_curve(self) -> None:
        assert is_on_curve(GENERATOR_POINT)

    def test_infinity_on_curve(self) -> None:
        assert is_on_curve(INFINITY_POINT)

    def test_off_curve(self) -> None:
        p = Point(x=1, y=2)
        assert not is_on_curve(p)

    def test_invalid_field_range(self) -> None:
        with pytest.raises(ValueError, match="out of field"):
            Point(x=FIELD_PRIME + 1, y=0)

    def test_repr_infinity(self) -> None:
        assert repr(INFINITY_POINT) == "Point(infinity=True)"

    def test_repr_affine(self) -> None:
        r = repr(GENERATOR_POINT)
        assert r.startswith("Point(x=0x")


class TestPointOperations:
    def test_negate(self) -> None:
        neg = negate(GENERATOR_POINT)
        assert is_on_curve(neg)
        assert negate(neg) == GENERATOR_POINT

    def test_negate_infinity(self) -> None:
        assert negate(INFINITY_POINT) == INFINITY_POINT

    def test_add_generator_and_negation(self) -> None:
        result = add(GENERATOR_POINT, negate(GENERATOR_POINT))
        assert result == INFINITY_POINT

    def test_add_with_infinity(self) -> None:
        assert add(GENERATOR_POINT, INFINITY_POINT) == GENERATOR_POINT
        assert add(INFINITY_POINT, GENERATOR_POINT) == GENERATOR_POINT

    def test_double_generator(self) -> None:
        d = double(GENERATOR_POINT)
        assert is_on_curve(d)
        assert d != GENERATOR_POINT

    def test_double_infinity(self) -> None:
        assert double(INFINITY_POINT) == INFINITY_POINT

    def test_multiply_by_one(self) -> None:
        assert multiply(1, GENERATOR_POINT) == GENERATOR_POINT

    def test_multiply_by_zero(self) -> None:
        assert multiply(0, GENERATOR_POINT) == INFINITY_POINT

    def test_multiply_by_order(self) -> None:
        assert multiply(CURVE_ORDER, GENERATOR_POINT) == INFINITY_POINT

    def test_double_equals_add_self(self) -> None:
        assert double(GENERATOR_POINT) == add(GENERATOR_POINT, GENERATOR_POINT)


class TestPointSecRoundtrip:
    def test_compressed_roundtrip(self) -> None:
        ser = GENERATOR_POINT.to_sec_compressed()
        assert len(ser) == 33
        parsed = Point.from_sec_compressed(ser)
        assert parsed == GENERATOR_POINT

    def test_uncompressed_roundtrip(self) -> None:
        ser = GENERATOR_POINT.to_sec_uncompressed()
        assert len(ser) == 65
        parsed = Point.from_sec_uncompressed(ser)
        assert parsed == GENERATOR_POINT

    def test_compressed_prefix(self) -> None:
        ser = GENERATOR_POINT.to_sec_compressed()
        assert ser[0] in (0x02, 0x03)

    def test_invalid_sec(self) -> None:
        with pytest.raises(ValueError):
            Point.from_sec_compressed(b"\x00" * 33)
        with pytest.raises(ValueError):
            Point.from_sec_uncompressed(b"\x00" * 65)

    def test_infinity_cannot_serialize(self) -> None:
        from btx.encoding.sec import serialize_sec

        with pytest.raises(ValueError, match="Cannot serialize"):
            serialize_sec(INFINITY_POINT)


class TestPointMethods:
    def test_negate(self) -> None:
        neg = GENERATOR_POINT.negate()
        assert GENERATOR_POINT.y is not None
        assert neg.x == GENERATOR_POINT.x
        assert neg.y is not None
        assert neg.y == -GENERATOR_POINT.y % FIELD_PRIME

    def test_add(self) -> None:
        result = GENERATOR_POINT.add(GENERATOR_POINT)
        assert result == double(GENERATOR_POINT)

    def test_double(self) -> None:
        result = GENERATOR_POINT.double()
        assert result == double(GENERATOR_POINT)

    def test_multiply(self) -> None:
        result = GENERATOR_POINT.multiply(2)
        assert result == double(GENERATOR_POINT)

    def test_multiply_by_zero(self) -> None:
        result = GENERATOR_POINT.multiply(0)
        assert result.infinity

    def test_is_on_curve(self) -> None:
        assert GENERATOR_POINT.is_on_curve()

    def test_is_on_curve_infinity(self) -> None:
        assert INFINITY_POINT.is_on_curve()

    def test_serialize_compressed(self) -> None:
        ser = GENERATOR_POINT.serialize(compressed=True)
        assert len(ser) == 33

    def test_serialize_uncompressed(self) -> None:
        ser = GENERATOR_POINT.serialize(compressed=False)
        assert len(ser) == 65

    def test_operator_add(self) -> None:
        assert GENERATOR_POINT + GENERATOR_POINT == double(GENERATOR_POINT)

    def test_operator_sub(self) -> None:
        assert GENERATOR_POINT - GENERATOR_POINT == INFINITY_POINT

    def test_operator_mul(self) -> None:
        assert GENERATOR_POINT * 2 == double(GENERATOR_POINT)

    def test_operator_rmul(self) -> None:
        assert 2 * GENERATOR_POINT == double(GENERATOR_POINT)

    def test_operator_neg(self) -> None:
        assert -GENERATOR_POINT == GENERATOR_POINT.negate()


class TestBackendDispatch:
    def test_default_backend(self) -> None:
        assert get_backend() is None

    def test_set_backend(self) -> None:
        backend = NativeBackend()
        set_backend(backend)
        assert get_backend() is backend
        import btx.curve.dispatch as d

        d.backend = None
        d.resolved_default = None
        assert get_backend() is None

    def test_invalid_backend(self) -> None:
        with pytest.raises(TypeError):
            set_backend("invalid")  # type: ignore[arg-type]

    def test_dispatch_auto_resolve(self) -> None:
        """Dispatch functions auto-resolve backend without explicit set_backend."""
        from btx.curve.dispatch import resolve_backend

        backend = resolve_backend()
        from btx.curve.backend.native import NativeBackend

        assert isinstance(backend, NativeBackend)

    def test_dispatch_functions_work_without_set_backend(self) -> None:
        """Operations work with auto-resolved backend."""
        from btx.curve.dispatch import add, is_on_curve, negate

        assert is_on_curve(GENERATOR_POINT)
        neg = negate(GENERATOR_POINT)
        assert add(GENERATOR_POINT, neg) == INFINITY_POINT
