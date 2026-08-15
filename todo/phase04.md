# Phase 04 — User-facing runtime strings

## Goal
Replace the runtime string literals that user-facing tools see: CLI app name, logger names, env var, version banner, USER_AGENT header, test assertions on CLI output.

## Context
Depends on Phase 03. After this phase, the CLI binary is fully `btx`-branded and no user-visible output mentions `bitcoin`. The `BitcoinError` exception class is still present (handled in Phase 05).

## Tasks

### Task 04.1 — Fix `importlib.metadata.version()` lookup
**Acceptance Criteria:**
- `btx/health.py:89` reads `importlib.metadata.version("btx")`
- `btx health` runs without `PackageNotFoundError` after `pip install -e .`

**Steps:**
1. Read `btx/health.py` line 89
2. Confirm the string literal is `"btx"` (Phase 03 should have caught this)
3. Run `btx health` and verify the JSON output contains `"version": "0.4.0"`

### Task 04.2 — Update health-check submodule list
**Acceptance Criteria:**
- `btx/health.py:59-68` lists `"btx.curve"`, `"btx.encoding"`, ..., `"btx.cli"` (not `bitcoin.X`)
- `btx health` reports `true` for every module

**Steps:**
1. Read lines 59-68
2. Confirm each entry uses the `btx.` prefix
3. Run `btx health` and verify all 10 modules report `true`

### Task 04.3 — Update Typer app name
**Acceptance Criteria:**
- `btx/cli/app.py:44` reads `typer.Typer(name="btx")`
- `btx --help` shows the program name as `btx`

**Steps:**
1. Read line 44
2. Confirm the literal is `"btx"`
3. Run `btx --help` and verify the program name

### Task 04.4 — Update CLI logger name
**Acceptance Criteria:**
- `btx/cli/app.py:46` reads `logging.getLogger("btx.cli")`
- A log message emitted via this logger is prefixed with `btx.cli` (verify with `BTX_LOG_LEVEL=DEBUG btx health` and inspect stderr)

**Steps:**
1. Read line 46
2. Confirm the literal

### Task 04.5 — Update root logger name and env var (with backward-compat fallback per Issue M1)
**Acceptance Criteria:**
- `btx/cli/app.py:94` reads `logging.getLogger("btx")`
- `btx/cli/app.py:95` reads the new env var with a backward-compat fallback to the old one
- `BTX_LOG_LEVEL=DEBUG btx health` increases log verbosity
- `BITCOIN_LOG_LEVEL=DEBUG btx health` also works AND emits a `DeprecationWarning` to stderr

**Steps:**
1. Read line 94; confirm literal is `"btx"`
2. Read line 95; rewrite to:
   ```python
   level = (
       os.getenv("BTX_LOG_LEVEL")
       or os.getenv("BITCOIN_LOG_LEVEL")
       or "WARNING"
   ).upper()
   ```
3. Add a `DeprecationWarning` immediately after, when the old var is detected:
   ```python
   if os.getenv("BITCOIN_LOG_LEVEL") and not os.getenv("BTX_LOG_LEVEL"):
       warnings.warn(
           "BITCOIN_LOG_LEVEL is deprecated; use BTX_LOG_LEVEL instead.",
           DeprecationWarning,
           stacklevel=2,
       )
   ```
4. Add `import warnings` at the top of the file if not already present
5. Run both `BTX_LOG_LEVEL=DEBUG` and `BITCOIN_LOG_LEVEL=DEBUG` and confirm the warning fires for the second

### Task 04.6 — Update docstring references to env var
**Acceptance Criteria:**
- `btx/cli/app.py:10, 77` (and any other docstring occurrences) reference `BTX_LOG_LEVEL`

**Steps:**
1. `grep -n BITCOIN_LOG_LEVEL btx/cli/app.py`
2. Replace any remaining hits with `BTX_LOG_LEVEL`

### Task 04.7 — Update CLI version banner
**Acceptance Criteria:**
- `btx/cli/app.py:351` emits `f"btx v{ver}"`
- `btx version` prints `btx v0.4.0`

**Steps:**
1. Read line 351
2. Confirm the f-string prefix is `btx`

### Task 04.8 — Update CLI completion snippet
**Acceptance Criteria:**
- `btx/cli/app.py:433` prints `eval "$(btx --install-completion)"`
- `btx/cli/app.py:435` prints `btx --help`

**Steps:**
1. Read lines 433 and 435
2. Replace any remaining `bitcoin` references with `btx`

### Task 04.9 — Update USER_AGENT header
**Acceptance Criteria:**
- `btx/services/blockchain.py:58` reads `USER_AGENT = "btx/0.4.0 (+https://github.com/sachncs/btx)"`
- An HTTP request to a provider includes this header (verify by capturing with a mock or by sniffing)

**Steps:**
1. Read line 58
2. Replace with the new string

### Task 04.10 — Update CLI test assertion
**Acceptance Criteria:**
- `tests/test_cli.py:20` asserts `"btx v" in result.stdout`
- The test passes

**Steps:**
1. Read the file
2. Replace `"bitcoin v"` with `"btx v"`

### Task 04.11 — Update health test mock paths
**Acceptance Criteria:**
- `tests/test_health.py:65, 74, 97-104, 111` all use `"btx.X.Y"` paths
- Tests pass

**Steps:**
1. Open the file
2. Replace each mock target string with the `btx.` prefix

### Task 04.12 — Update CLI coverage test mock paths
**Acceptance Criteria:**
- `tests/test_cli_coverage.py:57, 155, 186, 195, 202, 222, 246, 267, 297, 320, 330` all use `"btx.cli.app.X"` paths
- Tests pass

**Steps:**
1. Open the file
2. Replace each mock target string with the `btx.cli.app.` prefix

### Task 04.13 — Update coverage test mock paths
**Acceptance Criteria:**
- `tests/test_coverage_new.py:995, 1009, 1018` all use `"btx.services.blockchain.urlopen"`
- Tests pass

**Steps:**
1. Open the file
2. Replace `"bitcoin.services.blockchain.urlopen"` with `"btx.services.blockchain.urlopen"`

## End-of-Phase Verification
- `grep -rE '"bitcoin' btx/ tests/ --include='*.py'` returns no matches
- `btx --help` shows the new program name
- `btx health` runs successfully and reports `btx` branding
- `BITCOIN_LOG_LEVEL=DEBUG btx health` still works AND prints a deprecation warning
- `BTX_LOG_LEVEL=DEBUG btx health` works without warning

## Notes
- Phase 03's mechanical sed should have caught most of these. This phase is the safety net for any string literal that wasn't a Python identifier (and thus escaped the `\bbitcoin\b` regex in places where it appeared inside double quotes already — actually it would have caught those too, so this phase is mostly verification).
- The env var fallback is critical for downstream users with existing CI/CD pipelines that set `BITCOIN_LOG_LEVEL`.