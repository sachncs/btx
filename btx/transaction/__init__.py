# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Bitcoin transaction types, parsing, construction, and analysis.

This subpackage owns every aspect of the Bitcoin transaction model:

- :mod:`btx.transaction.models` – immutable ``frozen=True,
  slots=True`` dataclasses: :class:`OutPoint`, :class:`TxIn`,
  :class:`TxOut`, :class:`Witness`, :class:`Tx`, plus the
  :class:`TxSerializer` / :class:`TxRbf` / :class:`TxSighash` composed
  engines bound to ``Tx`` for fluent domain-chain access.
- :mod:`btx.transaction.parser` – wire-format deserialisation
  (legacy + SegWit) with explicit limits (max tx size, input/output
  counts, witness item count and size).
- :mod:`btx.transaction.tx` – :func:`make_tx` /
  :func:`build_transaction` convenience builder.
- :mod:`btx.transaction.builder` – :class:`TransactionBuilder`
  fluent API and :func:`tx_from_dict` validating factory.
- :mod:`btx.transaction.fee` – vsize, fee estimation, and
  output-value summation.
- :mod:`btx.transaction.rbf` – opt-in RBF (BIP-125) detection
  and relative-sequence-lock (BIP-68) inspection.

Hard-coded invariants enforced by the models' ``__post_init__``
hooks:

- ``txid`` is always 32 bytes; ``vout``, ``sequence``, ``value``, and
  ``lock_time`` are non-negative.
- ``value`` is capped at ``21_000_000 * 100_000_000`` satoshis (the
  Bitcoin supply ceiling).
"""

from btx.transaction.builder import TransactionBuilder, tx_from_dict
from btx.transaction.fee import (
    estimate_minimum_fee,
    estimate_optimal_fee,
    estimate_vsize,
    total_output_value,
)
from btx.transaction.models import EMPTY_WITNESS, OutPoint, Tx, TxIn, TxOut, Witness
from btx.transaction.parser import parse_tx
from btx.transaction.rbf import has_sequence_lock, is_opt_in_rbf
from btx.transaction.tx import make_tx

__all__ = [
    "EMPTY_WITNESS",
    "OutPoint",
    "TransactionBuilder",
    "Tx",
    "TxIn",
    "TxOut",
    "Witness",
    "estimate_minimum_fee",
    "estimate_optimal_fee",
    "estimate_vsize",
    "has_sequence_lock",
    "is_opt_in_rbf",
    "make_tx",
    "parse_tx",
    "total_output_value",
    "tx_from_dict",
]
