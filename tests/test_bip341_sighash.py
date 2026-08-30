# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""BIP-341 / BIP-342 sighash consensus tests.

Cross-checks :func:`btx.sighash.taproot.sighash_taproot` byte-for-byte
against an independent reference implementation of the BIP-341 common
signature message, exercises the BIP-340 sign/verify round-trip over
Taproot digests (key-path and script-path), and nails the historical
legacy ``SIGHASH_SINGLE`` and transaction-parser bounds behaviour.
"""

from __future__ import annotations

import pytest

from btx.curve import GENERATOR_POINT, add, multiply
from btx.curve.params import CURVE_ORDER
from btx.encoding.hasher import sha256, tagged_hash
from btx.encoding.varint import encode_varint
from btx.services.serializer import (
    serialize_legacy_tx,
    serialize_legacy_tx_for_sighash,
)
from btx.sighash.flag import SIGHASH_SINGLE
from btx.sighash.legacy import sighash_legacy
from btx.sighash.taproot import NO_CODESEPARATOR, sighash_taproot
from btx.signature.schnorr import verify_schnorr_signature
from btx.transaction.models import OutPoint, Tx, TxIn, TxOut, Witness
from btx.transaction.parser import parse_tx

FLAGS = (0x00, 0x01, 0x02, 0x03, 0x81, 0x82, 0x83)


def point_to_xonly(point) -> bytes:
    """Convert a Point to its 32-byte x-only encoding."""
    assert point.x is not None
    return point.x.to_bytes(32, "big")


def make_in(txid: bytes = b"\x01" * 32, vout: int = 0, sequence: int = 0xFFFFFFFF):
    return TxIn(OutPoint(txid, vout), b"", sequence, Witness(()))


def make_out(value: int = 1000, script: bytes = b"\x00"):
    return TxOut(value, script)


def make_tx() -> Tx:
    return Tx(
        version=2,
        inputs=(make_in(sequence=0xFFFFFFFE), make_in(b"\x02" * 32, 1)),
        outputs=(make_out(10000, b"\x01"), make_out(20000, b"\x02")),
        lock_time=500,
    )


AMOUNTS = (10000, 20000)
SCRIPTPUBKEYS = (b"", b"")


# ═══════════════════════════════════════════════════════════════════════════
# Independent reference: BIP-341 SigMsg
# ═══════════════════════════════════════════════════════════════════════════


def reference_sighash_taproot(
    tx,
    input_index,
    hash_type,
    *,
    ext_flag=0,
    tapleaf_hash=None,
    annex=None,
    amounts,
    scriptpubkeys,
):
    """Byte-level BIP-341 reference SigMsg (written straight from the spec)."""
    data = bytearray()
    data.append(0x00)  # epoch
    data.append(hash_type)
    data += tx.version.to_bytes(4, "little")
    data += tx.lock_time.to_bytes(4, "little")

    anyonecanpay = bool(hash_type & 0x80)
    base = hash_type & 0x1F

    if not anyonecanpay:
        data += sha256(
            b"".join(
                i.previous_output.txid
                + i.previous_output.vout.to_bytes(4, "little")
                for i in tx.inputs
            )
        )
        data += sha256(b"".join(a.to_bytes(8, "little") for a in amounts))
        data += sha256(
            b"".join(encode_varint(len(s)) + s for s in scriptpubkeys)
        )
        data += sha256(
            b"".join(i.sequence.to_bytes(4, "little") for i in tx.inputs)
        )

    output_type = 1 if base == 0 else base  # 1=ALL, 2=NONE, 3=SINGLE
    if output_type == 1:
        data += sha256(
            b"".join(
                o.value.to_bytes(8, "little")
                + encode_varint(len(o.script_pubkey))
                + o.script_pubkey
                for o in tx.outputs
            )
        )

    data.append(((ext_flag << 1) | (0 if annex is None else 1)) & 0xFF)

    inp = tx.inputs[input_index]
    if anyonecanpay:
        data += inp.previous_output.txid
        data += inp.previous_output.vout.to_bytes(4, "little")
        data += amounts[input_index].to_bytes(8, "little")
        data += encode_varint(len(scriptpubkeys[input_index]))
        data += scriptpubkeys[input_index]
        data += inp.sequence.to_bytes(4, "little")
    else:
        data += input_index.to_bytes(4, "little")

    if annex is not None:
        data += sha256(encode_varint(len(annex)) + annex)

    if output_type == 3:
        txout = tx.outputs[input_index]
        data += sha256(
            txout.value.to_bytes(8, "little")
            + encode_varint(len(txout.script_pubkey))
            + txout.script_pubkey
        )

    if ext_flag:
        assert tapleaf_hash is not None
        data += tapleaf_hash
        data += b"\x00"  # key_version
        data += NO_CODESEPARATOR.to_bytes(4, "little")

    return tagged_hash("TapSighash", bytes(data))


class TestSighashTaprootMatchesReference:
    """``sighash_taproot`` matches the independent BIP-341 reference."""

    tx = make_tx()

    @pytest.mark.parametrize("hash_type", FLAGS)
    def test_key_path(self, hash_type) -> None:
        for idx in (0, 1):
            digest = sighash_taproot(
                self.tx,
                idx,
                None,
                hash_type,
                amounts=AMOUNTS,
                scriptpubkeys=SCRIPTPUBKEYS,
            )
            assert digest == reference_sighash_taproot(
                self.tx,
                idx,
                hash_type,
                amounts=AMOUNTS,
                scriptpubkeys=SCRIPTPUBKEYS,
            )

    @pytest.mark.parametrize("hash_type", FLAGS)
    def test_key_path_with_annex(self, hash_type) -> None:
        idx = 1
        annex = b"\x50\x00"
        digest = sighash_taproot(
            self.tx,
            idx,
            None,
            hash_type,
            annex=annex,
            amounts=AMOUNTS,
            scriptpubkeys=SCRIPTPUBKEYS,
        )
        assert digest == reference_sighash_taproot(
            self.tx,
            idx,
            hash_type,
            annex=annex,
            amounts=AMOUNTS,
            scriptpubkeys=SCRIPTPUBKEYS,
        )

    @pytest.mark.parametrize("hash_type", FLAGS)
    def test_script_path(self, hash_type) -> None:
        leaf = b"\x20" + b"\x00" * 32 + b"\xac"
        tapleaf_hash = tagged_hash("TapLeaf", b"\xc0" + bytes([len(leaf)]) + leaf)
        digest = sighash_taproot(
            self.tx,
            0,
            b"\xc0" + leaf,
            hash_type,
            tapleaf_hash=tapleaf_hash,
            amounts=AMOUNTS,
            scriptpubkeys=SCRIPTPUBKEYS,
        )
        assert digest == reference_sighash_taproot(
            self.tx,
            0,
            hash_type,
            ext_flag=1,
            tapleaf_hash=tapleaf_hash,
            amounts=AMOUNTS,
            scriptpubkeys=SCRIPTPUBKEYS,
        )

    def test_single_out_of_range_raises(self) -> None:
        """Taproot SIGHASH_SINGLE with no matching output is a failure."""
        tx1 = Tx(2, (make_in(), make_in()), (make_out(5000),), 0)
        with pytest.raises(ValueError, match="out of bounds"):
            sighash_taproot(
                tx1,
                1,
                None,
                0x03,
                amounts=(5000, 5000),
                scriptpubkeys=(b"", b""),
            )

    def test_sequences_hashed_even_for_none_single(self) -> None:
        """sha_sequences commits to every input regardless of the base flag.

        The digest differs accordingly when an *unselected* input's
        sequence changes under SIGHASH_NONE / SIGHASH_SINGLE.
        """
        base = make_tx()
        altered = Tx(
            version=2,
            inputs=(
                make_in(sequence=0xFFFFFFFE),
                make_in(b"\x02" * 32, 1, sequence=0x11111111),
            ),
            outputs=(make_out(10000, b"\x01"), make_out(20000, b"\x02")),
            lock_time=500,
        )
        a = sighash_taproot(
            base, 0, None, 0x02, amounts=AMOUNTS, scriptpubkeys=SCRIPTPUBKEYS
        )
        b = sighash_taproot(
            altered, 0, None, 0x02, amounts=AMOUNTS, scriptpubkeys=SCRIPTPUBKEYS
        )
        assert a != b


# ═══════════════════════════════════════════════════════════════════════════
# BIP-340 sign / verify over Taproot digests
# ═══════════════════════════════════════════════════════════════════════════


def schnorr_sign(priv: int, msg: bytes) -> bytes:
    """Minimal deterministic BIP-340 signer used only for the tests."""
    xonly_pub = point_to_xonly(multiply(priv, GENERATOR_POINT))
    for attempt in range(16):
        seed = tagged_hash(
            "BIP340-Test-Nonce", priv.to_bytes(32, "big") + msg + bytes([attempt])
        )
        k = int.from_bytes(seed, "big") % CURVE_ORDER
        if k == 0:
            continue
        r_point = multiply(k, GENERATOR_POINT)
        if r_point.y is None or (r_point.y & 1) != 0:
            # BIP-340: negate the nonce so R has even y.
            k = CURVE_ORDER - k
            r_point = multiply(k, GENERATOR_POINT)
        r = r_point.x if r_point.x is not None else 0
        if r == 0 or r >= CURVE_ORDER:
            continue
        e = (
            int.from_bytes(
                tagged_hash(
                    "BIP0340/challenge",
                    r.to_bytes(32, "big") + xonly_pub + msg,
                ),
                "big",
            )
            % CURVE_ORDER
        )
        s = (k + e * priv) % CURVE_ORDER
        if s == 0 or s >= CURVE_ORDER:
            continue
        return r.to_bytes(32, "big") + s.to_bytes(32, "big")
    raise RuntimeError("Failed to produce a Schnorr signature")


class TestSchnorrRoundTripOverTaproot:
    def test_key_path_sign_verify(self) -> None:
        priv = 42
        script_pubkey = b"\x51\x20" + point_to_xonly(multiply(priv, GENERATOR_POINT))
        txin = TxIn(OutPoint(b"\x03" * 32, 0), b"", 0xFFFFFFFF, Witness(()))
        tx = Tx(2, (txin,), (TxOut(10_000_000, script_pubkey),), 0)
        digest = sighash_taproot(
            tx,
            0,
            None,
            0x00,
            amounts=(10_000_000,),
            scriptpubkeys=(b"",),
        )
        sig = schnorr_sign(priv, digest)
        assert verify_schnorr_signature(
            point_to_xonly(multiply(priv, GENERATOR_POINT)), sig, digest
        )
        tampered = digest[:-1] + bytes([digest[-1] ^ 0xFF])
        assert not verify_schnorr_signature(
            point_to_xonly(multiply(priv, GENERATOR_POINT)), sig, tampered
        )

    def test_script_path_sign_verify(self) -> None:
        """A script-path spend is signed with the internal (leaf) key."""
        priv = 7
        leaf_key = multiply(priv, GENERATOR_POINT)
        xonly = point_to_xonly(leaf_key)
        leaf_script = b"\x20" + xonly + b"\xac"  # <xonly> OP_CHECKSIG
        tapleaf = b"\xc0" + leaf_script
        leaf_hash = tagged_hash(
            "TapLeaf", tapleaf[:1] + bytes([len(leaf_script)]) + leaf_script
        )
        tweak = tagged_hash("TapTweak", xonly + leaf_hash)
        tweak_int = int.from_bytes(tweak, "big") % CURVE_ORDER
        output_key = add(leaf_key, multiply(tweak_int, GENERATOR_POINT))
        script_pubkey = b"\x51\x20" + point_to_xonly(output_key)

        txin = TxIn(OutPoint(b"\x04" * 32, 0), b"", 0xFFFFFFFF, Witness(()))
        tx = Tx(2, (txin,), (TxOut(5_000_000, script_pubkey),), 0)
        digest = sighash_taproot(
            tx,
            0,
            tapleaf,
            0x00,
            tapleaf_hash=leaf_hash,
            amounts=(5_000_000,),
            scriptpubkeys=(b"",),
        )
        sig = schnorr_sign(priv, digest)
        assert verify_schnorr_signature(xonly, sig, digest)


# ═══════════════════════════════════════════════════════════════════════════
# Legacy SIGHASH_SINGLE consensus behaviour
# ═══════════════════════════════════════════════════════════════════════════


def reference_legacy_sighash_preimage(tx, input_index, script, flag):
    """Independent legacy sighash serializer (Core ``Serialize`` semantics)."""
    base = flag & 0x1F
    anyonecanpay = bool(flag & 0x80)
    data = bytearray()
    data += tx.version.to_bytes(4, "little")

    if anyonecanpay:
        data += encode_varint(1)
        inp = tx.inputs[input_index]
        data += inp.previous_output.txid
        data += inp.previous_output.vout.to_bytes(4, "little")
        data += encode_varint(len(script)) + script
        data += inp.sequence.to_bytes(4, "little")
    else:
        data += encode_varint(len(tx.inputs))
        for i, inp in enumerate(tx.inputs):
            data += inp.previous_output.txid
            data += inp.previous_output.vout.to_bytes(4, "little")
            if i == input_index:
                data += encode_varint(len(script)) + script
                data += inp.sequence.to_bytes(4, "little")
            else:
                data += b"\x00"
                if base in (2, 3):  # NONE / SINGLE zero the other sequences
                    data += b"\x00\x00\x00\x00"
                else:
                    data += inp.sequence.to_bytes(4, "little")

    if base == 2:
        data += b"\x00"  # zero outputs
    elif base == 3:
        data += encode_varint(input_index + 1)
        for nout in range(input_index + 1):
            if nout == input_index:
                txout = tx.outputs[nout]
                data += txout.value.to_bytes(8, "little")
                data += encode_varint(len(txout.script_pubkey))
                data += txout.script_pubkey
            else:
                data += b"\xff" * 8 + b"\x00"  # null CTxOut
    else:
        data += encode_varint(len(tx.outputs))
        for txout in tx.outputs:
            data += txout.value.to_bytes(8, "little")
            data += encode_varint(len(txout.script_pubkey))
            data += txout.script_pubkey

    data += tx.lock_time.to_bytes(4, "little")
    data += flag.to_bytes(4, "little")
    return bytes(data)


class TestLegacySighashSingle:
    SCRIPTS = (0x01, 0x02, 0x03, 0x81, 0x82, 0x83)

    @pytest.mark.parametrize("flag", SCRIPTS)
    @pytest.mark.parametrize("idx", (0, 1))
    def test_preimage_matches_reference(self, flag, idx) -> None:
        tx = make_tx()
        preimage = serialize_legacy_tx_for_sighash(tx, idx, b"\x51", flag)
        assert preimage == reference_legacy_sighash_preimage(tx, idx, b"\x51", flag)

    def test_out_of_range_is_uint256_one(self) -> None:
        """Legacy SINGLE beyond the outputs returns the un-hashed ONE."""
        tx = make_tx()
        assert sighash_legacy(tx, 5, b"\x51", SIGHASH_SINGLE) == (
            b"\x01" + b"\x00" * 31
        )
        # The pre-image is the all-null substitution (never hashed by
        # sighash_legacy, but still well-defined at the serializer level).
        preimage = serialize_legacy_tx_for_sighash(tx, 5, b"\x51", SIGHASH_SINGLE)
        assert b"\xff" * 8 + b"\x00" in preimage

    def test_one_not_produced_for_valid_single(self) -> None:
        tx = make_tx()
        assert sighash_legacy(tx, 0, b"\x51", SIGHASH_SINGLE) != b"\x01" + b"\x00" * 31


# ═══════════════════════════════════════════════════════════════════════════
# Parser strict-bounds behaviour
# ═══════════════════════════════════════════════════════════════════════════


class TestParserBounds:
    def test_minimal_legacy_tx_parses(self) -> None:
        raw = serialize_legacy_tx(Tx(version=1, inputs=(), outputs=(), lock_time=0))
        assert len(raw) == 10
        parsed, consumed = parse_tx(raw)
        assert consumed == len(raw)
        assert parsed.version == 1

    def test_six_byte_legacy_tx_is_truncated(self) -> None:
        """version + 0x00 sequence-free header is NOT a valid transaction."""
        with pytest.raises(ValueError, match="Truncated transaction data"):
            parse_tx(b"\x01\x00\x00\x00\x00\x00")

    def test_truncated_input_rejected(self) -> None:
        tx = make_tx()
        raw = serialize_legacy_tx(tx)
        for cut in (6, 10, 30, len(raw) - 1):
            with pytest.raises(ValueError, match="Truncated transaction data"):
                parse_tx(raw[:cut])


# ═══════════════════════════════════════════════════════════════════════════
# SIGHASH_DEFAULT
# ═══════════════════════════════════════════════════════════════════════════


class TestSighashDefault:
    def test_constant(self) -> None:
        from btx.sighash.flag import SIGHASH_DEFAULT, sighash_name

        assert SIGHASH_DEFAULT == 0x00
        assert sighash_name(SIGHASH_DEFAULT) == "SIGHASH_DEFAULT"