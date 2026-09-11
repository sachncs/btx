# Changelog

All notable changes to this project will be documented in this file.

## 0.5.0 - 2026-06-05

This 0.5.0 release bundles the package rename to `btx` with an
architecture cleanup that drops every backward-compatibility shim,
alias, and thin wrapper, plus the additions / fixes shipped in
the 0.5.0 minor.

### Breaking changes

- **Package renamed**: `bitcoin` → `btx`. All imports become `import btx`.
  The `pip install bitcoin` command becomes `pip install btx`. The CLI
  binary becomes `btx`. The package directory is now `btx/` and the
  distribution name is `btx`.
- **Exception renamed**: `BitcoinError` → `BtxError`. Catch clauses
  must update.
- **Env var renamed**: `BITCOIN_LOG_LEVEL` → `BTX_LOG_LEVEL`. The
  old name still works with a `DeprecationWarning`.
- **CLI**: legacy static-method extractor convention removed. The five
  built-in extractors (`LegacyExtractor`, `P2WPKHExtractor`, etc.)
  are now instances, not classes. Code that called
  `LegacyExtractor.can_handle(...)` must construct an instance:
  `LegacyExtractor().can_handle(...)`.
- **Settings** is now a frozen dataclass; mutation requires
  `dataclasses.replace()`. Removed dead fields `strict_mode` and
  `max_extraction_inputs`.
- **`BatchResult` fields renamed**: `records` → `items`,
  `total_transactions` → `total`. Field `psbts` → `items` on the
  unified batch type.
- **`SignatureCollection.sort_records(key: str)` → `key: Callable`**:
  the string attribute lookup was replaced with a proper callable.
- **`GENERATOR` → `GENERATOR_POINT`** and **`INFINITY` → `INFINITY_POINT`**
  (PEP 8: module-level constants must be `UPPER_SNAKE_CASE`).
- **Dead Protocols removed**: `BlockchainProvider(Protocol)` and the
  `ExtractorPlugin` Protocol were removed (replaced with concrete
  ABCs `BaseExtractor` and `SighashScheme`).
- **Removed signature helpers (alias shims)**:
  `verify_sig` → use `verify_signature`,
  `verify_schnorr_sig` → use `verify_schnorr_signature`,
  `batch_verify` → use `verify_all` (the misnomer has been retired).
- **Removed transaction module shims**:
  `make_tx` / `build_transaction` (entire module
  `btx/transaction/tx.py` deleted) → use `tx_from_dict` (dict-based)
  or `TransactionBuilder` (fluent).
- **Removed PSBT surface**: `parse_psbt_impl` is now private;
  use the public `parse_psbt`.

### Removed (dead code)

- `NotInvertible`, `PointError`, `ParsingError`, `NoNonceReuseError`
  exceptions (never raised).
- `Settings.strict_mode`, `Settings.max_extraction_inputs`.
- `Record.vin`, `Record.sig` aliases (kept as canonical names).
- `collect_info(has_timelock, has_hash_lock)` unused parameters.
- `MutableInput` / `MutableOutput` shadow dataclasses.
- `btx/transaction/tx_services.py` (TxSerializer/TxRbf/TxSighash facades).
- `BlockstreamProvider`, `MempoolSpaceProvider` 0-method classes.
- Import-time auto-registration of extraction plugins (replaced by `register_builtin_extractors()`).
- `RuntimeError` from CLI exception handlers (typer.Exit is a RuntimeError; was being swallowed).
- `.pre-commit-config.yaml` (pre-commit checks moved to CI).
- `tests/helpers.py` (replaced by `conftest.py`).
- Dead exception classes from `exceptions.py`.
- `set_backend` setter (use the `BTX_DEFAULT_BACKEND` env var or
  install a backend at construction time).
- `emit_script`, `sorted_unique`, `split_args`, `*_BASE_URL`
  constants and most `services.*` async/batch fetchers.

### Architecture changes

- `Tx` is now a pure data carrier; every algorithm that used to
  live as a method forwarder now lives as a module-level function
  in `btx/transaction/ops.py`.
