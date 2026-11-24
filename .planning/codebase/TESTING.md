---
last_mapped_commit: a7b9bee89d73119a71319d41d2bf7ec2fefffc8e
last_mapped_at: 2026-11-23
---
<!-- refreshed: 2026-11-23 -->
# Testing Patterns

**Analysis Date:** 2026-11-23

## Test Framework

**Runner:**
- Pytest (minimum declared version `8.0`) with `pytest-xdist`; test configuration is in `pyproject.toml`.
- Shared fixtures and xdist resource grouping are in `tests/conftest.py`.

**Assertion Library:**
- Use pytest's built-in `assert`, `pytest.raises`, fixtures, and parametrization.
- `pytest-cov` is included in the `quality` optional dependency group in `pyproject.toml`.

**Run Commands:**
```bash
# Parallel suite, default TEST_WORKERS=4
make test
# Parallel suite with a chosen worker count
make test TEST_WORKERS=2
# Serial debugging run (-n 0)
make test-serial
uv run --no-sync python -m pytest -n 4 --dist loadgroup
```

The `Makefile` targets use `pytest -n $(TEST_WORKERS) --dist loadgroup`; `pyproject.toml` adds `-ra`, strict config/marker validation, and the same loadgroup distribution. Do not remove `--dist loadgroup` when using parallel workers because shared PostgreSQL tests rely on it.

## Test File Organization

**Location:**
- Most application, curriculum, browser-contract, CI, and repository checks are under `tests/`.
- Additional suites live beside specialized content or packages: `bridge/tests/`, `bridge/professional/tests/`, `python/professional/tests/`, and `packages/spark-likelihood/tests/` (including `packages/spark-likelihood/tests/torch_training/`).
- `sql/professional/tests/` contains SQL fixture/verification scripts rather than pytest modules.

**Naming:**
- Pytest modules use `test_*.py`; examples include `tests/test_catalog.py`, `bridge/tests/test_days01_04.py`, and `packages/spark-likelihood/tests/test_dataframe.py`.
- Test functions use `test_<behavior>` names; use parameterization for behavior that varies by input.

**Structure:**
```text
tests/
├── conftest.py
├── test_<application-area>.py
└── test_<curriculum-or-tooling-area>.py
bridge/tests/
python/professional/tests/
packages/spark-likelihood/tests/
```

Pytest discovers the directories declared by `testpaths` in `pyproject.toml`. Preserve this layout or update the test configuration when adding a new test root.

## Test Structure

**Suite Organization:**
```python
def test_invalid_input_is_rejected() -> None:
    with pytest.raises(ValueError, match="invalid log level"):
        load_settings({}, log_level="verbose")
```

This follows the assertion and exception style in `bridge/tests/test_days01_04.py`; use descriptive tests that state an observable contract.

**Patterns:**
- Use plain functions and local setup; no mandatory base test class is configured.
- Use `@pytest.mark.parametrize` for input matrices, as in `tests/test_classroom_http.py`.
- Prefer `tmp_path` for filesystem isolation and `monkeypatch` for controlled environment/module changes; examples appear in `tests/test_catalog.py` and `tests/test_sql_json_transport.py`.
- Use teardown in `finally` for manually started servers/threads, as in `tests/test_classroom_http.py`.
- `tests/conftest.py` registers/assigns the `shared-postgres` xdist group to tests that consume opt-in shared database fixtures and rejects unsafe scheduling.

## Mocking

**Framework:** Pytest fixtures and `monkeypatch`; fakes and small protocol-compatible test doubles are common. `unittest.mock` is available but is not the dominant pattern in the sampled suites.

**Patterns:**
```python
monkeypatch.setattr(module, "ROOT", tmp_path)
with pytest.raises(ValueError, match="expected message"):
    operation(invalid_input)
```

These patterns appear in `tests/test_release050_boundaries.py` and `bridge/tests/test_days01_04.py`.

