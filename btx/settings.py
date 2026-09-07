# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Application-wide configuration for the btx package.

A frozen, dataclass-based configuration holder exposed as the
module-level :data:`settings` instance.  Values are read once from
environment variables at import time, so configuration is a single
explicit boundary rather than scattered ``os.environ`` reads.

Supported environment variables:

- ``BTX_DEFAULT_BACKEND`` – preferred curve backend name
  (``"native"`` or ``"libsecp"``).  When unset, the native
  (pure-Python) backend is used and ``coincurve`` is auto-probed only
  when ``"libsecp"`` is explicitly requested.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

_VALID_BACKENDS = (None, "native", "libsecp")


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable holder of package-level configuration.

    Attributes:
        default_backend: Preferred curve backend name (``"native"`` or
            ``"libsecp"``), or ``None`` for auto-detect.
    """

    default_backend: str | None = None

    def __post_init__(self) -> None:
        """Validate ``default_backend`` is one of the allowed values.

        Raises:
            ValueError: If ``default_backend`` is not ``None``,
                ``"native"``, or ``"libsecp"``.
        """
        if self.default_backend not in _VALID_BACKENDS:
            raise ValueError(
                f"default_backend must be one of {_VALID_BACKENDS}, "
                f"got {self.default_backend!r}."
            )

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Settings(default_backend={self.default_backend!r})"


def _resolve_default_backend() -> str | None:
    """Read ``BTX_DEFAULT_BACKEND`` from the environment, or ``None``."""
    value = os.environ.get("BTX_DEFAULT_BACKEND")
    if value is None or value == "":
        return None
    # Normalise: accept a few common spellings for robustness.
    normalized = value.strip().lower().replace("_", "").replace("-", "")
    aliases = {
        "native": "native",
        "libsecp": "libsecp",
        "libsecp256k1": "libsecp",
        "coincurve": "libsecp",
    }
    return aliases.get(normalized, normalized)


settings = Settings(default_backend=_resolve_default_backend())
