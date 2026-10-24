"""Formatting preserves learner state, source boundaries and read-only checks."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from scripts import format_repo as formatting

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_source_inventory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DS60_FORMAT_FILE_LIST", raising=False)


def put(root: Path, name: str, value: str = "value\n") -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


def empty_policy(root: Path) -> None:
    put(root, "scripts/format-policy.json", '{"exclude": [], "preserve": []}\n')


def test_git_inventory_includes_new_sources_but_respects_ignores(tmp_path: Path) -> None:
    git = shutil.which("git")
    if git is None:
        pytest.skip("Git unavailable")
    put(tmp_path, ".gitignore", "scratch/\nignored.py\n")
    put(tmp_path, "tracked.py")
    put(tmp_path, "new module.py")
    put(tmp_path, "ignored.py")
    put(tmp_path, "scratch/temporary.py")
    put(tmp_path, ".learning/saved.py")
    put(tmp_path, "removed.py")
    for args in (["init", "--quiet"], ["add", ".gitignore", "tracked.py", "removed.py"]):
        subprocess.run([git, *args], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "removed.py").unlink()
    sources = formatting.source_files(tmp_path)
    assert {"tracked.py", "new module.py"} <= set(sources)
    assert not {"ignored.py", "scratch/temporary.py", ".learning/saved.py", "removed.py"} & set(
        sources
    )


def test_zip_inventory_keeps_sources_and_prunes_private_or_build_trees(tmp_path: Path) -> None:
    put(tmp_path, "courses/demo/main.py")
    for directory in (".learning", ".classroom", ".venv", "node_modules", "target", "work"):
        put(tmp_path, f"{directory}/private.py")
    put(tmp_path, "courses/demo/node_modules/dependency.js")
    assert formatting.source_files(tmp_path) == ["courses/demo/main.py"]


def test_inventory_never_follows_source_or_directory_symlinks(tmp_path: Path) -> None:
    root = tmp_path / "checkout"
    root.mkdir()
    external = put(tmp_path, "outside/private.py", "private = True\n")
    put(root, "real.py")
    try:
        (root / "linked.py").symlink_to(external)
        (root / "linked-directory").symlink_to(external.parent, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks unavailable")
    assert formatting.source_files(root) == ["real.py"]
    assert external.read_text() == "private = True\n"


def test_policy_requires_a_nonempty_reason_for_every_exception(tmp_path: Path) -> None:
    put(
        tmp_path, "scripts/format-policy.json", '{"exclude": [{"pattern": "*.py"}], "preserve": []}'
    )
    with pytest.raises(ValueError, match="reason"):
        formatting.load_policy(tmp_path)
    put(
        tmp_path,
        "scripts/format-policy.json",
        '{"exclude": [], "preserve": [{"path": "receipt.json", "reason": " "}]}',
    )
    with pytest.raises(ValueError, match="nonempty"):
        formatting.load_policy(tmp_path)


def test_inventory_reports_explicit_preservation_and_unknown_types(tmp_path: Path) -> None:
    put(
        tmp_path,
        "scripts/format-policy.json",
        json.dumps(
            {
                "exclude": [{"pattern": "generated/*", "reason": "Use its generator."}],
                "preserve": [{"path": "receipt.json", "reason": "Historical evidence."}],
            }
        ),
    )
    for name in ("source.py", "generated/reader.html", "receipt.json", "Cargo.lock", "sample.csv"):
        put(tmp_path, name)
    groups, excluded, unmanaged = formatting.inventory(tmp_path)
    assert groups["python"] == ["source.py"]
    assert excluded["generated/reader.html"] == "Use its generator."
    assert excluded["receipt.json"] == "Historical evidence."
    assert "Cargo.lock" in excluded
    assert unmanaged == ["sample.csv"]


@pytest.mark.parametrize(
    "path",
    [
        "courses/deep-learning-pytorch/authoring/review_runtime_evidence.json",
        "courses/llm-applied/authoring/review_runtime_evidence.json",
        "courses/kubernetes/fixtures/provenance/attestation.json",
        "src/ds60sqlpy/assets/vendor/d3.v7.9.0.min.js",
        "reference-pages/example.md.html",
    ],
)
def test_repository_policy_protects_generated_and_historical_bytes(path: str) -> None:
    assert formatting.exclusion(path, formatting.load_policy(ROOT))


@pytest.mark.parametrize(
    "path",
    [
        "courses/deep-learning-tensorflow/solutions/tf-002_solution.py",
        "courses/llm-theory/solutions/llm-002_solution.py",
        "courses/nlp/solutions/nlp-001_solution.py",
        "courses/kubernetes/lessons/k8s-003.yaml",
        "courses/cpp/solutions/cpp-014_solution.cpp",
        "courses/swift/fixtures/JourneyCore/Sources/JourneyCore/Plan.swift",
        "courses/csharp/fixtures/ApiLab/Program.cs",
        "courses/go/authoring/foundations.py",
    ],
)
def test_repository_policy_keeps_independently_maintained_source_eligible(path: str) -> None:
    assert formatting.exclusion(path, formatting.load_policy(ROOT)) is None


@pytest.mark.parametrize(
    "path,expected",
    [
        ("docker/workers/Dockerfile.java", "docker"),
        ("docker/workers/Dockerfile.go", "docker"),
        ("Dockerfile.c", "docker"),
        ("project/Main.java", "java"),
        ("project/Program.cs", "csharp"),
        ("project/NuGet.Config", "xml"),
        ("project/CMakeLists.txt", "cmake"),
        ("notebook.ipynb", "python"),
        ("classroom", "shell"),
        ("scripts/format-repo", "shell"),
        ("records.csv", None),
    ],
)
def test_routing_recognizes_special_filenames_before_suffixes(
    path: str, expected: str | None
) -> None:
    assert formatting.language_for(path) == expected


def test_stdout_formatter_check_reports_drift_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = put(tmp_path, "program.sql", "select 1;\n")
    command = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read().upper())",
    ]
    assert not formatting.streamed(command, [path.name], tmp_path, check=True)
    assert path.read_bytes() == b"select 1;\n"
    assert "program.sql" in capsys.readouterr().out
    assert formatting.streamed(command, [path.name], tmp_path, check=False)
    assert path.read_bytes() == b"SELECT 1;\n"


def test_failed_stdout_formatter_preserves_original_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = put(tmp_path, "main.rs", "fn main() {}\n")
    command = [
        sys.executable,
        "-c",
        "import sys; print('partial'); sys.stderr.write('parse failed'); sys.exit(1)",
    ]
    assert not formatting.streamed(command, [path.name], tmp_path, check=False)
    assert path.read_text() == "fn main() {}\n"
    assert "parse failed" in capsys.readouterr().err


def test_sql_formatter_receives_psql_program_verbatim_and_ignores_user_rc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = (
        b"\\set ON_ERROR_STOP on\nSELECT current_database() AS name \\gset\n"
        b"\\if :ok\n\\ir fixture.sql\n\\endif\n"
    )
    path = put(tmp_path, "lesson.sql")
    path.write_bytes(source)
    observed: list[tuple[list[str], bytes]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        observed.append((command, kwargs["input"]))
        return subprocess.CompletedProcess(command, 0, stdout=kwargs["input"], stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert formatting.format_group("sql", [path.name], tmp_path, check=True)
    assert len(observed) == 1
    assert observed[0][0][0] == "pg_format" and "--no-rcfile" in observed[0][0]
    assert observed[0][1] == source
    assert path.read_bytes() == source


@pytest.mark.parametrize(
    "language",
    [
        "python",
        "web",
        "java",
        "c",
        "cpp",
        "csharp",
        "swift",
        "scala",
        "shell",
        "toml",
        "xml",
        "cmake",
    ],
)
def test_check_commands_do_not_request_in_place_writes(
    language: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    commands: list[list[str]] = []

    def capture(command: list[str], _root: Path) -> bool:
        commands.append(command)
        return True

    monkeypatch.setattr(formatting, "run", capture)
    assert formatting.format_group(language, ["folder/a source.ext", "-option.ext"], tmp_path, True)
    assert commands
    for command in commands:
        assert not {"--write", "--in-place", "-i", "-w"} & set(command[1:]) or (
            command[0] == "shfmt" and "-w" not in command
        )
        assert "./folder/a source.ext" in command
        assert "./-option.ext" in command


def test_go_check_detects_listed_drift_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = put(tmp_path, "main.go", "package main\n")

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        assert "-l" in command and "-w" not in command
        return subprocess.CompletedProcess(command, 0, stdout="./main.go\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert not formatting.format_group("go", [path.name], tmp_path, True)
    assert path.read_text() == "package main\n"


def test_list_needs_no_language_tools_or_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    empty_policy(tmp_path)
    put(tmp_path, "main.go")
    monkeypatch.setattr(formatting, "ROOT", tmp_path)
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    monkeypatch.setattr(
        formatting, "format_group", lambda *_args: pytest.fail("List formatted source")
    )
    monkeypatch.setattr(
        formatting, "generated_views", lambda *_args: pytest.fail("List generated output")
    )
    assert formatting.main(["--list"]) == 0
    assert "FORMAT [go] main.go" in capsys.readouterr().out


def test_language_only_pass_leaves_shared_generators_for_full_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty_policy(tmp_path)
    put(tmp_path, "main.go")
    put(tmp_path, "other.py")
    calls: list[tuple[str, bool]] = []
    monkeypatch.setattr(formatting, "ROOT", tmp_path)
    monkeypatch.setattr(shutil, "which", lambda name: f"/tools/{name}")
    monkeypatch.setattr(
        formatting, "generated_views", lambda *_args: pytest.fail("Partial generation")
    )

    def capture(language: str, paths: list[str], root: Path, check: bool) -> bool:
        calls.append((language, check))
        assert paths == ["main.go"] and root == tmp_path
        return True

    monkeypatch.setattr(formatting, "format_group", capture)
    assert formatting.main(["--check", "--language", "go"]) == 0
    assert calls == [("go", True)]


def test_full_check_passes_readonly_mode_to_generated_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty_policy(tmp_path)
    commands: list[list[str]] = []
    checks: list[bool] = []
    monkeypatch.setattr(formatting, "ROOT", tmp_path)
    monkeypatch.setattr(shutil, "which", lambda name: f"/tools/{name}")
    monkeypatch.setattr(formatting, "format_group", lambda *_args: True)

    def run(command: list[str], root: Path) -> bool:
        assert root == tmp_path
        commands.append(command)
        return True

    def generated(root: Path, check: bool) -> bool:
        assert root == tmp_path
        checks.append(check)
        return True

    monkeypatch.setattr(formatting, "run", run)
    monkeypatch.setattr(formatting, "generated_views", generated)
    assert formatting.main(["--check"]) == 0
    assert checks == [True]
    assert commands and all("--write" not in command for command in commands)


@pytest.fixture
def wrapper(tmp_path: Path) -> Any:
    bash = shutil.which("bash")
    if bash is None or os.name == "nt":
        pytest.skip("Run the supported Bash wrapper on Linux, macOS or WSL 2")
    root = tmp_path / "checkout with spaces"
    (root / "scripts").mkdir(parents=True)
    shutil.copyfile(ROOT / "scripts/format-repo", root / "scripts/format-repo")
    put(root, "docker/formatting/Dockerfile", "FROM example\n")
    binaries = tmp_path / "fake-tools"
    binaries.mkdir()
    calls = tmp_path / "docker-calls.jsonl"
    docker = binaries / "docker"
    docker.write_text(
        f"#!{sys.executable}\n"
        + """import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ["FORMAT_TEST_CALLS"]).open("a") as out:
    out.write(json.dumps(args) + "\\n")