**What to Mock:**
- Replace external boundaries or process-global state when testing deterministic local behavior; for example, `tests/test_sql_json_transport.py` installs controlled `psycopg` module doubles and supplies a fake connection/cursor contract.
- Use fakes to assert interaction and transaction outcomes, as in `bridge/tests/test_days01_04.py`.

**What NOT to Mock:**
- Do not replace the behavior the test is intended to verify. Loopback HTTP behavior is exercised against a real temporary server in `tests/test_classroom_http.py`.
- Keep opt-in PostgreSQL integration checks connected to their explicitly disposable database; the actual connection fixture is in `tests/test_execution.py`.

## Fixtures and Factories

**Test Data:**
```python
def resolver(tmp_path: Path) -> LinkResolver:
    return LinkResolver(repo_root=tmp_path, source_path=tmp_path / "lesson.md", targets={})
```

This fixture-local factory pattern appears in `tests/test_rich_content.py`. Other tests build focused fakes directly in the test module, such as the `Connection` and `Cursor` doubles in `tests/test_sql_json_transport.py`.

**Location:**
- Shared pytest hooks are in `tests/conftest.py`; area-specific factories and fakes generally stay in the corresponding test module.
- Real database fixtures are localized to `tests/test_execution.py` and `tests/test_sql_expansion_live.py`.

## Coverage

**Requirements:** No minimum coverage threshold is configured. `pyproject.toml` enables branch coverage for `ds60sqlpy`, requests missing-line reporting, and skips fully covered files. `pytest-cov` is installed in the quality extra, but no canonical coverage command or `fail_under` value is declared.

**View Coverage:**
```bash
# No repository-standard coverage command is configured.
```

## Test Types

**Unit Tests:**
- Broad deterministic tests cover application logic, catalog and curriculum contracts, error handling, state transitions, and repository tooling; examples include `tests/test_catalog.py` and `tests/test_sql_json_transport.py`.

**Integration Tests:**
- Opt-in PostgreSQL tests in `tests/test_execution.py` and `tests/test_sql_expansion_live.py` skip unless their test-database environment is explicitly configured. `tests/conftest.py` keeps shared consumers in one xdist group.
- CI provisions PostgreSQL 17 and executes database checks in `.github/workflows/ci.yml`.

**E2E Tests:**
- Browser behavior uses the framework-free Node checker `scripts/check_classroom_ui.mjs`, run by `.github/workflows/ci.yml`.
- HTTP integration behavior is exercised against a local threaded server in `tests/test_classroom_http.py`; this is not a separate browser E2E framework.
- No single dedicated E2E test framework is configured.

## Common Patterns

**Async / Background Work Testing:**
```python
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    # Perform loopback requests and assertions.
    ...
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
```

This lifecycle pattern is used in `tests/test_classroom_http.py`; adapt teardown for the resource under test.

**Error Testing:**
```python
with pytest.raises(HTTPError) as response:
    request_invalid_state()
assert response.value.code == 403
```

`tests/test_classroom_http.py` verifies both exception and protocol status. For domain contracts, use `pytest.raises(..., match=...)` as in `bridge/tests/test_days01_04.py`.

## CI and Quality Gates

- `.github/workflows/ci.yml` runs core pytest checks on Python 3.11 and 3.12 using four workers with `--dist loadgroup`; it also runs a PostgreSQL-backed job and separate format, lint, type, curriculum, notebook, and UI checks.
- `Makefile` exposes `make check` for repository validations plus the test suite. `docs/validation.md` documents focused checks and advises recording actual passed, failed, and skipped totals rather than assuming optional integrations ran.

## Evidence

- `pyproject.toml`
- `Makefile`
- `tests/conftest.py`
- `tests/test_catalog.py`
- `tests/test_classroom_http.py`
- `tests/test_execution.py`
- `tests/test_sql_expansion_live.py`
- `tests/test_sql_json_transport.py`
- `tests/test_rich_content.py`
- `bridge/tests/test_days01_04.py`
- `packages/spark-likelihood/tests/test_dataframe.py`
- `.github/workflows/ci.yml`
- `scripts/check_classroom_ui.mjs`
- `docs/validation.md`

---

*Testing analysis: 2026-11-23*
