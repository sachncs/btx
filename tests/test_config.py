# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Tests for the Settings singleton."""

from __future__ import annotations

import dataclasses

import pytest

from btx.settings import Settings, settings


def test_defaults() -> None:
    assert settings.default_backend is None


def test_default_backend() -> None:
    s = Settings(default_backend="native")
    assert s.default_backend == "native"
    s = Settings(default_backend="libsecp")
    assert s.default_backend == "libsecp"
    s = Settings(default_backend=None)
    assert s.default_backend is None


def test_default_backend_invalid() -> None:
    with pytest.raises(ValueError, match="default_backend"):
        Settings(default_backend="invalid")


def test_immutable() -> None:
    s = Settings(default_backend="native")
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.default_backend = "libsecp"  # type: ignore[misc]


def test_replace() -> None:
    s = Settings()
    s2 = dataclasses.replace(s, default_backend="libsecp")
    assert s.default_backend is None
    assert s2.default_backend == "libsecp"


def test_repr() -> None:
    s = Settings(default_backend="native")
    r = repr(s)
    assert "default_backend" in r
    assert "'native'" in r
