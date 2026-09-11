# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
"""Immutable collection of extracted signature records.

The :class:`SignatureCollection` dataclass wraps a tuple of
:class:`Record` instances with sequence-like access (``len``,
iteration, integer indexing) and a :meth:`sort_records` method that
returns a new collection sorted by any ``Record`` attribute.

Immutability follows from ``frozen=True, slots=True``; calling
:meth:`sort_records` therefore returns a new collection rather than
mutating the receiver.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from btx.signature.record import Record


@dataclass(frozen=True, slots=True)
class SignatureCollection:
    """An immutable collection of ``Record`` instances.

    Provides sequence-like access: ``len()``, iteration, and integer indexing.

    Attributes:
        records: Tuple of ``Record`` objects in insertion order.
    """

    records: tuple[Record, ...]

    def __len__(self) -> int:
        """Return the number of records in the collection."""
        return len(self.records)

    def __iter__(self) -> Iterator[Record]:
        """Yield records in order."""
        return iter(self.records)

    def __getitem__(self, index: int) -> Record:
        """Return the record at *index*."""
        return self.records[index]

    def sort_records(self, key: Callable[[Record], Any]) -> SignatureCollection:
        """Return a new collection sorted by *key*.

        Args:
            key: A callable that maps each ``Record`` to a sortable
                value (e.g. ``attrgetter("input_index")``).

        Returns:
            A new ``SignatureCollection`` with sorted records.
        """
        sorted_records = tuple(sorted(self.records, key=key))
        return SignatureCollection(records=sorted_records)
