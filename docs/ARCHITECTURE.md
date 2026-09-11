# Architecture

## High-Level Design

11 packages with strict one-way dependency. No package imports from
a package at the same or deeper level in a way that creates a cycle.

```
field  →  curve  →  encoding  →  script  →  transaction  →  sighash  →  signature  →  psbt
                                                                                   │
                                                                                   ▼
                                                                              services  →  cli
                                                                    descriptor ─────▲
```

## Package Boundaries

| Package | Submodules | Owns |
|---------|------------|------|
| `field` | `__init__.py`, `modular.py`, `sqrt.py` | Modular inverse, field square root |
| `curve` | `__init__.py`, `params.py`, `point.py`, `operations.py`, `dispatch.py`, `libsecp256k1.py`, `backend/{base,native,libsec}.py` | Point type, affine ops, SEC encoding, pluggable backends |
| `encoding` | `__init__.py`, `hex.py`, `varint.py`, `der.py`, `sec.py`, `hasher.py` | Binary formats, DER/SEC parsing, SHA256, hash160 |
| `script` | `__init__.py`, `opcodes.py`, `parser.py`, `classifier.py`, `builder.py`, `taproot.py` | Script chunking, type classification, building, tapscript parsing |
| `transaction` | `__init__.py`, `models.py`, `parser.py`, `builder.py`, `ops.py`, `fee.py`, `rbf.py` | TxIn/TxOut structs, raw byte parsing, construction, fluent builder |
| `sighash` | `__init__.py`, `flag.py`, `legacy.py`, `segwit.py`, `taproot.py`, `scheme.py` | Sighash flag parsing, legacy/SegWit/Taproot digest |
| `signature` | `__init__.py`, `record.py`, `collection.py`, `check.py`, `attack.py`, `signer.py`, `schnorr.py`, `pipeline.py`, `extraction/{engine,helpers}.py`, `linearization/coefficients.py`, `batch_verify.py` | Record, extraction, verification, nonce-reuse attack, signing, batch processing, linearization |
| `psbt` | `__init__.py`, `models.py`, `parser.py`, `editor.py`, `extraction.py`, `pipeline.py` | PSBT structs, BIP-174 parse/serialize, fluent editing, extraction |
| `descriptor` | `__init__.py`, `compiler.py`, `analyzer.py` | Miniscript descriptor parsing, compilation, analysis |
| `services` | `__init__.py`, `serializer.py`, `blockchain.py` | Transaction serialization, blockchain data fetching |
| `cli` | `__init__.py`, `app.py` | Typer commands: `decode`, `extract`, `linearize`, `broadcast`, `health`, `schema`, `sign`, `verify`, `recover`, `parse-script`, `version` |

## Layering Rules

1. `field` — stdlib only, no internal imports
2. `curve` — imports `field` only
3. `encoding` — stdlib only
4. `script` — imports `encoding` (for opcode values), `exceptions`
5. `transaction` — imports `encoding`, `exceptions`
6. `sighash` — imports `encoding`, `transaction`, `script`, `exceptions`
7. `signature` — imports `curve`, `encoding`, `transaction`, `sighash`, `field`, `script`
8. `psbt` — imports `transaction`, `encoding`, `signature`
9. `descriptor` — imports `script`, `encoding`
10. `services` — imports `transaction`, `encoding`
11. `cli` — imports `signature`, `encoding`, `transaction`, `services`, `script`

## Public Interface

The public API surface is defined in `btx/__init__.py` with an explicit
`__all__`. Every public symbol is re-exported from the top-level `btx`
package.

## Backend Architecture

Curve operations support pluggable backends:

- **NativeBackend** — pure Python implementation (always available, default)
- **LibsecpBackend** — wraps `coincurve` (libsecp256k1 C bindings, optional)

`set_backend(instance)` installs a `CurveBackend` instance;
`resolve_backend()` returns the active one. All point operations
(`add`, `double`, `multiply`, `negate`) dispatch through
`curve/dispatch.py`.

The `BTX_DEFAULT_BACKEND` environment variable selects the default
backend at import time. `settings.default_backend` records that
selection.

## Key Design Decisions

- **Frozen dataclasses with slots** for all value objects (`Point`, `Tx`, `Record`, `Psbt`, etc.)
- **Exhaustive type annotations** — `mypy` strict-ish clean across all source files
- **`__init__.py` is the public API surface** — submodules are implementation details
- **models.py is the zero-import leaf** — `transaction/models.py` imports nothing from the package, avoiding circular deps
- **Pure Python first, C optional** — core library has zero runtime dependencies (only `typer` for CLI)

