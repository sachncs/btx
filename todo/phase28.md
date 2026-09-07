# Phase 28 — Commit

## Goal
Stage and commit all changes if the user requests it.

**Status**: ⬜ NOT DONE — opt-in. Execute only if the user explicitly asks to commit.

## Context
Depends on all prior phases being verified. This phase is opt-in — only execute if the user explicitly asks to commit.

## Tasks

### Task 28.1 — Review staged files
**Acceptance Criteria:**
- `git status` shows the expected set of files modified/added/deleted
- No untracked files except build artefacts that should be ignored

**Steps:**
1. Run `git status`
2. Review the file list against expectations

### Task 28.2 — Review diff magnitude
**Acceptance Criteria:**
- `git diff --stat` shows the expected line-count delta (~ −500 code, +250 docstrings)

**Steps:**
1. Run `git diff --stat`
2. Sanity-check the magnitude

### Task 28.3 — Stage files
**Acceptance Criteria:**
- `git diff --cached --stat` shows the same set as 28.1

**Steps:**
1. `git add .` (or selective staging if user prefers)

### Task 28.4 — Commit
**Acceptance Criteria:**
- Commit created with a message documenting the rename and refactor

**Steps:**
1. `git commit -m "Rename to btx; refactor facades to methods/ABCs; Google docstring sweep

- Package renamed from bitcoin to btx (CLI binary, env var, GitHub URLs).
- BitcoinError -> BtxError.
- Deleted facade classes: PointArithmetic, TxSerializer/TxRbf/TxSighash, JSONFormatter, BlockstreamProvider/MempoolSpaceProvider, MutableInput/Output, dead Protocols, dead exceptions, dead Settings fields.
- Added BaseExtractor and SighashScheme ABCs.
- Settings converted to frozen dataclass.
- All semi-private (_name) and double-underscore (__name) identifiers removed, except Point.__infinity.
- GENERATOR -> GENERATOR_POINT, INFINITY -> INFINITY_POINT.
- New Point methods: negate, add, double, multiply, is_on_curve, operator overloading (+, -, *, unary -).
- New Tx methods: serialize, serialize_legacy, is_opt_in_rbf, sighash_*, total_output_value, to_dict, __len__, __iter__.
- New CLI commands: sign, verify, recover, parse-script.
- Google-style docstring sweep (~20 sites)."`
2. Verify with `git log --oneline -1`

## End-of-Phase Verification
- A single commit exists with the expected message
- All files from Phase 26 are in the commit
- No secrets or credentials are included

## Notes
- If the user did not explicitly request a commit, do not execute this phase.
- If the user wants multiple commits (one per major area: rename, facade deletion, ABCs, naming, docstrings), split accordingly.