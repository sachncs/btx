# Phase 04 — User-facing runtime strings

## Goal
Replace the runtime string literals that user-facing tools see: CLI app name, logger names, env var, version banner, USER_AGENT header, test assertions on CLI output.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The env var fallback (`BITCOIN_LOG_LEVEL` still works with a `DeprecationWarning`) is critical for downstream users with existing CI/CD pipelines that set `BITCOIN_LOG_LEVEL`.
