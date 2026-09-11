# API Reference

## Top-level symbols (`btx/__init__.py`)

The canonical list lives in `btx/__init__.py` under `__all__`.
Representative top-level symbols include:

```python
from btx import (
    # Curve and field
    CURVE_ORDER, FIELD_PRIME, GENERATOR_POINT, INFINITY_POINT,
    Point, CurveBackend, NativeBackend, LibsecpBackend,
    add, double, multiply, negate, is_on_curve,
    get_backend, parse_public_key, serialize_public_key,
    inverse, sqrt,

    # Encoding
    sha256, hash256, hash160, tagged_hash,
    encode_hex, decode_hex, encode_der, decode_der,
    encode_varint, decode_varint, parse_sec, serialize_sec,

    # Script
    P2PKH, P2SH, P2WPKH, P2WSH, P2TR,
    parse_script, classify_script_pubkey,
    build_p2pkh, build_p2sh, build_p2wpkh, build_p2wsh, build_p2tr,

    # Sighash
    SIGHASH_ALL, SIGHASH_NONE, SIGHASH_SINGLE,
    SIGHASH_ANYONECANPAY, SIGHASH_DEFAULT,
    sighash_legacy, sighash_segwit, sighash_taproot,

    # Transaction
    Tx, TxIn, TxOut, OutPoint, Witness, EMPTY_WITNESS,
    TransactionBuilder, parse_tx, tx_from_dict,
    estimate_minimum_fee, estimate_optimal_fee, estimate_vsize,
    is_opt_in_rbf, has_sequence_lock,

    # Signature
    Record, SignatureCollection,
    extract_signatures, linearize_signatures,
    verify_signature, verify_schnorr_signature, verify_all,
    recover_public_key, sign, sign_tx_input,
    batch_extract, batch_extract_from_file,
    correlate_across_transactions,

    # PSBT
    Psbt, PsbtEditor, PsbtInput, PsbtOutput,
    parse_psbt, parse_psbt_from_file, parse_psbt_hex,
    serialize_psbt, psbt_extract_signatures,

    # Descriptor
    DescriptorError, DescriptorInfo, DescriptorNode,
    analyze_descriptor, compile_descriptor, extract_keys,
    estimate_satisfaction, contains_op,

    # Services
    BaseBlockchainProvider, BlockchainInfoProvider, GenericHttpProvider,
    blockstream_provider, mempool_space_provider,
    broadcast_transaction,

    # Errors and settings
    BtxError, UnsupportedScriptPathError,
    settings,
)
```

---

## Signature Extraction

### `btx.extract_signatures`

```python
def extract_signatures(
    tx: Tx,
    utxo_script_pubkeys: Sequence[bytes] | None = None,
    utxo_values: Sequence[int] | None = None,
) -> list[Record]:
```

Parse all signature-bearing inputs of a transaction. Returns a `list[Record]` — one entry per ECDSA signature found. Supports P2PKH, P2SH, P2WPKH, P2WSH, P2SH-P2WPKH, P2SH-P2WSH, P2TR key-path and script-path.

For SegWit v0 inputs, provide either `utxo_script_pubkeys` or `utxo_values` (amount needed for BIP-143 sighash).

### `btx.Record`

```python
@dataclass(frozen=True, slots=True)
class Record:
    txid: bytes
    input_index: int
    signature: bytes
    public_key: Point
    parity: int
    sighash_flag: bytes
    script_type: str
    script_class: str
    amount: int | None
```

### `btx.linearize_signatures`

```python
def linearize_signatures(
    records: list[Record],
) -> list[Record]:
```

Sort records by `(txid, vin)` ascending (lexicographic txid, numeric vin). Prepares records for nonce-reuse analysis.

---

## Transaction Parsing & Construction

### `btx.parse_tx`

```python
def parse_tx(raw: bytes, /) -> tuple[Tx, int]:
```

Parse a raw Bitcoin transaction. Returns `(Tx, bytes_consumed)`. Supports both legacy and SegWit v0/v1 (taproot) transactions. Raises `ValueError` on malformed data.

### `btx.transaction.TransactionBuilder`

```python
class TransactionBuilder:
    def __init__(self, version: int = 2, lock_time: int = 0) -> None: ...
    def add_input(self, txid: bytes, vout: int, script_sig: bytes = b"", sequence: int = 0xffffffff, witness: Witness | None = None) -> TransactionBuilder: ...
    def add_output(self, value: int, script_pubkey: bytes) -> TransactionBuilder: ...
    def build(self) -> Tx: ...
```

### `btx.transaction.tx_from_dict`

```python
def tx_from_dict(data: dict) -> Tx:
```

Validate and build a `Tx` from a dict with schema: `{"version": int, "inputs": [...], "outputs": [...], "lock_time": int}`.

---

## Sighash Computation

### `btx.sighash_legacy`

```python
def sighash_legacy(tx: Tx, input_index: int, script_code: bytes, sighash_flag: int = SIGHASH_ALL) -> bytes:
```

