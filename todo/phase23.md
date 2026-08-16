# Phase 23 — CLI new features

## Goal
Add four new CLI commands that wrap existing library functions: `btx sign`, `btx verify`, `btx recover`, `btx parse-script`.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- `sign` / `verify` / `recover` operate on a 32-byte message hash, **not** transaction inputs (see the note in 23.1). The CHANGELOG 0.5.0 entry documents these semantics.
- Decision: keep message-hash semantics. Transaction-level signing is available via the `btx.signature.sign_tx_input` Python API; the CLI docstring documents this explicitly.
- `parse-script` is registered via `@app.command(name="parse-script")`.
