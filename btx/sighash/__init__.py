# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Signature-hash computation for legacy, SegWit v0, and Taproot inputs.

Three sighash algorithms are supported, each implementing a different
Bitcoin specification:

- :mod:`btx.sighash.flag` – SIGHASH flag constants and validation.
- :mod:`btx.sighash.legacy` – pre-SegWit sighash (hash of full
  transaction with input scripts and selected outputs modified per
  the flag).
- :mod:`btx.sighash.segwit` – BIP-143 SegWit v0 sighash (commits
  to amounts and uses amortised hashes of prevouts and sequences for
  a factor-of-~3 speedup over the legacy algorithm).
- :mod:`btx.sighash.taproot` – BIP-341 Taproot sighash (tagged
  hash over an extensible, script/key-path-aware digest).

The legacy and SegWit sighashes are LRU-cached because they are
typically computed repeatedly for the same transaction during
extraction and signing pipelines.  The Taproot algorithm is not
cached because it carries a much larger set of parameters.

The :class:`SighashScheme` ABC exposes a uniform ``compute`` interface
across all three algorithms, enabling polymorphic dispatch in
:func:`btx.signature.extraction.helpers.compute_sighash`.

References
----------

- Bitcoin developer guide: "Signature hash modification"
- BIP-143: "Transaction Signature Verification for SegWit v0"
- BIP-341: "Taproot: SegWit version 1 spending rules"
"""

from abc import ABC, abstractmethod

from btx.sighash.flag import (
    SIGHASH_ALL,
    SIGHASH_ALL_ANYONECANPAY,
    SIGHASH_ANYONECANPAY,
    SIGHASH_MASK,
    SIGHASH_NAMES,
    SIGHASH_NONE,
    SIGHASH_NONE_ANYONECANPAY,
    SIGHASH_SINGLE,
    SIGHASH_SINGLE_ANYONECANPAY,
    require_sighash_flag,
    sighash_name,
)
from btx.sighash.legacy import sighash_legacy
from btx.sighash.segwit import sighash_segwit
from btx.sighash.taproot import sighash_taproot

__all__ = [
    "SIGHASH_ALL",
    "SIGHASH_ALL_ANYONECANPAY",
    "SIGHASH_ANYONECANPAY",
    "SIGHASH_MASK",
    "SIGHASH_NAMES",
    "SIGHASH_NONE",
    "SIGHASH_NONE_ANYONECANPAY",
    "SIGHASH_SINGLE",
    "SIGHASH_SINGLE_ANYONECANPAY",
    "LegacySighash",
    "SegwitSighash",
    "SighashScheme",
    "TaprootSighash",
    "require_sighash_flag",
    "sighash_legacy",
    "sighash_name",
    "sighash_segwit",
    "sighash_taproot",
]


class SighashScheme(ABC):
    """Abstract base for sighash computation strategies.

    Subclasses implement a single ``compute`` method that returns the
    32-byte sighash digest for a given transaction input.
    """

    @abstractmethod
    def compute(
        self,
        tx: object,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
    ) -> bytes:
        """Compute the sighash digest.

        Args:
            tx: The parent transaction.
            input_index: Index of the input being signed.
            script_code: The script code for this input.
            value: Amount of the UTXO being spent (for SegWit/Taproot).
            sighash_flag: SIGHASH flag byte.

        Returns:
            32-byte sighash digest.
        """


class LegacySighash(SighashScheme):
    """Pre-SegWit sighash scheme (BIP-pre-143)."""

    def compute(
        self,
        tx: object,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
    ) -> bytes:
        return sighash_legacy(tx, input_index, script_code, sighash_flag)


class SegwitSighash(SighashScheme):
    """BIP-143 SegWit v0 sighash scheme."""

    def compute(
        self,
        tx: object,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
    ) -> bytes:
        return sighash_segwit(tx, input_index, script_code, value, sighash_flag)


class TaprootSighash(SighashScheme):
    """BIP-341 Taproot sighash scheme."""

    def compute(
        self,
        tx: object,
        input_index: int,
        script_code: bytes,
        value: int,
        sighash_flag: int,
    ) -> bytes:
        return sighash_taproot(
            tx,
            input_index,
            script_code,
            sighash_flag,
        )
