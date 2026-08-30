# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Deserialise Bitcoin transactions from wire format.

Supports both legacy and SegWit (BIP-144) encoded transactions.
Auto-detection is performed by looking for the ``0x00 0x01`` SegWit
marker + flag bytes immediately after the 4-byte version field.

Defensive limits
----------------

The parser enforces four upper bounds to prevent malicious inputs from
causing excessive memory allocation or denial-of-service:

- :data:`MAX_TX_SIZE` – overall transaction size (4 MB).
- :data:`MAX_INPUTS` / :data:`MAX_OUTPUTS` – input/output counts.
- :data:`MAX_WITNESS_ITEMS` / :data:`MAX_WITNESS_ITEM_SIZE` – per-input
  witness item count and individual size.

All four limits are conservative (well above any legitimate mainnet
transaction) and can be tuned per-deployment if needed.
"""

from __future__ import annotations

from btx.encoding.varint import decode_varint
from btx.transaction.models import OutPoint, Tx, TxIn, TxOut, Witness

MAX_TX_SIZE = 4_000_000
MAX_INPUTS = 100000
MAX_OUTPUTS = 100000
MAX_WITNESS_ITEMS = 10000
MAX_WITNESS_ITEM_SIZE = 10_000_000


def _take(data: bytes, offset: int, length: int, what: str) -> tuple[bytes, int]:
    """Read exactly *length* bytes, rejecting truncated input.

    Args:
        data: Raw transaction bytes.
        offset: Current position within *data*.
        length: Number of bytes to consume.
        what: Field name used in the error message.

    Returns:
        A tuple ``(field_bytes, new_offset)``.

    Raises:
        ValueError: If fewer than *length* bytes remain at *offset*.
    """
    end = offset + length
    if end > len(data):
        raise ValueError(
            f"Truncated transaction data: field {what!r} needs {length} "
            f"bytes at offset {offset}, only {len(data) - offset} remain."
        )
    return data[offset:end], end


def parse_tx(data: bytes, offset: int = 0) -> tuple[Tx, int]:
    """Parse a transaction from raw bytes, detecting SegWit.

    Automatically detects the SegWit marker + flag (``0x00 0x01``) and
    deserialises witness data accordingly.

    Args:
        data: Raw transaction bytes.
        offset: Starting offset within *data* (default ``0``).

    Returns:
        A tuple ``(Tx, new_offset)`` where *new_offset* is the position
        immediately after the parsed transaction.

    Raises:
        ValueError: If *data* exceeds ``MAX_TX_SIZE``.
    """
    if len(data) > MAX_TX_SIZE:
        raise ValueError(f"Transaction size {len(data)} exceeds maximum {MAX_TX_SIZE}")
    raw_version, offset = _take(data, offset, 4, "version")
    version = int.from_bytes(raw_version, "little")

    # BIP-144: immediately after the version, a 0x00 0x01 pair marks a
    # SegWit transaction.  Peek without consuming — a legacy transaction
    # starts with its input-count varint here and parse_inputs decodes it.
    raw_header, _ = _take(data, offset, 2, "input count / segwit marker+flag")
    is_segwit = raw_header == b"\x00\x01"
    if is_segwit:
        offset += 2

    inputs_list, offset = parse_inputs(data, offset)
    outputs, offset = parse_outputs(data, offset)
    if is_segwit:
        for i in range(len(inputs_list)):
            witness, offset = parse_witness(data, offset)
            inputs_list[i] = TxIn(
                previous_output=inputs_list[i].previous_output,
                script_sig=inputs_list[i].script_sig,
                sequence=inputs_list[i].sequence,
                witness=witness,
            )

    raw_lock_time, offset = _take(data, offset, 4, "lock_time")
    lock_time = int.from_bytes(raw_lock_time, "little")

    return Tx(
        version=version,
        inputs=tuple(inputs_list),
        outputs=tuple(outputs),
        lock_time=lock_time,
    ), offset


def parse_inputs(data: bytes, offset: int) -> tuple[list[TxIn], int]:
    """Parse the input list from a serialised transaction.

    Each input consists of a 32-byte txid, 4-byte vout, varint-length
    script_sig, and 4-byte sequence.  Witness is initialised as empty
    and filled later in ``parse_tx`` if the transaction is SegWit.

    Args:
        data: Raw transaction bytes.
        offset: Start of the input count varint.

    Returns:
        A tuple ``(inputs, new_offset)``.
    """
    n, offset = decode_varint(data, offset)
    if n > MAX_INPUTS:
        raise ValueError(f"Input count {n} exceeds maximum {MAX_INPUTS}")
    inputs: list[TxIn] = []
    for _ in range(n):
        txid, offset = _take(data, offset, 32, "outpoint txid")
        raw_vout, offset = _take(data, offset, 4, "outpoint vout")
        vout = int.from_bytes(raw_vout, "little")
        script_len, offset = decode_varint(data, offset)
        script_sig, offset = _take(data, offset, script_len, "script_sig")
        raw_sequence, offset = _take(data, offset, 4, "sequence")
        sequence = int.from_bytes(raw_sequence, "little")
        inputs.append(
            TxIn(
                previous_output=OutPoint(txid=txid, vout=vout),
                script_sig=script_sig,
                sequence=sequence,
                witness=Witness(()),
            )
        )
    return inputs, offset


def parse_outputs(data: bytes, offset: int) -> tuple[list[TxOut], int]:
    """Parse the output list from a serialised transaction.

    Each output consists of an 8-byte value and a varint-length
    script_pubkey.

    Args:
        data: Raw transaction bytes.
        offset: Start of the output count varint.

    Returns:
        A tuple ``(outputs, new_offset)``.
    """
    n, offset = decode_varint(data, offset)
    if n > MAX_OUTPUTS:
        raise ValueError(f"Output count {n} exceeds maximum {MAX_OUTPUTS}")
    outputs: list[TxOut] = []
    for _ in range(n):
        raw_value, offset = _take(data, offset, 8, "output value")
        value = int.from_bytes(raw_value, "little")
        script_len, offset = decode_varint(data, offset)
        script_pubkey, offset = _take(data, offset, script_len, "script_pubkey")
        outputs.append(TxOut(value=value, script_pubkey=script_pubkey))
    return outputs, offset


def parse_witness(data: bytes, offset: int) -> tuple[Witness, int]:
    """Parse a witness stack from a serialised transaction.

    The witness is encoded as a varint item count followed by
    varint-length-prefixed items.

    Args:
        data: Raw transaction bytes.
        offset: Start of the witness item count varint.

    Returns:
        A tuple ``(witness, new_offset)``.
    """
    n, offset = decode_varint(data, offset)
    if n > MAX_WITNESS_ITEMS:
        raise ValueError(f"Witness item count {n} exceeds maximum {MAX_WITNESS_ITEMS}")
    items: list[bytes] = []
    for _ in range(n):
        item_len, offset = decode_varint(data, offset)
        if item_len > MAX_WITNESS_ITEM_SIZE:
            raise ValueError(
                f"Witness item size {item_len} exceeds maximum {MAX_WITNESS_ITEM_SIZE}"
            )
        item, offset = _take(data, offset, item_len, "witness item")
        items.append(item)
    return Witness(tuple(items)), offset
