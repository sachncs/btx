# Phase 10 — Delete `TxSerializer` / `TxRbf` / `TxSighash` facades (priority)

## Goal
Remove the three facade classes that wrap `Tx` and forward to module-level functions. Promote the wrapped operations into direct methods on `Tx`.

**Status**: COMPLETE — all tasks verified in the current tree.

## Notes
- This phase is marked priority per your direct feedback: these three facades are the clearest examples of unnecessary wrapper classes.
- The deleted `tx_services.py` contained ~200 lines; the net LOC delta is heavily negative.
