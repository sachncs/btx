# btx maintenance and release-readiness plan

## Current state

`btx` is a source-distributed Python 3.12+ package. The public site is an
Astro application deployed to GitHub Pages at `/btx`; GitHub Pages is
configured to deploy from the Pages workflow, not from a branch-root legacy
build. Public documentation is standalone Astro content and does not load
repository Markdown at runtime.

The package is not published to PyPI. All installation instructions therefore
use a source checkout or a direct Git URL. The release workflow keeps PyPI
publication behind an explicit dispatch input and environment approval.

## Completed work

- Built a reproducible local environment with `uv`, npm, and the project
  lockfiles.
- Hardened parser, provider, batch, health, and CLI behavior with regression
  coverage.
- Reworked the public site around source installation, accurate capability
  claims, accessible responsive UI, and base-path-safe assets.
- Published standalone pages for getting started, API, architecture, testing,
  security, contributing, and changelog content.
- Removed the obsolete root Pages entrypoints.
- Removed the obsolete Read the Docs configuration, docs build ignore rule,
  and placeholder HTML docs entrypoint.
- Rewrote the repository README as the concise source-install and contributor
  entry point.
- Updated repository documentation to match the current provider factories,
  configuration boundary, dependency model, supported commands, and release
  state.
- Removed the obsolete `todo/` phase checklist; current work belongs here and
  in the changelog.
- Used atomic commits and pushed the requested changes to `origin/master`.

## Verification gates

Run from a fresh checkout:

```bash
uv sync --extra dev --frozen
cd site && npm ci && cd ..
make test-all
```

The gate covers Python formatting, linting, type checking, tests and
coverage, dependency auditing, Astro checks, production build, standalone
documentation checks, and `/btx` base-path validation.

For a clean-room run:

```bash
make docker-test
```

For the live deployment, verify the homepage and documentation routes:

```text
https://sachncs.github.io/btx/
https://sachncs.github.io/btx/docs/
https://sachncs.github.io/btx/docs/getting-started/
```

## Ongoing release policy

- Do not advertise `pip install btx` until a deliberate PyPI release is
  approved and published.
- Keep `coincurve` optional; the pure-Python backend is the compatibility
  baseline.
- Keep network access isolated behind the services layer.
- Add regression tests before changing malformed-input, provider, CLI, or
  concurrency behavior.
- Update the standalone site documentation and repository guidance together
  when public APIs or distribution state changes.