- `btx/curve/batch.py` deleted; `multi_multiply`, `batch_validate`,
  `batch_normalize` had zero callers.
- `dispatch.resolve_backend()` caches the resolved default; no
  longer constructs a fresh `NativeBackend()` per call.
- `BTX_DEFAULT_BACKEND` environment variable is now wired through
  `btx/settings.py`; the canonical route to select libsecp is the
  env var.
- `SighashScheme` ABC and its three concrete strategies live in
  `btx/sighash/scheme.py` so the package `__init__` is a clean
  facade.
- Tapleaf hash has a single canonical implementation
  (`btx/sighash/scheme.tapleaf_hash`).
- Plugin registry deleted; replaced with an explicit
  `BUILTIN_EXTRACTORS` tuple whose order encodes priority
  (Legacy last as fallback).
- Backend selection: env var or `set_backend` instance hook;
  the legacy `settings.default_backend = "string"` assignment
  no longer exists.
- Settings is frozen; use `dataclasses.replace(settings, ...)` to
  derive a customised copy.

### Added

- `health()`, `check_backend()`, `check_imports()` library health introspection.
- `recover_from_related_nonces()` for exploiting nonces with known
  offset (`k2 = k1 + delta`).
- `batch_extract_from_file()` for reading tx hexes from a file.
- `lift_x()` for BIP-340 x-only public key lifting.
- `MempoolSpaceProvider()` blockchain data provider.
- `classify_script_sig()` and `P2PK` / `MULTISIG` script type constants.
- `build_p2pkh()`, `build_p2sh()`, `build_p2wpkh()`, `build_p2wsh()`,
  `build_p2tr()` script builders.
- `is_opt_in_rbf()` and `has_sequence_lock()` transaction utilities.
- Dependabot configuration for automated dependency updates.
- Mainnet signature extraction test vectors (`test_mainnet_vectors.py`).
- Concurrency tests (`test_concurrency.py`).
- Shared test fixtures in `conftest.py`.

### Changed

- `Settings` is now thread-safe with `threading.Lock`.
- Fixed-base multiplication optimization for generator point
  (4-bit window table).
- TXID validation added to all `BaseBlockchainProvider` subclasses.
- Sighash modules refactored for cleaner implementation.
- `sign()` and `sign_tx_input()` wipe sensitive values from stack
  frames after signing.
- HMAC-DRBG bounded retry limit (raises after 1000 attempts instead
  of infinite loop).
- Type annotations modernized (PEP 604: `str | None` instead of
  `Optional[str]`).
- Extraction engine logging improved (warning instead of debug on
  skipped signatures).
- `Record` dataclass enhancements.
- Backend dispatch validates scalar non-negativity and reduces
  modulo `CURVE_ORDER`.
- Taproot sighash computation edge cases hardened.

### Fixed

- `health.py` silent exception swallow — now logs `logger.warning`
  with module name and error.
- Mypy: `coincurve` import-not-found errors suppressed per-module override.
- Ruff naming violations: `# noqa` annotations for crypto-standard
  uppercase variables.
- `setup.sh` no longer crashes when `.pre-commit-config.yaml` is absent.
- Sighash legacy calculation for edge cases.
- Various minor bug fixes across extraction, PSBT parsing, and signing.

### Security

- `pip-audit` scans for known CVEs in CI and release workflows.
- PyPI publish uses Test PyPI dry-run before production push.
- Build provenance attestation generated for every release.
- Pip version pinned in `setup.sh` to mitigate supply-chain risk.

## [Unreleased]

Public-API promotion and docstring expansion landed after the
0.5.0 release.

### Added
- Public re-exports from package root: `DescriptorError`, `DescriptorInfo`,
  `DescriptorNode`, `ESTIMATED_SATISFACTION`, `collect_info`,
  `collect_keys`, `contains_op`, `emit_script`, `estimate_satisfaction`,
  `sorted_unique`, `split_args`, `parse_psbt_impl`, `parse_psbt_worker`,
  `process_psbt_batch`, `process_psbt_batch_with`, `CURVE_A`, `CURVE_B`.
