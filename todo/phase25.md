# Phase 25 — Regenerate build artefacts

## Goal
Regenerate `btx.egg-info/` and `uv.lock` to reflect the new package name.

## Context
Depends on Phases 02 and 24. After this phase, build artefacts are consistent with the source.

## Tasks

### Task 25.1 — Remove old `btx.egg-info/` if present
**Acceptance Criteria:**
- `ls btx.egg-info/` fails (directory removed)

**Steps:**
1. `rm -rf btx.egg-info/`

### Task 25.2 — Run `python -m build`
**Acceptance Criteria:**
- `python -m build` exits 0
- `ls btx.egg-info/` succeeds and contains:
  - `PKG-INFO` with `Name: btx`
  - `entry_points.txt` with `btx = btx.cli:main`
  - `top_level.txt` with `btx`

**Steps:**
1. `python -m build`

### Task 25.3 — Run `uv lock`
**Acceptance Criteria:**
- `uv lock` exits 0
- `uv.lock` shows the package as `btx` (not `bitcoin`)

**Steps:**
1. `uv lock`

## End-of-Phase Verification
- `cat btx.egg-info/PKG-INFO | head -3` shows `Name: btx`
- `grep '^name = ' pyproject.toml` matches the egg-info name
- `uv lock --check` succeeds

## Notes
- These artefacts are auto-generated; if anything in source conflicts with the metadata, the build will fail with a clear error.