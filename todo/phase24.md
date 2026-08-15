# Phase 24 — Markdown / RST / JSON / GitHub updates

## Goal
Update all documentation, schema, and CI configuration files to use the new package name `btx`.

## Context
Depends on Phase 03. After this phase, no documentation refers to the package as `bitcoin`.

## Tasks

### Task 24.1 — `README.md`
**Acceptance Criteria:**
- All 54 occurrences of `bitcoin` as a package name are replaced with `btx`
- `bitcoin-cli` references (Bitcoin Core RPC) are preserved
- `github.com/bitcoin/bips/...` URLs are preserved

**Steps:**
1. Read the file
2. Apply word-boundary substitutions: `sed -i '' -E 's/\bbitcoin\b/btx/g' README.md`
3. Manually verify preserved exceptions

### Task 24.2 — `CHANGELOG.md` (per Issue M7)
**Acceptance Criteria:**
- A new 0.5.0 entry is added at the top documenting the rename
- 0.4.0 historical entries remain unchanged
- `BitcoinError` mention at line 157 remains unchanged (historical record)

**Steps:**
1. Add the 0.5.0 entry per Phase 27's text

### Task 24.3 — `CONTRIBUTING.md`
**Acceptance Criteria:**
- 10 references to `bitcoin` updated to `btx`

**Steps:**
1. Read the file
2. Apply substitutions

### Task 24.4 — `SECURITY.md`
**Acceptance Criteria:**
- 3 references updated

### Task 24.5 — `docs/API.md`
**Acceptance Criteria:**
- 48 module references updated to `btx.X`
- `btx.BtxError` replaces `btx.BitcoinError` (per Phase 05)

### Task 24.6 — `docs/getting-started.md`
**Acceptance Criteria:**
- 23 references updated

### Task 24.7 — `docs/faq.md`
**Acceptance Criteria:**
- 21 references updated
- `BITCOIN_LOG_LEVEL` mentioned in faq updated to `BTX_LOG_LEVEL` (with backward-compat note per Phase 04)

### Task 24.8 — `docs/MODULES.md`
**Acceptance Criteria:**
- 16 references updated
- Exception section header uses `BtxError`

### Task 24.9 — `docs/source/api.rst`
**Acceptance Criteria:**
- 14 `automodule:: btx.X` directives

### Task 24.10 — `docs/DATA_FLOW.md`
**Acceptance Criteria:**
- 6 references updated

### Task 24.11 — `docs/TESTING.md`
**Acceptance Criteria:**
- 5 references updated, including `--cov=btx`

### Task 24.12 — `docs/source/conf.py` (per Issue M4)
**Acceptance Criteria:**
- `project = "btx"`
- `import btx` (after the rename)
- `release = btx.__version__`

**Steps:**
1. Apply substitutions
2. Verify `cd docs && make html` succeeds

### Task 24.13 — `docs/CONFIGURATION.md`
**Acceptance Criteria:**
- 4 references updated

### Task 24.14 — `docs/schemas/health.json`
**Acceptance Criteria:**
- 3 references updated, including `$id` → `github.com/sachncs/btx`

### Task 24.15 — `docs/schemas/extraction.json`
**Acceptance Criteria:**
- 2 references updated, including `$id`

### Task 24.16 — `docs/BENCHMARKING.md`
**Acceptance Criteria:**
- 2 references updated

### Task 24.17 — `docs/source/index.rst`
**Acceptance Criteria:**
- Title is `Welcome to btx's documentation!`

### Task 24.18 — `docs/ARCHITECTURE.md`
**Acceptance Criteria:**
- 1 reference updated

### Task 24.19 — `.github/workflows/ci.yml`
**Acceptance Criteria:**
- 5 lines reference `btx/` and `--cov=btx`

### Task 24.20 — `.github/workflows/release.yml`
**Acceptance Criteria:**
- 1 line references `--cov=btx`

### Task 24.21 — `.github/ISSUE_TEMPLATE/bug_report.md`
**Acceptance Criteria:**
- 2 lines reference `btx`

### Task 24.22 — `Makefile`
**Acceptance Criteria:**
- 2 lines reference `-p btx` and `--cov=btx`

## End-of-Phase Verification
- `grep -rE '\bbitcoin\b' docs/ README.md CONTRIBUTING.md SECURITY.md CHANGELOG.md .github/ Makefile --include='*.md' --include='*.rst' --include='*.yml' --include='*.json' --include='*.toml'` returns only intentional `bitcoin-cli` and `github.com/bitcoin/bips/...` references
- `cd docs && make html` succeeds

## Notes
- Historical CHANGELOG entries are immutable records; do not retroactively rewrite.