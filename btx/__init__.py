# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
"""btx: A pure-Python ECDSA signing, extraction, and analysis library.

The top-level package exposes the library's public surface.  Callers
who want a curated set of common symbols can ``import btx``; callers
who want narrower, sub-domain APIs should import from the
appropriate submodule:

- :mod:`btx.curve` – secp256k1 arithmetic, point type, pluggable
  backends (pure Python and optional ``coincurve``/libsecp256k1).
- :mod:`btx.field` – modular-arithmetic primitives (inverse,
  square root) shared by the curve layer.
- :mod:`btx.encoding` – low-level binary helpers: hex, varint,
  DER, SEC public-key encoding, and Bitcoin hash functions
  (SHA-256, double-SHA-256, HASH-160, BIP-340 tagged hash).
- :mod:`btx.script` – script parsing, classification (P2PK,
  P2PKH, P2SH, P2WPKH, P2WSH, P2TR, multisig, timelock),
  construction, and Taproot script-path helpers.
- :mod:`btx.sighash` – signature-hash computation for legacy,
  SegWit v0 (BIP-143), and Taproot (BIP-341) transactions, plus
  SIGHASH flag constants.
- :mod:`btx.transaction` – immutable transaction models, wire
  parser, fluent builder, RBF detection, fee estimation, and the
  ``transaction.ops`` module for serialisation, hashing and sighash.
- :mod:`btx.signature` – ECDSA and Schnorr (BIP-340) signature
  extraction, linearisation (canonical sorting), verification,
  signing, batch extraction pipelines, and nonce-reuse attack
  utilities.
- :mod:`btx.descriptor` – Miniscript descriptor parser/compiler
  and analyzer (subset of the Miniscript language).
- :mod:`btx.psbt` – Partially Signed Bitcoin Transaction (BIP-174)
  parsing, serialisation, in-memory editor, and signature extraction.
- :mod:`btx.services` – blockchain data providers (Blockstream,
  Mempool.space, blockchain.info, generic HTTP), transaction
  serialisation helpers, and async/batch fetching.
- :mod:`btx.cli` – Typer-based command-line interface exposing
  the most common operations.

Design notes
------------

- Pure-Python by default; libsecp256k1 is opt-in via the
  ``coincurve`` extra.  See :data:`btx.settings.settings` and the
  ``BTX_DEFAULT_BACKEND`` environment variable for backend
  selection.
- No network dependencies at the core layer; blockchain services
  are isolated in :mod:`btx.services` and are never imported by
  the signature or script modules.
- All public dataclasses are ``frozen=True, slots=True`` for value
  semantics and predictable hashing.
"""

__version__ = "0.5.0"

from btx.curve import (
    CURVE_ORDER,
    FIELD_PRIME,
    GENERATOR_POINT,
    INFINITY_POINT,
    CurveBackend,
    LibsecpBackend,
    NativeBackend,
    Point,
    add,
    double,
    get_backend,
    is_on_curve,
    multiply,
    negate,
    parse_public_key,
    serialize_public_key,
)
from btx.descriptor import (
    DescriptorError,
    DescriptorInfo,
    DescriptorNode,
    analyze_descriptor,
    compile_descriptor,
    contains_op,
    estimate_satisfaction,
    extract_keys,
)
from btx.encoding import (
    decode_der,
    decode_hex,
    decode_varint,
    encode_der,
    encode_hex,
    encode_varint,
    hash160,
    hash256,
    parse_sec,
    serialize_sec,
    sha256,
    tagged_hash,
)
from btx.exceptions import BtxError, UnsupportedScriptPathError
from btx.field import inverse, sqrt
from btx.psbt import (
    Psbt,
    PsbtEditor,
    PsbtInput,
    PsbtOutput,
    parse_psbt,
    parse_psbt_from_file,
    parse_psbt_hex,
    psbt_extract_signatures,
    serialize_psbt,
)
from btx.script import (
    P2PK,
    P2PKH,
    P2SH,
    P2TR,
    P2WPKH,
    P2WSH,
    build_p2pkh,
    build_p2sh,
    build_p2tr,
    build_p2wpkh,
    build_p2wsh,
    classify_script_pubkey,
    parse_script,
)
from btx.services import (
    BaseBlockchainProvider,
    BlockchainInfoProvider,
    GenericHttpProvider,
    blockstream_provider,
    broadcast_transaction,
    mempool_space_provider,
)
from btx.settings import settings
from btx.sighash import (
    SIGHASH_ALL,
    SIGHASH_ANYONECANPAY,
    SIGHASH_DEFAULT,
    SIGHASH_NONE,
    SIGHASH_SINGLE,
    sighash_legacy,
    sighash_segwit,
    sighash_taproot,
)
from btx.signature import (
    Record,
    SignatureCollection,
    batch_extract,
    batch_extract_from_file,
    correlate_across_transactions,
    extract_signatures,
    linearize_signatures,
    recover_public_key,
    sign,
    sign_tx_input,
    verify_all,
    verify_schnorr_signature,
    verify_signature,
)
from btx.transaction import (
    EMPTY_WITNESS,
    OutPoint,
    TransactionBuilder,
    Tx,
    TxIn,
    TxOut,
    Witness,
    estimate_minimum_fee,
    estimate_optimal_fee,
    estimate_vsize,
    has_sequence_lock,
    is_opt_in_rbf,
    parse_tx,
    tx_from_dict,
)

