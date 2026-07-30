from __future__ import annotations

from pathlib import Path

from ds60sqlpy.secret_scan import local_sensitive_paths, scan_text, sensitive_filename


def test_secret_scan_detects_token_without_echoing_it() -> None:
    fake_key = "AK" + "IA" + ("A" * 16)

    findings = scan_text(Path("sample.txt"), f"token={fake_key}\n")

    assert [(finding.line, finding.kind) for finding in findings] == [(1, "AWS access key")]
    assert all(fake_key not in repr(finding) for finding in findings)


def test_secret_scan_allows_documented_disposable_and_placeholder_urls() -> None:
    text = "\n".join(
        (
            "postgresql://ds60:ds60@localhost:5432/advanced_sql_training",
            "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training",
        )
    )

    assert scan_text(Path(".env.example"), text) == []


def test_secret_scan_reports_unapproved_url_without_reproducing_password() -> None:
    credential_url = "postgresql://real-user:" + "not-a-fixture@database.example/course"

    findings = scan_text(Path("bad.txt"), credential_url)

    assert [(finding.line, finding.kind) for finding in findings] == [(1, "credential-bearing URL")]
    assert credential_url not in repr(findings[0])


def test_secret_scan_allows_explicit_test_fixture_marker() -> None:
    credential_url = "postgresql://fixture:" + "not-real@example.test/course"

    assert (
        scan_text(
            Path("fixture.py"),
            f'# secret-scan: allow-fixture\nvalue = "{credential_url}"',
        )
        == []
    )


def test_sensitive_filename_allows_only_the_documented_environment_template() -> None:
    assert sensitive_filename(Path(".env"))
    assert sensitive_filename(Path("private.pem"))
    assert sensitive_filename(Path("credentials.json"))
    assert not sensitive_filename(Path(".env.example"))
    assert not sensitive_filename(Path("fixtures.json"))


def test_local_sensitive_paths_checks_ignored_files_but_prunes_venv(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("local only\n", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "credentials.json").write_text("{}\n", encoding="utf-8")
    generated = tmp_path / ".venv"
    generated.mkdir()
    (generated / "ignored.pem").write_text("generated\n", encoding="utf-8")

    relative = {path.relative_to(tmp_path) for path in local_sensitive_paths(tmp_path)}

    assert relative == {Path(".env"), Path("nested/credentials.json")}
