"""R source adapters are scoped, read-only when requested and fail closed."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import format_repo as formatting
from scripts import lint_repo as linting

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", ["main.R", "main.r", "courses/r/lesson.R"])
def test_r_source_suffixes_are_explicit(name: str) -> None:
    assert formatting.language_for(name) == "r"
    assert formatting.language_for("report.Rmd") is None
    assert formatting.language_for("report.qmd") is None


def test_r_format_check_and_write_preserve_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "example.R"
    path.write_text("value<-1\nstop('must not execute')\n")
    path.chmod(0o640)
    original = path.read_bytes()
    inode = path.stat().st_ino

    def formatter(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        assert command[:2] == ["Rscript", "--vanilla"]
        assert command[-1] == "format" and command[-2].endswith("scripts/r_source_tools.R")
        assert kwargs["cwd"] == tmp_path
        return subprocess.CompletedProcess(
            command, 0, kwargs["input"].replace(b"value<-1", b"value <- 1"), b""
        )

    monkeypatch.setattr(subprocess, "run", formatter)
    assert not formatting.format_group("r", [path.name], tmp_path, check=True)
    assert path.read_bytes() == original
    assert formatting.format_group("r", [path.name], tmp_path, check=False)
    assert path.read_text() == "value <- 1\nstop('must not execute')\n"
    assert path.stat().st_ino == inode and path.stat().st_mode & 0o777 == 0o640


def test_r_formatter_failure_never_replaces_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "bad.R"
    path.write_text("broken <- function( {\n")
    original = path.read_bytes()
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 1, b"untrusted replacement", b"parse rejected"
        ),
    )
    assert not formatting.format_group("r", [path.name], tmp_path, check=False)
    assert path.read_bytes() == original


def test_r_lint_uses_fixed_stdin_operation_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "source.R"
    path.write_text("stop('this source must not execute')\n")
    calls: list[list[str]] = []

    def check(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append(command)
        assert kwargs["input"] == path.read_bytes() and kwargs["capture_output"]
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", check)
    original = path.read_bytes()
    assert linting.syntax_errors(path.name, tmp_path, "r") == []
    assert linting.lint_group("r", [path.name], tmp_path)
    assert [call[-1] for call in calls] == ["parse", "lint"]
    assert path.read_bytes() == original


def test_internal_r_handoff_preserves_public_argument_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/format-policy.json").write_text('{"exclude":[],"preserve":[]}')
    (tmp_path / "one.R").write_text("value <- 1\n")
    (tmp_path / "two.py").write_text("value = 2\n")
    monkeypatch.setattr(formatting, "ROOT", tmp_path)
    monkeypatch.setattr(shutil, "which", lambda _: "/prepared/tool")
    selected: list[str] = []

    def select_language(language: str, paths: list[str], root: Path, check: bool) -> bool:
        selected.append(language)
        return True

    monkeypatch.setattr(
        formatting,
        "format_group",
        select_language,
    )
    monkeypatch.setattr(
        formatting,
        "generated_views",
        lambda *args: pytest.fail("A language pass must not regenerate readers"),
    )
    assert (
        formatting.main(
            ["--language", "python", "--language", "r", "--only-language", "r", "--check"]
        )
        == 0
    )
    assert selected == ["r"]
    with pytest.raises(SystemExit):
        formatting.main(["--language", "not-a-language", "--only-language", "r"])


def test_r_helper_actual_parser_does_not_evaluate_source(tmp_path: Path) -> None:
    executable = shutil.which("Rscript")
    if executable is None:
        pytest.skip("Actual R helper is qualified in the separate R tools image")
    helper = ROOT / "scripts/r_source_tools.R"
    source = "writeLines('executed', 'must-not-exist')\n"
    result = subprocess.run(
        [executable, "--vanilla", str(helper), "parse"],
        input=source,
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "must-not-exist").exists()
    invalid = subprocess.run(
        [executable, "--vanilla", str(helper), "parse"],
        input="function( {",
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert invalid.returncode != 0
