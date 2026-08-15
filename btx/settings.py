# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Application-wide settings singleton for the btx package.

A frozen, dataclass-based configuration holder exposed as the
module-level :data:`settings` instance.  One knob is currently
exposed:

- :attr:`Settings.default_backend` – preferred curve backend name
  (``"native"``, ``"libsecp"``, or ``None`` for auto-detect).

All access is via standard frozen-dataclass attribute reads (no
locks needed; the instance is immutable).  Mutations must use
:func:`dataclasses.replace`, which is atomic at the Python level
but **not** safe across concurrent threads — callers requiring
thread-safe mutation should wrap ``replace()`` in an external lock.

The instance is created at module load time:
``python -c "import btx; print(btx.settings.default_backend)"``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable singleton holding package-level configuration.

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
        allowed = (None, "native", "libsecp")
        if self.default_backend not in allowed:
            raise ValueError(
                f"default_backend must be one of {allowed}, "
                f"got {self.default_backend!r}."
            )

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Settings(default_backend={self.default_backend!r})"


settings = Settings()