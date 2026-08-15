# Phase 02 — Update `pyproject.toml`

## Goal
Update the package metadata in `pyproject.toml` to reflect the new package name `btx`, new CLI entry-point, new GitHub URLs, and the new internal path globs used by ruff.

## Context
Depends on Phase 01. No Python source changes yet. After this phase, `pyproject.toml` is consistent with the new package name but Python source still references `bitcoin`.

## Tasks

### Task 02.1 — Update project name
**Acceptance Criteria:**
- `grep -n '^name = ' pyproject.toml` returns `name = "btx"`
- No occurrence of `name = "bitcoin"` remains

**Steps:**
1. Read `pyproject.toml` line 6
2. Change `"bitcoin"` to `"btx"`

### Task 02.2 — Update project description
**Acceptance Criteria:**
- The description on line 8 (or current equivalent) either no longer contains the word `bitcoin` as a package reference, or the phrase is rephrased to mention `btx`

**Steps:**
1. Read line 8
2. If the description uses the package name, rephrase to use `btx`
3. If it describes what the library does without naming the package, leave it

### Task 02.3 — Update keywords list
**Acceptance Criteria:**
- `grep -n 'keywords' pyproject.toml` shows a list containing both `btx` and `bitcoin`

**Steps:**
1. Read line 14
2. Replace `keywords = ["bitcoin", ...]` with `keywords = ["btx", "bitcoin", ...]`

### Task 02.4 — Update project URLs
**Acceptance Criteria:**
- `grep -n 'sachncs/bitcoin' pyproject.toml` returns no matches
- `grep -n 'sachncs/btx' pyproject.toml` shows the new repo path on lines 29-33

**Steps:**
1. Read lines 29-33
2. Replace every `https://github.com/sachncs/bitcoin` with `https://github.com/sachncs/btx`

### Task 02.5 — Update optional-dependencies self-reference
**Acceptance Criteria:**
- Line 38 reads `all = ["btx[coincurve,dev]"]`

**Steps:**
1. Read line 38
2. Change `bitcoin[coincurve,dev]` to `btx[coincurve,dev]`

### Task 02.6 — Update CLI script entry-point
**Acceptance Criteria:**
- Line 41 reads `btx = "btx.cli:main"`

**Steps:**
1. Read line 41
2. Change both occurrences of `bitcoin` to `btx`

### Task 02.7 — Update setuptools package finder glob
**Acceptance Criteria:**
- Line 47 reads `include = ["btx*"]`

**Steps:**
1. Read line 47
2. Change `["bitcoin*"]` to `["btx*"]`

### Task 02.8 — Update ruff per-file-ignores paths
**Acceptance Criteria:**
- `grep -n 'bitcoin/' pyproject.toml` returns no matches
- Lines 67-69 and 72 reference `btx/curve/...`, `btx/signature/...`, `btx/psbt/...`

**Steps:**
1. Read lines 67-72
2. Change `bitcoin/curve/dispatch.py` to `btx/curve/dispatch.py`
3. Change `bitcoin/signature/schnorr.py` to `btx/signature/schnorr.py`
4. Change `bitcoin/signature/signer.py` to `btx/signature/signer.py`
5. Change `bitcoin/psbt/parser.py` to `btx/psbt/parser.py`

## End-of-Phase Verification
- `grep -c 'bitcoin' pyproject.toml` returns 0 except for the keyword entry (which keeps `bitcoin` as a generic cryptocurrency keyword alongside `btx`)
- All sections reference `btx` consistently

## Notes
- After this phase, `pip install -e .` will install `btx`, but Python imports will still fail until Phase 03 rewrites the source.
- The keyword list deliberately keeps `bitcoin` so that PyPI searches for "bitcoin" still surface the package; we add `btx` as the primary keyword.