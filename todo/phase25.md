# Phase 25 — Regenerate build artefacts

## Goal
Regenerate `btx.egg-info/` and `uv.lock` to reflect the new package name.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- Verified: `btx.egg-info/` exists with `PKG-INFO` (`Name: btx`), `entry_points.txt` (`btx = btx.cli:main`), and `top_level.txt` (`btx`). `pyproject.toml` declares `name = "btx"`. `uv lock --check` succeeds and `uv.lock` lists the root package as `btx`.
- These artefacts are auto-generated; if anything in source conflicts with the metadata, the build will fail with a clear error.
