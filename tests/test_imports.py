# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Test that the top-level public API imports correctly and has no circular deps."""

import btx


def test_version_exists() -> None:
    assert hasattr(btx, "__version__")


def test_core_imports() -> None:
    assert btx.Point is not None
    assert btx.GENERATOR is not None
    assert btx.INFINITY is not None
    assert btx.CURVE_ORDER is not None
    assert btx.FIELD_PRIME is not None


def test_function_imports() -> None:
    assert callable(btx.inverse)
    assert callable(btx.sqrt)
    assert callable(btx.add)
    assert callable(btx.double)
    assert callable(btx.multiply)
    assert callable(btx.is_on_curve)
    assert callable(btx.encode_der)
    assert callable(btx.decode_der)
    assert callable(btx.parse_sec)
    assert callable(btx.serialize_sec)
    assert callable(btx.parse_tx)
    assert callable(btx.sighash_legacy)
    assert callable(btx.extract_signatures)
    assert callable(btx.linearize_signatures)
    assert callable(btx.verify_sig)


def test_class_imports() -> None:
    assert btx.CurveBackend is not None
    assert btx.NativeBackend is not None
    assert btx.Tx is not None
    assert btx.TxIn is not None
    assert btx.TxOut is not None
    assert btx.OutPoint is not None
    assert btx.Witness is not None
    assert btx.Record is not None
    assert btx.Psbt is not None


def test_exception_imports() -> None:
    assert btx.NotInvertible is not None
    assert btx.PointError is not None
    assert btx.ParsingError is not None


def test_removed_exceptions_gone() -> None:
    """Verify removed exception classes no longer exist."""
    import btx.exceptions

    for name in (
        "InvalidSignature",
        "InvalidDerSignature",
        "NotInvertibleError",
        "InvalidLinearCoefficientError",
        "NonInvertibleLinearCoefficientError",
    ):
        assert not hasattr(btx.exceptions, name), f"{name} should have been removed"


def test_derive_linear_coefficients_import_path() -> None:
    """Verify derive_linear_coefficients imports from correct module."""
    from btx.signature.linearization.coefficients import (
        LinearCoefficientCollection,
        LinearCoefficientRecord,
        derive_linear_coefficients,
    )

    assert callable(derive_linear_coefficients)
    assert LinearCoefficientCollection is not None
    assert LinearCoefficientRecord is not None


def test_attack_imports_correct() -> None:
    """Verify attack module imports from correct locations."""
    from btx.signature.attack import (
        NonceReuseGroup,
        RecoveredKey,
        detect_nonce_reuse,
        recover_from_nonce_reuse,
    )

    assert RecoveredKey is not None
    assert NonceReuseGroup is not None
    assert callable(recover_from_nonce_reuse)
    assert callable(detect_nonce_reuse)


def test_signer_imports() -> None:
    """Verify signer module imports."""
    from btx.signature import sign, sign_tx_input

    assert callable(sign)
    assert callable(sign_tx_input)


def test_settings_import() -> None:
    assert btx.settings is not None
    assert hasattr(btx.settings, "strict_mode")
    assert hasattr(btx.settings, "default_backend")
    assert hasattr(btx.settings, "max_extraction_inputs")


def test_no_circular_imports() -> None:
    """Import every package module and submodule explicitly."""
