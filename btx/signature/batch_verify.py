# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Sequential ECDSA signature verification for multiple signatures.

Provides :func:`verify_all` for verifying multiple signatures in one
call.  Each signature is verified individually via
:func:`btx.signature.check.verify_signature`, which means verification
is sequential and a single invalid signature short-circuits the batch
via Python's short-circuiting ``all``.

This is *not* a Bellare–Neven multi-signature verification scheme
and does **not** achieve the throughput gains of true batch
verification; the name reflects the convenience of the API rather
than a cryptographic primitive.  It is, however, simpler and
safer: a failure in any signature is immediately attributable to
that signature, with no risk of a false batch failure masking an
individual forgery.
"""

from __future__ import annotations

from btx.curve.point import Point
from btx.signature.check import verify_signature


def verify_all(
    message_hashes: list[bytes],
    der_signatures: list[bytes],
    public_keys: list[Point],
) -> bool:
    """Verify a sequence of ECDSA signatures.

    All signatures must be valid for the function to return ``True``.
    A single invalid signature makes the entire batch fail.

    Args:
        message_hashes: 32-byte message hashes, one per signature.
        der_signatures: DER-encoded signatures, one per message.
        public_keys: Public-key ``Point`` instances, one per message.

    Returns:
        ``True`` iff **all** signatures are valid.

    Raises:
        ValueError: If the three lists differ in length.
    """
    n = len(message_hashes)
    if len(der_signatures) != n or len(public_keys) != n:
        raise ValueError(
            f"Length mismatch: {len(message_hashes)} messages, "
            f"{len(der_signatures)} signatures, {len(public_keys)} keys."
        )

    zipped = zip(message_hashes, der_signatures, public_keys, strict=True)
    return all(verify_signature(m, s, pk) for m, s, pk in zipped)


# Backward-compatible alias for the misnomer that has stuck.
batch_verify = verify_all

__all__ = ["verify_all", "batch_verify"]
