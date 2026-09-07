# Phase 20 — Duplicated `HASH_BYTE_LENGTH`

## Goal
Eliminate the duplicate `HASH_BYTE_LENGTH = 32` constant that appears in both `btx/signature/check.py` and `btx/signature/signer.py`.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The alternative from the plan was chosen: `HASH_BYTE_LENGTH` now lives once in `btx/encoding/hasher.py` (where the hash functions are defined) and is imported by both `btx/signature/check.py` and `btx/signature/signer.py`.
