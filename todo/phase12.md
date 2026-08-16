# Phase 12 — Simplify `BlockstreamProvider` / `MempoolSpaceProvider`

## Goal
Replace the two 0-method classes (whose only payload is `BASE_URL`) with module-level constants and an updated `BaseBlockchainProvider` factory that takes the URL as a constructor argument.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- This change makes provider selection explicit at construction time, which is more discoverable than implicit class hierarchy.
- The `_tx_hex_path`, `_tx_json_path` etc. attributes that were deleted in Phase 19 are replaced by string-formatting on `self.base_url` directly.
