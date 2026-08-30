# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Engine for extracting ECDSA and Schnorr signatures from Bitcoin transactions.

Supports every standard script type:

- **Legacy**: P2PK, P2PKH (handled by :class:`LegacyExtractor`).
- **SegWit v0**: P2WPKH, P2WSH (:class:`P2WPKHExtractor` and
  :class:`P2WSHExtractor`).
- **P2SH-wrapped SegWit**: P2SH-P2WPKH, P2SH-P2WSH
  (:class:`P2SHSegWitExtractor`).
- **Taproot**: P2TR key-path and script-path spends
  (:class:`TaprootExtractor`).

Public-key recovery is attempted for each discovered ECDSA signature;
for Taproot, the x-only public key is recovered directly from the
P2TR ``scriptPubKey``.

Design: Strategy pattern with plugin registry
---------------------------------------------

The five built-in extractors are subclasses of
:class:`~btx.signature.extraction.engine.BaseExtractor`.
They are registered via :func:`register_builtin_extractors` (called
automatically by :func:`extract_signatures`) and selected per-input
via the registry.  This avoids a hard-coded ``if/elif`` chain and
lets external code add custom script-type extractors without
forking the library.

For each extracted signature, the dispatcher:

1. Looks up the script type from the previous output's
   ``scriptPubKey`` (if provided).
2. Selects the first registered plugin whose ``can_handle`` returns
   ``True``.
3. Calls ``plugin.extract(tx, vin, txin, script_pubkey, value)`` and
   appends the returned records.
4. Falls back to a debug log line if no plugin matches (the input is
   skipped, but processing of subsequent inputs continues).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar

from btx.curve import INFINITY_POINT, Point
from btx.encoding.der import decode_der
from btx.script.classifier import (
    P2SH,
    P2TR,
    P2WPKH,
    P2WSH,
    classify_script_pubkey,
)
from btx.script.parser import parse_script, parse_script_chunks
from btx.sighash.flag import SIGHASH_DEFAULT
from btx.signature.extraction.helpers import (
    default_script_code,
    extract_pubkey_from_script_sig,
    p2wpkh_script_code,
    recover_or_parse_pubkey,
)
from btx.signature.extraction.plugins import register_plugin
from btx.signature.record import Record

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from btx.transaction.models import Tx, TxIn

# ── Polymorphic extraction strategies (Strategy pattern) ────────────


class BaseExtractor(ABC):
    """Abstract base for script-path signature extractors.

    Subclasses implement two instance methods:

    - :meth:`can_handle` reports whether this extractor handles a
      given ``(script_type, is_segwit)`` pair.
    - :meth:`extract` performs the actual signature extraction for
      one input.

    The legacy static-method convention is removed: extractors are
    instantiated and registered as instances, enabling future
    per-extractor state (e.g. caching).

    Attributes:
        name: Unique registry key for this extractor.
    """

    name: ClassVar[str]

    @abstractmethod
    def can_handle(self, script_type: str, is_segwit: bool) -> bool:
        """Return True if this extractor handles the given script type.

        Args:
            script_type: The classified script type (e.g. ``"p2pkh"``).
            is_segwit: Whether the input carries witness data.

        Returns:
            ``True`` if this extractor should handle the input.
        """

    @abstractmethod
    def extract(
        self,
        tx: Tx,
        vin: int,
        txin: TxIn,
        script_pubkey: bytes,
        value: int,
    ) -> list[Record]:
        """Extract signatures from this input.

        Args:
            tx: The parent transaction.
            vin: Index of the input being processed.
            txin: The ``TxIn`` providing scriptSig and witness data.
            script_pubkey: The previous output's ``scriptPubKey``.
            value: The UTXO value in satoshis (for SegWit sighash).

        Returns:
            A list of :class:`~btx.signature.record.Record` instances.
        """


