# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Tests for the new transaction/ package models and parsing."""

import pytest

from btx.transaction import make_tx
from btx.transaction.models import (
    EMPTY_WITNESS,
    OutPoint,
    Tx,
    TxIn,
    TxOut,
    Witness,
)


class TestOutPoint:
    def test_creation(self) -> None:
        op = OutPoint(txid=b"\x00" * 32, vout=0)
        assert len(op.txid) == 32
        assert op.vout == 0

    def test_invalid_txid_length(self) -> None:
        with pytest.raises(ValueError, match="txid must be 32 bytes"):
            OutPoint(txid=b"\x00" * 31, vout=0)

    def test_invalid_vout(self) -> None:
        with pytest.raises(ValueError, match="vout must be non-negative"):
            OutPoint(txid=b"\x00" * 32, vout=-1)


class TestWitness:
    def test_empty(self) -> None:
        w = EMPTY_WITNESS
        assert len(w) == 0
        assert w.items == ()

    def test_with_items(self) -> None:
        w = Witness((b"sig", b"pubkey"))
        assert len(w) == 2
        assert w.items[0] == b"sig"

    def test_immutable(self) -> None:
        w = Witness((b"item",))
        with pytest.raises(AttributeError):
            w.items = ()  # type: ignore[misc]


class TestTxIn:
    def test_creation(self) -> None:
        txin = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=EMPTY_WITNESS,
        )
        assert txin.sequence == 0xFFFFFFFF

    def test_negative_sequence(self) -> None:
        with pytest.raises(ValueError, match="Sequence must be non-negative"):
            TxIn(
                previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
                script_sig=b"",
                sequence=-1,
                witness=EMPTY_WITNESS,
            )


class TestTxOut:
    def test_creation(self) -> None:
        txout = TxOut(
            value=10000,
            script_pubkey=b"\x76\xa9\x14" + b"\x00" * 20 + b"\x88\xac",
        )
        assert txout.value == 10000

    def test_negative_value(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            TxOut(value=-1, script_pubkey=b"")

    def test_excessive_value(self) -> None:
        with pytest.raises(ValueError, match="exceeds maximum"):
            TxOut(value=21_000_001 * 100_000_000, script_pubkey=b"")


class TestTx:
    def test_creation(self) -> None:
        tx = Tx(
            version=2,
            inputs=(),
            outputs=(),
            lock_time=0,
        )
        assert tx.version == 2
        assert not tx.is_segwit()

    def test_is_segwit(self) -> None:
        txin = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness((b"sig",)),
        )
        tx = Tx(version=2, inputs=(txin,), outputs=(), lock_time=0)
        assert tx.is_segwit()

    def test_make_tx(self) -> None:
        tx = make_tx(
            version=2,
            inputs=[{"txid": b"\x00" * 32, "vout": 0}],
            outputs=[{"value": 1000, "script_pubkey": b"\x6a"}],
        )
        assert len(tx.inputs) == 1
        assert len(tx.outputs) == 1
        assert tx.outputs[0].value == 1000

    def test_frozen(self) -> None:
        tx = Tx(version=2, inputs=(), outputs=(), lock_time=0)
        with pytest.raises(Exception):
            tx.version = 3  # type: ignore[misc]

    def test_serialize(self) -> None:
        tx = Tx(version=2, inputs=(), outputs=(), lock_time=0)
        ser = tx.serialize()
        assert len(ser) > 0
        legacy = tx.serialize_legacy()
        assert legacy == ser

    def test_to_json(self) -> None:
        tx = Tx(version=2, inputs=(), outputs=(), lock_time=0)
        js = tx.to_json()
        assert js["version"] == 2

    def test_rbf_not_opt_in(self) -> None:
        tx = Tx(version=2, inputs=(), outputs=(), lock_time=0)
        assert not tx.is_opt_in_rbf()
        assert not tx.has_sequence_lock()

    def test_sighash_legacy(self) -> None:
        txin = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness(()),
        )
        tx = Tx(version=2, inputs=(txin,), outputs=(), lock_time=0)
        h = tx.sighash_legacy(0, b"", 0x01)
        assert len(h) == 32

    def test_sighash_segwit(self) -> None:
        txin = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness(()),
        )
        tx = Tx(version=2, inputs=(txin,), outputs=(), lock_time=0)
        h = tx.sighash_segwit(0, b"", 0, 0x01)
        assert len(h) == 32

    def test_len(self) -> None:
        txin = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness(()),
        )
        txout = TxOut(value=50000, script_pubkey=b"\x00\x14" + b"\x00" * 20)
        tx = Tx(version=2, inputs=(txin,), outputs=(txout,), lock_time=0)
        assert len(tx) == 2

    def test_iter(self) -> None:
        txin1 = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness(()),
        )
        txin2 = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=1),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness(()),
        )
        tx = Tx(version=2, inputs=(txin1, txin2), outputs=(), lock_time=0)
        inputs = list(tx)
        assert len(inputs) == 2
        assert inputs[0] is txin1
        assert inputs[1] is txin2

    def test_total_output_value(self) -> None:
        out1 = TxOut(value=1000, script_pubkey=b"\x00\x14" + b"\x00" * 20)
        out2 = TxOut(value=2000, script_pubkey=b"\x00\x14" + b"\x01" * 20)
        tx = Tx(
            version=2,
            inputs=(),
            outputs=(out1, out2),
            lock_time=0,
        )
        assert tx.total_output_value() == 3000

    def test_to_dict_roundtrip(self) -> None:
        txin = TxIn(
            previous_output=OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"\x01\x02",
            sequence=0xFFFFFFFE,
            witness=Witness((b"\x03\x04",)),
        )
        out = TxOut(value=50000, script_pubkey=b"\x00\x14" + b"\x00" * 20)
        tx = Tx(version=2, inputs=(txin,), outputs=(out,), lock_time=42)
        d = tx.to_dict()
        assert d["version"] == 2
        assert d["lock_time"] == 42
        assert len(d["inputs"]) == 1
        assert d["inputs"][0]["script_sig"] == b"\x01\x02"
        assert d["inputs"][0]["sequence"] == 0xFFFFFFFE
        assert d["inputs"][0]["witness"] == (b"\x03\x04",)
        assert d["outputs"][0]["value"] == 50000

        from btx.transaction.builder import tx_from_dict

        roundtrip = tx_from_dict(d)
        assert roundtrip == tx
