# Phase 19 — Underscore-naming sweep

## Goal
Enforce the policy: no semi-private naming (`_name`) anywhere; no double-underscore (`__name`) anywhere except the explicit exception `__infinity` on `Point`. All formerly-underscored names become public.

## Context
Depends on Phase 03. After this phase, the codebase contains no `_name` or `__name` identifiers other than standard dunders and `__infinity`.

## Tasks

### Class attributes: single-underscore → public

#### Task 19.1 — `BlockstreamProvider._tx_hex_path` etc.
**Acceptance Criteria:**
- `BlockstreamProvider` class is being deleted in Phase 12; this task becomes moot once Phase 12 completes
- If Phase 12 has not yet completed, temporarily skip this task

**Steps:**
1. Confirm Phase 12 status
2. If `BlockstreamProvider` still exists, rename the 5 attributes:
   - `_tx_hex_path` → `tx_hex_path`
   - `_tx_json_path` → `tx_json_path`
   - `_utxo_script_path` → `utxo_script_path`
   - `_utxo_value_path` → `utxo_value_path`
   - `_broadcast_path` → `broadcast_path`

### Closure-local single-underscore → public

#### Task 19.2 — `_fetch_one` → `fetch_one` in `services/blockchain.py`
**Acceptance Criteria:**
- `btx/services/blockchain.py:760` defines `def fetch_one(...)` inside `batch_fetch_transactions`
- The call site at line 767 reads `fetch_one(...)`

**Steps:**
1. Rename the function definition and call site

#### Task 19.3 — `_enrich_one` → `enrich_one`
**Acceptance Criteria:**
- `btx/services/blockchain.py:801` defines `def enrich_one(...)` inside `batch_enrich_transactions`
- The call site at line 806 reads `enrich_one(...)`

**Steps:**
1. Rename

#### Task 19.4 — Second `_fetch_one` → `async_fetch_one`
**Acceptance Criteria:**
- `btx/services/blockchain.py:841` defines `def async_fetch_one(...)` (renamed to avoid collision with Task 19.2)
- The call site at line 845 reads `async_fetch_one(...)`

**Steps:**
1. Rename

#### Task 19.5 — Verify no function-name assertion collisions
**Acceptance Criteria:**
- `grep -rn 'fetch_one\|enrich_one' tests/` shows no assertion on the function name (e.g. via `__name__` or stack-trace parsing)

**Steps:**
1. Run the grep
2. Update any hits

### Double-underscore class attributes → public (except `__infinity`)

#### Task 19.6 — `TransactionBuilder.__*` → public
**Acceptance Criteria:**
- `btx/transaction/builder.py:47-50` reads:
  - `self.version: int = version`
  - `self.lock_time: int = 0`
  - `self.inputs: list[dict[str, object]] = []`
  - `self.outputs: list[dict[str, object]] = []`
- All references in lines 72, 93, 115, 128, 130, 134, 165, 175, 178 updated accordingly

**Steps:**
1. Read the file
2. Rename each occurrence

#### Task 19.7 — `Point.__x` → `x`, `Point.__y` → `y` (public direct attributes)
**Acceptance Criteria:**
- `btx/curve/point.py:149-150` reads `self.x` and `self.y`
- `btx/curve/point.py:133` `__slots__` reads `("x", "y", "__infinity")`

**Steps:**
1. Rename the slot entries
2. Rename the `__init__` assignments

#### Task 19.8 — Keep `Point.__infinity` (per your Option 1)
**Acceptance Criteria:**
- `btx/curve/point.py:151` still reads `self.__infinity: bool = True` and `self.__infinity = False`
- The slot at line 133 still includes `"__infinity"` (mangled storage)

**Steps:**
1. Make no change here

#### Task 19.9 — Delete `Point.x` and `Point.y` `@property` decorators (per Issue C2)
**Acceptance Criteria:**
- `btx/curve/point.py` no longer has `@property` for `x` or `y` (since they are now direct public attributes)
- The `@property def infinity(self)` remains (lines 175-178) because `__infinity` is still mangled

