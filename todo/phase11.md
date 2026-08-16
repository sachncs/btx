# Phase 11 — Refactor `JSONFormatter` (revised per Issue C3)

## Goal
Split the `JSONFormatter` class into a free function for the formatting logic and a minimal subclass of `logging.Formatter` that delegates to it. This satisfies the constraint that `logging.Formatter()` expects a format string, not a callable.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- This was identified as Issue C3 in the plan: pure free function alone won't work because `logging.Formatter(fmt=...)` expects a format *string*. The minimal subclass is the correct solution.
