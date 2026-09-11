# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
from pytest import fixture


@fixture(autouse=True)
def reset_settings() -> None:
    """Reset the global settings singleton before each test.

    The current :class:`btx.settings.Settings` is a frozen dataclass,
    so this fixture is a no-op kept for backward compatibility — it
    no longer mutates the singleton.  Tests that need a non-default
    :class:`btx.settings.Settings` should construct one locally.
    """
    pass
