# Phase 26 — Verification

## Goal
Confirm every phase has been completed correctly by running the full verification suite.

## Context
All checks now pass, including the ruff format check (26.5) and the Astro
documentation build (26.9).

## Remaining Tasks

### Task 26.5 — `ruff format` clean — COMPLETE
**Acceptance Criteria:**
- `uv run ruff format --check btx/ tests/` exits 0

**Current state:**
- Passes. `uv run ruff format btx/signature/extraction/helpers.py btx/transaction/parser.py` applied; `uv run ruff format --check btx/ tests/` now exits 0 (105 files already formatted).

### Task 26.9 — Astro documentation build — COMPLETE
**Acceptance Criteria:**
- `cd site && npm run check` exits 0
- `cd site && npm run build && npm run verify` exits 0

**Current state:**
- Passes. Astro is the only documentation build system. The generated site
  contains the standalone documentation pages under `/btx/docs/`; repository
  Markdown is not loaded at runtime.

## Notes
- This phase is the gate. Do not commit until every task passes.
- Verified-complete tasks in the current tree include the formatting, lint,
  type-check, test, coverage, CLI, health, import, and sighash dispatch gates.
  The exact output is intentionally validated by the current `make test-all`
  run rather than copied into this historical phase note.
