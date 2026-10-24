import subprocess
from pathlib import Path

import pytest

from scripts.check_public_release import scan, scan_text


def test_reports_private_residue_without_reproducing_values() -> None:
    # public-release: synthetic-fixture
    text = "OpenAI classroom\n/home/private-owner/project/\nhttps://tracker.example.corp/ticket"
    findings = scan_text("README.md", text)
    assert [item.category for item in findings] == [
        "assistant branding",
        "personal home path",
        "internal host URL",
    ]
    assert [item.line for item in findings] == [1, 2, 3]
    assert all("private-owner" not in repr(item) for item in findings)
    assert all("tracker.example" not in repr(item) for item in findings)


def test_fixture_exemption_is_test_only_and_single_line() -> None:
    marker = "# public-release: synthetic-fixture\n"
    # public-release: synthetic-fixture
    sample = "ChatGPT fixture\nCodex product branding\n"
    assert len(scan_text("tests/test_policy.py", marker + sample)) == 1
    assert len(scan_text("README.md", marker + sample)) == 2


def test_docker_credential_exclusion_is_exact() -> None:
    # public-release: synthetic-fixture
    assert not scan_text(".dockerignore", ".codex\n")
    # public-release: synthetic-fixture
    assert scan_text(".dockerignore", "# Powered by Codex\n")


