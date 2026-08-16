# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
# ruff: noqa: B008  # typer uses mutable defaults intentionally
"""Typer-based CLI app — decode, extract, linearize, broadcast, health commands.

The CLI is a thin wrapper around the library's Python API.  Each
command:

1. Calls :func:`configure_logging` to enable structured (JSON) logging
   at the level selected by the ``BTX_LOG_LEVEL`` env var (the legacy
   ``BITCOIN_LOG_LEVEL`` name still works with a :class:`DeprecationWarning`).
2. Resolves the transaction hex via :func:`read_tx_hex` (either a
   positional argument or ``--input-file``).
3. Invokes the corresponding library function
   (:func:`parse_tx`, :func:`extract_signatures`, ...).
4. Formats the result as text, JSON, or CSV per the ``--format`` /
   ``--json`` / ``--csv`` flags.

Errors are caught and logged via :mod:`logging`; the process exits
with a non-zero status so shell pipelines can detect failure.

The ``main`` entry point is the function referenced by
``[project.scripts]`` in ``pyproject.toml`` — ``btx = btx.cli:main``.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import warnings
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import typer

from btx import __version__
from btx.curve import parse_public_key
from btx.encoding.hex import decode_hex, encode_hex
from btx.health import health as run_health
from btx.script import classify_script_pubkey, parse_script
from btx.services.blockchain import (
    BlockchainInfoProvider,
    blockstream_provider,
    broadcast_transaction,
    mempool_space_provider,
)
from btx.services.serializer import tx_to_json
from btx.signature import extract_signatures, linearize_signatures
from btx.signature.check import recover_public_key, verify_signature
from btx.signature.record import Record
from btx.signature.signer import sign as sign_msg
from btx.transaction import parse_tx

app = typer.Typer(name="btx")

logger = logging.getLogger("btx.cli")
LOGGING_CONFIGURED: bool = False
"""Module-level flag tracking whether :func:`configure_logging` has run.