Pre-SegWit (BIP-67) sighash. 32-byte double-SHA256 digest.

### `btx.sighash_segwit`

```python
def sighash_segwit(tx: Tx, input_index: int, script_code: bytes, amount: int, sighash_flag: int = SIGHASH_ALL) -> bytes:
```

SegWit v0 (BIP-143) sighash. Requires `amount` (prevout value).

### `btx.sighash_taproot`

```python
def sighash_taproot(
    tx: Tx,
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
```

Taproot (BIP-341) sighash. Requires `amounts` and `scriptpubkeys` for
every input. Pass `script` (with the `0xc0` leaf-version prefix) for
script-path spending, or `None` for key-path; `tapleaf_hash` is derived
from the script when not supplied. Accepts the seven BIP-341 hash_type
values `{0x00, 0x01, 0x02, 0x03, 0x81, 0x82, 0x83}`.

---

## Signature Verification

### `btx.verify_signature`

```python
def verify_signature(message_hash: bytes, der_sig: bytes, public_key: Point) -> bool:
```

Verify an ECDSA signature. Returns `True` if valid. Uses constant-time comparison internally.

### `btx.recover_public_key`

```python
def recover_public_key(message_hash: bytes, der_sig: bytes, rec_id: int) -> Point:
```

Recover the public key from a message hash and signature with recovery ID (0–3).

### `btx.verify_schnorr_signature`

```python
def verify_schnorr_signature(
    message_hash: bytes, schnorr_sig: bytes, x_only_pubkey: bytes
) -> bool:
```

Verify a BIP-340 Schnorr signature.

### `btx.verify_all`

```python
def verify_all(message_hash: bytes, signatures: list[bytes], public_keys: list[Point]) -> bool:
```

Batch-verify multiple ECDSA signatures against the same message hash.

---

## Nonce Reuse & Linearization

### `btx.signature.derive_linear_coefficients`

```python
@dataclass(frozen=True, slots=True)
class LinearCoefficientRecord:
    alpha: int
    beta: int
    input_index: int

def derive_linear_coefficients(r: int, s: int, z: int, input_index: int) -> LinearCoefficientRecord:
```

Given ECDSA identity `s ≡ k⁻¹(z + rd)`, derive `α = s·r⁻¹ (mod n)` and `β = z·r⁻¹ (mod n)`.
Linearized form: `d ≡ α·k − β (mod n)`.

### `btx.signature.attack.detect_nonce_reuse`

```python
@dataclass(frozen=True, slots=True)
class NonceReuseGroup:
    r_value: int
    indices: list[int]

def detect_nonce_reuse(collection: LinearCoefficientCollection) -> list[NonceReuseGroup]:
```

Find groups of signatures sharing the same `r` value within a `LinearCoefficientCollection`.

### `btx.signature.attack.recover_from_nonce_reuse`

```python
@dataclass(frozen=True, slots=True)
class RecoveredKey:
    private_key: int
    nonce: int

def recover_from_nonce_reuse(record_1: LinearCoefficientRecord, record_2: LinearCoefficientRecord) -> RecoveredKey:
```

Recover private key and nonce from two signatures sharing the same `k`.

### `btx.signature.attack.recover_from_related_nonces`

```python
def recover_from_related_nonces(
    r1: int, s1: int, z1: int,
    r2: int, s2: int, z2: int,
    delta: int,
) -> tuple[int, int]:
```

Recover private key and nonce when `k₂ = k₁ + δ` is known.

---

## Signing

### `btx.signature.sign`

```python
def sign(message_hash: bytes, private_key: int) -> bytes:
```

Deterministic ECDSA signing using RFC 6979 (SHA256-based nonce generation). Returns DER-encoded signature.

### `btx.signature.sign_tx_input`

```python
def sign_tx_input(
    tx: Tx,
    vin: int,
    private_key: int,
    *,
    script: bytes | None = None,
    value: int | None = None,
    sig_version: str = "segwit",
) -> bytes:
```

High-level transaction input signing. Automatically computes the correct sighash, signs, and appends the sighash flag byte. Returns DER-encoded signature with sighash flag.

---

## Batch & Pipeline

### `btx.signature.batch_extract`

```python
def batch_extract(tx_raws: list[bytes], utxo_map: dict | None = None, max_workers: int | None = None) -> list[list[Record]]:
```

Extract signatures from multiple transactions in parallel using `concurrent.futures.ThreadPoolExecutor`.

### `btx.signature.correlate_across_transactions`

```python
def correlate_across_transactions(grouped_records: list[list[Record]]) -> list[tuple[int, int, int]]:
```

Find nonce reuse across multiple transactions. Returns `(tx_a_idx, tx_b_idx, input_idx)` triples with matching `r` values.

---

## PSBT

### `btx.parse_psbt`

```python
def parse_psbt(raw: bytes) -> Psbt:
```

Parse a BIP-174 PSBT. Returns `Psbt` with typed per-input/output maps.

### `btx.serialize_psbt`

```python
def serialize_psbt(psbt: Psbt) -> bytes:
```

