# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Taproot (BIP-341/BIP-342) sighash computation.

Implements BIP-341's common signature message (``SigMsg``) and the
BIP-342 tapscript extension, producing the 32-byte ``TapSighash``
tagged-hash digest used for both key-path and script-path spends.

The message is assembled as (all integers little-endian)::

    epoch (0x00) || hash_type (1) || nVersion (4) || nLockTime (4)

    || sha_prevouts (32) || sha_amounts (32) || sha_scriptpubkeys (32)
       || sha_sequences (32)                -- omitted under ANYONECANPAY

    || sha_outputs (32)                     -- only when base is SIGHASH_ALL

    || spend_type (1)

    || outpoint (36) || amount (8) || scriptPubKey || nSequence (4)
                                        -- ANYONECANPAY only
       || input_index (4)              -- otherwise

    || sha_annex (32)                       -- if an annex is present

    || sha_single_output (32)               -- only when base is SIGHASH_SINGLE

    || [tapleaf_hash (32) || key_version (1) || codeseparator_position (4)
                                 -- BIP-342 tapscript extension, script-path only]

Hashes:

- The four amortised ``sha_*`` components are single SHA-256 digests of
  the serialised concatenation of the matching BIP-341 fields.
  ``sha_sequences`` commits to the sequence of **every** input
  regardless of the SIGHASH base flag (BIP-341 rationale #4).
- A present annex is committed via its length-prefixed serialized
  form: ``sha_annex = SHA256(compact_size(len) || annex)``.  The
  *annex* argument must include the mandatory ``0x50`` prefix.
- ``tapleaf_hash`` is the leaf hash committed to by the merkle tree
  (``TaggedHash("TapLeaf", leaf_version || CompactSize(len) || script)``),
  *not* the leaf script itself, in line with the BIP-342 extension.
- The digest is ``tagged_hash("TapSighash", 0x00 || SigMsg)``.

BIP-341 commits to the UTXO value and ``scriptPubKey`` of **every**
output being spent (they are needed even for the current input), so
callers MUST supply ``amounts`` and ``scriptpubkeys`` with one entry
per transaction input.

The function is **not** LRU-cached because its parameter surface is
much wider than the legacy and SegWit variants — caching would be
ineffective.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from btx.encoding.hasher import sha256, tagged_hash
from btx.encoding.varint import encode_varint
from btx.sighash.flag import (
    SIGHASH_ALL,
    SIGHASH_ANYONECANPAY,
    SIGHASH_MASK,
    SIGHASH_SINGLE,
)

if TYPE_CHECKING:
    from btx.transaction.models import Tx, TxIn, TxOut

NO_CODESEPARATOR = 0xFFFFFFFF

# BIP-341/342 leaf version byte for Tapscript.  The only currently
# defined leaf version is 0xC0 (Tapscript); BIP-341 reserves future
# leaf versions to bytes ``v`` with ``(v & 0xfe) == 0xc0`` and
# ``v != 0x50``.
LEAF_VERSION_TAPSCRIPT = 0xC0

# Leaf-version bytes that identify a Taproot script-path spend when
# they appear as the first byte of the script code.
TAPROOT_SCRIPT_PATH_PREFIXES: tuple[int, ...] = (LEAF_VERSION_TAPSCRIPT,)

# The seven hash_type values permitted by BIP-341: 0x00 (default),
# SIGHASH_ALL/NONE/SINGLE and their ANYONECANPAY variants.
VALID_BIP341_HASH_TYPES: tuple[int, ...] = (0x00, 0x01, 0x02, 0x03, 0x81, 0x82, 0x83)


def _hash_outpoints(inputs: Sequence[TxIn]) -> bytes:
    data = bytearray()
    for txin in inputs:
        data.extend(txin.previous_output.txid)
        data.extend(txin.previous_output.vout.to_bytes(4, "little"))
    return sha256(bytes(data))


def _hash_amounts(amounts: Sequence[int]) -> bytes:
    return sha256(b"".join(amt.to_bytes(8, "little") for amt in amounts))


def _hash_scriptpubkeys(scriptpubkeys: Sequence[bytes]) -> bytes:
    data = bytearray()
    for script in scriptpubkeys:
        data.extend(encode_varint(len(script)))
        data.extend(script)
    return sha256(bytes(data))


def _hash_sequences(sequences: Sequence[int]) -> bytes:
    data = bytearray().join(seq.to_bytes(4, "little") for seq in sequences)
    return sha256(bytes(data))


def _hash_outputs(outputs: Sequence[TxOut]) -> bytes:
    data = bytearray()
    for txout in outputs:
        data.extend(txout.value.to_bytes(8, "little"))
        data.extend(encode_varint(len(txout.script_pubkey)))
        data.extend(txout.script_pubkey)
    return sha256(bytes(data))


def _serialize_outpoint(txin: TxIn) -> bytes:
    return txin.previous_output.txid + txin.previous_output.vout.to_bytes(4, "little")


def _serialize_output(value: int, script: bytes) -> bytes:
    return value.to_bytes(8, "little") + encode_varint(len(script)) + script


def sighash_taproot(
    transaction: Tx,
    input_index: int,
    script: bytes | None,
    sighash_flag: int,
    *,
    tapleaf_hash: bytes | None = None,
    key_version: int = 0,
    codeseparator_position: int = NO_CODESEPARATOR,
    annex: bytes | None = None,
    amounts: Sequence[int],
    scriptpubkeys: Sequence[bytes],
) -> bytes:
    """Compute the BIP-341 Taproot sighash for a transaction input.

    Supports both key-path (``script=None``) and script-path spending.
    The digest is ``tagged_hash("TapSighash", 0x00 || SigMsg)`` over the
    BIP-341 signature message described in the module docstring.

    Args:
        transaction: The transaction.
        input_index: Index of the input being signed.
        script: The leaf script being executed for script-path spending,
            or ``None`` for key-path spending.  When set, it must carry
            the BIP-341 leaf version prefix (``0xc0``) so that
            *tapleaf_hash* can be derived from it; otherwise pass
            *tapleaf_hash* explicitly.
        sighash_flag: SIGHASH hash_type byte.  Must be one of the
            seven BIP-341 values ``{0x00, 0x01, 0x02, 0x03, 0x81,
            0x82, 0x83}``.
        tapleaf_hash: The 32-byte ``tapleaf_hash`` (BIP-341) of the
            leaf being spent.  Required when *script* is not ``None``.
            When it is ``None`` and *script* carries the tapscript leaf
            version prefix, it is derived from *script*.
        key_version: Key version byte (``0`` for current BIP-341).
        codeseparator_position: Position of the last ``OP_CODESEPARATOR``
            executed (default :data:`NO_CODESEPARATOR`).
        annex: Optional annex data, including the mandatory ``0x50``
            prefix (BIP-341).
        amounts: UTXO value of **every** input, one entry per input.
        scriptpubkeys: ``scriptPubKey`` of **every** spent output, one
            entry per input (empty bytes for Taproot inputs).

    Returns:
        The 32-byte tagged sighash digest.

    Raises:
        IndexError: If *input_index* is out of range for the
            transaction inputs.
        ValueError: If *script* is provided but no ``tapleaf_hash``
            can be determined, if ``SIGHASH_SINGLE`` is used with an
            index without a matching output, if *sighash_flag* is not
            a BIP-341 hash_type, or if *amounts* / *scriptpubkeys*
            are missing or do not cover every input.
    """
    if input_index >= len(transaction.inputs):
        raise IndexError("Input index out of range.")

    if sighash_flag not in VALID_BIP341_HASH_TYPES:
        raise ValueError(f"Invalid BIP-341 hash_type: {sighash_flag}.")

    if len(amounts) != len(transaction.inputs):
        raise ValueError(
            f"amounts must contain one entry per input "
            f"({len(transaction.inputs)}), got {len(amounts)}."
        )
    if len(scriptpubkeys) != len(transaction.inputs):
        raise ValueError(
            f"scriptpubkeys must contain one entry per input "
            f"({len(transaction.inputs)}), got {len(scriptpubkeys)}."
        )

    if not (0 <= key_version <= 0xFF):
        raise ValueError(f"key_version must fit in one byte, got {key_version}.")
    if not (0 <= codeseparator_position <= 0xFFFFFFFF):
        raise ValueError(
            f"codeseparator_position must fit in 32 bits, "
            f"got {codeseparator_position}."
        )

    base_flag = sighash_flag & SIGHASH_MASK
    output_type = SIGHASH_ALL if base_flag == 0x00 else base_flag
    inp = transaction.inputs[input_index]

    if script is not None:
        if tapleaf_hash is None:
            if script and script[0] in TAPROOT_SCRIPT_PATH_PREFIXES:
                leaf_version = script[0]
                leaf_script = script[1:]
                tapleaf_hash = tagged_hash(
                    "TapLeaf",
                    bytes([leaf_version])
                    + encode_varint(len(leaf_script))
                    + leaf_script,
                )
            else:
                raise ValueError(
                    "tapleaf_hash required for script-path signing."
                )
        ext_flag = 1
    else:
        ext_flag = 0

    sequence_hashes = not (sighash_flag & SIGHASH_ANYONECANPAY)

    data = bytearray()
    data.append(0x00)  # epoch
    data.extend(sighash_flag.to_bytes(1, "little"))
    data.extend(transaction.version.to_bytes(4, "little"))
    data.extend(transaction.lock_time.to_bytes(4, "little"))

    if sequence_hashes:
        data.extend(_hash_outpoints(transaction.inputs))
        data.extend(_hash_amounts(amounts))
        data.extend(_hash_scriptpubkeys(scriptpubkeys))
        data.extend(_hash_sequences([txin.sequence for txin in transaction.inputs]))

    if output_type == SIGHASH_ALL:
        data.extend(_hash_outputs(transaction.outputs))

    data.append((ext_flag << 1) | (0x01 if annex is not None else 0x00))

    if sighash_flag & SIGHASH_ANYONECANPAY:
        data.extend(_serialize_outpoint(inp))
        data.extend(amounts[input_index].to_bytes(8, "little"))
        data.extend(encode_varint(len(scriptpubkeys[input_index])))
        data.extend(scriptpubkeys[input_index])
        data.extend(inp.sequence.to_bytes(4, "little"))
    else:
        data.extend(input_index.to_bytes(4, "little"))

    if annex is not None:
        data.extend(sha256(encode_varint(len(annex)) + annex))

    if output_type == SIGHASH_SINGLE:
        if input_index >= len(transaction.outputs):
            raise ValueError(
                f"Input index {input_index} out of bounds for "
                f"SIGHASH_SINGLE with {len(transaction.outputs)} outputs."
            )
        txout = transaction.outputs[input_index]
        data.extend(sha256(_serialize_output(txout.value, txout.script_pubkey)))

    if ext_flag:
        assert tapleaf_hash is not None
        data.extend(tapleaf_hash)
        data.extend(key_version.to_bytes(1, "little"))
        data.extend(codeseparator_position.to_bytes(4, "little"))

    return tagged_hash("TapSighash", bytes(data))