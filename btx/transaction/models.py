# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Immutable data models for Bitcoin transaction components.

Defines the core :class:`Tx`, :class:`TxIn`, :class:`TxOut`,
:class:`OutPoint`, and :class:`Witness` dataclasses.  Domain
operations (serialisation, RBF detection, sighash, etc.) live in
:mod:`btx.transaction.ops` and are also re-exposed as thin
convenience methods on :class:`Tx` for ergonomics.

All dataclasses are ``frozen=True, slots=True``:

- ``frozen`` gives value semantics — two ``Tx`` instances with the
  same fields hash and compare equal, and they cannot be mutated
  after construction.
- ``slots`` removes the per-instance ``__dict__`` and dramatically
  reduces memory usage (a non-trivial concern when a single
  extraction pipeline may hold millions of records).

Validation in ``__post_init__`` is intentionally minimal: it checks
field-level invariants (byte length, non-negativity, supply cap) but
does **not** verify that the transaction is well-formed for consensus
or spendable.  Use the parser/builder modules for that level of
validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass(frozen=True, slots=True)
class OutPoint:
    """Reference to a specific output of a previous transaction.

    Attributes:
        txid: 32-byte transaction hash (little-endian).
        vout: Output index (non-negative).
    """

    txid: bytes  # 32 bytes, little-endian
    vout: int  # output index

    def __post_init__(self) -> None:
        """Validate txid length and vout non-negativity.

        Raises:
            ValueError: If ``txid`` is not 32 bytes or ``vout`` is
                negative.
        """
        if len(self.txid) != 32:
            raise ValueError(f"txid must be 32 bytes, got {len(self.txid)}.")
        if self.vout < 0:
            raise ValueError(f"vout must be non-negative, got {self.vout}.")


@dataclass(frozen=True, slots=True)
class TxIn:
    """A transaction input, including witness data.

    Attributes:
        previous_output: The UTXO being spent.
        script_sig: Legacy input script (signature + public key).
        sequence: Sequence number (``0xFFFFFFFF`` by default).
        witness: Witness stack (SegWit); empty for non-SegWit inputs.
    """

    previous_output: OutPoint
    script_sig: bytes
    sequence: int
    witness: Witness

    def __post_init__(self) -> None:
        """Validate sequence is non-negative.

        Raises:
            ValueError: If ``sequence`` is negative.
        """
        if self.sequence < 0:
            raise ValueError(f"Sequence must be non-negative, got {self.sequence}.")


@dataclass(frozen=True, slots=True)
class TxOut:
    """A transaction output (value + script).

    Attributes:
        value: Amount in satoshis (non-negative, capped at 21M BTC).
        script_pubkey: Locking script (``scriptPubKey``).
    """

    value: int  # satoshis
    script_pubkey: bytes

    def __post_init__(self) -> None:
        """Validate value is non-negative and within supply cap.

        Raises:
            ValueError: If ``value`` is negative or exceeds 21M BTC.
        """
        if self.value < 0:
            raise ValueError(f"Value must be non-negative, got {self.value}.")
        # 21 million BTC max
        if self.value > 21_000_000 * 100_000_000:
            raise ValueError(f"Value exceeds maximum: {self.value}.")


@dataclass(frozen=True, slots=True)
class Witness:
    """A SegWit witness stack (ordered list of byte items).

    Attributes:
        items: Tuple of witness elements, each as raw bytes.
    """

    items: tuple[bytes, ...] = ()

    def __len__(self) -> int:
        """Return the number of witness items."""
        return len(self.items)


EMPTY_WITNESS = Witness(())


