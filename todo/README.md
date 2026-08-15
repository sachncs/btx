# Plan Overview — `bitcoin` → `btx` Refactor

This directory contains the atomic checklist for the refactor of `/Users/sachin/repo/bitcoin`. Each phase has its own file with detailed tasks and acceptance criteria.

## Phases at a glance

| Phase | File | Goal | Status |
|---|---|---|---|
| 00 | [phase00.md](phase00.md) | Pre-flight verification | ⬜ |
| 01 | [phase01.md](phase01.md) | Filesystem rename | ⬜ |
| 02 | [phase02.md](phase02.md) | Update `pyproject.toml` | ⬜ |
| 03 | [phase03.md](phase03.md) | Bulk Python source rename | ⬜ |
| 04 | [phase04.md](phase04.md) | User-facing runtime strings | ⬜ |
| 05 | [phase05.md](phase05.md) | Rename `BitcoinError` → `BtxError` | ⬜ |
| 06 | [phase06.md](phase06.md) | Rename `GENERATOR` / `INFINITY` constants | ⬜ |
| 07 | [phase07.md](phase07.md) | Delete dead code | ⬜ |
| 08 | [phase08.md](phase08.md) | Replace `Settings` with frozen dataclass | ⬜ |
| 09 | [phase09.md](phase09.md) | Delete `PointArithmetic`, expose methods on `Point` | ⬜ |
| 10 | [phase10.md](phase10.md) | Delete `TxSerializer` / `TxRbf` / `TxSighash` | ⬜ |
| 11 | [phase11.md](phase11.md) | Refactor `JSONFormatter` | ⬜ |
| 12 | [phase12.md](phase12.md) | Simplify `BlockstreamProvider` / `MempoolSpaceProvider` | ⬜ |
| 13 | [phase13.md](phase13.md) | Unify `MutableInput` / `MutableOutput` | ⬜ |
| 14 | [phase14.md](phase14.md) | Convert `ScriptChunk` | ⬜ |
| 15 | [phase15.md](phase15.md) | Add `BaseExtractor` ABC | ⬜ |
| 16 | [phase16.md](phase16.md) | Add `SighashScheme` ABC | ⬜ |
| 17 | [phase17.md](phase17.md) | Unify `BatchResult` ↔ `PsbtBatchResult` | ⬜ |
| 18 | [phase18.md](phase18.md) | Replace `sort_records(key: str)` with callable | ⬜ |
| 19 | [phase19.md](phase19.md) | Underscore-naming sweep | ⬜ |
| 20 | [phase20.md](phase20.md) | Duplicated `HASH_BYTE_LENGTH` | ⬜ |
| 21 | [phase21.md](phase21.md) | Google-style docstring sweep | ⬜ |
| 22 | [phase22.md](phase22.md) | In-scope new features for `Tx` | ⬜ |
| 23 | [phase23.md](phase23.md) | CLI new features | ⬜ |
| 24 | [phase24.md](phase24.md) | Markdown / RST / JSON / GitHub updates | ⬜ |
| 25 | [phase25.md](phase25.md) | Regenerate build artefacts | ⬜ |
| 26 | [phase26.md](phase26.md) | Verification | ⬜ |
| 27 | [phase27.md](phase27.md) | CHANGELOG entry | ⬜ |
| 28 | [phase28.md](phase28.md) | Commit (opt-in) | ⬜ |

## Naming policy

- **No** single-underscore (`_name`) identifiers anywhere
- **No** double-underscore (`__name`) identifiers anywhere
- **One exception**: `Point.__infinity` is kept as `__infinity` (mangled storage) and exposed via the `infinity` `@property`. This was your explicit Option 1 confirmation.
- `x` and `y` are direct public attributes on `Point` (no `@property`, no leading underscore)

## Public-API breaks

- `BitcoinError` → `BtxError`
- `BITCOIN_LOG_LEVEL` → `BTX_LOG_LEVEL` (with backward-compat fallback + `DeprecationWarning`)
- `pip install bitcoin` → `pip install btx`
- `bitcoin` CLI binary → `btx`
- Static-method extractors → instance-method extractors
- `Settings` interface change (now a frozen dataclass)
- `Record.vin` / `Record.sig` aliases removed

## Expected outcome

- Net LOC delta: ~ −500 code, +250 docstrings
- Coverage: ≥ 80% (mitigation in Phase 26.8 if drop)
- All ruff, mypy, pytest checks pass
- 7 wrapper classes deleted
- 2 new ABCs added (`BaseExtractor`, `SighashScheme`)
- 4 new CLI commands (`sign`, `verify`, `recover`, `parse-script`)
- 2 new `Tx` methods (`to_dict`, `__len__`/`__iter__`)
- Operator overloading on `Point` (`+`, `-`, `*`, unary `-`)

## How to use this directory

1. Read `phase00.md` and run the pre-flight checks.
2. Execute each phase in order, opening the corresponding file and ticking each task.
3. After each phase, run the "End-of-Phase Verification" section.
4. If verification fails, return to the relevant phase and fix before moving on.
5. After Phase 26 (full verification), update CHANGELOG (Phase 27).
6. Phase 28 is opt-in; commit only when the user explicitly requests it.

## Total

- 29 phase files (phase00.md through phase28.md + this README)
- ~260 atomic tasks
- All with explicit acceptance criteria