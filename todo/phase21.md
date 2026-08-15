# Phase 21 — Google-style docstring sweep

## Goal
Add or improve docstrings at ~20 sites to bring them to Google-style compliance.

## Context
Depends on Phase 03. The codebase is already 81% Google-compliant; this phase covers the gaps.

## Tasks

### Public plugin methods

#### Task 21.1 — `BaseExtractor.can_handle()` docstring
**Acceptance Criteria:**
- The abstract method has a Google-style docstring with `Args:` (script_type, is_segwit) and `Returns:`

**Steps:**
1. Add the docstring on the abstract method declaration

#### Task 21.2 — `BaseExtractor.extract()` docstring
**Acceptance Criteria:**
- The abstract method has a Google-style docstring with `Args:` (tx, vin, txin, script_pubkey, value) and `Returns:` (list[Record])

#### Task 21.3 — `LegacyExtractor.extract()` docstring
**Acceptance Criteria:**
- Has a full Google-style docstring matching the abstract base

#### Task 21.4 — `P2WPKHExtractor.extract()` docstring
**Acceptance Criteria:**
- Same as Task 21.3

#### Task 21.5 — `P2WSHExtractor.extract()` docstring
**Acceptance Criteria:**
- Same as Task 21.3

#### Task 21.6 — `P2SHSegWitExtractor.extract()` docstring
**Acceptance Criteria:**
- Same as Task 21.3

#### Task 21.7 — `TaprootExtractor.extract()` docstring
**Acceptance Criteria:**
- Same as Task 21.3

### Internal init/repr

#### Task 21.8 — `LibsecpBackend.__init__` docstring
**Acceptance Criteria:**
- `btx/curve/backend/libsec.py:46` has a Google-style docstring with `Raises:` (`ImportError` if `coincurve` not installed)

**Steps:**
1. Add the docstring

#### Task 21.9 — `GenericHttpProvider.__init__` docstring (biggest gap)
**Acceptance Criteria:**
- `btx/services/blockchain.py:356` has a Google-style docstring with `Args:` listing all 11 kwargs (`base_url`, `tx_hex_path`, `tx_json_path`, etc.)

**Steps:**
1. Add the docstring

#### Task 21.10 — `tx_json_url()` docstring
**Acceptance Criteria:**
- `btx/services/blockchain.py:323` has a one-line Google docstring

#### Task 21.11 — `do_get_transaction_hex()` docstring
**Acceptance Criteria:**
- `btx/services/blockchain.py:379` has a Google docstring with `Args:`, `Returns:`, and `Raises:`

#### Task 21.12 — `get_utxo_script_pubkey()` docstring
**Acceptance Criteria:**
- `btx/services/blockchain.py:387` has a Google docstring

#### Task 21.13 — `get_utxo_value()` docstring
**Acceptance Criteria:**
- `btx/services/blockchain.py:402` has a Google docstring

#### Task 21.14 — `broadcast_url()` docstring
**Acceptance Criteria:**
- `btx/services/blockchain.py:417` has a Google docstring

#### Task 21.15 — `is_shutdown_requested()` docstring
**Acceptance Criteria:**
- `btx/signature/pipeline.py:74` has a docstring explaining that it reads the module-level flag under a lock

**Steps:**
1. Add the docstring

#### Task 21.16 — `OutPoint.__post_init__` docstring
**Acceptance Criteria:**
- `btx/transaction/models.py:48` has a brief docstring with `Raises:` (ValueError if txid is not 32 bytes or vout is negative)

#### Task 21.17 — `TxIn.__post_init__` docstring
**Acceptance Criteria:**
- `btx/transaction/models.py:71` has a brief docstring

#### Task 21.18 — `TxOut.__post_init__` docstring
**Acceptance Criteria:**
- `btx/transaction/models.py:88` has a brief docstring

#### Task 21.19 — `Witness.__len__` docstring
**Acceptance Criteria:**
- `btx/transaction/models.py:106` has a one-line docstring: `"""Return the number of witness items."""`

### Docstring bug

#### Task 21.20 — Fix `is_valid_leaf_version` contradiction
**Acceptance Criteria:**
- `btx/script/taproot.py:162` docstring says "bit 0 clear (even)" (matching the predicate `(version & 0x01) == 0x00` which is correct per BIP-342)
- No reference to "bit 0 set" or "odd"

**Steps:**
1. Read the docstring
2. Replace "bit 0 set (odd)" with "bit 0 clear (even)"

## End-of-Phase Verification
- All 20 sites have Google-style docstrings
- `ruff check` passes (docstring-convention rules)
- Tests pass

## Notes
- The bug in `is_valid_leaf_version` is a documentation-only fix; the code is correct.