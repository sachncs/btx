# Configuration

## Settings Object — `btx.settings`

A global `Settings` singleton exposed as `btx.settings`:

```python
from btx import settings

settings.default_backend                # immutable str | None snapshot
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
export BTX_DEFAULT_BACKEND=libsecp  # set before importing btx
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

## Configuration boundary

`btx` has one supported configuration variable: `BTX_DEFAULT_BACKEND`.
Network providers are configured explicitly by constructing a provider or by
using one of the provider factory helpers; there is no implicit network or
configuration-file state.

