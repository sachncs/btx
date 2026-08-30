# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Secp256k1 curve arithmetic, backends, and the ``Point`` type.

This subpackage is the lowest-level layer of the library: it implements
elliptic-curve operations over the secp256k1 group
(``y² = x³ + 7 mod p`` with prime order ``n``) and is intentionally
**independent** of Bitcoin transactions, scripts, and signatures.

Layers
------

- :mod:`btx.curve.params` – SEC-1 curve constants (``p``, ``n``,
  ``a``, ``b``, generator coordinates).
- :mod:`btx.curve.point` – immutable :class:`Point` type with
  ``__slots__`` storage, direct arithmetic methods (``negate``,
  ``add``, ``double``, ``multiply``, ``is_on_curve``) and Python
  operator overloads (``+``, ``-``, ``*``, unary ``-``).
- :mod:`btx.curve.backend` – pluggable :class:`CurveBackend` ABC
  with two concrete implementations: :class:`NativeBackend` (pure
  Python) and :class:`LibsecpBackend` (optional ``coincurve``/libsecp256k1
  C bindings).
- :mod:`btx.curve.operations` – Montgomery-ladder scalar
  multiplication and field-arithmetic primitives used by
  :class:`NativeBackend`.
- :mod:`btx.curve.dispatch` – module-level backend singleton and
  the public ``add``/``double``/``multiply``/``negate``/``is_on_curve``/
  ``parse_public_key``/``serialize_public_key``/``sqrt_field``/
  ``normalize`` entry points.  Also caches a 4-bit-window table for
  the generator point.

Backend selection
-----------------

Use :func:`set_backend` to force a backend, or set
``settings.default_backend = "libsecp"`` (or ``"native"``) to influence
auto-resolution via :func:`btx.curve.dispatch.resolve_backend`.
"""

from btx.curve import libsecp256k1
from btx.curve.backend.base import CurveBackend
from btx.curve.backend.libsec import LibsecpBackend
from btx.curve.backend.native import NativeBackend
from btx.curve.dispatch import (
    add,
    double,
    get_backend,
    is_on_curve,
    multiply,
    negate,
    parse_public_key,
    serialize_public_key,
    set_backend,
    sqrt_field,
)
from btx.curve.params import (
    CURVE_A,
    CURVE_B,
    CURVE_ORDER,
    FIELD_PRIME,
    GENERATOR_X,
    GENERATOR_Y,
)
from btx.curve.point import Point

# Singleton points
GENERATOR_POINT = Point(x=GENERATOR_X, y=GENERATOR_Y)  # The secp256k1 generator point
INFINITY_POINT = Point(infinity=True)  # The point at infinity

__all__ = [
    "CURVE_A",
    "CURVE_B",
    "CURVE_ORDER",
    "CurveBackend",
    "FIELD_PRIME",
    "GENERATOR_POINT",
    "GENERATOR_X",
    "GENERATOR_Y",
    "INFINITY_POINT",
    "LibsecpBackend",
    "NativeBackend",
    "Point",
    "add",
    "double",
    "libsecp256k1",
    "get_backend",
    "is_on_curve",
    "multiply",
    "negate",
    "parse_public_key",
    "serialize_public_key",
    "set_backend",
    "sqrt_field",
]