- Public `BUILTINS_REGISTERED` flag in `btx.signature.extraction.engine`
  and public `registry` dict in `btx.signature.extraction.plugins`
  so callers can introspect plugin registration state.
- Public `LOGGING_CONFIGURED` flag in `btx.cli.app`.
- `CURVE_A = 0` and `CURVE_B = 7` constants exported from
  `btx.curve.params` (and the package root) so the documented curve
  equation `y² = x³ + a·x + b (mod p)` is fully representable in Python.
- Comprehensive module-, class-, and method-level docstrings (Google
  style) across every module, including algorithm background sections
  (RFC-6979 deterministic nonces, BIP-143 amortised hashes, BIP-340
  tagged-hash discrimination, BIP-341 key-path vs. script-path spends,
  Straus's interleaved-window multi-exponentiation, RFC-6979 HMAC-DRBG,
  Template-Method provider pattern).
- Inline comments for the nonce-reuse `d = α·k − β` algebra, the
  BIP-341 hash-type byte, the BIP-32 keypath parser, the SegWit
  witness-stack parser, and the multi-level matching key-path code.

### Changed
- Promoted semi-private (`__name`) helpers to plain public names:
  - `btx.descriptor.analyzer`: `__ESTIMATED_SATISFACTION` →
    `ESTIMATED_SATISFACTION`, `__collect_info` → `collect_info`,
    `__contains_op` → `contains_op`, `__estimate_satisfaction` →
    `estimate_satisfaction`, `__sorted_unique` → `sorted_unique`,
    `__collect_keys` → `collect_keys`.
  - `btx.descriptor.compiler`: `__split_args` → `split_args`,
    `__emit_script` → `emit_script`.
  - `btx.psbt.parser`: `__parse_psbt_impl` → `parse_psbt_impl`.
  - `btx.psbt.pipeline`: `__parse_psbt_worker` → `parse_psbt_worker`.
  - `btx.signature.pipeline`: `__process_single_worker` →
    `process_single_worker`.
  - `btx.signature.extraction.engine`: `__BUILTINS_REGISTERED` →
    `BUILTINS_REGISTERED`.
  - `btx.signature.extraction.plugins`: `__registry` → `registry`.
  - `btx.cli.app`: `__LOGGING_CONFIGURED` → `LOGGING_CONFIGURED`.
- Each renamed helper received a full Google-style docstring explaining
  intent, parameters, return values, side effects, and edge cases.
- Expanded module-level docstrings across every package
  (`btx.curve`, `btx.encoding`, `btx.field`,
  `btx.script`, `btx.sighash`, `btx.transaction`,
  `btx.signature`, `btx.descriptor`, `btx.psbt`,
  `btx.services`, `btx.cli`) with architecture overviews,
  design notes, and references to BIPs and RFCs.
- `services/blockchain.py`: `async_enrich_transaction` and
  `async_batch_fetch_transactions` now carry full Google-style
  docstrings matching their sync counterparts.
- `btx/__init__.py`: rewritten as a layered package overview with
  deduplicated, alphabetised `__all__` listing the public symbols.
- `verify_sig` → use `verify_signature`
- `verify_schnorr_sig` → use `verify_schnorr_signature`
- `batch_verify` → use `verify_all` (the misnomer has been retired)

**Removed transaction module shims**:
- `make_tx` / `build_transaction` (entire module
  `btx/transaction/tx.py` deleted) → use `tx_from_dict` (dict-based)
  or `TransactionBuilder` (fluent).
- `Tx.is_segwit`, `Tx.total_output_value`, `Tx.serialize`,
  `Tx.serialize_legacy`, `Tx.to_json`, `Tx.to_dict`, `Tx.txid`,
  `Tx.wtxid`, `Tx.is_opt_in_rbf`, `Tx.has_sequence_lock`,
  `Tx.sighash_legacy`, `Tx.sighash_segwit`, `Tx.sighash_taproot`
  (all method-forwarders removed; `Tx` is now a pure data carrier)
  → use the module-level functions in `btx.transaction`:
  `is_segwit`, `total_output_value`, `serialize_tx`,
  `serialize_legacy_tx`, `tx_to_json`, `to_dict`, `txid`, `wtxid`,
  `is_opt_in_rbf`, `has_sequence_lock`, `sighash_*`.

