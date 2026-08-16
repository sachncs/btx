# Phase 08 — Replace `Settings` with frozen dataclass

## Goal
Convert the hand-rolled `Settings` class (with `__slots__`, internal lock, and 3 property/setter pairs) into a frozen dataclass with a single validated field.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- The frozen dataclass gives us immutability + value semantics for free. The trade-off (no built-in thread-safety) is acceptable because `Settings` is read-mostly; the only mutation path is `dataclasses.replace()`.
- If future thread-safety becomes a requirement, wrap `replace()` calls in a `threading.Lock` at the call site.
