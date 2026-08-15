# Phase 00 — Pre-flight verification

## Goal
Confirm the repository is in a known-good state before any modification, so that any subsequent failure is attributable to a specific phase rather than pre-existing damage.

## Context
This is the first phase. No code changes yet. All subsequent phases depend on this baseline.

## Tasks

### Task 00.1 — Verify working tree is clean
**Acceptance Criteria:**
- `git status` reports `nothing to commit, working tree clean`
- No untracked files that would interfere with the refactor

**Steps:**
1. Run `git status`
2. If any file is modified, commit or stash it before proceeding
3. If any untracked file would be touched by the rename (e.g. `bitcoin.egg-info/`), delete it

### Task 00.2 — Verify no pending stashes
**Acceptance Criteria:**
- `git stash list` returns empty output

**Steps:**
1. Run `git stash list`
2. If non-empty, drop or apply stashes before proceeding

### Task 00.3 — Record baseline test pass count
**Acceptance Criteria:**
- `uv run pytest tests/ -q` exits with code 0
- The reported summary line shows `N passed` — record `N`

**Steps:**
1. Run `uv run pytest tests/ -q 2>&1 | tail -5`
2. Save the pass count for later comparison

### Task 00.4 — Record baseline coverage
**Acceptance Criteria:**
- `uv run pytest tests/ --cov=btx --cov-report=term --cov-fail-under=80` exits with code 0
- The TOTAL line shows coverage percentage ≥ 80%

**Steps:**
1. Run the baseline command
2. Record the coverage percentage

### Task 00.5 — Record baseline lint and type-check
**Acceptance Criteria:**
- `uv run ruff check btx/ tests/` exits 0
- `uv run ruff format --check btx/ tests/` exits 0
- `uv run mypy btx/` exits 0

**Steps:**
1. Run all three commands
2. Record results

## End-of-Phase Verification
- Working tree clean
- Stash list empty
- Test pass count recorded
- Coverage baseline recorded
- Lint and mypy baselines recorded

## Notes
- If any baseline fails, stop and investigate before starting Phase 01. A pre-existing failure will mask the impact of later phases.
- The pre-flight targets `btx/` because that is the post-rename path. Until Phase 01 completes, substitute `bitcoin/` for `btx/` in the commands.