__all__ = [
    "BaseBlockchainProvider",
    "BlockchainInfoProvider",
    "BtxError",
    "CURVE_ORDER",
    "CurveBackend",
    "DescriptorError",
    "DescriptorInfo",
    "DescriptorNode",
    "EMPTY_WITNESS",
    "FIELD_PRIME",
    "GENERATOR_POINT",
    "GenericHttpProvider",
    "INFINITY_POINT",
    "LibsecpBackend",
    "NativeBackend",
    "OutPoint",
    "P2PK",
    "P2PKH",
    "P2SH",
    "P2TR",
    "P2WPKH",
    "P2WSH",
    "Point",
    "Psbt",
    "PsbtEditor",
    "PsbtInput",
    "PsbtOutput",
    "Record",
    "SIGHASH_ALL",
    "SIGHASH_ANYONECANPAY",
    "SIGHASH_DEFAULT",
    "SIGHASH_NONE",
    "SIGHASH_SINGLE",
    "SignatureCollection",
    "TransactionBuilder",
    "Tx",
    "TxIn",
    "TxOut",
    "UnsupportedScriptPathError",
    "Witness",
    "add",
    "analyze_descriptor",
    "batch_extract",
    "batch_extract_from_file",
    "blockstream_provider",
    "broadcast_transaction",
    "build_p2pkh",
    "build_p2sh",
    "build_p2tr",
    "build_p2wpkh",
    "build_p2wsh",
    "classify_script_pubkey",
    "compile_descriptor",
    "contains_op",
    "correlate_across_transactions",
    "decode_der",
    "decode_hex",
    "decode_varint",
    "double",
    "encode_der",
    "encode_hex",
    "encode_varint",
    "estimate_minimum_fee",
    "estimate_optimal_fee",
    "estimate_satisfaction",
    "estimate_vsize",
    "extract_keys",
    "extract_signatures",
    "get_backend",
    "has_sequence_lock",
    "hash160",
    "hash256",
    "inverse",
    "is_on_curve",
    "is_opt_in_rbf",
    "linearize_signatures",
    "mempool_space_provider",
    "multiply",
    "negate",
    "parse_psbt",
    "parse_psbt_from_file",
    "parse_psbt_hex",
    "parse_public_key",
    "parse_script",
    "parse_sec",
    "parse_tx",
    "psbt_extract_signatures",
    "recover_public_key",
    "serialize_psbt",
    "serialize_public_key",
    "serialize_sec",
    "settings",
    "sha256",
    "sighash_legacy",
    "sighash_segwit",
    "sighash_taproot",
    "sign",
    "sign_tx_input",
    "sqrt",
    "tagged_hash",
    "tx_from_dict",
    "verify_all",
    "verify_schnorr_signature",
    "verify_signature",
]
