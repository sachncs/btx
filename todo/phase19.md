# Phase 19 — Underscore-naming sweep

## Goal
Enforce the policy: no semi-private naming (`_name`) anywhere; no double-underscore (`__name`) anywhere except the explicit exception `__infinity` on `Point`. All formerly-underscored names become public.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The asymmetry on `Point` (`x`/`y` public, `__infinity` mangled) is intentional per your Option 1 confirmation.
- Task 19.1 (BlockstreamProvider `_tx_hex_path` etc.) was moot — Phase 12 deleted the class before this phase's conditional rename applied.