if args[:1] == ["info"]:
    print(os.environ.get("FORMAT_TEST_ENGINE", "linux"))
elif args[:2] == ["context", "inspect"]:
    print(os.environ.get("FORMAT_TEST_ENDPOINT", "unix:///fake/docker.sock"))
elif args[:2] == ["image", "inspect"]:
    sys.exit(0 if os.environ.get("FORMAT_TEST_IMAGE", "present") == "present" else 1)
elif args[:1] not in (["build"], ["run"]):
    sys.exit(7)
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"DOCKER_HOST", "DOCKER_CONTEXT"}
    }
    env.update(PATH=f"{binaries}{os.pathsep}{env.get('PATH', '')}", FORMAT_TEST_CALLS=str(calls))

    def invoke(
        *arguments: str, settings: dict[str, str] | None = None
    ) -> tuple[subprocess.CompletedProcess[str], list[list[str]]]:
        calls.unlink(missing_ok=True)
        result = subprocess.run(
            [bash, str(root / "scripts/format-repo"), *arguments],
            cwd=root,
            env={**env, **(settings or {})},
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        recorded = (
            [json.loads(line) for line in calls.read_text().splitlines()] if calls.exists() else []
        )
        return result, recorded

    return root, invoke


@pytest.mark.parametrize("option", ["--check", "--list"])
def test_wrapper_reuses_cached_image_and_mounts_checks_readonly(wrapper: Any, option: str) -> None:
    root, invoke = wrapper
    result, calls = invoke(option)
    assert result.returncode == 0, result.stderr
    assert not any(command[0] == "build" for command in calls)
    run = next(command for command in calls if command[0] == "run")
    assert "--network=none" in run and "--read-only" in run and "--cap-drop=ALL" in run
    mount = run[run.index("--mount") + 1]
    assert str(root) in mount and mount.endswith(",readonly")
    assert run[-1] == option
    assert not any(command[0] in {"stop", "rm", "compose", "prune"} for command in calls)


def test_wrapper_prepares_missing_tools_with_visible_logs_then_formats(wrapper: Any) -> None:
    root, invoke = wrapper
    result, calls = invoke(settings={"FORMAT_TEST_IMAGE": "missing"})
    assert result.returncode == 0, result.stderr
    builds = [command for command in calls if command[0] == "build"]
    assert len(builds) == 1 and "--progress=plain" in builds[0]
    assert builds[0][-1] == str(root / "docker/formatting")
    run = next(command for command in calls if command[0] == "run")
    assert not run[run.index("--mount") + 1].endswith(",readonly")


@pytest.mark.parametrize(
    "settings",
    [
        {"DOCKER_HOST": "ssh://remote.example"},
        {"FORMAT_TEST_ENDPOINT": "tcp://remote.example:2376"},
        {"FORMAT_TEST_ENGINE": "windows"},
    ],
)
def test_wrapper_refuses_remote_or_non_linux_engine_before_build_or_mount(
    wrapper: Any, settings: dict[str, str]
) -> None:
    _root, invoke = wrapper
    result, calls = invoke("--check", settings=settings)
    assert result.returncode != 0
    assert not any(command[0] in {"build", "run"} for command in calls)


def test_host_inventory_rejects_escaping_state_and_linked_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "checkout"
    root.mkdir()
    external = put(tmp_path, "outside.py")
    put(root, "source.py")
    put(root, "--option.py")
    put(root, ".learning/attempt.py")
    put(root, "nested/real.py")
    try:
        (root / "linked.py").symlink_to(external)
        (root / "linked-folder").symlink_to(root / "nested", target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks unavailable")
    names = [
        "source.py",
        "source.py",
        "--option.py",
        ".learning/attempt.py",
        "../outside.py",
        str(external),
        "linked.py",
        "linked-folder/real.py",
        "nested/real.py",
        "missing.py",
    ]
    manifest = tmp_path / "inventory.bin"
    manifest.write_bytes(b"\0".join(name.encode() for name in names) + b"\0")
    monkeypatch.setenv("DS60_FORMAT_FILE_LIST", str(manifest))
    assert formatting.source_files(root) == ["--option.py", "nested/real.py", "source.py"]
    assert formatting.batches(["--option.py"]) == [["./--option.py"]]
    assert external.read_text() == "value\n"


def test_missing_host_inventory_fails_without_broadening_file_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    put(tmp_path, "source.py")
    monkeypatch.setenv("DS60_FORMAT_FILE_LIST", str(tmp_path / "missing.bin"))
    with pytest.raises(FileNotFoundError):
        formatting.source_files(tmp_path)


def test_wrapper_cleans_host_git_inventory_after_container_exit(wrapper: Any) -> None:
    root, invoke = wrapper
    git = shutil.which("git")
    if git is None:
        pytest.skip("Git unavailable")
    subprocess.run([git, "init", "--quiet"], cwd=root, check=True, capture_output=True)
    put(root, "example.py", "answer = 42\n")
    result, calls = invoke("--check")
    assert result.returncode == 0, result.stderr
    run = next(command for command in calls if command[0] == "run")
    assert "DS60_FORMAT_FILE_LIST=/tmp/source-files.bin" in run
    inventory = next(value for value in run if "dst=/tmp/source-files.bin" in value)
    assert inventory.endswith(",readonly")
    temporary = inventory.split("src=", 1)[1].split(",dst=", 1)[0]
    assert not Path(temporary).exists()


def guarded_scandir(
    monkeypatch: pytest.MonkeyPatch, *, duplicate_entries: bool = False
) -> dict[Path, int]:
    """Model a mounted filesystem that forbids nested open directory streams."""
    real_scandir = os.scandir
    visits: dict[Path, int] = {}
    open_streams = 0

    @contextmanager
    def scan(directory: Path | str) -> Iterator[Iterator[os.DirEntry[str]]]:
        nonlocal open_streams
        assert open_streams == 0, "Close the parent directory stream before descending"
        path = Path(directory)
        visits[path] = visits.get(path, 0) + 1
        with real_scandir(path) as original:
            entries = list(original)
        if duplicate_entries:
            entries = entries + entries
        open_streams += 1
        try:
            yield iter(entries)
        finally:
            open_streams -= 1

    monkeypatch.setattr(os, "scandir", scan)
    return visits


@pytest.mark.parametrize("duplicate_entries", [False, True])
def test_source_inventory_closes_streams_and_visits_each_directory_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, duplicate_entries: bool
) -> None:
    root = tmp_path / "checkout"
    put(root, "src/deep/module.py")
    put(root, "src/sibling.py")
    manifest = tmp_path / "sources.bin"
    manifest.write_bytes(b"src/deep/module.py\0src/sibling.py\0")
    monkeypatch.setenv("DS60_FORMAT_FILE_LIST", str(manifest))
    visits = guarded_scandir(monkeypatch, duplicate_entries=duplicate_entries)
    assert formatting.source_files(root) == ["src/deep/module.py", "src/sibling.py"]
    assert visits == {root: 1, root / "src": 1, root / "src/deep": 1}


@pytest.mark.parametrize("duplicate_entries", [False, True])
def test_publication_preflight_closes_streams_and_deduplicates_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, duplicate_entries: bool
) -> None:
    put(tmp_path, "courses/topic/guides/chapter.md")
    put(tmp_path, "src/assets/classroom.html")
    put(tmp_path, "courses/.learning/private.md")
    visits = guarded_scandir(monkeypatch, duplicate_entries=duplicate_entries)
    formatting.ensure_publication_paths(tmp_path)
    assert visits == {
        tmp_path / "courses": 1,
        tmp_path / "courses/topic": 1,
        tmp_path / "courses/topic/guides": 1,
        tmp_path / "src": 1,
        tmp_path / "src/assets": 1,
    }


def test_publication_preflight_still_rejects_links_after_materializing_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "checkout"
    put(root, "courses/topic/guide.md")
    outside = put(tmp_path, "private/notes.md")
    try:
        (root / "courses/topic/linked.md").symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks unavailable")
    guarded_scandir(monkeypatch, duplicate_entries=True)
    with pytest.raises(ValueError, match="symlink"):
        formatting.ensure_publication_paths(root)
    assert outside.read_text() == "value\n"
