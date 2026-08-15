# Phase 16 — Add `SighashScheme` ABC (revised per Issue C5)

## Goal
Introduce a `SighashScheme` ABC with three concrete subclasses (Legacy, Segwit, Taproot). Replace the byte-prefix `if/else` in `compute_sighash` with a polymorphic dispatch table. Taproot becomes reachable through `compute_sighash` for the first time.

## Context
Depends on Phase 03. The revision (per Issue C5) requires adding a Taproot-prefix detection path that previously did not exist.

## Tasks

### Task 16.1 — Define `SighashScheme` ABC
**Acceptance Criteria:**
- `btx/sighash/__init__.py` defines:
  ```python
  class SighashScheme(ABC):
      @abstractmethod
      def compute(self, tx, vin, script_code, value, sighash_type) -> bytes: ...
  ```

**Steps:**
1. Add the imports and the class

### Task 16.2 — Create `LegacySighash` subclass
**Acceptance Criteria:**
- `btx/sighash/legacy.py` defines `LegacySighash(SighashScheme)` whose `compute` calls the existing `sighash_legacy` function

**Steps:**
1. Add the subclass wrapping the existing function

### Task 16.3 — Create `SegwitSighash` subclass
**Acceptance Criteria:**
- `btx/sighash/segwit.py` defines `SegwitSighash(SighashScheme)` whose `compute` calls `sighash_segwit`

**Steps:**
1. Add the subclass

### Task 16.4 — Create `TaprootSighash` subclass
**Acceptance Criteria:**
- `btx/sighash/taproot.py` defines `TaprootSighash(SighashScheme)` whose `compute` calls `sighash_taproot`

**Steps:**
1. Add the subclass

### Task 16.5 — Define Taproot script-path prefixes
**Acceptance Criteria:**
- `btx/sighash/taproot.py` defines `TAPROOT_SCRIPT_PATH_PREFIXES: tuple[int, ...]` containing the valid BIP-342 leaf-version bytes (0xC0, 0xC1, etc., or whatever is documented in BIP-342)
- These prefixes are used to detect Taproot script-path spends from the script_code

**Steps:**
1. Verify against BIP-342
2. Add the tuple

### Task 16.6 — Replace byte-prefix dispatch with `SCHEME_BY_PREFIX`
**Acceptance Criteria:**
- `btx/signature/extraction/helpers.py:109-137` no longer contains `if is_witness:` / `else:`
- Instead, defines:
  ```python
  SCHEME_BY_PREFIX: dict[int, SighashScheme] = {
      0x00: SegwitSighash(),  # P2WPKH (0x0014...) and P2WSH (0x0020...)
      # Taproot detection via TAPROOT_SCRIPT_PATH_PREFIXES handled separately
  }
  ```
- Taproot script-path detection happens via the leaf-version byte (the first byte of script_code in taproot context)

**Steps:**
1. Read the existing `compute_sighash`
2. Replace the dispatch logic
3. Verify that legacy, segwit, and taproot script-path all dispatch correctly

### Task 16.7 — Update tests for taproot dispatch
**Acceptance Criteria:**
- `tests/test_sighash_full.py` includes a test that exercises `compute_sighash` on a taproot input and gets a valid sighash
- All sighash tests pass

**Steps:**
1. Add a taproot test case
2. Run `uv run pytest tests/test_sighash_full.py -v`

## End-of-Phase Verification
- 3 concrete sighash schemes share `SighashScheme` base
- `compute_sighash` correctly dispatches to legacy, segwit, and taproot
- All sighash tests pass

## Notes
- Taproot sighash was previously unreachable through `compute_sighash` (Issue C5). This phase fixes that gap by adding the prefix detection.
- The dispatch table may need careful validation against BIP-340/341/342 to ensure all script types route correctly.