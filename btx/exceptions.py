# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
"""Exception hierarchy for the btx package.

A small tree of domain exceptions rooted at :exc:`BtxError`,
which itself inherits from :exc:`ValueError` so it integrates
transparently with stdlib APIs that catch value errors (e.g.
``json.loads``).

Hierarchy::

    ValueError
    └── BtxError
        └── UnsupportedScriptPathError  # script features this
                                         # library does not implement

Callers should catch :exc:`BtxError` to handle package-level domain errors
in a single ``except`` clause. Malformed values at low-level parsing and
arithmetic boundaries raise the standard :exc:`ValueError`.
"""

__all__ = [
    "BtxError",
    "UnsupportedScriptPathError",
]


class BtxError(ValueError):
    """Base exception for all btx package errors."""


class UnsupportedScriptPathError(BtxError):
    """Raised when a script contains unsupported structures or features."""
