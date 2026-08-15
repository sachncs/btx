# Phase 23 — CLI new features

## Goal
Add four new CLI commands that wrap existing library functions: `btx sign`, `btx verify`, `btx recover`, `btx parse-script`.

## Context
Depends on Phase 03 and Phase 04 (CLI naming already migrated). After this phase, the CLI is a complete wrapper around the public API.

## Tasks

### Task 23.1 — Add `btx sign` command (per F11)
**Acceptance Criteria:**
- `btx sign <tx-hex> --privkey <hex>` signs each input with the given private key and prints the signed tx
- The command reuses `configure_logging` and `read_tx_hex` like other commands

**Steps:**
1. Read `btx/cli/app.py` to find the existing command pattern
2. Add a new `sign` Typer command
3. Wire it up to call `btx.signature.sign_tx_input` per input

### Task 23.2 — Add `btx verify` command (per F12)
**Acceptance Criteria:**
- `btx verify <tx-hex>` extracts and verifies all signatures
- Prints a per-input verification report

**Steps:**
1. Add a `verify` command
2. Wire it up to call `btx.signature.verify_all`

### Task 23.3 — Add `btx recover` command (per F13)
**Acceptance Criteria:**
- `btx recover <tx-hex>` attempts public-key recovery on each signature
- Prints recovered keys

**Steps:**
1. Add a `recover` command
2. Wire it up to call `btx.signature.recover_public_key`

### Task 23.4 — Add `btx parse-script <hex>` command (per F14)
**Acceptance Criteria:**
- `btx parse-script <hex>` parses the script bytes and prints decompiled opcodes and pushes
- Output includes script type if recognizable

**Steps:**
1. Add a `parse-script` command
2. Wire it up to call `btx.script.parse_script` and `classify_script_pubkey`

### Task 23.5 — Verify auto-completion (per F15)
**Acceptance Criteria:**
- `btx --help` lists all commands including the new four
- Typer's auto-completion metadata is correct

**Steps:**
1. Run `btx --help`
2. Confirm new commands are listed

## End-of-Phase Verification
- All four new commands work
- `btx --help` lists them
- Tests pass

## Notes
- These commands make the CLI a more complete interface, reducing the need for users to write Python scripts.