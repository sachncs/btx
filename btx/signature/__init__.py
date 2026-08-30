# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""ECDSA and Schnorr signature types.

This subpackage is the analytical heart of the library: it takes raw
transactions as input and produces structured ``Record`` objects
containing the ``(r, s, z)`` triple needed for nonce-reuse analysis.

Submodules:

- :mod:`btx.signature.record` – the :class:`Record` dataclass and
  its convenience properties.
- :mod:`btx.signature.collection` – :class:`SignatureCollection`
  and the ``sort_records`` helper.
- :mod:`btx.signature.check` – ECDSA verification and public-key
  recovery from signatures.
- :mod:`btx.signature.batch_verify` – sequential verification of
  multiple signatures.
- :mod:`btx.signature.schnorr` – BIP-340 Schnorr verification and
  the ``lift_x`` helper.
- :mod:`btx.signature.signer` – RFC-6979 deterministic ECDSA
  signing and the high-level :func:`sign_tx_input` helper.
- :mod:`btx.signature.extraction` – the extractor-plugin
  registry and the polymorphic ``extract_signatures`` dispatcher
  that handles every standard script type.
- :mod:`btx.signature.linearization` – derivation of the
  ``(α, β)`` linear coefficients used by the nonce-reuse attack.
- :mod:`btx.signature.attack` – nonce-reuse detection and
  private-key recovery.
- :mod:`btx.signature.pipeline` – batch and parallel extraction
  with graceful shutdown, per-batch logging, and cross-transaction
  correlation.

The two halves of the pipeline (``extraction`` and ``linearization``)
are deliberately decoupled: the extractor produces raw records, and
the lineariser produces the algebraic coefficients.  This lets
attack code work on either form without depending on parsing logic.
"""

from btx.signature.attack import NonceReuseGroup
from btx.signature.batch_verify import verify_all
from btx.signature.check import recover_public_key, verify_signature
from btx.signature.collection import SignatureCollection
from btx.signature.extraction import extract_signatures
from btx.signature.linearization import linearize_signatures
from btx.signature.pipeline import (
    BatchResult,
    batch_extract,
    batch_extract_from_file,
    correlate_across_transactions,
    merge_records,
)
from btx.signature.record import Record
from btx.signature.schnorr import lift_x, verify_schnorr_signature
from btx.signature.signer import sign, sign_tx_input

__all__ = [
    "BatchResult",
    "NonceReuseGroup",
    "Record",
    "SignatureCollection",
    "batch_extract",
    "batch_extract_from_file",
    "correlate_across_transactions",
    "extract_signatures",
    "lift_x",
    "linearize_signatures",
    "merge_records",
    "recover_public_key",
    "sign",
    "sign_tx_input",
    "verify_all",
    "verify_schnorr_signature",
    "verify_signature",
]
