# Phase 14 — Convert `ScriptChunk` (revised per Issue C6)

## Goal
Convert `ScriptChunk` to a `NamedTuple` (immutable) since the mutation audit found no callers that mutate it.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- Decision recorded: no caller assigns to `chunk.opcode` or `chunk.data` after construction, so `ScriptChunk` was converted to a `NamedTuple` (immutable, simpler).
- The redundant `__slots__` was removed (`NamedTuple` provides it automatically).
