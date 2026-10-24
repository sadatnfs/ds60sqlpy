"""Keep opt-in PostgreSQL proofs together while unit tests use other workers."""

from __future__ import annotations

import os

import pytest

SHARED_POSTGRES_GROUP = "shared-postgres"
SHARED_POSTGRES_FIXTURES = {
    "live_database": "DS60_TEST_DATABASE_URL",
    "live_psql": "DS60_SQL_EXPANSION_TEST_URL",
}
_RESOURCE_ERROR = pytest.StashKey[str]()


def pytest_configure(config: pytest.Config) -> None:
    # Keep serial collection valid even when pytest-xdist is not installed.
    config.addinivalue_line(
        "markers", "xdist_group(name): keep a shared-resource group on one loadgroup worker"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Group fixture consumers before xdist appends its scheduling node IDs.

    Both opt-in URLs may identify the same database. The expansion proofs own a
    fixed concurrency schema, while execution proofs change roles and inspect
    active sessions. Fixture dependency closure includes indirect consumers;
    ordinary Python, HTTP servers on port zero, and tmp_path tests stay parallel.
    """

    shared = [
        item
        for item in items
        if SHARED_POSTGRES_FIXTURES.keys() & set(getattr(item, "fixturenames", ()))
    ]
    if not shared:
        return
    # xdist deliberately resets dist/numprocesses inside workers. Its saved
    # loadgroup flag, rather than those controller options, is authoritative.
    worker = hasattr(config, "workerinput")
    processes = config.getoption("numprocesses", default=None)
    distribution = config.getoption("dist", default="no")
    parallel = worker or (processes not in (None, 0) and distribution != "no")
    loadgroup = (
        config.getoption("loadgroup", default=False) if worker else distribution == "loadgroup"
    )
    for item in shared:
        fixtures = set(getattr(item, "fixturenames", ()))
        enabled = any(
            os.environ.get(variable)
            for fixture, variable in SHARED_POSTGRES_FIXTURES.items()
            if fixture in fixtures
        )
        if enabled and parallel and not loadgroup:
            item.stash[_RESOURCE_ERROR] = (
                "Shared PostgreSQL proofs require --dist loadgroup when using -n. "
                "Use pytest -n 4 --dist loadgroup, or pytest -n 0 for serial execution."
            )
        for marker in item.iter_markers("xdist_group"):
            group = marker.args[0] if marker.args else marker.kwargs.get("name", "default")
            if group != SHARED_POSTGRES_GROUP:
                # Multiple xdist marks form a new combined group. That would
                # split these tests away from the other PostgreSQL consumers.
                item.stash[_RESOURCE_ERROR] = (
                    f"{item.nodeid} uses shared PostgreSQL and cannot also use "
                    f"xdist_group({group!r}). Keep only {SHARED_POSTGRES_GROUP!r}."
                )
        item.add_marker(pytest.mark.xdist_group(name=SHARED_POSTGRES_GROUP))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    # A collection-hook UsageError is poorly relayed by xdist workers. A normal
    # setup failure is readable and happens before pytest initializes fixtures.
    error = item.stash.get(_RESOURCE_ERROR, None)
    if error is not None:
        pytest.fail(error, pytrace=False)
