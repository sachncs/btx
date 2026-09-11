# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
# ruff: noqa: E501
"""Threading and concurrency safety tests."""

from __future__ import annotations

import threading

import pytest

from btx.curve import (
    CURVE_ORDER,
    GENERATOR_POINT,
    INFINITY_POINT,
    NativeBackend,
    get_backend,
    multiply,
    set_backend,
)
from btx.settings import Settings


class TestSettingsThreadSafety:
    def test_concurrent_reads(self) -> None:
        """Concurrent reads on a frozen dataclass are always safe."""
        local_settings = Settings(default_backend="native")
        errors: list[Exception] = []

        def worker() -> None:
            try:
                for _ in range(100):
                    _ = local_settings.default_backend
                    _ = repr(local_settings)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors

    def test_frozen_blocks_mutation(self) -> None:
        """A frozen dataclass rejects attribute assignment."""
        import dataclasses

        s = Settings(default_backend="native")
        with pytest.raises(dataclasses.FrozenInstanceError):
            s.default_backend = "libsecp"  # type: ignore[misc]


class TestBackendDispatchRaceCondition:
    def setup_method(self) -> None:
        import btx.curve.dispatch as d

        d.backend = None
        d.resolved_default = None

    def teardown_method(self) -> None:
        import btx.curve.dispatch as d

        d.backend = None
        d.resolved_default = None

    def test_set_and_get_concurrent(self) -> None:
        errors: list[Exception] = []

        def setter() -> None:
            try:
                backend = NativeBackend()
                set_backend(backend)
            except Exception as exc:
                errors.append(exc)

        def getter() -> None:
            try:
                _ = get_backend()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=setter) for _ in range(2)] + [
            threading.Thread(target=getter) for _ in range(2)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors

    def test_resolve_backend_under_contention(self) -> None:
        from btx.curve.dispatch import resolve_backend

        errors: list[Exception] = []

        def worker() -> None:
            try:
                resolved = resolve_backend()
                assert resolved is not None
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors

    def test_multiply_after_concurrent_set(self) -> None:
        errors: list[Exception] = []

        def set_and_multiply() -> None:
            try:
                backend = NativeBackend()
                set_backend(backend)
                p = multiply(2, GENERATOR_POINT)
                assert not p.infinity
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=set_and_multiply) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors


class TestMultiplyScalarNormalization:
    def setup_method(self) -> None:
        import btx.curve.dispatch as d

        d.backend = None
        d.resolved_default = None

    def teardown_method(self) -> None:
        import btx.curve.dispatch as d

        d.backend = None
        d.resolved_default = None

    def test_negative_scalar_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            multiply(-1, GENERATOR_POINT)

    def test_zero_scalar(self) -> None:
        assert multiply(0, GENERATOR_POINT) == INFINITY_POINT

    def test_one_scalar(self) -> None:
        assert multiply(1, GENERATOR_POINT) == GENERATOR_POINT

    def test_scalar_equal_curve_order(self) -> None:
        assert multiply(CURVE_ORDER, GENERATOR_POINT) == INFINITY_POINT

    def test_scalar_above_curve_order(self) -> None:
        assert multiply(CURVE_ORDER + 1, GENERATOR_POINT) == GENERATOR_POINT

    def test_large_scalar(self) -> None:
        p = multiply(CURVE_ORDER * 100 + 42, GENERATOR_POINT)
        assert not p.infinity


class TestPsbtMaxSizeLimits:
    def test_key_exceeds_max_size(self) -> None:
        from btx.encoding.varint import encode_varint
        from btx.psbt import parse_psbt
        from btx.psbt.parser import MAX_KEY_SIZE

        magic = b"psbt\xff"
        key_len_varint = encode_varint(MAX_KEY_SIZE + 1)
        data = magic + key_len_varint

        with pytest.raises(ValueError, match="exceeds maximum"):
            parse_psbt(data)

    def test_value_exceeds_max_size(self) -> None:
        from btx.encoding.varint import encode_varint
        from btx.psbt import parse_psbt
        from btx.psbt.parser import MAX_VALUE_SIZE

        magic = b"psbt\xff"
        data = (
            magic
            + encode_varint(1)  # key_len = 1
            + b"\x00"  # key_type = 0 (unsigned tx)
            + encode_varint(MAX_VALUE_SIZE + 1)  # value_len too large
        )

        with pytest.raises(ValueError, match="exceeds maximum"):
            parse_psbt(data)

    def test_max_map_entries(self) -> None:
        from btx.encoding.varint import encode_varint
        from btx.psbt import parse_psbt
        from btx.psbt.parser import MAX_KEY_VALUE_MAP_ENTRIES

        magic = b"psbt\xff"
        entry = (
            encode_varint(1)  # key_len = 1
            + b"\x01"  # key_type
            + encode_varint(1)  # value_len = 1
            + b"\x01"  # value
        )
        data = magic + entry * (MAX_KEY_VALUE_MAP_ENTRIES + 1)

        with pytest.raises(ValueError, match="exceeds maximum"):
            parse_psbt(data)
