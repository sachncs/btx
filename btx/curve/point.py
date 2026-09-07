# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""The ``Point`` value type — a point on the secp256k1 curve.

Defines the immutable, slot-based :class:`Point` value object with
direct arithmetic methods.

Design choices:

- ``Point`` uses ``__slots__`` for a compact memory footprint — every
  ``Point`` allocates only two ``int``/``None`` slots plus one flag.
- Affine coordinates only; we deliberately avoid Jacobian/projective
  representation to keep the type tiny and the SEC-1 round-trip
  trivial.  Backend implementations are free to use other coordinate
  systems internally.
- :attr:`Point.infinity` is the point at infinity (the secp256k1 group
  identity); its ``x``/``y`` are always ``None``.
- Arithmetic methods (``negate``, ``add``, ``double``, ``multiply``,
  ``is_on_curve``) are first-class on the value type, supporting the
  Python operator overloads (``+``, ``-``, ``*``, unary ``-``).

Validation is performed eagerly in :meth:`Point.__init__`; points
constructed without an on-curve check must be verified before use in
elliptic-curve operations.
"""

from __future__ import annotations

from btx.curve.params import CURVE_B, FIELD_PRIME


class Point:
    """An affine point on secp256k1, or the point at infinity.

    Slots are used for a compact memory layout.  The point is guaranteed
    to lie on the curve when *infinity* is ``False``.

    Attributes:
        x: The affine x-coordinate, or ``None`` for the point at infinity.
        y: The affine y-coordinate, or ``None`` for the point at infinity.
        infinity: ``True`` if this is the point at infinity.
    """

    __slots__ = ("x", "y", "__infinity")

    def __init__(
        self, x: int | None = None, y: int | None = None, *, infinity: bool = False
    ) -> None:
        """Initialize a Point on the secp256k1 curve.

        Args:
            x: The affine x-coordinate.
            y: The affine y-coordinate.
            infinity: If True, create the point at infinity (ignores x, y).

        Raises:
            ValueError: If not infinity and x or y is missing or out of range.
        """
        if infinity:
            self.x: int | None = None
            self.y: int | None = None
            self.__infinity: bool = True
            return
        if x is None or y is None:
            raise ValueError("Affine point requires both x and y.")
        if not (0 <= x < FIELD_PRIME):
            raise ValueError(f"x coordinate out of field: {x}")
        if not (0 <= y < FIELD_PRIME):
            raise ValueError(f"y coordinate out of field: {y}")
        self.x = x
        self.y = y
        self.__infinity = False

    # -- read-only property (only infinity remains mangled) -----------------

    @property
    def infinity(self) -> bool:
        """``True`` if this is the point at infinity."""
        return self.__infinity

    # -- arithmetic methods --------------------------------------------------

    def negate(self) -> Point:
        """Return the additive inverse of this point.

        Returns:
            The negated Point, or the point at infinity unchanged.
        """
        from btx.curve.operations import negate

        return negate(self)

    def add(self, other: Point) -> Point:
        """Return the sum of this point and *other*.

        Args:
            other: The point to add.

        Returns:
            The sum Point.
        """
        from btx.curve.operations import add

        return add(self, other)

    def double(self) -> Point:
        """Return this point doubled (2 * point).

        Returns:
            The doubled Point.
        """
        from btx.curve.operations import double

        return double(self)

    def multiply(self, scalar: int) -> Point:
        """Return scalar multiplication ``scalar * point``.

        Args:
            scalar: The scalar multiplier (non-negative).

        Returns:
            The resulting Point.

        Raises:
            ValueError: If *scalar* is negative.
        """
        from btx.curve.operations import multiply

        return multiply(scalar, self)

    def is_on_curve(self) -> bool:
        """Check whether this point lies on the secp256k1 curve.

        Returns:
            ``True`` if the point is on the curve.  The point at
            infinity is always considered on the curve.
        """
        from btx.curve.operations import is_on_curve

        return is_on_curve(self)

    # -- operator overloading ------------------------------------------------

    def __add__(self, other: Point) -> Point:
        """Return ``self + other`` via :meth:`add`."""
        return self.add(other)

    def __sub__(self, other: Point) -> Point:
        """Return ``self - other`` via :meth:`add` and :meth:`negate`."""
        return self.add(other.negate())

    def __mul__(self, scalar: int) -> Point:
        """Return ``scalar * self`` via :meth:`multiply`.

        Raises:
            TypeError: If *scalar* is not an int.
        """
        if not isinstance(scalar, int):
            return NotImplemented
        return self.multiply(scalar)

    def __rmul__(self, scalar: int) -> Point:
        """Return ``scalar * self`` for ``scalar * point``."""
        return self.__mul__(scalar)

    def __neg__(self) -> Point:
        """Return ``-self`` via :meth:`negate`."""
        return self.negate()

    # -- equality / hashing --------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Return True if *other* is a Point with identical coordinates."""
        if not isinstance(other, Point):
            return NotImplemented
        if self.__infinity and other.__infinity:
            return True
        if self.__infinity != other.__infinity:
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """Return a hash based on the point's coordinates."""
        if self.__infinity:
            return hash((True,))
        return hash((False, self.x, self.y))

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        if self.__infinity:
            return "Point(infinity=True)"
        return f"Point(x=0x{self.x:064x}, y=0x{self.y:064x})"

    # -- constructors --------------------------------------------------------

    @classmethod
    def from_sec_compressed(cls, data: bytes) -> Point:
        """Parse a 33-byte compressed SEC-encoded public key.

        Validates that the decompressed y-coordinate satisfies the curve
        equation ``y^2 = x^3 + b (mod p)``, rejecting invalid encodings.

        Args:
            data: A 33-byte SEC-compressed key.

        Returns:
            A new Point parsed from the encoding.

        Raises:
            ValueError: If *data* is not a valid compressed SEC key or
                the decompressed point is not on the curve.
        """
        if len(data) != 33 or data[0] not in (0x02, 0x03):
            raise ValueError("Invalid compressed SEC key.")
        x = int.from_bytes(data[1:33], "big")
        y_sq = (pow(x, 3, FIELD_PRIME) + CURVE_B) % FIELD_PRIME
        y = pow(y_sq, (FIELD_PRIME + 1) // 4, FIELD_PRIME)
        if (y & 1) != (data[0] & 1):
            y = FIELD_PRIME - y
        # Validate that the decompressed y satisfies the curve equation.
        if (y * y) % FIELD_PRIME != y_sq:
            raise ValueError("Decompressed point is not on the secp256k1 curve.")
        return cls(x=x, y=y)

    @classmethod
    def from_sec_uncompressed(cls, data: bytes) -> Point:
        """Parse a 65-byte uncompressed SEC-encoded public key.

        Args:
            data: A 65-byte SEC-uncompressed key.

        Returns:
            A new Point parsed from the encoding.

        Raises:
            ValueError: If *data* is not a valid uncompressed SEC key.
        """
        if len(data) != 65 or data[0] != 0x04:
            raise ValueError("Invalid uncompressed SEC key.")
        x = int.from_bytes(data[1:33], "big")
        y = int.from_bytes(data[33:], "big")
        return cls(x=x, y=y)

    # -- serialization -------------------------------------------------------

    def to_sec_compressed(self) -> bytes:
        """Encode this point as a 33-byte compressed SEC key.

        Returns:
            The 33-byte SEC-compressed encoding.

        Raises:
            ValueError: If this is the point at infinity.
        """
        y = self.y
        x = self.x
        if y is None or x is None:
            raise ValueError("Cannot serialize infinity point.")
        prefix = bytes([0x02 | (y & 1)])
        return prefix + x.to_bytes(32, "big")

    def to_sec_uncompressed(self) -> bytes:
        """Encode this point as a 65-byte uncompressed SEC key.

        Returns:
            The 65-byte uncompressed SEC encoding.

        Raises:
            ValueError: If this is the point at infinity.
        """
        x = self.x
        y = self.y
        if x is None or y is None:
            raise ValueError("Cannot serialize infinity point.")
        return b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")

    def serialize(self, compressed: bool = True) -> bytes:
        """Serialize this point to SEC-encoded bytes.

        Args:
            compressed: Whether to use compressed encoding (default ``True``).

        Returns:
            SEC-encoded bytes (33 bytes if compressed, 65 bytes otherwise).

        Raises:
            ValueError: If this is the point at infinity.
        """
        if compressed:
            return self.to_sec_compressed()
        return self.to_sec_uncompressed()