**Removed PSBT surface**:
- `parse_psbt_impl` (now `_parse_psbt_impl`, private) → use
  `parse_psbt`.
- `parse_psbt_worker` (no longer exported) → use `process_psbt_batch`
  which manages the executor internally.

**Removed descriptor shim**:
- `collect_keys` (alias of `collect_info`) → use `collect_info`.

**Removed dispatch / internal helpers**:
- `determine_script_type`'s unused `script_sig` parameter.
- The 1-entry `SCHEME_BY_PREFIX` dispatch table; `compute_sighash`
  now uses an explicit if/elif.

**Removed top-level re-exports** (`btx/__init__.py` was shrunk
from ~190 symbols to ~88): all `OP_*` opcode constants, the
`MULTISIG`/`NON_STANDARD`/`TIMELOCK` script-type strings,
`OPCODES_BY_NAME`/`OPCODES_BY_VALUE` lookup dicts, the
`TaprootControlBlock`/`TaprootScriptPath` dataclasses, every
script helper except the canonical `build_p2*`, `parse_script`,
`classify_script_pubkey`, all the `make_*_p2pkh_script` and
`is_*_script` helpers, the `SIGHASH_*_ANYONECANPAY` flag
combinations except `SIGHASH_ANYONECANPAY` itself,
`require_sighash_flag`, `sighash_name`, `SIGHASH_MASK`,
`SIGHASH_NAMES`, the `ESTIMATED_SATISFACTION` table and
descriptor-tree `emit_script`/`sorted_unique`/`split_args`
helpers, the `*_BASE_URL` constants and most `services.*`
async/batch fetchers, `merge_records`, the `set_backend`
setter, the `GENERATOR_X`/`GENERATOR_Y`/`CURVE_A`/`CURVE_B`
internal constants.  All remain importable from their respective
submodules.

### Architecture changes

- **Tx is now a pure data model.** Only `__len__` and `__iter__`
  dunders remain. Every algorithm that used to live as a method
  forwarder now lives as a module-level function in
  `btx/transaction/ops.py`.
- **Curve field helpers.** `field.pow_mod` (wrapper around `pow`)
  and `field.validate_non_negative` deleted (no production
  callers).
- **Encoding dead code.** `btx/encoding/binary.py` deleted
  entirely (`bytes_to_int`/`int_to_bytes` were builtin renames;
  `iter_bytes`/`read_exactly` were unused and `read_exactly`
  duplicated `transaction/parser._take`).
- **Curve batch helpers.** `btx/curve/batch.py` deleted
  (`multi_multiply`, `batch_validate`, `batch_normalize` had zero
  callers).
- **Backend caching.** `dispatch.resolve_backend()` no longer
  constructs a fresh `NativeBackend()` per call; the resolved
  default is cached.
- **Backend selection.** `BTX_DEFAULT_BACKEND` environment variable
  is now wired through `btx/settings.py`; the canonical route to
  select libsecp is the env var, not the previously-non-functional
  `settings.default_backend = "libsecp"` assignment.
- **Sighash scheme module.** `SighashScheme` ABC and its three
  concrete strategies were moved out of `btx/sighash/__init__.py`
  into a dedicated `btx/sighash/scheme.py` so the package
  `__init__` is a clean facade.
- **Tapleaf hash.** The BIP-341 `TapLeaf` tagged-hash computation
  has a single canonical implementation
  (`btx/sighash/scheme.tapleaf_hash`);
  `btx/script/taproot.compute_tapleaf_hash` is a thin wrapper.
- **Plugin registry deleted.** `btx/signature/extraction/plugins.py`
  (`registry`, `register_plugin`, `unregister_plugin`,
  `get_plugin`, `list_plugins`) removed; replaced with an explicit
  `BUILTIN_EXTRACTORS` tuple whose order encodes priority
  (Legacy last as fallback).

