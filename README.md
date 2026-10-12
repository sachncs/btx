# btx

Pure-Python Bitcoin transaction and secp256k1 tooling for inspecting raw
transactions, signatures, scripts, sighashes, and PSBTs.

[![CI](https://github.com/sachncs/btx/actions/workflows/ci.yml/badge.svg)](https://github.com/sachncs/btx/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-7C3AED)](LICENSE)

> **Distribution status:** `btx` is not published to PyPI yet. Install it
> from a checkout or directly from GitHub. Do not use `pip install btx`.

## What it provides

- Legacy, SegWit v0, and Taproot transaction parsing and serialization.
- ECDSA and Schnorr signature extraction, verification, signing, and recovery.
- Sighash computation for legacy, SegWit v0, and Taproot transactions.
- Bitcoin Script classification, parsing, construction, and Taproot helpers.
- PSBT (BIP-174) parsing, editing, signing, and extraction.
- Descriptor parsing and analysis.
- Nonce-reuse and related-nonce analysis for ECDSA signatures.
- Optional blockchain providers for fetching UTXO data and broadcasting.
- A pure-Python curve backend by default, with optional `coincurve`
  acceleration.

## Documentation

The [public documentation](https://sachncs.github.io/btx/docs/) is standalone
and is the source of truth for users:

- [Getting started](https://sachncs.github.io/btx/docs/getting-started/)
- [API reference](https://sachncs.github.io/btx/docs/api/)
- [Architecture](https://sachncs.github.io/btx/docs/architecture/)
- [Testing](https://sachncs.github.io/btx/docs/testing/)
- [Security](https://sachncs.github.io/btx/docs/security/)
- [Contributing](https://sachncs.github.io/btx/docs/contributing/)
- [Changelog](https://sachncs.github.io/btx/docs/changelog/)

The repository also contains deeper design notes in [`docs/`](docs/).

## Install from source

### Editable install

```bash
git clone https://github.com/sachncs/btx.git
cd btx
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/btx health
```

For development and tests:

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

For the optional `libsecp256k1` backend:

```bash
.venv/bin/python -m pip install -e ".[coincurve]"
```

### Direct Git installation

```bash
python -m pip install "btx @ git+https://github.com/sachncs/btx.git"
```

`typer` is the package's CLI dependency. The core parsing and cryptographic
modules use the Python standard library; `coincurve` is optional.

## Quick start

### Command line

```bash
# Decode a raw transaction
btx decode < transaction.hex

# Extract signatures
btx extract < transaction.hex

# Emit JSON
btx extract < transaction.hex --json

# Check the local installation and available backends
btx health
```

### Python API

```python
from btx import extract_signatures, parse_tx

raw_hex = "..."
tx, bytes_consumed = parse_tx(bytes.fromhex(raw_hex))
records = extract_signatures(tx)

print(bytes_consumed, len(records))
```

SegWit v0 signature extraction requires the spent output's script and value:

```python
records = extract_signatures(
    tx,
    utxo_script_pubkeys=[bytes.fromhex(script_pubkey_hex)],
    utxo_values=[100_000_000],
)
```

## Architecture

The package is layered so byte-level primitives and curve operations can be
tested independently from Bitcoin models, signature analysis, PSBT handling,
and network access:

```text
field / curve / encoding
          ↓
script / transaction / sighash
          ↓
signature / psbt / descriptor
          ↓
services (optional network I/O)
          ↓
cli
```

Network access is opt-in. Importing and using the core parser does not contact
remote services. Providers validate transaction IDs, URLs, response sizes,
timeouts, and retryable failures at their boundary.

## Configuration

Set `BTX_DEFAULT_BACKEND` before importing `btx`:

```bash
BTX_DEFAULT_BACKEND=native   # default pure-Python backend
BTX_DEFAULT_BACKEND=libsecp  # optional coincurve backend
```

The value is exposed through the immutable `btx.settings` object. Use
`dataclasses.replace()` to derive a different settings snapshot instead of
mutating global state.

## Development

Prerequisites: Python 3.12 or later, [`uv`](https://docs.astral.sh/uv/), and
Node.js 22 for site checks.

```bash
./setup.sh
make test-all
```

Useful focused commands:

```bash
make test
make test-cov
make lint
make typecheck
make docker-test
cd site && npm run check && npm run build
```

The site is an Astro application under [`site/`](site/) and is deployed by
the workflow in [`.github/workflows/deploy-site.yml`](.github/workflows/deploy-site.yml).

## Security and scope

`btx` is analysis and developer tooling, not a wallet or custody system. Do
not provide private keys or signing material to an unreviewed workflow. See
[`SECURITY.md`](SECURITY.md) for responsible disclosure instructions.

## Contributing

Bug reports, tests, documentation improvements, and focused code changes are
welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md), run `make test-all`, and
include the relevant test or documentation update with your change.

## License

MIT. See [`LICENSE`](LICENSE).
