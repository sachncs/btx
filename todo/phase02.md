# Phase 02 — Update `pyproject.toml`

## Goal
Update the package metadata in `pyproject.toml` to reflect the new package name `btx`, new CLI entry-point, new GitHub URLs, and the new internal path globs used by ruff.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The keyword list deliberately keeps `bitcoin` so that PyPI searches for "bitcoin" still surface the package; `btx` is added as the primary keyword.