class LegacyExtractor(BaseExtractor):
    """Extractor for non-SegWit (legacy P2PK/P2PKH) inputs."""

    name: ClassVar[str] = "legacy"

    def can_handle(self, script_type: str, is_segwit: bool) -> bool:
        return not is_segwit

    def extract(
        self,
        tx: Tx,
        vin: int,
        txin: TxIn,
        script_pubkey: bytes,
        value: int,
    ) -> list[Record]:
        """Extract signatures from a legacy (non-SegWit) input.

        Args:
            tx: The parent transaction.
            vin: Index of the input being processed.
            txin: The ``TxIn`` providing scriptSig data.
            script_pubkey: The previous output's ``scriptPubKey``.
            value: The UTXO value in satoshis (unused by legacy).

        Returns:
            A list of :class:`~btx.signature.record.Record` instances.
        """
        parsed_sig: Sequence[object] = (
            list(parse_script(txin.script_sig)) if txin.script_sig else []
        )
        return extract_legacy(tx, vin, script_pubkey, parsed_sig)


class P2WPKHExtractor(BaseExtractor):
    """Extractor for P2WPKH (SegWit v0 key-path) inputs."""

    name: ClassVar[str] = P2WPKH

    def can_handle(self, script_type: str, is_segwit: bool) -> bool:
        return script_type == P2WPKH and is_segwit

    def extract(
        self,
        tx: Tx,
        vin: int,
        txin: TxIn,
        script_pubkey: bytes,
        value: int,
    ) -> list[Record]:
        """Extract signatures from a P2WPKH (SegWit v0 key-path) input.

        Args:
            tx: The parent transaction.
            vin: Index of the input being processed.
            txin: The ``TxIn`` providing witness data.
            script_pubkey: The previous output's ``scriptPubKey``.
            value: The UTXO value in satoshis (used for SegWit sighash).

        Returns:
            A list of :class:`~btx.signature.record.Record` instances.
        """
        return extract_p2wpkh(tx, vin, script_pubkey, value, txin.witness.items)


class P2WSHExtractor(BaseExtractor):
    """Extractor for P2WSH (SegWit v0 script-path) inputs."""

    name: ClassVar[str] = P2WSH

    def can_handle(self, script_type: str, is_segwit: bool) -> bool:
        return script_type == P2WSH and is_segwit

    def extract(
        self,
        tx: Tx,
        vin: int,
        txin: TxIn,
        script_pubkey: bytes,
        value: int,
    ) -> list[Record]:
        """Extract signatures from a P2WSH (SegWit v0 script-path) input.

        Args:
            tx: The parent transaction.
            vin: Index of the input being processed.
            txin: The ``TxIn`` providing witness data.
            script_pubkey: The previous output's ``scriptPubKey``.
            value: The UTXO value in satoshis (used for SegWit sighash).

        Returns:
            A list of :class:`~btx.signature.record.Record` instances.
        """
        return extract_p2wsh(tx, vin, script_pubkey, value, txin.witness.items)


class P2SHSegWitExtractor(BaseExtractor):
    """Extractor for P2SH-wrapped SegWit inputs."""

    name: ClassVar[str] = f"p2sh_{P2WPKH}"

    def can_handle(self, script_type: str, is_segwit: bool) -> bool:
        return script_type == P2SH and is_segwit

    def extract(
        self,
        tx: Tx,
        vin: int,
        txin: TxIn,
        script_pubkey: bytes,
        value: int,
    ) -> list[Record]:
        """Extract signatures from a P2SH-wrapped SegWit input.

        Args:
            tx: The parent transaction.
            vin: Index of the input being processed.
            txin: The ``TxIn`` providing scriptSig and witness data.
            script_pubkey: The previous output's ``scriptPubKey``.
            value: The UTXO value in satoshis (used for SegWit sighash).

        Returns:
            A list of :class:`~btx.signature.record.Record` instances.
        """
        return extract_p2sh_segwit(tx, vin, script_pubkey, value, txin)


class TaprootExtractor(BaseExtractor):
    """Extractor for P2TR (Taproot) inputs — both key-path and script-path."""

    name: ClassVar[str] = P2TR

    def can_handle(self, script_type: str, is_segwit: bool) -> bool:
        return script_type == P2TR and is_segwit

    def extract(
        self,
        tx: Tx,
        vin: int,
        txin: TxIn,
        script_pubkey: bytes,
        value: int,
    ) -> list[Record]:
        """Extract signatures from a P2TR (Taproot) input.

        Handles both key-path and script-path spends.

        Args:
            tx: The parent transaction.
            vin: Index of the input being processed.
            txin: The ``TxIn`` providing witness data.
            script_pubkey: The previous output's ``scriptPubKey``.
            value: The UTXO value in satoshis (used for Taproot sighash).

        Returns:
            A list of :class:`~btx.signature.record.Record` instances.
        """
        return extract_taproot(tx, vin, script_pubkey, value, txin.witness.items)


