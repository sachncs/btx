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
- :mod:`btx.sighash.scheme` – the polymorphic :class:`SighashScheme`
  ABC and its three concrete strategies used by signature
  extraction.

The legacy and SegWit sighashes are LRU-cached because they are
typically computed repeatedly for the same transaction during
extraction and signing pipelines.  The Taproot algorithm is not
cached because it carries a much larger set of parameters.

References
----------

- Bitcoin developer guide: "Signature hash modification"
- BIP-143: "Transaction Signature Verification for SegWit v0"
- BIP-341: "SegWit version 1 spending rules"
"""

from __future__ import annotations

from btx.sighash.flag import (
    SIGHASH_ALL,
    SIGHASH_ALL_ANYONECANPAY,
    SIGHASH_ANYONECANPAY,
    SIGHASH_DEFAULT,
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
from btx.sighash.scheme import (
    LegacySighash,
    SegwitSighash,
    SighashScheme,
    TaprootSighash,
    tapleaf_hash,
)
from btx.sighash.segwit import sighash_segwit
from btx.sighash.taproot import (
    LEAF_VERSION_TAPSCRIPT,
    NO_CODESEPARATOR,
    TAPROOT_SCRIPT_PATH_PREFIXES,
    sighash_taproot,
)

__all__ = [
    "LEAF_VERSION_TAPSCRIPT",
    "LegacySighash",
    "NO_CODESEPARATOR",
    "SIGHASH_ALL",
    "SIGHASH_ALL_ANYONECANPAY",
    "SIGHASH_ANYONECANPAY",
    "SIGHASH_DEFAULT",
    "SIGHASH_MASK",
    "SIGHASH_NAMES",
    "SIGHASH_NONE",
    "SIGHASH_NONE_ANYONECANPAY",
    "SIGHASH_SINGLE",
    "SIGHASH_SINGLE_ANYONECANPAY",
    "SegwitSighash",
    "SighashScheme",
    "TAPROOT_SCRIPT_PATH_PREFIXES",
    "TaprootSighash",
    "require_sighash_flag",
    "sighash_legacy",
    "sighash_name",
    "sighash_segwit",
    "sighash_taproot",
    "tapleaf_hash",
]
