# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Fluent builder for constructing and editing PSBTs (BIP-174).

Provides :class:`PsbtEditor` for programmatic construction, signing,
and finalisation of :class:`Psbt` instances.  The editor stores its
in-progress state as frozen :class:`PsbtInput` / :class:`PsbtOutput`
dataclasses and uses :func:`dataclasses.replace` to update individual
fields, preserving the immutability contract of the underlying
types.  Calling :meth:`PsbtEditor.build` returns a frozen :class:`Psbt`.

Typical usage:

1. Construct from an unsigned transaction via
   :meth:`PsbtEditor.from_tx`.
2. Attach UTXO data, redeem/witness scripts, and BIP-32 derivations
   via the ``set_input_*`` methods.
3. Add partial signatures with
   :meth:`PsbtEditor.add_input_partial_sig` or sign directly with
   :meth:`PsbtEditor.sign_input`.
4. Finalise inputs with :meth:`PsbtEditor.finalize_input`.
5. Build the final :class:`Psbt` with :meth:`PsbtEditor.build`.
"""

from __future__ import annotations

import dataclasses
from typing import Self

from btx.psbt.models import Psbt, PsbtInput, PsbtOutput
from btx.transaction.parser import parse_tx


class PsbtEditor:
    """Fluent builder for constructing and editing PSBTs.

    The editor stores in-progress state as frozen
    :class:`PsbtInput` / :class:`PsbtOutput` dataclasses.  Each
    mutator replaces the affected element via
    :func:`dataclasses.replace`, preserving hashability.

    Use :meth:`from_tx` to create an editor from an unsigned transaction,
    or construct directly from an existing ``Psbt``.
    """

    def __init__(self, psbt: Psbt) -> None:
        """Initialize the editor from an existing ``Psbt``.

        Args:
            psbt: A ``Psbt`` instance to edit.
        """
        self.tx: bytes = psbt.tx
        self.unknown: dict[bytes, bytes] = dict(psbt.unknown)
        self.inputs: list[PsbtInput] = list(psbt.inputs)
        self.outputs: list[PsbtOutput] = list(psbt.outputs)

    @staticmethod
    def from_tx(tx: bytes) -> PsbtEditor:
        """Create a ``PsbtEditor`` from an unsigned transaction.

        Args:
            tx: Raw unsigned transaction bytes.

        Returns:
            A new ``PsbtEditor`` initialised with empty input/output maps.
        """
        parsed_tx, _ = parse_tx(tx)
        num_inputs = len(parsed_tx.inputs)
        num_outputs = len(parsed_tx.outputs)

        psbt = Psbt(
            tx=tx,
            inputs=tuple(PsbtInput() for _ in range(num_inputs)),
            outputs=tuple(PsbtOutput() for _ in range(num_outputs)),
        )
        return PsbtEditor(psbt)

    def _replace_input(self, vin: int, **changes: object) -> None:
        """Replace the input at *vin* via :func:`dataclasses.replace`."""
        self.inputs[vin] = dataclasses.replace(self.inputs[vin], **changes)

    def _replace_output(self, vout: int, **changes: object) -> None:
        """Replace the output at *vout* via :func:`dataclasses.replace`."""
        self.outputs[vout] = dataclasses.replace(self.outputs[vout], **changes)

    def set_input_utxo(
        self,
        vin: int,
        *,
        non_witness_utxo: bytes | None = None,
        witness_utxo: bytes | None = None,
    ) -> Self:
        """Set the UTXO data for a given input.

        Args:
            vin: Input index.
            non_witness_utxo: Raw non-witness UTXO (full previous tx).
            witness_utxo: Raw witness UTXO (value + scriptPubKey).

        Returns:
            ``self`` for chaining.
        """
        if non_witness_utxo is not None:
            self._replace_input(vin, non_witness_utxo=non_witness_utxo)
        if witness_utxo is not None:
            self._replace_input(vin, witness_utxo=witness_utxo)
        return self

    def set_input_redeem_script(self, vin: int, script: bytes) -> Self:
        """Set the redeem script for a PSBT input.

        Args:
            vin: Input index.
            script: Redeem script bytes.

        Returns:
            ``self`` for chaining.
        """
        self._replace_input(vin, redeem_script=script)
        return self

    def set_input_witness_script(self, vin: int, script: bytes) -> Self:
        """Set the witness script for a PSBT input.

        Args:
            vin: Input index.
            script: Witness script bytes.

        Returns:
            ``self`` for chaining.
        """
        self._replace_input(vin, witness_script=script)
        return self

    def set_input_sighash_type(self, vin: int, flag: int) -> Self:
        """Set the sighash type for a PSBT input.

        Args:
            vin: Input index.
            flag: Sighash flag integer.

        Returns:
            ``self`` for chaining.
        """
        self._replace_input(vin, sighash_type=flag)
        return self

    def add_input_partial_sig(self, vin: int, pubkey: bytes, sig: bytes) -> Self:
        """Add a partial signature for a PSBT input.

        Args:
            vin: Input index.
            pubkey: Public key bytes.
            sig: Signature bytes (DER + sighash byte).

        Returns:
            ``self`` for chaining.
        """
        inp = self.inputs[vin]
        new_sigs = dict(inp.partial_sigs)
        new_sigs[pubkey] = sig
        self._replace_input(vin, partial_sigs=new_sigs)
        return self

    def set_output_redeem_script(self, vout: int, script: bytes) -> Self:
        """Set the redeem script for a PSBT output.

        Args:
            vout: Output index.
            script: Redeem script bytes.

        Returns:
            ``self`` for chaining.
        """
        self._replace_output(vout, redeem_script=script)
        return self

    def set_output_witness_script(self, vout: int, script: bytes) -> Self:
        """Set the witness script for a PSBT output.

        Args:
            vout: Output index.
            script: Witness script bytes.

        Returns:
            ``self`` for chaining.
        """
        self._replace_output(vout, witness_script=script)
        return self

    def sign_input(
        self,
        vin: int,
        private_key: int,
        *,
        pubkey: bytes | None = None,
        sighash_flag: int | None = None,
    ) -> Self:
        """Sign a PSBT input with a private key.

        Parses the unsigned transaction, determines the script code and
        value from the PSBT input data, signs the input, and stores the
        resulting signature in ``partial_sigs``.

        Args:
            vin: Input index to sign.
            private_key: Private key as an integer.
            pubkey: Public key bytes.  If ``None``, derived from
                *private_key* via multiplication with GENERATOR_POINT.
            sighash_flag: Sighash flag.  If ``None``, uses the input's
                ``sighash_type`` or defaults to ``SIGHASH_ALL``.

        Returns:
            ``self`` for chaining.
        """
        from btx.curve import GENERATOR_POINT, multiply
        from btx.sighash.flag import SIGHASH_ALL
        from btx.signature.signer import sign_tx_input

        tx, _ = parse_tx(self.tx)
        inp = self.inputs[vin]

        flag = (
            sighash_flag
            if sighash_flag is not None
            else (inp.sighash_type if inp.sighash_type is not None else SIGHASH_ALL)
        )

        # Determine the script code from the PSBT input data.
        script_code = b""
        value = 0

        if inp.witness_script is not None:
            script_code = inp.witness_script
        elif inp.redeem_script is not None:
            script_code = inp.redeem_script
        else:
            # Derive the script code from the witness_utxo scriptPubKey
            if inp.witness_utxo is not None:
                from btx.encoding.varint import decode_varint

                offset = 0
                value, offset = decode_varint(inp.witness_utxo, offset)
                script_pubkey_len, offset = decode_varint(inp.witness_utxo, offset)
                script_pubkey = inp.witness_utxo[offset : offset + script_pubkey_len]
                from btx.script.classifier import classify_script_pubkey

                st = classify_script_pubkey(script_pubkey)
                if st in ("p2wpkh", "p2sh"):
                    from btx.script.builder import build_p2pkh

                    script_code = build_p2pkh(script_pubkey[-20:])
                else:
                    script_code = script_pubkey

        if pubkey is None:
            pubkey_point = multiply(private_key, GENERATOR_POINT)
            from btx.curve import serialize_public_key

            pubkey = serialize_public_key(pubkey_point)

        sig = sign_tx_input(
            tx, vin, private_key, script=script_code, value=value, sighash_flag=flag
        )
        new_sigs = dict(inp.partial_sigs)
        new_sigs[pubkey] = sig
        self._replace_input(vin, partial_sigs=new_sigs)
        return self

    def finalize_input(
        self,
        vin: int,
        *,
        final_script_sig: bytes | None = None,
        final_witness: tuple[bytes, ...] | None = None,
    ) -> Self:
        """Finalize a PSBT input with concrete script/witness data.

        Args:
            vin: Input index.
            final_script_sig: Final ``scriptSig`` bytes.
            final_witness: Final witness stack items.

        Returns:
            ``self`` for chaining.
        """
        if final_script_sig is not None:
            self._replace_input(vin, final_script_sig=final_script_sig)
        if final_witness is not None:
            self._replace_input(vin, final_script_witness=final_witness)
        return self

    def build(self) -> Psbt:
        """Construct and return the final ``Psbt``.

        Returns:
            A new frozen ``Psbt`` instance reflecting all edits.
        """
        return Psbt(
            tx=self.tx,
            inputs=tuple(self.inputs),
            outputs=tuple(self.outputs),
            unknown=dict(self.unknown),
        )