from __future__ import annotations

import subprocess

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.doctor import _course_database_diagnostic, diagnose


def test_course_database_check_is_noninteractive_and_read_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[str] = []
    observed_environment: dict[str, str] = {}

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed.extend(command)
        environment = kwargs.get("env")
        assert isinstance(environment, dict)
        observed_environment.update(environment)
        return subprocess.CompletedProcess(command, 0, "advanced_sql_training\n", "")

    connection = "postgresql://" + "ds60:temporary@localhost:5432/advanced_sql_training"
    monkeypatch.setenv("DS60_DATABASE_URL", connection)
    monkeypatch.setattr(subprocess, "run", fake_run)

    diagnostic = _course_database_diagnostic("psql")

    assert diagnostic.status == "pass"
    assert "-w" in observed
    assert observed[-1] == "SELECT current_database();"
    assert connection not in observed
    assert observed_environment["PGDATABASE"] == connection
    assert "DS60_DATABASE_URL" not in observed_environment
    assert not any(fragment in observed for fragment in ("CREATE", "DROP", "00_setup.sql"))


def test_course_database_check_refuses_an_unapproved_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DS60_DATABASE_URL",
        "postgresql://learner:" + "do-not-print@db.example/valuable_database",
    )

    def unexpected_run(*_: object, **__: object) -> None:
        raise AssertionError("an unapproved database must not be contacted")

    monkeypatch.setattr(subprocess, "run", unexpected_run)

    diagnostic = _course_database_diagnostic("psql")

    assert diagnostic.status == "warn"
    assert "was not contacted" in diagnostic.detail
    assert "do-not-print" not in diagnostic.detail


def test_course_database_check_refuses_query_database_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DS60_DATABASE_URL",
        "postgresql:///advanced_sql_training?dbname=postgres",
    )

    def unexpected_run(*_: object, **__: object) -> None:
        raise AssertionError("a URL database override must not be contacted")

    monkeypatch.setattr(subprocess, "run", unexpected_run)

    diagnostic = _course_database_diagnostic("psql")

    assert diagnostic.status == "warn"
    assert "was not contacted" in diagnostic.detail


def test_course_database_failure_does_not_echo_connection_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = "postgresql://learner:" + "do-not-print@localhost:5432/advanced_sql_training"
    monkeypatch.setenv("DS60_DATABASE_URL", connection)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command,
            2,
            "",
            f"could not connect using {connection}",
        ),
    )

    diagnostic = _course_database_diagnostic("psql")

    assert diagnostic.status == "warn"
    assert "do-not-print" not in diagnostic.detail


def test_doctor_can_skip_all_database_contact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("ds60sqlpy.doctor.shutil.which", lambda name: name)

    def refuse_database_contact(psql: str):  # type: ignore[no-untyped-def]
        raise AssertionError(f"database contact is forbidden during bootstrap: {psql}")

    monkeypatch.setattr(
        "ds60sqlpy.doctor._course_database_diagnostic",
        refuse_database_contact,
    )

    diagnostics = diagnose(Catalog.load(), check_database=False)

    assert all(item.name != "Course database" for item in diagnostics)
