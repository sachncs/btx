# btx production hardening and source-first site redesign

## Objective

Make `btx` dependable to install, test, operate, document, and eventually release while redesigning the public Astro site as a documentation-first developer portal.

The current public site is visually polished but materially misleading for the current release state: it promotes PyPI even though the project is not published there, advertises `0` runtime dependencies even though `typer` is required, and hard-codes project metrics. The implementation must make source installation the only current installation promise and keep the future PyPI release path safely gated.

## Current baseline

- The site is a static Astro 4 + Tailwind application deployed to GitHub Pages at `/btx`.
- The Python project targets Python 3.12–3.14 and uses `uv.lock` plus optional `dev` and `coincurve` extras.
- `uv` is available locally; a plain `uv run pytest` does not provide pytest, while `uv run --extra dev pytest tests/ -q` completes successfully.
- `site/node_modules` is absent, so site checks/builds currently cannot run until `npm ci` is executed.
- The existing release workflow publishes to TestPyPI and PyPI on `v*` tags; this must be guarded before PyPI is intentionally launched.
- Existing working-tree changes, including `uv.lock`, are user-owned and must not be reverted or overwritten.

## Implementation plan

### 1. Build a reproducible local validation environment

- Add a native bootstrap path using the existing lockfiles:
  - `uv sync --extra dev --frozen`
  - `cd site && npm ci`
- Add a single top-level validation command, preferably `make test-all`, that runs:
  - Python formatting/lint checks with Ruff.
  - mypy for package and tests.
  - pytest with coverage and the existing benchmark expectations.
  - `pip-audit`.
  - Astro type checking and production build.
- Add a Docker-based clean-room runner with pinned Python, `uv`, Node, and npm versions. It must execute the same validation command without depending on host virtual environments, `node_modules`, or caches.
- Document supported tool versions, bootstrap commands, troubleshooting, and the distinction between the fast native loop and clean-room Docker validation.
- Keep generated environments and build output ignored; do not commit `.venv`, `site/node_modules`, `site/dist`, or Docker caches.

### 2. Redesign the site around source installation and developer trust

- Replace every active PyPI install CTA, badge, footer link, and command with source-first messaging.
- Lead with both supported paths:
  - Clone and editable install using a virtual environment.
  - Direct Git URL installation using `python -m pip`.
- Show optional development and `coincurve` installation separately from the minimal runtime path.
- Rewrite the information hierarchy around:
  - What `btx` does.
  - A short source-install quick start.
  - Supported Bitcoin/transaction capabilities.
  - Core-versus-services/network boundaries.
  - Reliability, testing, compatibility, and security posture.
  - Documentation, API reference, architecture, testing, changelog, issues, and security policy.
- Keep the dark emerald identity but reduce decorative density, excessive terminal mockups, and unsupported marketing claims.
- Remove or generate hard-coded numbers such as test counts, coverage, and performance claims. If generated values are not available during the site build, use qualitative wording instead.
- Add robust responsive navigation, semantic landmarks, skip links, keyboard-visible focus, accessible tab behavior, sufficient contrast, reduced-motion support, and mobile layout QA.
- Make clipboard actions resilient: use the Clipboard API when available, provide a fallback, and expose a visible/announced copied state without relying on color alone.
- Correct base-path, canonical, Open Graph, favicon, and 404 behavior for GitHub Pages.
- Validate all internal and external links; use repository-relative links or stable GitHub URLs where dedicated docs hosting is not guaranteed.

### 3. Align project documentation and public claims

- Update the root README, `docs/getting-started.md`, FAQ, site README, and site copy from one source-install policy.
- State accurately that `typer` is the runtime dependency and that `coincurve` is optional acceleration.
- Document the supported Python range, expected source-install workflow, CLI smoke test, API smoke test, development setup, and test commands.
- Keep the future PyPI instructions in a clearly marked release-only section if useful, but do not present them as available installation paths.
- Remove stale or inconsistent links, branch names, version labels, and claims that cannot be verified from the repository.

### 4. Harden the Python runtime and service boundaries

- Audit parser limits and malformed-input behavior for transactions, scripts, PSBTs, signatures, and serialized data; preserve deterministic failure modes and actionable domain errors.
- Standardize the public exception hierarchy where it improves caller handling, without changing successful API behavior unnecessarily.
- Review CLI parsing, output formats, logging, error messages, and exit codes for stable shell/automation use.
- Harden blockchain providers with explicit URL validation, bounded response sizes, connect/read timeouts, retryable-versus-terminal error classification, exponential backoff, and clear broadcast failure semantics.
- Verify batch and concurrent operations propagate worker failures, support cancellation/shutdown, preserve deterministic result ordering where promised, and do not leak resources.
- Make health checks report version, active backend, optional capabilities, and actionable failures without implying network availability or cryptographic audit status.
- Add regression tests for all identified defects before changing behavior.

### 5. Make CI and release workflows safe and representative

- Run the native-equivalent Python and site checks in CI from clean environments.
- Add a site job that uses `npm ci`, Astro checks, production build, and link/screenshot validation where practical.
- Make the development dependency path explicit with `uv sync --extra dev --frozen`.
- Pin GitHub Actions and major tool versions consistently, preserving existing security-conscious commit pins where present.
- Keep GitHub Pages deployment limited to site changes, verify the built artifact, and retain the `404.html` fallback.
- Gate TestPyPI/PyPI publication behind an explicit release input or environment approval so pushing a `v*` tag cannot publish accidentally.
- Preserve build artifacts, provenance attestation, and GitHub Releases for the future publication workflow.

## Verification and acceptance criteria

### Local native checks

From a fresh checkout:

```bash
uv sync --extra dev --frozen
cd site && npm ci && cd ..
make test-all
```

The command must finish with passing Python tests, coverage threshold, Ruff, mypy, dependency audit, Astro checks, and production build.

### Clean-room checks

The Docker runner must execute the same `make test-all` workflow successfully without using host `.venv`, `site/node_modules`, or host caches.

### Site acceptance

- No active PyPI installation promise appears before publication.
- Both source-install paths work as documented.
- The primary above-the-fold action is understandable within seconds.
- Desktop and mobile layouts are readable, navigable, and visually coherent.
- Keyboard-only and reduced-motion behavior are usable.
- Production build works under the `/btx` base path and produces a valid 404 fallback.

### Package acceptance

- Existing public APIs and supported transaction behavior remain compatible.
- Malformed input fails predictably with documented exceptions/messages.
- Provider timeouts/retries and broadcast failures are bounded and testable.
- Concurrent/batch operations shut down cleanly and report failures.
- Health and CLI output remain machine-consumable and accurate.

## Explicit non-goals

- Do not publish to PyPI as part of this work.
- Do not introduce a new hosted backend or runtime service for the static site.
- Do not perform a gratuitous public API rewrite.
- Do not discard or reset unrelated working-tree changes.

