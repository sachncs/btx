# Getting Started

This guide will help you get up and running with the btx library quickly.

## Installation

### From Source (current distribution method)

```bash
git clone https://github.com/sachncs/btx.git
cd btx
python -m venv .venv
.venv/bin/python -m pip install -e .
```

For development and tests, install the development extra:

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

For optional C-backed acceleration:

```bash
.venv/bin/python -m pip install -e ".[coincurve]"
```

PyPI publication is planned but is not enabled yet.

If you only need an installed package and do not need a checkout, install
directly from the Git repository:

```bash
python -m pip install "btx @ git+https://github.com/sachncs/btx.git"
```

### Using uv (Recommended for Development)

```bash
git clone https://github.com/sachncs/btx.git
cd btx
./setup.sh  # Syncs locked dev deps, installs the site, and runs validation
```

## Basic Usage

### Parse a Transaction

```python
from btx import parse_tx, extract_signatures

# Parse raw transaction hex
raw_hex = "0200000001..."
tx, bytes_consumed = parse_tx(bytes.fromhex(raw_hex))

print(f"Parsed {len(tx.inputs)} inputs, {len(tx.outputs)} outputs")
print(f"Transaction ID: {tx.txid().hex()}")
```

### Extract Signatures

```python
from btx import parse_tx, extract_signatures, encode_hex

tx, _ = parse_tx(bytes.fromhex(raw_hex))
records = extract_signatures(tx)

for rec in records:
    print(f"Input {rec.input_index}: {encode_hex(rec.signature)}")
```

### Verify a Signature

```python
from btx import verify_signature
from btx.encoding import sha256

message_hash = sha256(b"message to verify")
public_key = bytes.fromhex("02...")  # Compressed public key
der_sig = bytes.fromhex("30...")     # DER-encoded signature

ok = verify_signature(message_hash, der_sig, public_key)
print(f"Signature valid: {ok}")
```

## CLI Usage

The library includes a command-line tool for quick analysis:

```bash
# Check version
btx version

# Decode a transaction
btx decode <tx-hex>

# Extract signatures
btx extract <tx-hex>

# Extract with UTXO info (needed for SegWit)
btx extract <tx-hex> --utxo-value 100000000

# Output as JSON
btx extract <tx-hex> --json

# Linearize (sort) signatures
btx linearize <tx-hex>

# Health check
btx health
```

## Common Patterns

### SegWit Transaction Handling

SegWit transactions require UTXO values and/or scriptPubKeys for sighash computation:

```python
from btx import parse_tx, extract_signatures

tx, _ = parse_tx(bytes.fromhex(raw_hex))

# Provide UTXO metadata for accurate sighash
records = extract_signatures(tx,
    utxo_script_pubkeys=[bytes.fromhex("0014...")],  # P2WPKH script
    utxo_values=[100000000],  # 1 BTC in satoshis
)
```

### Batch Processing

Process multiple transactions efficiently:

```python
from btx import batch_extract, correlate_across_transactions

tx_hexes = ["0200...", "0200..."]  # Multiple transactions

# Extract in parallel
results = batch_extract(tx_hexes)

# Find nonce reuse across transactions
correlations = correlate_across_transactions(results)
```

### Nonce Reuse Detection

```python
from btx.signature.linearization.coefficients import (
    LinearCoefficientCollection, derive_linear_coefficients,
)
from btx.signature.attack import detect_nonce_reuse, recover_from_nonce_reuse

# Derive linear coefficients from extracted signatures
collection = LinearCoefficientCollection(records=tuple(
    derive_linear_coefficients(r=rec.r, s=rec.s, z=rec.z, input_index=i)
    for i, rec in enumerate(records)
))

# Detect nonce reuse
groups = detect_nonce_reuse(collection)

# Recover private keys
for group in groups:
    result = recover_from_nonce_reuse(
        collection.records[group.indices[0]],
        collection.records[group.indices[1]],
    )
    print(f"Recovered private key: {result.private_key.hex()}")
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BTX_LOG_LEVEL` | `WARNING` | Log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |

### Programmatic Settings

```python
from btx import settings

settings.default_backend = "libsecp"  # Requires coincurve
```

`settings` is a frozen dataclass; derive customised copies with
`dataclasses.replace(settings, ...)` rather than mutating in place.

## Next Steps

- Read the [Architecture Overview](ARCHITECTURE.md) for design details
- Explore the [API Reference](API.md) for complete documentation
- Check [Configuration](CONFIGURATION.md) for advanced options
- Review [Testing](TESTING.md) for contributing guidelines
