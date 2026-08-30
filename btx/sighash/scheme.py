# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Polymorphic sighash computation strategies.

Defines the :class:`SighashScheme` abstract base and its three concrete
implementations (:class:`LegacySighash`, :class:`SegwitSighash`,
:class:`TaprootSighash`).  Each scheme owns a single algorithm — pre-
SegWit, BIP-143, or BIP-341 — and exposes a uniform ``compute`` method
so callers can dispatch without an if/elif chain on script type.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from btx.encoding.hasher import tagged_hash
from btx.encoding.varint import encode_varint
from btx.sighash.legacy import sighash_legacy
from btx.sighash.segwit import sighash_segwit
from btx.sighash.taproot import (
    LEAF_VERSION_TAPSCRIPT,
    TAPROOT_SCRIPT_PATH_PREFIXES,
    sighash_taproot,
)
from btx.transaction.models import Tx

__all__ = [
    "LegacySighash",
    "SegwitSighash",
    "SighashScheme",
    "TaprootSighash",
    "tapleaf_hash",
]


def tapleaf_hash(leaf_version: int, leaf_script: bytes) -> bytes:
    """Compute the BIP-341 ``TapLeaf`` tagged hash.

    The canonical computation lives here so :mod:`btx.script.taproot`
    and :mod:`btx.sighash.taproot` share one definition.

    Args:
        leaf_version: The leaf version byte (typically ``0xC0`` for
            BIP-342 tapscript).
        leaf_script: The leaf script bytes (without the leaf version).

    Returns:
        32-byte tagged hash digest.
    """
    return tagged_hash(
        "TapLeaf",
        bytes([leaf_version]) + encode_varint(len(leaf_script)) + leaf_script,
    )


class SighashScheme(ABC):
    """Abstract base for sighash computation strategies.

    Subclasses implement a single ``compute`` method that returns the
    32-byte sighash digest for a given transaction input.
    """

    @abstractmethod
    def compute(
        self,
        tx: Tx,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
        *,
        amounts: Sequence[int] | None = None,
        scriptpubkeys: Sequence[bytes] | None = None,
    ) -> bytes:
        """Compute the sighash digest.

        Args:
            tx: The parent transaction.
            input_index: Index of the input being signed.
            script_code: The script code for this input.
            value: Amount of the UTXO being spent (for SegWit/Taproot).
            sighash_flag: SIGHASH flag byte.
            amounts: UTXO value of every input (required by the
                Taproot scheme; ignored by the legacy and SegWit
                schemes).
            scriptpubkeys: ``scriptPubKey`` of every spent output
                (required by the Taproot scheme; ignored by the legacy
                and SegWit schemes).

        Returns:
            32-byte sighash digest.
        """


class LegacySighash(SighashScheme):
    """Pre-SegWit sighash scheme (BIP-pre-143)."""

    def compute(
        self,
        tx: Tx,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
        *,
        amounts: Sequence[int] | None = None,
        scriptpubkeys: Sequence[bytes] | None = None,
    ) -> bytes:
        return sighash_legacy(tx, input_index, script_code, sighash_flag)


class SegwitSighash(SighashScheme):
    """BIP-143 SegWit v0 sighash scheme."""

    def compute(
        self,
        tx: Tx,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
        *,
        amounts: Sequence[int] | None = None,
        scriptpubkeys: Sequence[bytes] | None = None,
    ) -> bytes:
        return sighash_segwit(tx, input_index, script_code, value, sighash_flag)


class TaprootSighash(SighashScheme):
    """BIP-341 Taproot sighash scheme.

    For script-path spending the ``tapleaf_hash`` (BIP-341) is derived
    from *script_code*, which must carry the BIP-342 leaf version
    prefix (``0xc0``) as the first byte; the prefix is split off and
    the remaining leaf script is hashed.  Callers only need to supply
    the versioned tapleaf script plus the per-input ``amounts`` and
    ``scriptpubkeys`` that BIP-341 commits to.
    """

    def compute(
        self,
        tx: Tx,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
        *,
        amounts: Sequence[int] | None = None,
        scriptpubkeys: Sequence[bytes] | None = None,
    ) -> bytes:
        if script_code and script_code[0] in TAPROOT_SCRIPT_PATH_PREFIXES:
            leaf_version = script_code[0]
            leaf_script = script_code[1:]
        else:
            leaf_version = LEAF_VERSION_TAPSCRIPT
            leaf_script = script_code
        leaf_hash = tapleaf_hash(leaf_version, leaf_script)
        if amounts is None or scriptpubkeys is None:
            raise ValueError("Taproot sighash requires both amounts and scriptpubkeys.")
        return sighash_taproot(
            tx,
            input_index,
            script_code,
            sighash_flag,
            tapleaf_hash=leaf_hash,
            amounts=amounts,
            scriptpubkeys=scriptpubkeys,
        )