**Steps:**
1. Delete lines 165-173

#### Task 19.10 — Update all `self.__x` / `self.__y` references
**Acceptance Criteria:**
- All occurrences of `self.__x` / `self.__y` in `btx/curve/point.py` (lines 197, 199, 201, 205, 207, 211, 213, 276, 277, 292, 293) read `self.x` / `self.y`
- `self.__infinity` references remain unchanged

**Steps:**
1. Read each line
2. Rename (preserving the `__infinity` mangling)

### Module-level / closure-local double-underscore → public

#### Task 19.11 — `tests/test_attack.py:26` `__sign` → `sign`
**Acceptance Criteria:**
- `tests/test_attack.py:26` reads `def sign(...)`
- All call sites in lines 45, 46, 61, 62, 80, 81 updated

**Steps:**
1. Rename

#### Task 19.12 — Verify no shadowing (per Issue C1)
**Acceptance Criteria:**
- `grep -E '^(from|import).*\bsign\b' tests/test_attack.py` returns no matches
- If shadowing detected, rename local helper to `sign_helper` instead

**Steps:**
1. Run the grep
2. If shadowing is detected, use `sign_helper` as the new name

#### Task 19.13 — `btx/encoding/der.py:47` `__encode_int` → `encode_int`
**Acceptance Criteria:**
- `btx/encoding/der.py:47` reads `def encode_int(value: int) -> bytes:` inside `encode_der`
- The call sites at lines 62, 63 read `encode_int(r)` and `encode_int(s)`

**Steps:**
1. Rename the nested function
2. Rename the call sites

### Test class methods: double-underscore → public

#### Task 19.14 — `tests/test_extraction.py` `__make_tx` → `make_tx`
**Acceptance Criteria:**
- `tests/test_extraction.py:72, 106, 133` read `def make_tx(self, ...)`
- Call sites at lines 82, 86, 92, 116, 120, 126 updated

**Steps:**
1. Rename

#### Task 19.15 — `tests/test_extraction.py:156` `__p2tr_script_pubkey` → `p2tr_script_pubkey`
**Acceptance Criteria:**
- Line 156 reads `def p2tr_script_pubkey(self, ...) -> bytes`
- Call sites at lines 173, 180, 183 updated

**Steps:**
1. Rename

#### Task 19.16 — `tests/test_extraction.py:161` `__make_tx_with_witness` → `make_tx_with_witness`
**Acceptance Criteria:**
- Line 161 reads `def make_tx_with_witness(self, ...) -> Tx`
- Call sites at lines 192, 195, 205, 208, 215, 218 updated

**Steps:**
1. Rename

#### Task 19.17 — `tests/test_psbt_parser.py:348` `__rx` → `rx`
**Acceptance Criteria:**
- Line 348 reads `def rx(self, ...) -> bytes` (or whatever it returns)
- Call sites at lines 352, 359, 372, 380, 387, 395, 410, 427, 437, 447, 463 updated

**Steps:**
1. Rename

## End-of-Phase Verification
- `grep -rE '\b_[a-z][a-zA-Z]*\b' btx/ tests/ --include='*.py'` returns only:
  - Standard dunders (`__init__`, `__post_init__`, `__len__`, `__iter__`, `__getitem__`, `__eq__`, `__hash__`, `__repr__`, `__slots__`, `__all__`, `__version__`, `__name__`)
  - The `__infinity` references on `Point` (and references in `__eq__`, `__hash__`, `__repr__`)
  - Any standard-library or test-fixture private names that are unavoidable
- `Point` has public `x`, `y` attributes (no `@property`); `infinity` still uses `@property` due to mangled storage

## Notes
- The asymmetry on `Point` (`x`/`y` public, `__infinity` mangled) is intentional per your Option 1 confirmation.
- Phase 19 tasks that depend on Phase 12 (Task 19.1) are conditional; mark them skipped if Phase 12 has already removed the class.