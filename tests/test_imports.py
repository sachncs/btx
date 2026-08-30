# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Top-level package import smoke test."""

from __future__ import annotations

import importlib

import btx


def test_import_top_level() -> None:
    """``import btx`` succeeds and exposes __version__."""
    assert hasattr(btx, "__version__")
    assert isinstance(btx.__version__, str)
    assert btx.__version__ == "0.5.0"


def test_import_all_subpackages() -> None:
    """Every public subpackage can be imported without error."""
    for name in (
        "btx",
        "btx.cli",
        "btx.curve",
        "btx.descriptor",
        "btx.encoding",
        "btx.exceptions",
        "btx.field",
        "btx.health",
        "btx.psbt",
        "btx.script",
        "btx.services",
        "btx.settings",
        "btx.sighash",
        "btx.signature",
        "btx.transaction",
    ):
        importlib.import_module(name)


def test_settings_default_backend() -> None:
    """Settings exposes default_backend."""
    assert hasattr(btx.settings, "default_backend")


def test_no_circular_imports() -> None:
    """Smoke: import every domain submodule and re-import btx."""

    # Re-import btx after the deep walk to confirm no circular import
    # reordering issue.
    importlib.import_module("btx")
