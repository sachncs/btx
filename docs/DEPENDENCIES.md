# Dependencies

## Runtime

| Package | Required | Condition | License | Purpose |
|---------|----------|-----------|---------|---------|
| `typer` | Yes (CLI only) | — | MIT | CLI argument parsing |
| `coincurve` | No | `[coincurve]` extra | Apache-2.0 AND MIT | Optional secp256k1 C bindings |

`typer` is only needed when using the CLI. The Python API has **zero** runtime dependencies outside the standard library.

## Development (`[dev]` extra)

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| `pytest` | ≥9.0.3 | MIT | Test runner |
| `pytest-cov` | ≥7.1.0 | MIT | Coverage reporting |
| `pytest-benchmark` | ≥5.2.3 | BSD-2-Clause | Benchmarks |
| `hypothesis` | ≥6.155.2 | MPL-2.0 | Property-based fuzz testing |
| `mypy` | ≥2.1.0 | MIT | Static type checking |
| `ruff` | ≥0.15.16 | MIT | Linter & formatter |
| `pre-commit` | ≥4.6.0 | MIT | Git hook runner |
| `pip-audit` | ≥2,<3 | Apache-2.0 | CVE scanning |

## CI

`uv sync --extra dev` installs all dev dependencies for CI.

## Build

| Tool | Version | License | Purpose |
|------|---------|---------|---------|
| `setuptools` | ≥82.0.1 | MIT | Build backend |

## Transitive (notable)

| Package | Transitive from | License | Note |
|---------|-----------------|---------|------|
| `click` | `typer` | BSD-3-Clause | Not a direct dependency |
| `shellingham` | `typer` | ISC | Shell detection |
| `rich` | `typer` | MIT | Pretty CLI output |
| `typing_extensions` | `typer` | MIT | Python version backport |
| `certifi` | `pip-audit` → `requests` | MPL-2.0 | CA certificate bundle |
| `pathspec` | `mypy` | MPL-2.0 | Gitignore pattern matching |
