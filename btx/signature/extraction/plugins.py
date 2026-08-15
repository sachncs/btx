# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Lightweight plugin registry for custom script-path extractors.

A tiny in-memory registry for :class:`~btx.signature.extraction.engine.BaseExtractor`
subclasses:

- :data:`registry` – the underlying ``{name: plugin}`` mapping.
- :func:`register_plugin` – add a plugin by its ``name`` attribute.
- :func:`unregister_plugin` – remove a previously registered plugin.
- :func:`get_plugin` – look up a plugin by name.
- :func:`list_plugins` – return the names of all registered plugins.

The five built-in extractors (Legacy, P2WPKH, P2WSH, P2SH-SegWit,
Taproot) are registered automatically by
:func:`btx.signature.extraction.engine.register_builtin_extractors`,
which is called by :func:`~btx.signature.extraction.engine.extract_signatures`
on first use.  External code can register additional plugins to
support new script types without modifying this library.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from btx.signature.extraction.engine import BaseExtractor


@runtime_checkable
class ExtractorPlugin(Protocol):
    """Structural interface for extractor plugins.

    Implemented structurally by :class:`~btx.signature.extraction.engine.BaseExtractor`
    and any third-party plugin registered via :func:`register_plugin`.
    """

    name: str

    def can_handle(self, script_type: str, is_segwit: bool) -> bool: ...

    def extract(
        self, tx: object, vin: int, txin: object, script_pubkey: bytes, value: int
    ): ...


registry: dict[str, BaseExtractor] = {}
"""The process-wide extractor-plugin registry.

Keys are plugin ``name`` attributes; values are the plugin
instances.  Mutate only through :func:`register_plugin` and
:func:`unregister_plugin` to keep the registry consistent.
"""


def register_plugin(plugin: BaseExtractor) -> None:
    """Register a custom extractor plugin.

    The plugin's :attr:`~BaseExtractor.name` is used as the registry
    key; registering a plugin whose name is already present
    overwrites the previous entry.

    Args:
        plugin: The plugin instance to register.
    """
    registry[plugin.name] = plugin


def unregister_plugin(name: str) -> None:
    """Remove a plugin from the registry.

    Args:
        name: The plugin name to remove.  Silently does nothing if
            no plugin is registered under that name.
    """
    registry.pop(name, None)


def get_plugin(name: str) -> BaseExtractor | None:
    """Retrieve a registered plugin by name.

    Args:
        name: The plugin name to look up.

    Returns:
        The plugin instance, or ``None`` if no plugin is registered
        under *name*.
    """
    return registry.get(name)


def list_plugins() -> list[str]:
    """Return the names of all registered plugins."""
    return list(registry)


__all__ = [
    "ExtractorPlugin",
    "get_plugin",
    "list_plugins",
    "register_plugin",
    "registry",
    "unregister_plugin",
]