# ── Built-in extractor registry ──────────────────────────────────────

BUILTIN_EXTRACTOR_INSTANCES: list[BaseExtractor] = [
    LegacyExtractor(),
    P2WPKHExtractor(),
    P2WSHExtractor(),
    P2SHSegWitExtractor(),
    TaprootExtractor(),
]

BUILTINS_REGISTERED: bool = False
"""Whether :func:`register_builtin_extractors` has already run.

Public so callers can introspect registration state.  Mutated only
through :func:`register_builtin_extractors`.
"""


def register_builtin_extractors() -> None:
    """Register all built-in script-path extractor plugins.

    Idempotent — subsequent calls are no-ops once registered.

    Side effects:
        Sets the module-level :data:`BUILTINS_REGISTERED` flag on
        success.
    """
    global BUILTINS_REGISTERED
    if BUILTINS_REGISTERED:
        return
    for extractor in BUILTIN_EXTRACTOR_INSTANCES:
        register_plugin(extractor)
    BUILTINS_REGISTERED = True


# ── Public dispatch ─────────────────────────────────────────────────


def extract_signatures(
    tx: Tx,
    utxo_script_pubkeys: list[bytes] | None = None,
    utxo_values: list[int] | None = None,
) -> list[Record]:
    """Extract all signatures (ECDSA and Schnorr) from a transaction.

    Iterates over each input, determines the script type, and dispatches
    to the appropriate extraction handler via registered plugins.

    Args:
        tx: The transaction to extract from.
        utxo_script_pubkeys: The ``scriptPubKey`` for each UTXO being spent.
            Required for P2SH, P2WPKH, P2WSH, and P2TR.
        utxo_values: The value (in satoshis) for each UTXO being spent.
            Required for SegWit inputs (used in sighash computation).

    Returns:
        A list of ``Record`` instances — one per extracted signature.

    Raises:
        IndexError: If *utxo_script_pubkeys* or *utxo_values* are shorter
            than *tx.inputs*.
        AttributeError: If *tx* is malformed.
        ValueError: If sighash computation fails (e.g. invalid flag).
    """
    register_builtin_extractors()
    records: list[Record] = []
    script_type_counts: dict[str, int] = {}
    failed_inputs = 0

    if not tx.inputs:
        return records

    from btx.signature.extraction.plugins import get_plugin, list_plugins

    for vin, txin in enumerate(tx.inputs):
        parsed_sig: Sequence[object] = (
            list(parse_script(txin.script_sig)) if txin.script_sig else []
        )
        script_pubkey = utxo_script_pubkeys[vin] if utxo_script_pubkeys else b""
        script_type = determine_script_type(script_pubkey, parsed_sig)
        script_type_counts[script_type] = script_type_counts.get(script_type, 0) + 1
        logger.debug("Processing input %d, script_type=%s", vin, script_type)
        value = utxo_values[vin] if utxo_values else 0
        is_segwit = bool(txin.witness.items)

        dispatched = False
        for plugin_name in list_plugins():
            plugin = get_plugin(plugin_name)
            if plugin is not None and plugin.can_handle(script_type, is_segwit):
                records.extend(plugin.extract(tx, vin, txin, script_pubkey, value))
                dispatched = True
                break

        if not dispatched:
            failed_inputs += 1

    type_summary = ", ".join(f"{n} {t}" for t, n in sorted(script_type_counts.items()))
    logger.info(
        "Extracted %d signatures from %d inputs (%s). failed=%d",
        len(records),
        len(tx.inputs),
        type_summary,
        failed_inputs,
    )
    return records


