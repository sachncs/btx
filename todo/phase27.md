# Phase 27 — CHANGELOG entry

## Goal
Add a new top-level entry to `CHANGELOG.md` documenting the 0.5.0 release.

## Context
Depends on all prior phases. After this phase, users can read what changed.

## Tasks

### Task 27.1 — Add the 0.5.0 entry at the top of CHANGELOG.md
**Acceptance Criteria:**
- A new section appears above the existing 0.4.0 entry
- The section header reads `## 0.5.0` (or whatever the next version is)
- The body lists the major changes

**Steps:**
1. Read `CHANGELOG.md`
2. Insert the following at the top:

```markdown
## 0.5.0

### Breaking changes
- **Package renamed**: `bitcoin` → `btx`. All imports become `import btx`. The `pip install bitcoin` command becomes `pip install btx`. The CLI binary becomes `btx`.
- **Exception renamed**: `BitcoinError` → `BtxError`. Catch clauses must update.
- **Env var renamed**: `BITCOIN_LOG_LEVEL` → `BTX_LOG_LEVEL`. The old name still works with a `DeprecationWarning`.
- **GitHub repo**: `github.com/sachncs/bitcoin` → `github.com/sachncs/btx`.

### Removed (dead code)
- `NotInvertible`, `PointError`, `ParsingError` exceptions (never raised).
- `NoNonceReuseError` exception (never raised).
- `dead Protocols`: `BlockchainProvider(Protocol)`, `ExtractorPlugin(Protocol)` (never subclassed).
- `Settings.strict_mode`, `Settings.max_extraction_inputs` (never read).
- `Record.vin`, `Record.sig` alias properties (use canonical names).
- `collect_info(has_timelock, has_hash_lock)` unused parameters.

### Refactors
- `Settings` is now a frozen dataclass; mutations via `dataclasses.replace()`.
- `PointArithmetic` facade deleted; methods `negate()`, `add()`, `double()`, `multiply()`, `is_on_curve()` are now on `Point` directly. Operator overloading added: `p1 + p2`, `k * p`, `-p`.
- `TxSerializer`, `TxRbf`, `TxSighash` facades deleted; `Tx` gained methods `serialize()`, `serialize_legacy()`, `is_opt_in_rbf()`, `sighash_legacy/segwit/taproot()`, `total_output_value()`, `to_dict()`, `__len__()`, `__iter__()`.
- `JSONFormatter` split into free function `format_json()` + minimal `JsonFormatter` subclass.
- `BlockstreamProvider`, `MempoolSpaceProvider` deleted; use `BaseBlockchainProvider(BLOCKSTREAM_BASE_URL)` etc.
- `MutableInput` / `MutableOutput` deleted; `PsbtEditor` edits via `dataclasses.replace()` on the frozen `PsbtInput`/`PsbtOutput`.
- `BatchResult` / `PsbtBatchResult` unified as `BatchResult[T]`.
- `ScriptChunk` cleaned up (decision per code: either `NamedTuple` or stripped-down dataclass).
- `SignatureCollection.sort_records(key: str)` → `key: Callable[[Record], Any]`.

### New polymorphism
- `BaseExtractor(ABC)` with 5 subclasses: `LegacyExtractor`, `P2WPKHExtractor`, `P2WSHExtractor`, `P2SHSegWitExtractor`, `TaprootExtractor`. Each is now an instance (was static methods).
- `SighashScheme(ABC)` with 3 subclasses: `LegacySighash`, `SegwitSighash`, `TaprootSighash`. `compute_sighash` is now polymorphic; Taproot script-path dispatch is reachable.

### Naming convention
- All single-underscore (`_name`) and double-underscore (`__name`) identifiers removed, except `Point.__infinity` (kept as the explicit asymmetry).
- `GENERATOR` → `GENERATOR_POINT`, `INFINITY` → `INFINITY_POINT` (PEP 8 compliant).

### New CLI commands
- `btx sign`, `btx verify`, `btx recover`, `btx parse-script`.

### New docs and tests
- Sphinx docs build cleanly.
- New unit tests for `Point` methods, `Tx` methods, `BaseExtractor`/`SighashScheme` dispatch, and new CLI commands.

## 0.4.0
... (existing content unchanged)
```

## End-of-Phase Verification
- `CHANGELOG.md` has the new 0.5.0 entry at the top
- The historical 0.4.0 content is unchanged

## Notes
- Historical CHANGELOG entries are immutable; do not retroactively edit.