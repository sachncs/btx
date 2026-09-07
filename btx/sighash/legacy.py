# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Legacy (pre-SegWit) sighash computation.

Implements the original Bitcoin sighash algorithm — the one that
serialises the entire transaction (with the scriptSig of every input
cleared except for the input being signed, which is replaced with the
*provided script*) and double-SHA256-hashes the result, with output
pruning based on the SIGHASH flag.  Superseded by BIP-143 for SegWit
inputs but still required for legacy P2PKH / P2PK / P2SH spends.

The function is :func:`functools.lru_cache`-decorated because
extraction pipelines typically call it many times for the same
``(tx, input_index, script, sighash_flag)`` tuple.
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from btx.encoding.hasher import hash256
from btx.sighash.flag import SIGHASH_MASK, SIGHASH_SINGLE

if TYPE_CHECKING:
    from btx.transaction.models import Tx


@functools.lru_cache(maxsize=128)
def sighash_legacy(
    transaction: Tx, input_index: int, script: bytes, sighash_flag: int
) -> bytes:
    """Compute the legacy (pre-SegWit) sighash for a transaction input.

    The serialisation depends on the SIGHASH flags: inputs/outputs may be
    omitted or zeroed according to the flag semantics.

    In line with Bitcoin Core's ``SignatureHash``, a ``SIGHASH_SINGLE``
    digest with *input_index* beyond the transaction's output range
    short-circuits to the 32-byte value ``0x01 || 0x00 * 31``
    (``uint256::ONE``) rather than being hashed — such a signature is
    invalid under consensus rules.

    Args:
        transaction: The transaction to sign.
        input_index: Index of the input being signed.
        script: The script to evaluate (usually ``script_pubkey`` or
            ``redeemScript``).
        sighash_flag: SIGHASH flag determining which parts of the transaction
            are committed to.

    Returns:
        The 32-byte sighash digest.

    Raises:
        IndexError: If *input_index* is out of range for the transaction
            inputs.
        ValueError: If *sighash_flag* is not a recognised SIGHASH flag.
    """
    from btx.services.serializer import serialize_legacy_tx_for_sighash

    base_flag = sighash_flag & SIGHASH_MASK
    if base_flag == SIGHASH_SINGLE and input_index >= len(transaction.outputs):
        return b"\x01" + b"\x00" * 31

    preimage = serialize_legacy_tx_for_sighash(
        transaction, input_index, script, sighash_flag
    )
    return hash256(preimage)
