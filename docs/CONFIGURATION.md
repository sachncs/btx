# Configuration

## Settings Object — `btx.settings`

A global `Settings` singleton exposed as `btx.settings`:

```python
from btx import settings

settings.default_backend                # str | None (default None → "native")
```

`default_backend` is read from the `BTX_DEFAULT_BACKEND` environment
variable at import time; the singleton itself is a frozen dataclass so
derive a customised copy with `dataclasses.replace(settings, ...)`
rather than mutating in place.

## Backend Selection

Two backends are available:

| Backend | Class | Availability |
|---------|-------|--------------|
| Pure Python | `NativeBackend` | Always (default) |
| C-backed (libsecp256k1) | `LibsecpBackend` | Requires `uv sync --extra coincurve` or `uv pip install coincurve` |

The default backend is selected at import time via the
`BTX_DEFAULT_BACKEND` environment variable.

```bash
export BTX_DEFAULT_BACKEND=native   # activate pure Python (default)
export BTX_DEFAULT_BACKEND=libsecp  # activate C-backed (ImportError if coincurve missing)
```

The active backend singleton can be inspected at runtime:

```python
from btx.curve.dispatch import resolve_backend

backend = resolve_backend()         # → CurveBackend
```

Install a custom backend with the `set_backend` instance hook:

```python
from btx import LibsecpBackend
from btx.curve.dispatch import set_backend

set_backend(LibsecpBackend())       # activate C-backed explicitly
```

## Former Config File Support

The old `Config` class (file + env-var loading) has been replaced by
the simpler `Settings` singleton. Environment variables
(`BITCOIN_ECC_BACKEND`, `BITCOIN_NETWORK`, etc.) are no longer
supported; configuration is done programmatically or via the
`BTX_*` environment variables documented above.

