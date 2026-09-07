# Phase 16 — Add `SighashScheme` ABC (revised per Issue C5)

## Goal
Introduce a `SighashScheme` ABC with three concrete subclasses (Legacy, Segwit, Taproot). Replace the byte-prefix `if/else` in `compute_sighash` with a polymorphic dispatch table. Taproot becomes reachable through `compute_sighash` for the first time.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- Taproot sighash was previously unreachable through `compute_sighash` (Issue C5). This phase fixes that gap by adding the prefix detection.
- The dispatch table may need careful validation against BIP-340/341/342 to ensure all script types route correctly.
- Implementation detail (verified): `btx/sighash/taproot.py` defines `LEAF_VERSION_TAPSCRIPT = 0xC0` and `TAPROOT_SCRIPT_PATH_PREFIXES: tuple[int, ...] = (LEAF_VERSION_TAPSCRIPT,)`. `btx/signature/extraction/helpers.py` dispatches via `SCHEME_BY_PREFIX: dict[int, SighashScheme] = {0x00: SegwitSighash()}` plus a separate leaf-version check for Taproot; there are no private helpers or underscore names. `TaprootSighash.compute` derives the `tapleaf_hash` from the script code (tagged hash `"TapLeaf"` over `LEAF_VERSION_TAPSCRIPT ‖ varint(len) ‖ script_code`).
- `tests/test_sighash_full.py` has `TestComputeSighashDispatch` covering taproot/segwit/legacy dispatch.