@dataclass(frozen=True, slots=True)
class Tx:
    """A Bitcoin transaction with optional SegWit support.

    Attributes:
        version: Transaction version (typically ``1`` or ``2``).
        inputs: Tuple of transaction inputs.
        outputs: Tuple of transaction outputs.
        lock_time: Lock time (absolute block height or timestamp).
    """

    version: int
    inputs: tuple[TxIn, ...]
    outputs: tuple[TxOut, ...]
    lock_time: int

    def __len__(self) -> int:
        """Return the total number of inputs plus outputs."""
        return len(self.inputs) + len(self.outputs)

    def __iter__(self) -> Any:  # Iterator[TxIn]
        """Iterate over inputs.

        Yields:
            Each :class:`TxIn` in ``self.inputs`` in order.
        """
        return iter(self.inputs)

    # ── Convenience methods delegating to btx.transaction.ops ──
    # These are thin wrappers that exist for ergonomics; the real
    # implementations live in ops.py so callers that prefer module-
    # level functions can use them directly.

    def is_segwit(self) -> bool:
        """Check whether this transaction uses SegWit.

        Returns:
            ``True`` if at least one input has a non-empty witness stack.
        """
        from btx.transaction.ops import is_segwit

        return is_segwit(self)

    def total_output_value(self) -> int:
        """Return the sum of all output values in satoshis."""
        from btx.transaction.ops import total_output_value

        return total_output_value(self)

    def serialize(self) -> bytes:
        """Serialize this transaction to wire format (SegWit-aware)."""
        from btx.transaction.ops import serialize_tx

        return serialize_tx(self)

    def serialize_legacy(self) -> bytes:
        """Serialize this transaction in legacy (non-SegWit) format."""
        from btx.transaction.ops import serialize_legacy_tx

        return serialize_legacy_tx(self)

    def to_json(self) -> dict[str, Any]:
        """Convert this transaction to a JSON-serializable dict."""
        from btx.transaction.ops import tx_to_json

        return tx_to_json(self)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation of this transaction."""
        from btx.transaction.ops import to_dict as _to_dict

        return _to_dict(self)

    def txid(self) -> bytes:
        """Compute the transaction ID (hash of legacy serialisation)."""
        from btx.transaction.ops import txid as _txid

        return _txid(self)

    def wtxid(self) -> bytes:
        """Compute the witness transaction ID (hash of full serialisation)."""
        from btx.transaction.ops import wtxid as _wtxid

        return _wtxid(self)

    def is_opt_in_rbf(self) -> bool:
        """Return True if at least one input signals opt-in RBF (BIP-125)."""
        from btx.transaction.rbf import is_opt_in_rbf

        return is_opt_in_rbf(self)

    def has_sequence_lock(self) -> bool:
        """Return True if any input uses a relative sequence lock (BIP-68)."""
        from btx.transaction.rbf import has_sequence_lock

        return has_sequence_lock(self)

    def sighash_legacy(
        self, input_index: int, script: bytes, sighash_flag: int
    ) -> bytes:
        """Compute the legacy (pre-SegWit) sighash for *input_index*."""
        from btx.transaction.ops import sighash_legacy as _sighash_legacy

        return _sighash_legacy(self, input_index, script, sighash_flag)

    def sighash_segwit(
        self, input_index: int, script: bytes, value: int, sighash_flag: int
    ) -> bytes:
        """Compute the BIP-143 SegWit v0 sighash for *input_index*."""
        from btx.transaction.ops import sighash_segwit as _sighash_segwit

        return _sighash_segwit(self, input_index, script, value, sighash_flag)

    def sighash_taproot(
        self,
        input_index: int,
        script: bytes | None,
        sighash_flag: int,
        *,
        amounts: tuple[int, ...],
        scriptpubkeys: tuple[bytes, ...],
        tapleaf_hash: bytes | None = None,
        key_version: int = 0,
        codeseparator_position: int = 0xFFFFFFFF,
        annex: bytes | None = None,
    ) -> bytes:
        """Compute the BIP-341 Taproot sighash for *input_index*."""
        from btx.transaction.ops import sighash_taproot as _sighash_taproot

        return _sighash_taproot(
            self,
            input_index,
            script,
            sighash_flag,
            amounts=amounts,
            scriptpubkeys=scriptpubkeys,
            tapleaf_hash=tapleaf_hash,
            key_version=key_version,
            codeseparator_position=codeseparator_position,
            annex=annex,
        )
