# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Transaction-level operations that take a :class:`Tx` as an argument.

These are the algorithms that conceptually belong to a transaction
(serialize, hash, sighash, RBF checks) but are exposed as module-level
functions rather than methods on ``Tx`` so that the model stays a
pure data carrier and ownership of the operation is explicit at the
call site.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from btx.transaction.models import Tx


def is_segwit(tx: Tx) -> bool:
    """Return ``True`` if *tx* uses SegWit (any input has witness data)."""
    return any(txin.witness.items for txin in tx.inputs)


def total_output_value(tx: Tx) -> int:
    """Return the sum of all output values of *tx* in satoshis."""
    return sum(out.value for out in tx.outputs)


def serialize_tx(tx: Tx) -> bytes:
    """Serialise *tx* to wire format (SegWit-aware).

    Re-exports :func:`btx.services.serializer.serialize_tx` to avoid
    forcing transaction-layer callers to import from the network
    services package.
    """
    from btx.services.serializer import serialize_tx as _serialize_tx

    return _serialize_tx(tx)


def serialize_legacy_tx(tx: Tx) -> bytes:
    """Serialise *tx* in legacy (non-SegWit) format.

    Re-exports :func:`btx.services.serializer.serialize_legacy_tx`.
    """
    from btx.services.serializer import serialize_legacy_tx as _legacy

    return _legacy(tx)


def tx_to_json(tx: Tx) -> dict[str, Any]:
    """Convert *tx* to a JSON-serialisable dict.

    Re-exports :func:`btx.services.serializer.tx_to_json`.
    """
    from btx.services.serializer import tx_to_json as _to_json

    return _to_json(tx)


def to_dict(tx: Tx) -> dict[str, Any]:
    """Return a plain-dict representation of *tx*.

    The result round-trips through :func:`btx.transaction.tx_from_dict`
    (i.e. ``tx_from_dict(tx_to_ops_dict(tx)) == tx`` value-wise).
    """
    return {
        "version": tx.version,
        "inputs": [
            {
                "txid": inp.previous_output.txid,
                "vout": inp.previous_output.vout,
                "script_sig": inp.script_sig,
                "sequence": inp.sequence,
                "witness": inp.witness.items,
            }
            for inp in tx.inputs
        ],
        "outputs": [
            {"value": out.value, "script_pubkey": out.script_pubkey}
            for out in tx.outputs
        ],
        "lock_time": tx.lock_time,
    }


def txid(tx: Tx) -> bytes:
    """Compute the transaction ID (double-SHA256 of legacy serialisation)."""
    from btx.encoding.hasher import hash256
    from btx.services.serializer import serialize_legacy_tx

    return hash256(serialize_legacy_tx(tx))


def wtxid(tx: Tx) -> bytes:
    """Compute the witness transaction ID (double-SHA256 of full serialisation)."""
    from btx.encoding.hasher import hash256
    from btx.services.serializer import serialize_tx

    return hash256(serialize_tx(tx))


def sighash_legacy(tx: Tx, input_index: int, script: bytes, sighash_flag: int) -> bytes:
    """Compute the legacy (pre-SegWit) sighash for ``input_index``."""
    from btx.sighash.legacy import sighash_legacy as _legacy

    return _legacy(tx, input_index, script, sighash_flag)


def sighash_segwit(
    tx: Tx, input_index: int, script: bytes, value: int, sighash_flag: int
) -> bytes:
    """Compute the BIP-143 SegWit v0 sighash for ``input_index``."""
    from btx.sighash.segwit import sighash_segwit as _segwit

    return _segwit(tx, input_index, script, value, sighash_flag)


def sighash_taproot(
    tx: Tx,
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
    """Compute the BIP-341 Taproot sighash for ``input_index``."""
    from btx.sighash.taproot import sighash_taproot as _taproot

    return _taproot(
        tx,
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


__all__ = [
    "is_segwit",
    "serialize_legacy_tx",
    "serialize_tx",
    "sighash_legacy",
    "sighash_segwit",
    "sighash_taproot",
    "to_dict",
    "total_output_value",
    "tx_to_json",
    "txid",
    "wtxid",
]
