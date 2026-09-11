# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
"""Pluggable secp256k1 curve backends.

Defines :class:`CurveBackend`, the abstract base class that every
backend implementation must satisfy.  Two concrete backends are
provided by sibling modules:

- :class:`~btx.curve.backend.native.NativeBackend` – pure-Python,
  always available.
- :class:`~btx.curve.backend.libsec.LibsecpBackend` – uses the
  optional ``coincurve`` C bindings (libsecp256k1) for fast scalar
  multiplication.  Falls back to pure Python for the operations that
  ``coincurve`` does not expose (negate/add/double).

The :mod:`btx.curve.dispatch` module is the typical entry point;
it routes each public operation through the currently active backend.
"""

from btx.curve.backend.base import CurveBackend

__all__ = ["CurveBackend"]
