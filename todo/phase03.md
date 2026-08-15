# Phase 03 — Bulk Python source rename

## Goal
Mechanically rewrite every `from bitcoin.X` and `import bitcoin` to use `btx` instead. This is the single largest phase by file count.

## Context
Depends on Phase 02. After this phase, `python -c "import btx"` succeeds, but the runtime string literals (CLI name, logger name, env var, USER_AGENT, version banner) still say `bitcoin`. Those are addressed in Phase 04.

## Tasks

### Task 03.1 — Bulk rename in `btx/**/*.py` source files
**Acceptance Criteria:**
- `grep -rE '\bbitcoin\b' btx/ --include='*.py'` returns no matches
- Every Python file under `btx/` that previously imported `bitcoin` now imports `btx`
- `python -c "import btx"` exits 0

**Steps:**
1. From the repository root, run:
   ```bash
   grep -rlE '\bbitcoin\b' btx/ --include='*.py' | tee /tmp/phase03_source_files.txt
   ```
2. For each file in the list, perform an in-place word-boundary substitution:
   ```bash
   find btx/ -name '*.py' -exec sed -i '' -E 's/\bbitcoin\b/btx/g' {} +
   ```
3. Verify with a fresh grep that the count is zero
4. Verify `python -c "import btx"` works

**Exclusions (must NOT be renamed):**
- `bitcoin-cli` (Bitcoin Core RPC tool, referenced in CLI help text)
- Capitalized `Bitcoin` (the cryptocurrency, referenced in docstrings as a generic concept)
- The exception class `BitcoinError` — rename handled in Phase 05, not here

### Task 03.2 — Bulk rename in `tests/**/*.py`
**Acceptance Criteria:**
- `grep -rE '\bbitcoin\b' tests/ --include='*.py'` returns no matches except for `bitcoin-cli` and capital `Bitcoin`
- All `from bitcoin.X` imports in tests now read `from btx.X`

**Steps:**
1. Find all test files:
   ```bash
   grep -rlE '\bbitcoin\b' tests/ --include='*.py'
   ```
2. Apply the same substitution:
   ```bash
   find tests/ -name '*.py' -exec sed -i '' -E 's/\bbitcoin\b/btx/g' {} +
   ```
3. Verify zero matches except excluded strings

**Caveat (from Issue C1 in the plan):**
- `tests/test_attack.py:26` has a module-level `__sign` helper. After Phase 19 renames it to `sign`, it would shadow `btx.signature.sign`. Defer the rename to Phase 19 and verify no shadowing collision at that time.

### Task 03.3 — Bulk rename in `docs/source/conf.py`
**Acceptance Criteria:**
- `grep -E '\bbitcoin\b' docs/source/conf.py` returns no matches
- `docs/source/conf.py` uses `import btx` and `project = "btx"`

**Steps:**
1. Apply the substitution:
   ```bash
   sed -i '' -E 's/\bbitcoin\b/btx/g' docs/source/conf.py
   ```
2. Verify

## End-of-Phase Verification
- `python -c "import btx"` exits 0
- `python -c "import btx.curve; import btx.signature; import btx.transaction; import btx.psbt; import btx.script"` all succeed
- `grep -rE '\bbitcoin\b' btx/ tests/ docs/source/conf.py --include='*.py'` returns no matches except for the intentional exclusions (exception class renamed later in Phase 05)

## Notes
- The `sed` substitution uses `\b...\b` word boundaries to avoid touching `bitcoin-cli`, `bitcoins`, or capital `Bitcoin`.
- File-level integrity (line counts, etc.) is preserved because this is a pure string substitution.
- If a file has line endings that confuse `sed`, fall back to Python: `python3 -c "import re, pathlib; [pathlib.Path(p).write_text(re.sub(r'\\bbitcoin\\b', 'btx', pathlib.Path(p).read_text())) for p in pathlib.Path('btx').rglob('*.py')]"`.