### Notes
- Bumped to 0.5.0. No backward-compat aliases are retained; this
  release hardens the API surface.

## [0.4.0] - 2026-05-31

### Added
- `TransactionBuilder` and `tx_from_dict` for programmatic transaction construction.
- `PsbtEditor` for fluent PSBT construction and editing.
- `sign()` and `sign_tx_input()` for deterministic ECDSA signing (RFC 6979).
- `batch_extract()` and `correlate_across_transactions()` for multi-tx processing with `ThreadPoolExecutor`.
- `BlockstreamProvider`, `BlockchainInfoProvider` for fetching blockchain data (optional runtime dep).
- `enrich_transaction()` to attach UTXO metadata to transactions.
- `TaprootScriptPath` type and `parse_taproot_witness_stack()` for taproot witness parsing.
- `get_x_only_pubkey()` to extract x-only pubkey from P2TR outputs.
- `classify_detailed()` with `is_op_return()`, `is_bare_multisig()`, `has_timelocks()`.
- `OP_RETURN`, `MULTISIG`, `TIMELOCK` script type constants.
- `ExtractorPlugin` registry for custom extraction logic.
- Structured logging with per-type telemetry in extraction engine.
- CLI output formats: `--json`, `--csv`, `--format`, `--input-file`.
- `settings.default_backend`, `settings.max_extraction_inputs` configuration.
- `UnsupportedScriptPathError` exception for unsupported script features.
- Hypothesis stateful testing via `RuleBasedStateMachine`.

### Changed
- CLI entry point renamed from `secp` to `btx`.
- `Settings` singleton replaces old file/env-var `Config`.
- All exception classes now inherit from `BitcoinError(ValueError)`.
- `verify_sig` uses constant-time comparison (`hmac.compare_digest`).
- DoS limits enforced: `MAX_INPUTS`, `MAX_OUTPUTS`, `MAX_WITNESS_ITEMS`.

### Removed
- Dead code: `btx/compat.py`, `btx/signature/memzero.py`.
- Duplicate exception classes from `exceptions.py` (canonical versions in `attack.py`).
- `InvalidSecp256k1PointError` (never raised).
- Dead `logger` imports and definitions from `dispatch.py`, `blockchain.py`, `attack.py`.

## [0.3.0] - 2026-05-30

### Added
- `scripts/taproot.py` with taproot witness stack parsing.
- P2TR public key extraction from scriptPubKey.
- PSBT editing via `psbt/editor.py`.
- Batch extraction pipeline (`signature/pipeline.py`).
- Deterministic signing (`signature/signer.py`).
- Blockchain data providers (`services/blockchain.py`).
- Structured logging in extraction engine.

### Changed
- Script classification split into `classifier.py` and `taproot.py`.
- `backend/` subpackage with base, native, and libsec backends.
- `signature/extraction/` subpackage with plugins.

### Fixed
- `_extract_taproot` uses real x-only pubkey from scriptPubKey (not `INFINITY`).
- Backend dispatch consumes `settings.default_backend`.

## [0.2.0] - 2026-05-29

### Added
- CI/CD: GitHub Actions workflow (lint, typecheck, test on 3.12/3.13).
- `py.typed` marker for PEP 561 typed-package distribution.
- Property-based tests for ECC operations and field arithmetic.
- Docstrings on all public functions.
- MIT `LICENSE` and `CONTRIBUTING.md`.
- Optional `coincurve` backend for accelerated curve operations.

### Changed
- Package renamed from `secp` to `btx`.
- `models.py` is now a zero-import leaf module (no circular import risk).
- Codebase restructured into 10 packages with strict layering.

## [0.1.0] - 2026-05-20

### Added
- Initial release: tx parsing, signature extraction, ECC operations, CLI.
- DER signature parsing, sighash computation, secp256k1 arithmetic.
- Linear coefficient derivation and verification.
- Nonce reuse detection and private key recovery.
