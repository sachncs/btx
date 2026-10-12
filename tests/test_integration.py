# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
"""Integration tests across the CLI, parser, and local HTTP provider boundary."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import threading
from collections.abc import Generator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import URLError

import pytest

from btx.services.blockchain import (
    GenericHttpProvider,
    async_batch_fetch_transactions,
    async_enrich_transaction,
    batch_enrich_transactions,
    batch_fetch_transactions,
    broadcast_transaction,
    enrich_transaction,
    fetch_and_extract,
    fetch_text,
    validate_http_url,
    validate_max_workers,
    validate_txid,
    validate_vout,
)
from btx.settings import Settings
from btx.transaction.fee import (
    estimate_minimum_fee,
    estimate_optimal_fee,
    estimate_vsize,
    varint_size,
)
from btx.transaction.models import OutPoint, Tx, TxIn, TxOut, Witness

TXID = "aa" * 32
TX_HEX = (
    "01000000"
    + "01"
    + TXID
    + "00000000"
    + "00"
    + "ffffffff"
    + "01"
    + "00e1f50500000000"
    + "1976a914000000000000000000000000000000000000000088ac"
    + "00000000"
)
SCRIPT_HEX = "0014" + "00" * 20


class ProviderHandler(BaseHTTPRequestHandler):
    """Small deterministic HTTP service used as an integration fixture."""

    retry_attempts = 0

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def send_body(self, body: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/retry":
            type(self).retry_attempts += 1
            if type(self).retry_attempts == 1:
                self.send_body(b"temporary failure", 503)
            else:
                self.send_body(b"ok")
            return
        if self.path.endswith("/hex"):
            self.send_body(TX_HEX.encode())
            return
        if self.path.endswith("/script"):
            self.send_body(json.dumps({"scriptpubkey": SCRIPT_HEX}).encode())
            return
        if self.path.endswith("/value"):
            self.send_body(b"100000000")
            return
        if self.path.endswith("/tx/" + TXID):
            self.send_body(
                json.dumps(
                    {"vout": [{"scriptpubkey": SCRIPT_HEX, "value": 100000000}]}
                ).encode()
            )
            return
        self.send_body(b"not found", 404)

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"] or 0)
        assert self.rfile.read(length) == bytes.fromhex("00")
        self.send_body(TXID.encode())


@pytest.fixture()
def provider_server() -> Generator[str, None, None]:
    ProviderHandler.retry_attempts = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProviderHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def make_provider(base_url: str) -> GenericHttpProvider:
    return GenericHttpProvider(
        base_url,
        utxo_script_path="/utxo/{txid}/{vout}/script",
        utxo_value_path="/utxo/{txid}/{vout}/value",
        broadcast_path="/broadcast",
    )


def test_local_http_provider_end_to_end(provider_server: str) -> None:
    provider = make_provider(provider_server)

    assert provider.get_transaction_hex(TXID) == TX_HEX
    scripts, values = enrich_transaction(TX_HEX, provider=provider)
    assert scripts == [bytes.fromhex(SCRIPT_HEX)]
    assert values == [100000000]
    assert fetch_and_extract(TX_HEX, provider=provider) == []
    assert batch_fetch_transactions([TXID, TXID], provider=provider) == {TXID: TX_HEX}
    assert batch_enrich_transactions([TX_HEX], provider=provider) == [(scripts, values)]
    assert broadcast_transaction("00", provider=provider) == TXID


def test_async_provider_operations(provider_server: str) -> None:
    provider = make_provider(provider_server)

    async def run() -> None:
        scripts, values = await async_enrich_transaction(TX_HEX, provider=provider)
        assert scripts == [bytes.fromhex(SCRIPT_HEX)]
        assert values == [100000000]
        assert await async_batch_fetch_transactions([TXID], provider=provider) == {
            TXID: TX_HEX
        }

    asyncio.run(run())


def test_http_retry_and_validation(provider_server: str) -> None:
    with patch("btx.services.blockchain.time.sleep") as sleep:
        assert fetch_text(provider_server + "/retry") == "ok"
        sleep.assert_called_once()

    with pytest.raises(ValueError, match="absolute HTTP"):
        validate_http_url("file:///tmp/tx")
    with pytest.raises(ValueError, match="Invalid txid"):
        validate_txid("not-a-txid")
    with pytest.raises(ValueError, match="non-negative"):
        validate_vout(True)
    with pytest.raises(ValueError, match="positive integer"):
        validate_max_workers(0)


def test_http_network_failure_is_bounded() -> None:
    with (
        patch(
            "btx.services.blockchain.urlopen",
            side_effect=URLError("offline"),
        ),
        patch("btx.services.blockchain.time.sleep") as sleep,
    ):
        with pytest.raises(OSError, match="URL error"):
            fetch_text("http://example.test/tx")
        assert sleep.call_count == 2


def test_configuration_and_serialization_boundaries() -> None:
    with pytest.raises(ValueError, match="default_backend"):
        Settings(default_backend="unsupported")
    assert [
        varint_size(value) for value in (0xFC, 0xFD, 0xFFFF, 0x10000, 0x100000000)
    ] == [
        1,
        3,
        3,
        5,
        9,
    ]


def test_settings_aliases_and_fee_estimation() -> None:
    import importlib

    settings_module = importlib.import_module("btx.settings")

    with patch.dict("os.environ", {"BTX_DEFAULT_BACKEND": "libsecp256k1"}):
        assert settings_module._resolve_default_backend() == "libsecp"
    with patch.dict("os.environ", {"BTX_DEFAULT_BACKEND": ""}):
        assert settings_module._resolve_default_backend() is None
    assert repr(Settings()) == "Settings(default_backend=None)"

    tx = Tx(
        version=2,
        inputs=(
            TxIn(
                previous_output=OutPoint(bytes(32), 0),
                script_sig=b"legacy",
                sequence=0xFFFFFFFF,
                witness=Witness((b"witness",)),
            ),
        ),
        outputs=(TxOut(value=1000, script_pubkey=bytes.fromhex(SCRIPT_HEX)),),
        lock_time=0,
    )
    assert estimate_vsize(tx) > 0
    assert estimate_minimum_fee(tx, sat_per_vbyte=2) == estimate_vsize(tx) * 2
    assert estimate_optimal_fee(tx, target_blocks=0) == estimate_vsize(tx) * 120


def test_cli_runs_in_a_clean_subprocess() -> None:
    code = (
        "from btx.cli import main; "
        "raise SystemExit(main(['decode', __import__('sys').argv[1]]))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, TX_HEX],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["version"] == 1