def test_portable_tree_scan_excludes_private_runtime_data(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("A local classroom.\n")
    (tmp_path / ".learning").mkdir()
    # public-release: synthetic-fixture
    (tmp_path / ".learning/private.md").write_text("/home/private-owner/notes/\n")
    (tmp_path / "guides").mkdir()
    # public-release: synthetic-fixture
    (tmp_path / "guides/setup.md").write_text("/Users/private-owner/source/\n")
    findings, count = scan(tmp_path)
    assert count == 2
    assert [(item.path, item.category) for item in findings] == [
        ("guides/setup.md", "personal home path")
    ]


def test_linked_paths_are_reported_without_reading_the_target(tmp_path: Path) -> None:
    secret = tmp_path / "private.txt"
    secret.write_text("not part of the source tree")
    source = tmp_path / "source"
    source.mkdir()
    try:
        (source / "linked.txt").symlink_to(secret)
    except OSError:
        pytest.skip("Symlink creation is unavailable on this host")
    findings, count = scan(source)
    assert count == 0
    assert [(item.path, item.category) for item in findings] == [
        ("linked.txt", "linked source path")
    ]


def test_technical_and_portable_examples_remain_publishable() -> None:
    text = (
        "https://docs.oracle.com/en/java/\nhttps://github.com/example/project\n~/workspace/course\n"
    )
    assert not scan_text("docs/setup.md", text)


def test_cached_git_paths_do_not_follow_a_linked_ancestor(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    subprocess.run(["git", "init", "-q", str(source)], check=True)
    content = source / "content"
    content.mkdir()
    (content / "example.md").write_text("Published source")
    subprocess.run(["git", "add", "content/example.md"], cwd=source, check=True)
    content.rename(tmp_path / "original-content")
    outside = tmp_path / "outside"
    outside.mkdir()
    # public-release: synthetic-fixture
    (outside / "example.md").write_text("/home/private-owner/workplace/\n")
    try:
        content.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlink creation is unavailable on this host")
    findings, count = scan(source)
    assert count == 0
    assert any(item.path == "content/example.md" for item in findings)
    assert all(item.category == "linked source path" for item in findings)


def test_junction_check_is_used_before_directory_descent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import check_public_release as policy

    junction = tmp_path / "junction"
    junction.mkdir()
    (junction / "outside.md").write_text("Private external source")
    from ds60sqlpy.curriculum_framework import is_content_link

    real_check = is_content_link
    monkeypatch.setattr(
        policy, "is_content_link", lambda path: path == junction or real_check(path)
    )
    findings, count = scan(tmp_path)
    assert count == 0
    assert [(item.path, item.category) for item in findings] == [("junction", "linked source path")]


def test_one_placeholder_does_not_hide_another_private_windows_path() -> None:
    # public-release: synthetic-fixture
    source = r"C:\Users\Ada\course and C:\Users\private-owner\workplace"
    findings = scan_text("docs/setup.md", source)
    assert len(findings) == 1
    assert findings[0].category == "personal Windows path"


def test_policy_definitions_do_not_exempt_unrelated_branding() -> None:
    # public-release: synthetic-fixture
    source = '"""Powered by OpenAI."""\n'
    assert scan_text("scripts/check_public_release.py", source)
    own_source = (
        Path(__file__).resolve().parents[1] / "scripts/check_public_release.py"
    ).read_text()
    assert not scan_text("scripts/check_public_release.py", own_source)


def test_internal_dns_names_are_case_insensitive() -> None:
    # public-release: synthetic-fixture
    findings = scan_text("docs/setup.md", "https://TRACKER.EXAMPLE.CORP/ticket")
    assert [item.category for item in findings] == ["internal host URL"]


def test_distribution_mode_reports_private_directories_without_reading_notes(
    tmp_path: Path,
) -> None:
    notes = tmp_path / "docs/.serena/memories"
    notes.mkdir(parents=True)
    # public-release: synthetic-fixture
    (notes / "private.md").write_text("/home/private-owner/workplace/")
    findings, count = scan(tmp_path, payload=True)
    assert count == 0
    assert [(item.path, item.category) for item in findings] == [
        ("docs/.serena", "private directory in distribution")
    ]


def test_staging_omits_nested_private_tool_metadata(tmp_path: Path) -> None:
    from scripts.build_app import stage_course

    source = tmp_path / "source"
    (source / "docs").mkdir(parents=True)
    (source / "docs/guide.md").write_text("Public course guide")
    # public-release: synthetic-fixture
    for name in (".serena", ".codex"):
        folder = source / "docs" / name
        folder.mkdir()
        (folder / "notes.md").write_text("Private tool session")
    destination = tmp_path / "distribution"
    stage_course(destination, source_root=source)
    assert sorted(
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    ) == ["docs/guide.md"]
    assert not scan(destination, payload=True)[0]


def test_missing_scan_root_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="existing source directory"):
        scan(tmp_path / "missing")


def test_tracked_nested_private_notes_are_reported_without_content_reads(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    notes = tmp_path / "docs/.serena/memories"
    notes.mkdir(parents=True)
    (notes / "private.md").write_text("Private note")
    subprocess.run(["git", "add", "docs"], cwd=tmp_path, check=True)
    findings, count = scan(tmp_path)
    assert count == 0
    assert [(item.path, item.category) for item in findings] == [
        ("docs/.serena/memories/private.md", "tracked private runtime path")
    ]


def test_distribution_rejects_environment_overrides(tmp_path: Path) -> None:
    (tmp_path / ".env.production").write_text("EXAMPLE=private")
    findings, count = scan(tmp_path, payload=True)
    assert count == 0
    assert [(item.path, item.category) for item in findings] == [
        (".env.production", "private file in distribution")
    ]


@pytest.mark.parametrize("prefix", ["", "é = 1; "])
def test_policy_literal_exemption_does_not_cover_trailing_comments(prefix: str) -> None:
    # public-release: synthetic-fixture
    source = prefix + 'RULES = (("x", re.compile(r"OpenAI")),) # Powered by OpenAI'
    findings = scan_text("scripts/check_public_release.py", source)
    assert len(findings) == 1
    assert findings[0].category == "assistant branding"


def test_private_directory_detection_is_case_insensitive(tmp_path: Path) -> None:
    private = tmp_path / "docs/.SERENA"
    private.mkdir(parents=True)
    (private / "note.md").write_text("Private note")
    findings, count = scan(tmp_path, payload=True)
    assert count == 0
    assert findings[0].category == "private directory in distribution"