def determine_script_type(script_pubkey: bytes, script_sig: Sequence[object]) -> str:
    """Classify the script type from the ``scriptPubKey``.

    Args:
        script_pubkey: The output script as raw bytes.
        script_sig: The input ``scriptSig`` (unused, kept for signature
            compatibility).

    Returns:
        A script-type string (e.g. ``"p2pkh"``, ``"p2wpkh"``) or
        ``"unknown"`` if *script_pubkey* is empty.
    """
    if not script_pubkey:
        return "unknown"
    return classify_script_pubkey(script_pubkey)


# ── Legacy (non-segwit) extraction ─────────────────────────────────


def extract_legacy(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    script_sig: Sequence[object],
) -> list[Record]:
    """Extract signatures from a non-SegWit (legacy) input.

    Scans the ``scriptSig`` for DER-encoded signatures and attempts
    public-key recovery for each.

    Args:
        tx: The parent transaction.
        vin: Input index.
        script_pubkey: The UTXO ``scriptPubKey``.
        script_sig: Parsed ``scriptSig`` elements.

    Returns:
        A list of ``Record`` instances.

    Raises:
        AttributeError: If *tx* is malformed (e.g. ``tx.txid()`` fails).
    """
    records: list[Record] = []
    guessed = guess_p2pkh_script(script_sig)
    effective_script = script_pubkey or guessed or b""
    pubkey_bytes = extract_pubkey_from_script_sig(script_sig)
    for element in script_sig:
        if isinstance(element, bytes) and len(element) > 1:
            der = element[:-1]
            flag = element[-1]
            try:
                decode_der(der)
            except ValueError:
                continue
            pubkey = recover_or_parse_pubkey(
                tx,
                vin,
                der,
                flag,
                effective_script,
                value=0,
                pubkey_bytes=pubkey_bytes,
            )
            if pubkey is None:
                logger.debug("Pubkey recovery failed for input %d", vin)
                continue
            records.append(
                Record(
                    txid=tx.txid(),
                    input_index=vin,
                    signature=der,
                    public_key=pubkey,
                    script_type=determine_script_type(script_pubkey, script_sig),
                    sighash_flag=flag,
                    amount=0,
                )
            )
            logger.debug("Signature extracted from input %d", vin)
    return records


def guess_p2pkh_script(script_sig: Sequence[object]) -> bytes | None:
    """Build a P2PKH scriptPubKey from the pubkey in *script_sig*, if present.

    Returns:
        The P2PKH ``scriptPubKey`` bytes, or ``None`` if no pubkey found.
    """
    for element in script_sig:
        if isinstance(element, bytes) and len(element) in {33, 65}:
            from btx.script.builder import make_p2pkh_script

            return make_p2pkh_script(element)
    return None


# ── SegWit extraction ─────────────────────────────────────────────


def extract_p2wpkh(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    value: int,
    witness_items: tuple[bytes, ...],
) -> list[Record]:
    """Extract signatures from a P2WPKH witness stack.

    Args:
        tx: The parent transaction.
        vin: Input index.
        script_pubkey: The P2WPKH witness program.
        value: UTXO value in satoshis (used for sighash).
        witness_items: Witness stack items.

    Returns:
        A list of ``Record`` instances.

    Raises:
        AttributeError: If *tx* is malformed.
    """
    script_code = (
        p2wpkh_script_code(script_pubkey) if script_pubkey else default_script_code()
    )
    records: list[Record] = []
    for item in witness_items[:-1]:
        if len(item) > 1:
            der = item[:-1]
            flag = item[-1]
            try:
                decode_der(der)
            except ValueError:
                continue
            pubkey = recover_or_parse_pubkey(
                tx,
                vin,
                der,
                flag,
                script_code,
                value=value,
            )
            if pubkey is None:
                logger.debug("P2WPKH pubkey recovery failed for input %d", vin)
                continue
            records.append(
                Record(
                    txid=tx.txid(),
                    input_index=vin,
                    signature=der,
                    public_key=pubkey,
                    script_type=P2WPKH,
                    sighash_flag=flag,
                    amount=value,
                )
            )
            logger.debug("P2WPKH signature extracted for input %d", vin)
    return records


