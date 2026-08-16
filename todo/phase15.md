# Phase 15 — Add `BaseExtractor` ABC (revised per Issue C9)

## Goal
Collapse the 5 parallel extractor classes (`LegacyExtractor`, `P2WPKHExtractor`, `P2WSHExtractor`, `P2SHSegWitExtractor`, `TaprootExtractor`) into subclasses of a new `BaseExtractor` ABC. Convert their staticmethods into instance methods.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- This is a public API break: callers using the old static-method convention must instantiate.
- The benefit is a uniform interface and the ability to add state to extractors later (e.g. caching).
