"""Bounded failure artifacts keep startup evidence without publishing local secrets."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SOURCE = (
    Path(__file__).resolve().parents[1] / "courses/python-web/projects/web-lab/check_project.py"
)


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("web_failure_check", SOURCE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def workspace(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "owned"
    evidence = root / ".workshop/evidence"
    evidence.mkdir(parents=True)
    (root / ".workshop/password").write_text("fixture-database-password\n")
    (root / ".workshop/signing-key").write_text("fixture-signing-material\n")
    return root, evidence


def test_startup_context_survives_while_credentials_and_headers_are_removed(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    (evidence / "start.log").write_text(
        "psycopg.OperationalError: connection to postgres:5432 refused\n"
        "raw fixture-database-password and fixture-signing-material\n"
        "Authorization: Bearer fixture-auth-value\n"
        "Cookie: session=fixture-cookie-value\n"
        "Cookie\x1b[0m: session=fixture-colored-cookie\n"
        "Set-Cookie: session=fixture-response-cookie; HttpOnly\n"
        '{"password": "fixture-body-password", "signing_key": "fixture-body-signing"}\n'
        'headers={"authorization": "Basic fixture-basic-auth"}\n'
        'escaped={\\"Cookie\\": \\"session=fixture-escaped-cookie\\"}\n'
        # secret-scan: allow-fixture
        "upstream postgresql://fixture-user:fixture-url-password@db.example/data\n"
        "download https://example.invalid/object?X-Amz-Signature=fixture-signed-value\n"
        '  - fill("fixture-browser-password")\n'
        "migration has not started\n"
    )
    result = load().collect_failure_diagnostics(evidence, root)
    serialized = json.dumps(result)
    for value in [
        "fixture-database-password",
        "fixture-signing-material",
        "fixture-auth-value",
        "fixture-cookie-value",
        "fixture-colored-cookie",
        "fixture-response-cookie",
        "fixture-body-password",
        "fixture-body-signing",
        "fixture-basic-auth",
        "fixture-escaped-cookie",
        "fixture-url-password",
        "fixture-signed-value",
        "fixture-browser-password",
    ]:
        assert value not in serialized
    assert "connection to postgres:5432 refused" in serialized
    assert "migration has not started" in serialized
    assert [row["name"] for row in result["logs"]] == ["start.log"]


def test_partial_tail_line_cannot_expose_unlabelled_authorization_suffix(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    (evidence / "start.log").write_text(
        "Authorization: Bearer " + "a" * 20_000 + "fixture-hidden-suffix\n"
        "safe final startup error\n"
    )
    result = load().collect_failure_diagnostics(evidence, root)
    text = result["logs"][0]["text"]
    assert "fixture-hidden-suffix" not in text
    assert text == "safe final startup error"
    assert result["logs"][0]["truncated"] is True


def test_allowlist_and_total_budget_do_not_publish_other_workspace_files(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    module = load()
    for name in module.DIAGNOSTIC_LOG_NAMES:
        (evidence / name).write_text("bounded useful context\n" * 1000)
    (evidence / "private-unlisted.log").write_text("fixture-unlisted-private-value")
    (root / ".workshop/credentials.json").write_text('{"private":"fixture-private-json"}')
    result = module.collect_failure_diagnostics(evidence, root)
    assert sum(len(row["text"].encode("utf-8")) for row in result["logs"]) <= 16384
    assert {row["name"] for row in result["logs"]} <= set(module.DIAGNOSTIC_LOG_NAMES)
    assert all(len(row["text"].encode("utf-8")) <= 4096 for row in result["logs"])
    assert result["omitted_logs"]
    assert "fixture-unlisted-private-value" not in json.dumps(result)
    assert "fixture-private-json" not in json.dumps(result)


def test_linked_log_is_not_followed(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("fixture-outside-secret")
    (evidence / "start.log").symlink_to(outside)
    result = load().collect_failure_diagnostics(evidence, root)
    assert result["logs"] == [] and result["omitted_logs"] == ["start.log"]
    assert "fixture-outside-secret" not in json.dumps(result)


def test_linked_private_redaction_input_withholds_all_new_log_text(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    key = root / ".workshop/signing-key"
    key.unlink()
    outside = tmp_path / "outside.txt"
    outside.write_text("fixture-outside-secret")
    key.symlink_to(outside)
    (evidence / "start.log").write_text("fixture-outside-secret")
    result = load().collect_failure_diagnostics(evidence, root)
    assert result["logs"] == [] and "warning" in result
    assert "fixture-outside-secret" not in json.dumps(result)


def test_special_log_file_is_refused_without_waiting_for_a_writer(tmp_path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("This platform has no POSIX FIFO creation")
    root, evidence = workspace(tmp_path)
    os.mkfifo(evidence / "start.log")
    result = load().collect_failure_diagnostics(evidence, root)
    assert result["logs"] == [] and result["omitted_logs"] == ["start.log"]


def test_redacted_startup_evidence_remains_in_final_report_after_cleanup(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    module = load()
    start = evidence / "start.log"
    start.write_text("connection refused\npassword=fixture-database-password\n")
    record: dict[str, Any] = {
        "accepted": False,
        "failure": {"type": "RuntimeError", "message": "password=fixture-database-password"},
    }
    report = tmp_path / "top-level-receipts.json"
    module.retain_failure_diagnostics(record, evidence, root)
    module.write_report(report, record)
    start.unlink()
    (evidence / "cleanup.log").write_text(
        "owned containers removed\nCookie: fixture-cleanup-cookie\n"
    )
    record["containers_cleaned"] = True
    module.retain_failure_diagnostics(record, evidence, root)
    module.write_report(report, record)
    final = json.loads(report.read_text())
    logs = {row["name"]: row["text"] for row in final["failure_diagnostics"]["logs"]}
    assert "connection refused" in logs["start.log"]
    assert "owned containers removed" in logs["cleanup.log"]
    assert final["containers_cleaned"] is True
    assert "fixture-database-password" not in report.read_text()
    assert "fixture-cleanup-cookie" not in report.read_text()
    assert report.stat().st_size < 65536


def test_success_receipt_does_not_gain_failure_diagnostics(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    record = {"accepted": True}
    load().retain_failure_diagnostics(record, evidence, root)
    assert record == {"accepted": True}


def test_redaction_expansion_still_obeys_each_log_budget(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    (root / ".workshop/password").write_text("x")
    (evidence / "start.log").write_text("x " * 1900)
    module = load()
    result = module.collect_failure_diagnostics(evidence, root)
    assert len(result["logs"][0]["text"].encode()) <= module.DIAGNOSTIC_TAIL_BYTES
    assert result["logs"][0]["truncated"] is True


@pytest.mark.parametrize(
    "service_timeout,cleanup_fails,report_failures",
    [
        (False, False, ()),
        (True, False, ()),
        (True, True, ()),
        (False, False, (1,)),
        (True, False, (1,)),
        (False, False, (2,)),
        (True, True, (1, 2)),
    ],
)
def test_qualifier_embeds_failure_logs_before_and_after_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    service_timeout: bool,
    cleanup_fails: bool,
    report_failures: tuple[int, ...],
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load()
    source = tmp_path / "source"
    source.mkdir()
    (source / "README.md").write_text("Owned test fixture source")
    monkeypatch.setattr(module, "SOURCE", source)
    monkeypatch.setattr(module, "inspect_containers", lambda *_args: {})
    monkeypatch.setattr(
        module,
        "image_identity",
        lambda *_args: {"id": "sha256:" + "a" * 64, "system": "linux", "architecture": "arm64"},
    )
    owned = tmp_path / "fresh-owned-copy"
    report = tmp_path / "uploaded-receipts.json"
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        log = kwargs.get("log")
        output, code = "", 0
        if command[:3] in [["docker", "volume", "inspect"], ["docker", "network", "inspect"]]:
            if "--format" in command:
                output = "python-web-lab\n"
            else:
                code = 1
        elif command[:2] == ["docker", "info"]:
            output = "linux arm64\n"
        elif command == ["./workshop", "prepare"]:
            private = owned / ".workshop"
            (private / "settings.env").write_text("WORKSHOP_PROJECT=owned-test\n")
            (private / "password").write_text("fixture-database-password\n")
            (private / "signing-key").write_text("fixture-signing-material\n")
        elif command[:2] == ["docker", "run"]:
            output = str(kwargs["input_text"])
        elif command == ["./workshop", "start"]:
            assert isinstance(log, Path)
            log.write_text("connection refused\nAuthorization: Bearer fixture-auth-value\n")
            raise RuntimeError("Controlled startup failure")
        elif "logs" in command:
            output = "temporary database server running\nCookie: fixture-service-cookie\n"
            if service_timeout:
                assert isinstance(log, Path)
                log.write_text(output)
                raise subprocess.TimeoutExpired(command, 1, output=output)
        elif "down" in command:
            # The earlier embedded failure survives even removal of the original log.
            (owned / ".workshop/evidence/start.log").unlink()
            output = "owned containers removed\npassword=fixture-database-password\n"
            if cleanup_fails:
                assert isinstance(log, Path)
                log.write_text(output)
                raise RuntimeError("Controlled cleanup failure")
        if isinstance(log, Path):
            log.write_text(output)
        return subprocess.CompletedProcess(command, code, output, "")

    monkeypatch.setattr(module, "run", fake_run)
    original_writer = module.write_report
    write_count = 0

    def report_writer(path: Path, record: dict[str, Any]) -> None:
        nonlocal write_count
        write_count += 1
        if write_count in report_failures:
            raise OSError("Controlled evidence storage failure")
        original_writer(path, record)

    monkeypatch.setattr(module, "write_report", report_writer)
    args = argparse.Namespace(
        workspace=owned,
        report=report,
        confirm_disposable=True,
        browser_python=Path(sys.executable),
        image="prepared-web:test",
        postgres_image="prepared-pg:test",
    )
    with pytest.raises(RuntimeError, match="qualification failed") as caught:
        module.qualify(args)
    assert str(caught.value.__cause__) == "Controlled startup failure"
    assert any("down" in command for command in commands)
    assert write_count == 2
    if 2 in report_failures:
        assert "final report unavailable" in str(caught.value)
        assert "retained report:" not in str(caught.value)
        if report.exists():
            partial = json.loads(report.read_text())
            assert partial["accepted"] is False
            assert partial["finalization"] == "owned-cleanup-pending"
        else:
            assert 1 in report_failures
        warning = json.loads(capsys.readouterr().err)
        assert warning["accepted"] is False
        phases = {item["phase"] for item in warning["diagnostic_warnings"]}
        assert "final" in phases
        if 1 in report_failures:
            assert "initial" in phases
        assert "fixture-database-password" not in json.dumps(warning)
        return
    stored = json.loads(report.read_text())
    if 1 in report_failures:
        assert {"phase": "initial", "type": "OSError"} in stored["diagnostic_warnings"]
    assert stored["accepted"] is False
    assert stored["failure"]["message"] == "Controlled startup failure"
    if cleanup_fails:
        assert stored["cleanup_failure"]["message"] == "Controlled cleanup failure"
        assert stored.get("containers_cleaned") is not True
    else:
        assert stored["containers_cleaned"] is True and stored["volume_preserved"] is True
    if service_timeout:
        assert stored["service_log_failure"]["type"] == "TimeoutExpired"
    logs = {row["name"]: row["text"] for row in stored["failure_diagnostics"]["logs"]}
    assert "connection refused" in logs["start.log"]
    assert "temporary database server running" in logs["services.log"]
    assert "owned containers removed" in logs["cleanup.log"]
    assert all(
        secret not in report.read_text()
        for secret in [
            "fixture-auth-value",
            "fixture-service-cookie",
            "fixture-database-password",
            "fixture-signing-material",
        ]
    )
    assert any("down" in command for command in commands)


@pytest.mark.parametrize("name", ["password", "signing-key"])
@pytest.mark.parametrize("remove", [True, False])
def test_missing_or_empty_redaction_input_keeps_only_previous_safe_text(
    tmp_path: Path, name: str, remove: bool
) -> None:
    root, evidence = workspace(tmp_path)
    (evidence / "start.log").write_text("connection refused; fixture-database-password\n")
    module = load()
    record: dict[str, Any] = {"accepted": False}
    module.retain_failure_diagnostics(record, evidence, root)
    previous = record["failure_diagnostics"]["logs"]
    private = root / ".workshop" / name
    if remove:
        private.unlink()
    else:
        private.write_text("")
    (evidence / "start.log").write_text("fixture-database-password fixture-signing-material\n")
    module.retain_failure_diagnostics(record, evidence, root)
    assert record["failure_diagnostics"]["logs"] == previous
    assert "warning" in record["failure_diagnostics"]
    assert "fixture-database-password" not in json.dumps(record)
    assert "fixture-signing-material" not in json.dumps(record)


def test_timeout_preserves_partial_output_for_sanitized_failure_receipt(tmp_path: Path) -> None:
    root, evidence = workspace(tmp_path)
    module = load()
    command = [
        sys.executable,
        "-c",
        (
            "import sys,time;print('decisive startup detail',flush=True);"
            "print('Authorization: Bearer fixture-timeout-auth',file=sys.stderr,flush=True);"
            "time.sleep(10)"
        ),
    ]
    with pytest.raises(subprocess.TimeoutExpired):
        module.run(command, cwd=root, log=evidence / "start.log", timeout=1)
    assert "decisive startup detail" in (evidence / "start.log").read_text()
    record: dict[str, Any] = {"accepted": False}
    module.retain_failure_diagnostics(record, evidence, root)
    assert "decisive startup detail" in json.dumps(record)
    assert "fixture-timeout-auth" not in json.dumps(record)


def test_timeout_is_not_replaced_if_partial_output_log_cannot_be_written(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load()
    original = subprocess.TimeoutExpired(["owned-command"], 1, output=b"partial detail")

    def timeout(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise original

    def cannot_write(*_args: Any, **_kwargs: Any) -> int:
        raise PermissionError("controlled diagnostic write failure")

    monkeypatch.setattr(module.subprocess, "run", timeout)
    monkeypatch.setattr(Path, "write_text", cannot_write)
    with pytest.raises(subprocess.TimeoutExpired) as caught:
        module.run(["owned-command"], cwd=tmp_path, log=tmp_path / "start.log", timeout=1)
    assert caught.value is original