def extract_p2wsh(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    value: int,
    witness_items: tuple[bytes, ...],
) -> list[Record]:
    """Extract signatures from a P2WSH witness stack.

    The last witness item is treated as the witness script (used as the
    script code for sighash computation).

    Args:
        tx: The parent transaction.
        vin: Input index.
        script_pubkey: The P2WSH witness program.
        value: UTXO value in satoshis.
        witness_items: Witness stack items.

    Returns:
        A list of ``Record`` instances.

    Raises:
        AttributeError: If *tx* is malformed.
    """
    witness_script = witness_items[-1] if witness_items else b""
    script_code = witness_script if witness_script else default_script_code()
    records: list[Record] = []
    for item in witness_items[:-1]:
        if len(item) > 1:
            der = item[:-1]
            flag = item[-1]
            try:
                decode_der(der)
            except ValueError:
                continue
            pubkey = recover_or_parse_pubkey(
                tx,
                vin,
                der,
                flag,
                script_code,
                value=value,
            )
            if pubkey is None:
                logger.debug("P2WSH pubkey recovery failed for input %d", vin)
                continue
            records.append(
                Record(
                    txid=tx.txid(),
                    input_index=vin,
                    signature=der,
                    public_key=pubkey,
                    script_type=P2WSH,
                    sighash_flag=flag,
                    amount=value,
                )
            )
            logger.debug("P2WSH signature extracted for input %d", vin)
    return records


def extract_p2sh_segwit(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    value: int,
    txin: TxIn,
) -> list[Record]:
    """Extract signatures from a P2SH-wrapped SegWit input.

    Unwraps the redeem script from ``scriptSig`` to determine whether it
    wraps P2WPKH or P2WSH, then derives the appropriate script code.

    Args:
        tx: The parent transaction.
        vin: Input index.
        script_pubkey: The P2SH ``scriptPubKey``.
        value: UTXO value in satoshis.
        txin: The full ``TxIn`` (provides both ``scriptSig`` and witness).

    Returns:
        A list of ``Record`` instances.

    Raises:
        AttributeError: If *tx* or *txin* is malformed.
    """
    records: list[Record] = []
    parsed_sig = list(parse_script(txin.script_sig))
    if not parsed_sig:
        return records
    redeem_script = parsed_sig[-1] if isinstance(parsed_sig[-1], bytes) else b""
    redeem_type = classify_script_pubkey(redeem_script) if redeem_script else "unknown"

    witness_items = txin.witness.items
    # Determine script code from the redeem type
    script_code: bytes
    if redeem_type == P2WPKH:
        script_code = p2wpkh_script_code(redeem_script)
    elif redeem_type == P2WSH:
        script_code = witness_items[-1] if witness_items else b""
    else:
        script_code = default_script_code()

    for item in witness_items[:-1]:
        if len(item) > 1:
            der = item[:-1]
            flag = item[-1]
            try:
                decode_der(der)
            except ValueError:
                continue
            pubkey = recover_or_parse_pubkey(
                tx,
                vin,
                der,
                flag,
                script_code,
                value=value,
            )
            if pubkey is None:
                logger.debug("P2SH-SegWit pubkey recovery failed for input %d", vin)
                continue
            records.append(
                Record(
                    txid=tx.txid(),
                    input_index=vin,
                    signature=der,
                    public_key=pubkey,
                    script_type=f"p2sh_{redeem_type}",
                    sighash_flag=flag,
                    amount=value,
                )
            )
            logger.debug("P2SH-SegWit signature extracted for input %d", vin)
    return records


# ── Taproot extraction ────────────────────────────────────────────


