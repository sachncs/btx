# Phase 01 — Filesystem rename

## Goal
Rename the top-level package directory from `bitcoin/` to `btx/` and clean up the egg-info directory.

## Context
Depends on Phase 00. After this phase, every file path that used `bitcoin/` now uses `btx/`. Subsequent phases operate on the renamed directory.

## Tasks

### Task 01.1 — Rename the `bitcoin/` directory to `btx/`
**Acceptance Criteria:**
- `ls btx/__init__.py` succeeds
- `ls bitcoin/` fails (no such directory)
- All subdirectories of the original `bitcoin/` are now under `btx/`
- File content is unchanged (this is a pure rename)

**Steps:**
1. `mv bitcoin/ btx/`
2. Verify with `ls btx/` that the package layout is intact
3. Verify with `ls bitcoin/` that the old directory is gone

### Task 01.2 — Delete `bitcoin.egg-info/`
**Acceptance Criteria:**
- `ls bitcoin.egg-info/` fails
- `ls btx.egg-info/` also fails (will be regenerated in Phase 25)

**Steps:**
1. `rm -rf bitcoin.egg-info/`
2. Verify with `ls bitcoin.egg-info/` that the directory is gone

### Task 01.3 — Update `cleanup.sh` reference
**Acceptance Criteria:**
- `grep -n 'egg-info' cleanup.sh` shows `btx.egg-info/`, not `bitcoin.egg-info/`

**Steps:**
1. Read `cleanup.sh`
2. Change `rm -rf bitcoin.egg-info/` to `rm -rf btx.egg-info/`
3. Verify the change

## End-of-Phase Verification
- Directory tree has `btx/` where `bitcoin/` used to be
- No `bitcoin.egg-info/` exists
- `cleanup.sh` is consistent with the new name

## Notes
- Do not run `import btx` yet — imports will fail until Phase 02 and Phase 03 update `pyproject.toml` and Python source.
- Do not delete `btx.egg-info/` if it already exists; leave it for Phase 25 to regenerate.