Public so external scripts (and the test suite) can introspect the
logging initialisation state without having to parse logger
configuration.  Mutated only through :func:`configure_logging`.
"""

EXIT_OK: int = 0
EXIT_ERROR: int = 1
"""Process exit codes used by :func:`main`."""


def fail(message: str) -> typer.Exit:
    """Print *message* to stderr and return a ``typer.Exit(1)`` for ``raise``."""
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(EXIT_ERROR)


def configure_logging() -> None:
    """Configure structured (JSON) logging for the btx CLI.

    Log level is read from the ``BTX_LOG_LEVEL`` environment variable
    (default: ``WARNING``).  The legacy ``BITCOIN_LOG_LEVEL`` variable
    still works as a fallback; if it is set without ``BTX_LOG_LEVEL``,
    a :class:`DeprecationWarning` is emitted.

    Idempotent — safe to call from multiple commands.  Subsequent
    calls become no-ops once :data:`LOGGING_CONFIGURED` flips to
    ``True``.

    Side effects:
        Sets the module-level :data:`LOGGING_CONFIGURED` flag and
        installs a :class:`JsonFormatter` handler on the ``btx``
        logger.
    """
    global LOGGING_CONFIGURED
    if LOGGING_CONFIGURED:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger("btx")
    new_level = os.getenv("BTX_LOG_LEVEL")
    legacy_level = os.getenv("BITCOIN_LOG_LEVEL")
    if new_level is None and legacy_level is not None:
        warnings.warn(
            "BITCOIN_LOG_LEVEL is deprecated; use BTX_LOG_LEVEL instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        level = legacy_level
    elif new_level is None:
        level = "WARNING"
    else:
        level = new_level
    root.setLevel(level.upper())
    LOGGING_CONFIGURED = True


def format_json(record: logging.LogRecord) -> str:
    """Format a :class:`logging.LogRecord` as a JSON string.

    Produces structured log entries suitable for ingestion by log
    aggregators (ELK, Datadog, etc.).

    Args:
        record: The log record to serialize.

    Returns:
        A JSON-encoded string with the standard structured fields.
    """
    return json.dumps(
        {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        },
        default=str,
    )


class JsonFormatter(logging.Formatter):
    """Logging formatter that delegates to :func:`format_json`."""

    def format(self, record: logging.LogRecord) -> str:
        """Format *record* by delegating to :func:`format_json`."""
        return format_json(record)


def parse_input_values(value_str: str) -> list[int | None]:
    """Parse a comma-separated string of input values into integers.

    Empty entries (e.g. ``"100,,300"``) yield ``None``.

    Args:
        value_str: Comma-separated integer values (e.g. ``"100,200,300"``).

    Returns:
        A list where each entry is an ``int`` or ``None`` for empty fields.
    """
    if not value_str or value_str.strip() == "":
        return []
    result: list[int | None] = []
    for part in value_str.split(","):
        part = part.strip()
        if part == "":
            result.append(None)
        else:
            result.append(int(part))
    return result


def resolve_output_format(
    *, json_output: bool, csv_output: bool, output_format: str
) -> str:
    """Resolve the effective output format, erroring on conflicting flags."""
    if json_output and csv_output:
        typer.echo("--json and --csv are mutually exclusive", err=True)
        raise typer.Exit(EXIT_ERROR)
    if output_format != "text":
        return output_format
    if json_output:
        return "json"
    if csv_output:
        return "csv"
    return "text"


def read_tx_hex(tx_hex: str | None, input_file: Path | None) -> str:
    """Return tx hex from the positional arg or ``--input-file``.

    If both are provided ``--input-file`` wins.
    """
    if input_file is not None:
        return input_file.read_text().strip()
    if tx_hex is not None:
        return tx_hex
    fail("Either provide tx_hex as argument or use --input-file")
    raise typer.Exit(EXIT_ERROR)


def output_records(records: list[Record], fmt: str) -> None:
    """Output records (for ``extract``) in the requested format."""
    if not records:
        typer.echo("No signatures found.")
        raise typer.Exit(EXIT_OK)

    if fmt == "json":
        data = [
            {
                "txid": encode_hex(r.txid),
                "input_index": r.input_index,
                "signature": encode_hex(r.signature),
                "type": r.script_type,
                "sighash_flag": r.sighash_flag,
                "value": r.amount,
            }
            for r in records
        ]
        typer.echo(json.dumps(data, indent=2))
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            ["txid", "input_index", "signature", "type", "sighash_flag", "value"]
        )
        for r in records:
            writer.writerow(
                [
                    encode_hex(r.txid),
                    r.input_index,
                    encode_hex(r.signature),
                    r.script_type,
                    r.sighash_flag,
                    r.amount,
                ]
            )
        typer.echo(buf.getvalue().rstrip())
    else:
        for rec in records:
            typer.echo(f"txid:  {encode_hex(rec.txid)}")
            typer.echo(f"input_index: {rec.input_index}")
            typer.echo(f"signature:   {encode_hex(rec.signature)}")
            typer.echo(f"type:  {rec.script_type}")
            typer.echo(f"sighash_flag:  {rec.sighash_flag}")
            typer.echo(f"value: {rec.amount}")
            typer.echo("---")


def output_sorted_records(records: list[Record], fmt: str) -> None:
    """Output sorted/linearized records (for ``linearize``) in the requested format."""
    if not records:
        typer.echo("No signatures found.")
        raise typer.Exit(EXIT_OK)

    if fmt == "json":
        data = [
            {
                "txid": encode_hex(r.txid),
                "input_index": r.input_index,
                "signature": encode_hex(r.signature),
            }
            for r in records
        ]
        typer.echo(json.dumps(data, indent=2))
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["txid", "input_index", "signature"])
        for r in records:
            writer.writerow(
                [encode_hex(r.txid), r.input_index, encode_hex(r.signature)]
            )
        typer.echo(buf.getvalue().rstrip())
    else:
        for rec in records:
            typer.echo(
                f"{encode_hex(rec.txid)}:{rec.input_index} {encode_hex(rec.signature)}"
            )


def _decode_tx(tx_hex_resolved: str):
    """Decode a tx hex string into a :class:`Tx`.

    Args:
        tx_hex_resolved: Hex string of the transaction.

    Returns:
        The parsed ``Tx`` and the number of bytes consumed.
    """
    return parse_tx(decode_hex(tx_hex_resolved))


@app.command()
def decode(
    tx_hex: str | None = typer.Argument(None, help="Transaction hex"),
    input_file: Path | None = typer.Option(
        None, "--input-file", help="Read tx hex from file"
    ),
) -> None:
    """Decode a raw transaction and output as JSON."""
    configure_logging()
    tx, _ = _decode_tx(read_tx_hex(tx_hex, input_file))
    typer.echo(json.dumps(tx_to_json(tx), indent=2))


@app.command()
def extract(
    tx_hex: str | None = typer.Argument(None, help="Transaction hex"),
    utxo_scripts: list[str] | None = typer.Option(
        None, "--utxo-script", help="UTXO scriptPubKey (one per input)"
    ),
    utxo_values: list[int] | None = typer.Option(
        None, "--utxo-value", help="UTXO value in satoshis (one per input)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    output_format: str = typer.Option("text", "--format", help="Output format"),
    input_file: Path | None = typer.Option(
        None, "--input-file", help="Read tx hex from file"
    ),
    progress: bool = typer.Option(False, "--progress", "-p", help="Show progress dots"),
) -> None:
    """Extract ECDSA signatures from a raw transaction hex."""
    configure_logging()
    fmt = resolve_output_format(
        json_output=json_output, csv_output=csv_output, output_format=output_format
    )
    tx, _ = _decode_tx(read_tx_hex(tx_hex, input_file))

    script_pubkeys = [decode_hex(s) for s in utxo_scripts] if utxo_scripts else None

    if progress:
        typer.echo(
            f"Parsed tx with {len(tx.inputs)} inputs, {len(tx.outputs)} outputs.",
            err=True,
        )

    records = extract_signatures(tx, script_pubkeys, utxo_values)

    if progress:
        typer.echo(f" Found {len(records)} signature(s).", err=True)

    output_records(records, fmt)


@app.command()
def linearize(
    tx_hex: str | None = typer.Argument(None, help="Transaction hex"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    output_format: str = typer.Option("text", "--format", help="Output format"),
    input_file: Path | None = typer.Option(
        None, "--input-file", help="Read tx hex from file"
    ),
    progress: bool = typer.Option(False, "--progress", "-p", help="Show progress dots"),
) -> None:
    """Extract and linearize (sort) signatures from a raw transaction hex."""
    configure_logging()
    fmt = resolve_output_format(
        json_output=json_output, csv_output=csv_output, output_format=output_format
    )
    tx, _ = _decode_tx(read_tx_hex(tx_hex, input_file))

    if progress:
        typer.echo(
            f"Parsed tx with {len(tx.inputs)} inputs, {len(tx.outputs)} outputs.",
            err=True,
        )

    records = extract_signatures(tx)
    sorted_records = linearize_signatures(records)

    if progress:
        typer.echo(f" Linearized {len(sorted_records)} signature(s).", err=True)

    output_sorted_records(sorted_records, fmt)


@app.command()
def version() -> None:
    """Print the installed btx package version."""
    typer.echo(f"btx v{__version__}")


_PROVIDERS = {
    "blockstream": blockstream_provider,
    "mempool": mempool_space_provider,
    "blockchain_info": BlockchainInfoProvider,
}


@app.command()
def broadcast(
    tx_hex: str = typer.Argument(..., help="Raw transaction hex to broadcast"),
    provider_name: str = typer.Option(
        "blockstream",
        "--provider",
        help="Blockchain provider (blockstream, mempool, blockchain_info)",
    ),
    input_file: Path | None = typer.Option(
        None, "--input-file", help="Read tx hex from file"
    ),
) -> None:
    """Broadcast a raw transaction to the Bitcoin network."""
    configure_logging()
    if provider_name not in _PROVIDERS:
        fail(f"Unknown provider: {provider_name}. Choose from: {', '.join(_PROVIDERS)}")
    provider = _PROVIDERS[provider_name]()
    txid = broadcast_transaction(read_tx_hex(tx_hex, input_file), provider=provider)
    typer.echo(txid)


_SCHEMAS = {
    "extraction": "docs/schemas/extraction.json",
    "health": "docs/schemas/health.json",
}


@app.command()
def schema(
    output_type: str = typer.Argument(..., help="Schema name: extraction, health"),
) -> None:
    """Print the JSON Schema for a CLI output format."""
    configure_logging()
    rel = _SCHEMAS.get(output_type)
    if rel is None:
        fail(f"Unknown schema: {output_type}. Choose from: {', '.join(_SCHEMAS)}")
    schema_path = Path(__file__).resolve().parent.parent.parent / str(rel)
    if not schema_path.exists():
        fail(f"Schema file not found: {schema_path}")
    typer.echo(schema_path.read_text())


@app.command()
def install_completion() -> None:
    """Install shell tab-completion for bash, zsh, fish, or PowerShell."""
    configure_logging()
    typer.echo("Run the following command to enable tab-completion:")
    typer.echo("")
    typer.echo('  eval "$(btx --install-completion)"')
    typer.echo("")
    typer.echo("Or see: btx --help  (completion is auto-enabled via shell)")


@app.command()
def health() -> None:
    """Run health checks and print a JSON status report."""
    configure_logging()
    status = run_health()
    typer.echo(json.dumps(status, indent=2, default=str))
    if not status.get("curve_operation", False):
        logger.critical("health check FAILED: curve operation failed")
        raise typer.Exit(EXIT_ERROR)


@app.command(name="parse-script")
def parse_script_cmd(
    script_hex: str = typer.Argument(..., help="Script bytes as hex"),
) -> None:
    """Parse and decompile a Bitcoin script."""
    configure_logging()
    script = decode_hex(script_hex)
    chunks = parse_script(script)
    st = classify_script_pubkey(script)
    typer.echo(f"Script type: {st}")
    typer.echo(f"Chunks ({len(chunks)}):")
    for i, chunk in enumerate(chunks):
        typer.echo(f"  [{i}] opcode=0x{chunk.opcode:02x} data={chunk.data!r}")


@app.command(name="sign")
def sign_cmd(
    message_hash: str = typer.Argument(..., help="32-byte message hash as hex"),
    privkey: str = typer.Option(..., "--privkey", help="Private key as hex (32 bytes)"),
    input_file: Path | None = typer.Option(
        None, "--input-file", help="Read message hash from file"
    ),
) -> None:
    """Sign a 32-byte message hash with a private key.

    Outputs the DER-encoded signature as hex.

    NOTE: this signs an arbitrary 32-byte digest, not a transaction
    input.  For transaction-level signing workflows, use the
    ``btx.signature.sign_tx_input`` Python API directly.
    """
    configure_logging()
    msg = decode_hex(read_tx_hex(message_hash, input_file))
    if len(msg) != 32:
        fail(f"message hash must be 32 bytes, got {len(msg)}")
    d = int(privkey, 16)
    typer.echo(sign_msg(msg, d).hex())


@app.command()
def verify(
    message_hash: str = typer.Argument(..., help="32-byte message hash as hex"),
    pubkey: str = typer.Option(..., "--pubkey", help="Public key as hex"),
    signature: str = typer.Option(..., "--signature", help="DER signature as hex"),
    input_file: Path | None = typer.Option(
        None, "--input-file", help="Read message hash from file"
    ),
) -> None:
    """Verify an ECDSA signature against a public key for a message hash."""
    configure_logging()
    msg = decode_hex(read_tx_hex(message_hash, input_file))
    pk = parse_public_key(decode_hex(pubkey))
    ok = verify_signature(msg, decode_hex(signature), pk)
    typer.echo("valid" if ok else "invalid")
    if not ok:
        raise typer.Exit(EXIT_ERROR)


@app.command()
def recover(
    message_hash: str = typer.Argument(..., help="32-byte message hash as hex"),
    signature: str = typer.Option(..., "--signature", help="DER signature as hex"),
    recovery_flag: int = typer.Option(
        27, "--recid", help="Recovery flag (27..30 compressed, 31..34 uncompressed)"
    ),
    input_file: Path | None = typer.Option(
        None, "--input-file", help="Read message hash from file"
    ),
) -> None:
    """Recover the public key from an ECDSA signature."""
    configure_logging()
    msg = decode_hex(read_tx_hex(message_hash, input_file))
    pk = recover_public_key(msg, decode_hex(signature), recovery_flag)
    if pk is None or pk.infinity:
        fail("recovery failed")
    typer.echo(encode_hex(pk.serialize(compressed=True)))


def main(args: Sequence[str] | None = None) -> int:
    """CLI entry point — delegates to the Typer app.

    Args:
        args: Optional argument list.  If ``None``, uses ``sys.argv``.

    Returns:
        ``0`` on success, ``1`` on unhandled error.
    """
    configure_logging()
    try:
        if args is not None:
            app(args)
        else:
            app()
    except typer.Exit as exc:
        return getattr(exc, "exit_code", 0) or 0
    except (ValueError, OSError, KeyError, IndexError) as exc:
        logger.critical("Unhandled CLI error: %s", exc, exc_info=True)
        typer.echo(f"Unexpected error: {exc}", err=True)
        return EXIT_ERROR
    return EXIT_OK
