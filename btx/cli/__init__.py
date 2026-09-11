# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Command-line interface for the btx package.

Re-exports the Typer :data:`app`, the :func:`main` console-script
entry point, and the small :func:`parse_input_values` helper used by
the ``extract`` command.  The actual command implementations live in
:mod:`btx.cli.app`.

Commands exposed by the CLI:

- ``decode`` – parse a raw transaction and emit JSON/CSV/text.
- ``extract`` – extract signatures from a transaction.
- ``linearize`` – extract and sort signatures.
- ``broadcast`` – broadcast a raw transaction via a configured
  provider.
- ``health`` – run health checks and print a JSON status report.
- ``schema`` – print the JSON Schema for an output format.
- ``sign`` – sign a 32-byte message hash with a private key.
- ``verify`` – verify an ECDSA signature.
- ``recover`` – recover the public key from a signature.
- ``parse-script`` – parse and decompile a Bitcoin script.
- ``version`` – print the installed package version.

The CLI is registered as the ``btx`` console script by the
project's ``pyproject.toml`` (``[project.scripts]``).
"""

from btx.cli.app import app, main, parse_input_values

__all__ = [
    "app",
    "main",
    "parse_input_values",
]