def extract_taproot(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    value: int,
    witness_items: tuple[bytes, ...],
) -> list[Record]:
    """Extract Schnorr signatures from a P2TR (Taproot) input.

    Handles both key-path spends (single 64/65-byte witness item) and
    script-path spends (multiple witness items where the last two are the
    leaf script and control block).  A bare 64-byte Schnorr signature
    carries the default hash type (``SIGHASH_DEFAULT`` / ``0x00``); a
    65-byte signature ends with the ``hash_type`` byte.  For key-path
    spends the tweaked output key is recovered from the P2TR
    ``scriptPubKey``; for script-path spends the signer is lifted from
    the first 32-byte push found in the tapscript leaf.

    Args:
        tx: The parent transaction.
        vin: Input index.
        script_pubkey: The P2TR ``scriptPubKey``.
        value: UTXO value in satoshis.
        witness_items: Witness stack items.

    Returns:
        A list of ``Record`` instances.

    Raises:
        AttributeError: If *tx* is malformed.
    """
    records: list[Record] = []
    if not witness_items:
        return records

    pubkey = pubkey_from_p2tr_script(script_pubkey)

    # Key-path spend: single witness item (signature)
    if len(witness_items) == 1:
        sig_bytes = witness_items[0]
        if len(sig_bytes) < 1:
            return records
        try:
            # Taproot signature: 64-byte Schnorr + optional sighash byte.
            # A bare 64-byte Schnorr signature uses the default hash type
            # (SIGHASH_DEFAULT / 0x00) per BIP-341.
            if len(sig_bytes) == 64:
                flag = SIGHASH_DEFAULT
            elif len(sig_bytes) == 65:
                flag = sig_bytes[-1]
            else:
                return records
            records.append(
                Record(
                    txid=tx.txid(),
                    input_index=vin,
                    signature=sig_bytes,
                    public_key=pubkey,
                    script_type=P2TR,
                    sighash_flag=flag,
                    amount=value,
                )
            )
        except ValueError:
            logger.debug("Taproot key-path spend extraction failed for input %d", vin)
        return records

    # Script-path spend: stack is [sig, ..., leaf_script, control_block].
    # The last two items (leaf script and control block) are metadata, not
    # signatures; only the items before them are scanned.
    last_idx = len(witness_items) - 1
    if last_idx < 1:
        return records
    signer = pubkey_from_taproot_leaf(witness_items[last_idx - 1])
    for i in range(last_idx - 1):
        item = witness_items[i]
        if len(item) < 1:
            continue
        try:
            if len(item) == 64 or len(item) == 65:
                sig_bytes = item[:64]
                flag = item[64] if len(item) == 65 else SIGHASH_DEFAULT
                records.append(
                    Record(
                        txid=tx.txid(),
                        input_index=vin,
                        signature=sig_bytes,
                        public_key=signer,
                        script_type=P2TR,
                        sighash_flag=flag,
                        amount=value,
                    )
                )
        except ValueError:
            logger.debug("Taproot script-path item skipped for input %d", vin)
    return records


def pubkey_from_taproot_leaf(leaf_script: bytes) -> Point:
    """Lift the first x-only public key push out of a tapscript leaf.

    Scans the leaf script for a 32-byte data push and lifts it to an
    even-y point per BIP-340 (the signer for a script-path spend).

    Args:
        leaf_script: The raw tapscript bytes (without the leaf version).

    Returns:
        The signer ``Point``, or ``INFINITY_POINT`` if none can be found.
    """
    from btx.signature.schnorr import lift_x

    try:
        chunks = parse_script_chunks(leaf_script)
    except ValueError:
        logger.debug("Failed to parse taproot leaf script")
        return INFINITY_POINT
    for chunk in chunks:
        data = chunk.data
        if chunk.is_push and data is not None and len(data) == 32:
            lifted = lift_x(int.from_bytes(data, "big"))
            if lifted is not None:
                return Point(x=lifted[0], y=lifted[1])
    return INFINITY_POINT


def pubkey_from_p2tr_script(script_pubkey: bytes) -> Point:
    """Recover the public key Point from a P2TR scriptPubKey.

    P2TR outputs contain a 32-byte x-only public key.  We reconstruct
    the full Point with even y-coordinate (BIP-340 convention) using
    ``Point.from_sec_compressed`` with a 0x02 prefix.

    Args:
        script_pubkey: The P2TR ``scriptPubKey`` (34 bytes:
            ``0x51 0x20 <32-byte-xonly>``).

    Returns:
        The public key ``Point``, or ``INFINITY_POINT`` if extraction fails.
    """
    if (
        len(script_pubkey) == 34
        and script_pubkey[0] == 0x51
        and script_pubkey[1] == 0x20
    ):
        xonly = script_pubkey[2:34]
        try:
            return Point.from_sec_compressed(bytes([0x02]) + xonly)
        except ValueError:
            logger.debug("Failed to lift x-only pubkey from P2TR script")
    return INFINITY_POINT
