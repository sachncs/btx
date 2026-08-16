# Phase 21 — Google-style docstring sweep

## Goal
Add or improve docstrings at ~20 sites to bring them to Google-style compliance.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The bug in `is_valid_leaf_version` was a documentation-only fix; the code was correct.
- Verified: all five concrete extractors (`LegacyExtractor`, `P2WPKHExtractor`, `P2WSHExtractor`, `P2SHSegWitExtractor`, `TaprootExtractor`) have Google-style docstrings on `extract()`, and `LibsecpBackend.__init__` documents `Raises: ImportError`.