Serialize a `Psbt` back to binary.

### `btx.serialize_tx`

```python
def serialize_tx(tx: Tx) -> bytes:
```

Serialize a transaction with segwit-awareness.

### `btx.serialize_legacy_tx`

```python
def serialize_legacy_tx(tx: Tx) -> bytes:
```

Serialize a transaction in legacy (pre-segwit) format.

### `btx.tx_to_json`

```python
def tx_to_json(tx: Tx) -> dict:
```

Convert a transaction to a JSON-serializable dict.

### `btx.is_opt_in_rbf`

```python
def is_opt_in_rbf(tx: Tx) -> bool:
```

Check if a transaction signals opt-in RBF (sequence &lt; 0xfffffffe on any input).

### `btx.has_sequence_lock`

```python
def has_sequence_lock(tx: Tx) -> bool:
```

Check if any input uses a sequence lock (sequence &lt; 0xffffffff with bit 22 set).

### `btx.psbt.PsbtEditor`

```python
class PsbtEditor:
    @staticmethod
    def from_tx(tx: Tx) -> PsbtEditor: ...
    def set_input_utxo(self, vin: int, witness_utxo: bytes | None = None, non_witness_utxo: bytes | None = None) -> PsbtEditor: ...
    def add_input_partial_sig(self, vin: int, pubkey: bytes, sig: bytes) -> PsbtEditor: ...
    def build(self) -> Psbt: ...
    def serialize(self) -> bytes: ...
```

Fluent builder for constructing and editing PSBTs.

---

## Script Classification

### `btx.script.classify_script_pubkey`

```python
def classify_script_pubkey(script_pubkey: bytes) -> str:
```

Classify a scriptPubKey and return one of the script-type strings
(`P2PKH`, `P2PK`, `P2SH`, `P2WPKH`, `P2WSH`, `P2TR`,
`NON_STANDARD`, etc.).

### `btx.get_x_only_pubkey`

```python
def get_x_only_pubkey(script_pubkey: bytes) -> bytes | None:
```

Extract the 32-byte x-only public key from a P2TR output (OP_1 <32-byte-push>). Returns `None` for non-P2TR scripts.

### `btx.parse_taproot_witness_stack`

```python
class TaprootScriptPath:
    script: bytes
    control_block: bytes

def parse_taproot_witness_stack(witness: Witness) -> tuple[Point | None, list[TaprootScriptPath]]:
```

Parse a taproot witness stack. Returns `(x_only_pubkey, list_of_script_paths)`.

Note: `is_bare_multisig`, `classify_detailed`, `is_op_return`,
`has_timelocks`, `MULTISIG`, `TIMELOCK`, and `OP_RETURN` were
removed in 0.5.0; classify via `btx.classify_script_pubkey` instead.

---

## Blockchain Services

### `btx.services.BlockstreamProvider`

```python
class BlockstreamProvider:
    def __init__(self, network: str = "mainnet") -> None: ...
    def fetch_raw_tx(self, txid: str) -> bytes: ...
    def fetch_outpoint_spend(self, txid: str, vout: int) -> dict | None: ...
```

Fetches transaction data from blockstream.info API. Optional runtime dependency via `urllib.request`.

### `btx.services.BlockchainInfoProvider`

```python
class BlockchainInfoProvider:
    def __init__(self) -> None: ...
    def fetch_raw_tx(self, txid: str) -> bytes: ...
```

Fetches transaction data from blockchain.info API.

### `btx.services.MempoolSpaceProvider`

```python
class MempoolSpaceProvider:
    def __init__(self, network: str = "mainnet") -> None: ...
    def fetch_raw_tx(self, txid: str) -> bytes: ...
```

Fetches transaction data from mempool.space API.

### `btx.services.enrich_transaction`

```python
def enrich_transaction(tx: Tx, provider: BaseBlockchainProvider | None = None) -> Tx:
```

Fetch UTXO details for each input and return an enriched transaction with metadata. Falls back to a default provider if none given.

---

## Settings

### `btx.Settings`

```python
@dataclass(frozen=True, slots=True)
class Settings:
    default_backend: str | None = None
```

Global settings object via `btx.settings`. Configure via the
`BTX_DEFAULT_BACKEND` environment variable or derive a customised
copy:

```python
from dataclasses import replace
from btx import settings

settings = replace(settings, default_backend="libsecp")
```

---

## Curve Backend

### `btx.curve.dispatch.set_backend`

```python
def set_backend(backend: CurveBackend) -> None:
```

Install a `CurveBackend` instance (e.g. `LibsecpBackend()`) as the
active backend for curve operations. Accepts only instances; pass a
string and it raises `TypeError`.

### `btx.curve.dispatch.resolve_backend`

```python
def resolve_backend() -> CurveBackend:
```

Return the active backend (or the default `NativeBackend()` when
none has been explicitly installed).

---

## Health Check

### `btx.health`

```python
def health() -> dict:
```

Run health checks and return a JSON status report with version, import info, backend status, and curve operation verification.
