---
last_mapped_commit: a7b9bee89d73119a71319d41d2bf7ec2fefffc8e
last_mapped_at: 2026-11-23
---
<!-- refreshed: 2026-11-23 -->
# Coding Conventions

**Analysis Date:** 2026-11-23

## Naming Patterns

**Files:**
- Use `snake_case.py` for Python implementation and script modules; use `test_<area>.py` for pytest modules. Examples: `src/ds60sqlpy/classroom_http.py`, `scripts/check_modules.py`, and `tests/test_classroom_http.py`.
- Course artifact filenames are owned by the curriculum and may include subject or lesson IDs; do not rename them to match Python module conventions. The formatter policy treats generated lesson artifacts separately in `scripts/format-policy.json`.

**Functions:**
- Use `snake_case` for Python functions and methods, including test functions named `test_<behavior>`. Examples: `Catalog.load` and `find_repo_root` in `src/ds60sqlpy/catalog.py`, and `test_catalog_prerequisite_graph_is_acyclic` in `tests/test_catalog.py`.
- Prefix implementation helpers that are not public with `_` where appropriate, as in `_derived_outcome` imported by `tests/test_catalog.py`.

**Variables:**
- Use `snake_case` for Python variables and parameters; use uppercase names for module-level constants such as `TRACK_ORDER` in `src/ds60sqlpy/catalog.py`.

**Types:**
- Use `PascalCase` for classes, protocols, and data types. The immutable `Lesson` dataclass in `src/ds60sqlpy/catalog.py` and test contracts in `tests/test_sql_json_transport.py` are representative.
- Add parameter and return annotations to maintained Python APIs and tests; examples include `Catalog.find_repo_root` in `src/ds60sqlpy/catalog.py` and fixtures in `tests/conftest.py`.

## Code Style

**Formatting:**
- Use `./scripts/format-repo` to format maintained sources and `./scripts/format-repo --check` to verify without editing. `make format` and `make format-check` are equivalent entrypoints in `Makefile`.
- Formatting is coordinated by `scripts/format_repo.py` and `scripts/format-policy.json`, with isolated toolchains for Python and the repository's other maintained languages. Preserve generated and historically qualified files according to the policy rather than formatting them independently.
- Follow `.editorconfig`: UTF-8, LF, final newline, trailing-space cleanup (except Markdown), four-space Python indentation, and two-space indentation for JSON/YAML and SQL.

**Linting:**
- Run `./scripts/lint-repo` or `make lint`; the wrappers in `scripts/lint-repo` and `scripts/format-repo` provide read-only checks through the prepared toolchains.
- Python lint settings live in `pyproject.toml`: Ruff targets Python 3.11 with a 100-character line length and selects `E`, `F`, `I`, `UP`, `B`, `SIM`, `C4`, and `PTH`. Mypy is configured with `strict = true`, `explicit_package_bases = true`, and paths for `src` and `packages/spark-likelihood/src`.
- Python tests relax the `S101` Ruff rule via the `tests/*` per-file setting in `pyproject.toml`; do not generalize that exception to production code.
- The pre-commit hooks in `.pre-commit-config.yaml` run the sensitive-content scan, `scripts/lint-repo`, and `scripts/format-repo --check`.

## Import Organization

**Order:**
1. `from __future__ import annotations`, when used.
2. Python standard-library imports.
3. Third-party dependencies.
4. Project-local imports.

The sequence is visible in `src/ds60sqlpy/catalog.py`, `tests/test_classroom_http.py`, and `tests/test_sql_json_transport.py`; Ruff's `I` rule is enabled in `pyproject.toml`, so keep imports sortable.

**Path Aliases:**
- Not detected for Python imports. Package imports use `ds60sqlpy...`; `pyproject.toml` configures `src` as the package source and mypy search path.

**Public Exports / Barrel Files:**
- Prefer imports from the defining module for tests and internal callers, as in `tests/test_catalog.py` importing from `ds60sqlpy.catalog`. No broad Python barrel-export convention is configured.

## Error Handling

**Patterns:**
- Validate invalid inputs at the owning boundary and raise a suitable exception; production examples include `ValueError` for unsupported lesson tracks and runners in `src/ds60sqlpy/catalog.py`.
- Keep error behavior explicit in tests with `pytest.raises`, including message checks where the contract requires them; see `tests/test_sql_json_transport.py` and `bridge/tests/test_days01_04.py`.
- Domain-specific exceptions are used where they clarify a contract, for example `ObjectiveError` in `packages/spark-likelihood/tests/test_dataframe.py`. There is no single repository-wide result/error type.

## Logging

**Framework:** Python's standard `logging` module is used in maintained Python code, including `src/ds60sqlpy/reader_tex.py`; `bridge/tests/test_days01_04.py` exercises log behavior with `caplog`.

**Patterns:**
- Use the relevant module's logger and avoid logging credentials or other sensitive values. The test in `bridge/tests/test_days01_04.py` checks that a customer name is absent from log output; `scripts/scan_secrets.py` is also wired into `.pre-commit-config.yaml`.
- Logging APIs and message conventions vary by runtime and component; no single structured logging schema is configured across the repository.

## Comments

**When to Comment:**
- Explain non-obvious safety, isolation, compatibility, or ownership constraints; examples include the scheduler safeguards in `tests/conftest.py` and generated-file preservation notes in `scripts/format-policy.json`.
- Use docstrings for public classes/functions and complex helper behavior, as in `src/ds60sqlpy/catalog.py` and `scripts/format_repo.py`.

**JSDoc/TSDoc:**
- Not detected as a repository-wide convention; use the language-appropriate documentation style for the file being changed.

## Function Design

**Size:** No enforced line-count limit is configured. Keep functions focused on one boundary or behavior; existing APIs use annotations and named helper functions, such as `find_repo_root` in `src/ds60sqlpy/catalog.py`.

**Parameters:** Prefer explicit, typed parameters and keyword-only options for optional behavior when it improves call-site clarity; examples include `Catalog.__init__` and `catalog_order_key` in `src/ds60sqlpy/catalog.py`.

**Return Values:** Annotate return types for maintained Python functions. Use immutable value objects where appropriate; `Lesson` in `src/ds60sqlpy/catalog.py` is a frozen, slotted dataclass.

## Module Design

**Exports:** Keep implementation in its owning module and import symbols from that module. Tests do this in `tests/test_catalog.py` and `tests/test_classroom_http.py`.

**Barrel Files:** No general barrel-file convention is configured. Keep new Python implementation under `src/ds60sqlpy/` and use the direct package/module path.

## Evidence

- `pyproject.toml`
- `.editorconfig`
- `.pre-commit-config.yaml`
- `scripts/format_repo.py`
- `scripts/format-policy.json`
- `src/ds60sqlpy/catalog.py`
- `src/ds60sqlpy/reader_tex.py`
- `tests/test_catalog.py`
- `tests/test_classroom_http.py`
- `tests/test_sql_json_transport.py`
- `tests/conftest.py`
- `bridge/tests/test_days01_04.py`

---

*Convention analysis: 2026-11-23*
