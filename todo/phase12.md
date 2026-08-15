# Phase 12 — Simplify `BlockstreamProvider` / `MempoolSpaceProvider`

## Goal
Replace the two 0-method classes (whose only payload is `BASE_URL`) with module-level constants and an updated `BaseBlockchainProvider` factory that takes the URL as a constructor argument.

## Context
Depends on Phase 03. After this phase, providers are constructed by passing a URL, and the empty wrapper classes are gone.

## Tasks

### Task 12.1 — Delete `BlockstreamProvider` class
**Acceptance Criteria:**
- `grep -rn 'BlockstreamProvider' btx/ --include='*.py'` returns no matches
- `btx/services/blockchain.py` no longer defines the class

**Steps:**
1. Read `btx/services/blockchain.py:295-303`
2. Delete the class definition

### Task 12.2 — Add `BLOCKSTREAM_BASE_URL` module constant
**Acceptance Criteria:**
- `btx/services/blockchain.py` defines `BLOCKSTREAM_BASE_URL: str = "https://blockstream.info"`
- The constant is module-level and `UPPER_SNAKE_CASE`

**Steps:**
1. Add the constant at module scope (near the other `*_BASE_URL` constants)

### Task 12.3 — Delete `MempoolSpaceProvider` class
**Acceptance Criteria:**
- `grep -rn 'MempoolSpaceProvider' btx/ --include='*.py'` returns no matches

**Steps:**
1. Read `btx/services/blockchain.py:327-335`
2. Delete the class definition

### Task 12.4 — Add `MEMPOOL_SPACE_BASE_URL` module constant
**Acceptance Criteria:**
- `btx/services/blockchain.py` defines `MEMPOOL_SPACE_BASE_URL: str = "https://mempool.space"`

**Steps:**
1. Add the constant

### Task 12.5 — Update `BaseBlockchainProvider.__init__`
**Acceptance Criteria:**
- `BaseBlockchainProvider.__init__(self, base_url: str, *, network: str = "main")` accepts the URL as a constructor argument
- `BaseBlockchainProvider(BLOCKSTREAM_BASE_URL)` and `BaseBlockchainProvider(MEMPOOL_SPACE_BASE_URL)` both instantiate correctly

**Steps:**
1. Read the existing `__init__`
2. Add `base_url` parameter
3. Store as `self.base_url` (public, no underscore prefix)

### Task 12.6 — Update all call sites and tests
**Acceptance Criteria:**
- Any code that did `BlockstreamProvider()` now does `BaseBlockchainProvider(BLOCKSTREAM_BASE_URL)` (or similar)
- Any code that did `MempoolSpaceProvider()` now does `BaseBlockchainProvider(MEMPOOL_SPACE_BASE_URL)`
- All services tests pass

**Steps:**
1. Find call sites: `grep -rn 'BlockstreamProvider()\|MempoolSpaceProvider()' btx/ tests/`
2. Replace with the new factory form

## End-of-Phase Verification
- `BlockstreamProvider` and `MempoolSpaceProvider` no longer exist
- `BLOCKSTREAM_BASE_URL` and `MEMPOOL_SPACE_BASE_URL` are reachable as `btx.services.blockchain.BLOCKSTREAM_BASE_URL`
- All services tests pass

## Notes
- This change makes provider selection explicit at construction time, which is more discoverable than implicit class hierarchy.
- The `_tx_hex_path`, `_tx_json_path` etc. attributes that were deleted in Phase 19 are replaced by string-formatting on `self.base_url` directly.