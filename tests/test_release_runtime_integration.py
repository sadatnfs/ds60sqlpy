"""Cross-layer release regressions without invoking Docker or learner toolchains."""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from ds60sqlpy.modules import LANGUAGES, SOURCE_SUFFIXES
from ds60sqlpy.worker_operations import PROFILES, validate_operation
from scripts import check_classroom_profiles as smoke
from scripts import format_repo as formatting
from scripts import lint_repo

ROOT = Path(__file__).resolve().parents[1]
JULIA_INPUTS = (
    "docker/workers/Dockerfile.julia",
    "docker/workers/native/releases.lock.json",
    "docker/workers/native/install_native.py",
    "docker/workers/julia/Project.toml",
    "docker/workers/julia/Manifest.toml",
)


@dataclass
class Wrapper:
    root: Path
    bash: str
    environment: dict[str, str]
    log: Path

    def invoke(
        self, *arguments: str, settings: dict[str, str] | None = None
    ) -> tuple[subprocess.CompletedProcess[str], list[list[str]]]:
        self.log.unlink(missing_ok=True)
        result = subprocess.run(
            [self.bash, str(self.root / "scripts/format-repo"), *arguments],
            cwd=self.root,
            env={**self.environment, **(settings or {})},
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        calls = [json.loads(line) for line in self.log.read_text().splitlines()]
        return result, calls


@pytest.fixture
def tool_wrapper(tmp_path: Path) -> Wrapper:
    bash = shutil.which("bash")
    if bash is None or os.name == "nt":
        pytest.skip("The supported wrapper runs in Bash on Linux, macOS or WSL 2")
    root = tmp_path / "source tree with spaces"
    inputs = (
        "scripts/format-repo",
        "docker/formatting/Dockerfile",
        "docker/formatting/Dockerfile.r",
        "docker/workers/r/packages.lock.json",
        "docker/workers/r/install_packages.py",
        *JULIA_INPUTS,
    )
    for name in inputs:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    binaries = tmp_path / "tools"
    binaries.mkdir()
    log = tmp_path / "calls.jsonl"
    docker = binaries / "docker"
    docker.write_text(
        f"#!{sys.executable}\n"
        + """import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ["REVIEW_DOCKER_LOG"]).open("a") as stream:
    stream.write(json.dumps(args) + "\\n")
if args[0] == "info":
    print("linux")
elif args[:2] == ["context", "inspect"]:
    print("unix:///fixture/engine.sock")
elif args[:2] == ["image", "inspect"]:
    missing = (os.environ.get("REVIEW_MISSING_JULIA")
               and args[2].startswith("ds60-formatting-julia:"))
    sys.exit(1 if missing else 0)
elif args[0] == "run":
    is_julia = any(x.startswith("ds60-formatting-julia:") for x in args)
    if os.environ.get("REVIEW_FAIL_JULIA") and is_julia:
        sys.exit(37)
elif args[0] != "build":
    sys.exit(99)
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"DOCKER_CONTEXT", "DOCKER_HOST"}
    }
    environment.update(PATH=str(binaries) + os.pathsep + environment.get("PATH", ""))
    environment["REVIEW_DOCKER_LOG"] = str(log)
    return Wrapper(root, bash, environment, log)


def tool_runs(calls: list[list[str]]) -> list[list[str]]:
    return [call for call in calls if call[0] == "run"]


def image_for(call: list[str]) -> str:
    return next(part for part in call if part.startswith("ds60-formatting"))


@pytest.mark.parametrize("option", ["--check", "--lint"])
def test_julia_only_routes_to_prepared_toolchain_with_readonly_source(
    tool_wrapper: Wrapper, option: str
) -> None:
    result, calls = tool_wrapper.invoke(option, "--language=julia")
    assert result.returncode == 0, result.stderr
    runs = tool_runs(calls)
    assert len(runs) == 1 and image_for(runs[0]).startswith("ds60-formatting-julia:")
    assert runs[0][-2:] == ["--only-language", "julia"]
    assert option in runs[0]
    assert any(
        part == f"type=bind,src={tool_wrapper.root},dst=/workspace,readonly" for part in runs[0]
    )
    assert "--network=none" in runs[0] and "--read-only" in runs[0]
    assert not any(call[0] == "build" for call in calls)


def test_mixed_selection_checks_julia_before_main_and_does_not_repeat_it(
    tool_wrapper: Wrapper,
) -> None:
    result, calls = tool_wrapper.invoke("--check", "--language", "julia", "--language", "python")
    assert result.returncode == 0
    runs = tool_runs(calls)
    assert len(runs) == 2
    assert image_for(runs[0]).startswith("ds60-formatting-julia:")
    assert image_for(runs[1]).startswith("ds60-formatting:")
    assert runs[1][-2:] == ["--exclude-language", "julia"]
    assert "--only-language" not in runs[1]


def test_julia_failure_stops_full_pass_before_other_source_writes(tool_wrapper: Wrapper) -> None:
    result, calls = tool_wrapper.invoke(settings={"REVIEW_FAIL_JULIA": "1"})
    assert result.returncode == 37
    images = [image_for(call) for call in tool_runs(calls)]
    assert len(images) == 2
    assert images[0].startswith("ds60-formatting-r:")
    assert images[1].startswith("ds60-formatting-julia:")
    assert not any(name.startswith("ds60-formatting:") for name in images)


def test_missing_julia_image_builds_only_toolchain_then_runs_selected_check(
    tool_wrapper: Wrapper,
) -> None:
    result, calls = tool_wrapper.invoke(
        "--check", "--language", "julia", settings={"REVIEW_MISSING_JULIA": "1"}
    )
    assert result.returncode == 0
    builds = [call for call in calls if call[0] == "build"]
    assert len(builds) == 1 and builds[0][builds[0].index("--target") + 1] == "toolchain"
    assert builds[0][-1] == str(tool_wrapper.root)
    assert "--progress=plain" in builds[0]
    assert calls.index(builds[0]) < calls.index(tool_runs(calls)[0])


def test_listing_julia_does_not_prepare_or_start_its_language_image(tool_wrapper: Wrapper) -> None:
    result, calls = tool_wrapper.invoke("--list", "--language", "julia")
    assert result.returncode == 0
    runs = tool_runs(calls)
    assert len(runs) == 1 and image_for(runs[0]).startswith("ds60-formatting:")
    assert "--list" in runs[0]
    assert not any("ds60-formatting-julia:" in part for call in calls for part in call)


@pytest.mark.parametrize("input_path", JULIA_INPUTS)
def test_julia_cache_key_changes_for_each_build_input_but_not_lesson_text(
    tool_wrapper: Wrapper, input_path: str
) -> None:
    def selected_image() -> str:
        result, calls = tool_wrapper.invoke("--check", "--language", "julia")
        assert result.returncode == 0
        return image_for(tool_runs(calls)[0])

    original = selected_image()
    lesson = tool_wrapper.root / "courses/julia/example.jl"
    lesson.parent.mkdir(parents=True)
    lesson.write_text('println("edited lesson")\n')
    assert selected_image() == original
    path = tool_wrapper.root / input_path
    path.write_bytes(path.read_bytes() + b"\n# changed build input\n")
    assert selected_image() != original


def test_new_language_routing_keeps_jinja_away_from_the_postgresql_formatter() -> None:
    assert formatting.language_for("courses/dbt/projects/retail/models/mart.sql") == "dbt"
    assert formatting.language_for("courses/dbt-other/model.sql") == "sql"
    assert formatting.language_for("sql/professional/model.sql") == "sql"
    assert formatting.language_for("courses/bayesian-computing/model.stan") == "stan"
    assert formatting.language_for("courses/julia/main.jl") == "julia"


@pytest.mark.parametrize("profile", ["julia", "stan-cpu", "dbt-duckdb", "data-engineering"])
def test_source_admission_and_fixed_runtime_agree_without_granting_a_verifier(profile: str) -> None:
    runtime = PROFILES[profile]
    assert runtime.language in LANGUAGES[profile]
    assert Path(runtime.filename).suffix in SOURCE_SUFFIXES[runtime.language]
    validate_operation(profile, runtime.language, None)
    with pytest.raises(ValueError, match="Language"):
        validate_operation(profile, "shell", None)
    with pytest.raises(ValueError, match="Verification"):
        validate_operation(profile, runtime.language, "llm-causal-attention-v1")


@pytest.mark.parametrize("language", ["julia", "stan", "dbt"])
def test_native_lint_uses_a_reviewed_helper_and_reports_source_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    language: str,
) -> None:
    source = tmp_path / "learner-source"
    source.write_bytes(b"invalid source with a visible diagnostic")
    commands: list[list[str]] = []

    def reject(command: list[str], **options: Any) -> subprocess.CompletedProcess[bytes]:
        commands.append(command)
        assert options["input"] == source.read_bytes()
        assert str(source) not in command and "learner-source" not in command
        assert options["cwd"] == tmp_path
        return subprocess.CompletedProcess(command, 1, b"", b"parser rejected malformed syntax")

    monkeypatch.setattr(subprocess, "run", reject)
    assert lint_repo.lint_group(language, [source.name], tmp_path) is False
    assert len(commands) == 1 and commands[0][-1] == "lint"
    assert any("source_tools" in value for value in commands[0])
    assert "learner-source: parser rejected malformed syntax" in capsys.readouterr().err


@pytest.mark.parametrize("architecture", ["amd64", "arm64"])
def test_formatter_and_worker_use_the_same_pinned_stan_release(
    monkeypatch: pytest.MonkeyPatch, architecture: str
) -> None:
    namespace = runpy.run_path(str(ROOT / "docker/formatting/install-downloads.py"))
    expected = json.loads((ROOT / "docker/workers/native/releases.lock.json").read_text())[
        "assets"
    ][architecture]["stan"]
    calls: list[tuple[str, str]] = []

    class StanDownloadObserved(Exception):
        pass

    def download(url: str, checksum: str) -> bytes:
        if "cmdstan" in url:
            calls.append((url, checksum))
            raise StanDownloadObserved
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            archive.writestr("scalafmt", b"synthetic executable")
        return data.getvalue()

    def discard_write(self: Path, data: bytes) -> int:
        assert self == Path("/usr/local/bin/scalafmt")
        return len(data)

    monkeypatch.setenv("TARGETARCH", architecture)
    monkeypatch.setattr(Path, "write_bytes", discard_write)
    monkeypatch.setattr(Path, "chmod", lambda *_args, **_kwargs: None)
    namespace["main"].__globals__["download"] = download
    with pytest.raises(StanDownloadObserved):
        namespace["main"]()
    assert calls == [(expected["url"], expected["sha256"])]


def test_unverified_native_archive_is_never_interpreted(monkeypatch: pytest.MonkeyPatch) -> None:
    original_read = Path.read_text
    lock = {
        "assets": {"arm64": {"julia": {"url": "https://fixture.invalid/tool", "sha256": "0" * 64}}}
    }

    def fixture_lock(self: Path, *args: Any, **kwargs: Any) -> str:
        if self == Path("/tmp/native-releases.lock.json"):
            return json.dumps(lock)
        return original_read(self, *args, **kwargs)

    def archive_must_not_open(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Unverified download reached archive extraction")

    monkeypatch.setattr(Path, "read_text", fixture_lock)
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_args, **_kwargs: io.BytesIO(b"corrupt"))
    monkeypatch.setattr(tarfile, "open", archive_must_not_open)
    monkeypatch.setattr(sys, "argv", ["install_native.py", "julia"])
    monkeypatch.setenv("TARGETARCH", "arm64")
    with pytest.raises(ValueError, match="checksum mismatch"):
        runpy.run_path(str(ROOT / "docker/workers/native/install_native.py"))


@pytest.mark.parametrize("persistence", [False, True])
def test_profile_qualification_rejects_another_run_even_when_source_and_outputs_match(
    monkeypatch: pytest.MonkeyPatch, persistence: bool
) -> None:
    source = "print(42)\n"
    source_hash = hashlib.sha256(source.encode()).hexdigest()
    actions: list[str] = []

    class Client(smoke.ClassroomClient):
        def __init__(self) -> None:
            pass

        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            actions.append(action)
            if action == "module-readiness":
                return {"profiles": [{"profile": "python-core", "ready": True}]}
            if action == "module-lesson":
                return {"session": {"source": source}, "history": [{"job_id": "expected-job"}]}
            if action == "module-job":
                return {
                    "job_id": "different-run-of-the-same-source",
                    "lesson_id": "fixture-001",
                    "profile": "python-core",
                    "source_sha256": source_hash,
                    "status": "succeeded",
                    "returncode": 0,
                    "checks": [],
                    "output": "42\n",
                }
            return {}

    monkeypatch.setattr(
        smoke, "reference_source", lambda *_args: ("fixture-001", "fixture.py", source)
    )
    monkeypatch.setattr(smoke, "EXPECTED_OUTPUT", {"python-core": ("42",)})
    monkeypatch.setattr(uuid, "uuid4", lambda: SimpleNamespace(hex="expected-job"))
    prior = {
        "profiles": ["python-core"],
        "receipts": [{"profile": "python-core", "job_id": "expected-job"}],
    }
    with pytest.raises(ValueError):
        smoke.qualify(Client(), ["python-core"], prior=prior if persistence else None)
    if persistence:
        assert set(actions) <= {"module-readiness", "module-job", "module-lesson"}


def test_stan_project_link_resolves_from_authoring_and_published_guide() -> None:
    course = ROOT / "courses/bayesian-computing"
    expected = course / "projects/normal-mean/README.md"
    for relative in ("authoring/chapters/bayes-017.md", "guides/bayes-017.md"):
        source = course / relative
        targets = re.findall(r"\[normal-mean project\]\(([^)]+)\)", source.read_text())
        assert len(targets) == 1
        actual = (source.parent / targets[0]).resolve()
        assert actual == expected.resolve() and actual.is_file()


def test_stan_formatter_removes_control_line_trailing_space_but_preserves_literals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = runpy.run_path(str(ROOT / "scripts/stan_source_tools.py"))
    output = io.BytesIO()
    formatted = b'generated quantities {\n  if (1) \t\r\n    print("inside  spaces ");\n}\n\n'
    monkeypatch.setattr(sys, "argv", ["stan_source_tools.py", "format"])
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(b"valid source")))
    monkeypatch.setattr(sys, "stdout", SimpleNamespace(buffer=output))
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, formatted, b""),
    )
    assert namespace["main"]() == 0
    assert output.getvalue() == (
        b'generated quantities {\n  if (1)\n    print("inside  spaces ");\n}\n'
    )
