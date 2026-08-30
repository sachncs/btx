# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Immutable data models for Bitcoin transaction components.

Defines the core :class:`Tx`, :class:`TxIn`, :class:`TxOut`,
:class:`OutPoint`, and :class:`Witness` dataclasses.  Domain
operations (serialisation, RBF detection, sighash, etc.) are
exposed as direct methods on :class:`Tx`.

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

    def is_segwit(self) -> bool:
        """Check whether this transaction uses SegWit.

        Returns:
            ``True`` if at least one input has a non-empty witness stack.
        """
        return any(txin.witness.items for txin in self.inputs)

    def total_output_value(self) -> int:
        """Return the sum of all output values in satoshis."""
        return sum(out.value for out in self.outputs)

    def serialize(self) -> bytes:
        """Serialize this transaction to wire format (SegWit-aware).

        Returns:
            Wire-format bytes including witness data if SegWit.
        """
        from btx.services.serializer import serialize_tx

        return serialize_tx(self)

    def serialize_legacy(self) -> bytes:
        """Serialize this transaction in legacy (non-SegWit) format.

        Returns:
            Legacy wire-format bytes.
        """
        from btx.services.serializer import serialize_legacy_tx

        return serialize_legacy_tx(self)

    def to_json(self) -> dict[str, Any]:
        """Convert this transaction to a JSON-serializable dict.

        Returns:
            A dict representing the full transaction structure.
        """
        from btx.services.serializer import tx_to_json

        return tx_to_json(self)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation of this transaction.

        The result round-trips through :func:`btx.transaction.tx.tx_from_dict`
        (i.e. ``tx_from_dict(tx.to_dict()) == tx`` value-wise).

        Returns:
            Dict with keys ``version``, ``inputs``, ``outputs``, ``lock_time``.
        """
        return {
            "version": self.version,
            "inputs": [
                {
                    "txid": inp.previous_output.txid,
                    "vout": inp.previous_output.vout,
                    "script_sig": inp.script_sig,
                    "sequence": inp.sequence,
                    "witness": inp.witness.items,
                }
                for inp in self.inputs
            ],
            "outputs": [
                {"value": out.value, "script_pubkey": out.script_pubkey}
                for out in self.outputs
            ],
            "lock_time": self.lock_time,
        }

    def txid(self) -> bytes:
        """Compute the transaction ID (hash of legacy serialisation).

        Uses ``double-SHA256`` of the non-witness serialisation.

        Returns:
            32-byte transaction hash.
        """
        from btx.encoding.hasher import hash256
        from btx.services.serializer import serialize_legacy_tx

        return hash256(serialize_legacy_tx(self))

    def wtxid(self) -> bytes:
        """Compute the witness transaction ID (hash of full serialisation).

        Uses ``double-SHA256`` of the SegWit-aware wire serialisation.

        Returns:
            32-byte witness transaction hash.
        """
        from btx.encoding.hasher import hash256
        from btx.services.serializer import serialize_tx

        return hash256(serialize_tx(self))

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
        """Compute the legacy (pre-SegWit) sighash for *input_index*.

        Args:
            input_index: Index of the input being signed.
            script: The script to evaluate.
            sighash_flag: SIGHASH flag byte.

        Returns:
            32-byte sighash digest.
        """
        from btx.sighash.legacy import sighash_legacy

        return sighash_legacy(self, input_index, script, sighash_flag)

    def sighash_segwit(
        self, input_index: int, script: bytes, value: int, sighash_flag: int
    ) -> bytes:
        """Compute the BIP-143 SegWit v0 sighash for *input_index*.

        Args:
            input_index: Index of the input being signed.
            script: The script code.
            value: Amount of the UTXO being spent in satoshis.
            sighash_flag: SIGHASH flag byte.

        Returns:
            32-byte sighash digest.
        """
        from btx.sighash.segwit import sighash_segwit

        return sighash_segwit(self, input_index, script, value, sighash_flag)

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
        """Compute the BIP-341 Taproot sighash for *input_index*.

        Args:
            input_index: Index of the input being signed.
            script: Versioned tapleaf script for script-path spending,
                or ``None`` for key-path.
            sighash_flag: BIP-341 SIGHASH hash_type byte.
            amounts: UTXO value of every input, one entry per input.
            scriptpubkeys: ``scriptPubKey`` of every spent output, one
                entry per input.
            tapleaf_hash: Hash of the tapleaf for script-path spending.
            key_version: Key version byte (0 or 1).
            codeseparator_position: Position of the last OP_CODESEPARATOR.
            annex: Optional annex data, including the ``0x50`` prefix.

        Returns:
            32-byte Taproot sighash digest.
        """
        from btx.sighash.taproot import sighash_taproot

        return sighash_taproot(
            self,
            input_index,
            script,
            sighash_flag,
            tapleaf_hash=tapleaf_hash,
            key_version=key_version,
            codeseparator_position=codeseparator_position,
            annex=annex,
            amounts=amounts,
            scriptpubkeys=scriptpubkeys,
        )
