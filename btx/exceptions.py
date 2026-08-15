# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Exception hierarchy for the btx package.

A small tree of domain exceptions rooted at :exc:`BtxError`,
which itself inherits from :exc:`ValueError` so it integrates
transparently with stdlib APIs that catch value errors (e.g.
``json.loads``).

Hierarchy::

    ValueError
    └── BtxError
        ├── NotInvertible        # field arithmetic
        ├── PointError           # curve point failures
        ├── ParsingError         # binary wire-format parsing
        └── UnsupportedScriptPathError  # script features this
                                         # library does not implement

Callers should catch :exc:`BtxError` to handle every library
error in a single ``except`` clause, or the more specific subclasses
when finer-grained recovery logic is needed.
"""

__all__ = [
    "BtxError",
    "NotInvertible",
    "PointError",
    "ParsingError",
    "UnsupportedScriptPathError",
]


class BtxError(ValueError):
    """Base exception for all btx package errors."""


class NotInvertible(BtxError):  # noqa: N818
    """Raised when a value is not invertible in the given finite field."""


class PointError(BtxError):
    """Raised for invalid curve-point operations."""


class ParsingError(BtxError):
    """Raised when binary parsing fails."""


class UnsupportedScriptPathError(BtxError):
    """Raised when a script contains unsupported structures or features."""
