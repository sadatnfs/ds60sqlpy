"""Exercise CI orchestration plans without Docker, networking or publication."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from scripts import ci_classroom, ci_profiles
from scripts.ci_source_quality import languages
from scripts.format_repo import LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40


def prepared(
    group: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[ci_classroom.ClassroomCI, list[list[str]]]:
    monkeypatch.setattr(ci_classroom, "ROOT", tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nversion="1.0.0"\n')
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    work = ci_classroom.ClassroomCI(group, "ds60-pub-test-123", "1.0.0", "arm64")
    work.marker.parent.mkdir(parents=True)
    work.marker.write_text(json.dumps(work.identity))
    (work.marker.parent / "classroom.url").write_text("http://127.0.0.1:8765/classroom\n")
    commands: list[list[str]] = []
    monkeypatch.setattr(work, "run", lambda command: commands.append(command))
    monkeypatch.setattr(work, "output", lambda command: REVISION)
    return work, commands


def script_calls(commands: list[list[str]], script: str) -> list[list[str]]:
    return [command for command in commands if script in command]


def test_seed_runs_every_reference_sql_failure_browser_and_persistence_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work, commands = prepared("python-core", tmp_path, monkeypatch)
    work.qualify()
    corpus = script_calls(commands, "scripts/check_module_references.py")
    assert len(corpus) == 1 and corpus[0][corpus[0].index("--profiles") + 1] == "python-core"
    failure = script_calls(commands, "scripts/check_classroom_failures.py")
    assert len(failure) == 1 and "--check-timeout" in failure[0]
    sql = script_calls(commands, "scripts/course.py")
    assert len(sql) == 2 and {command[-2] for command in sql} == {"all", "solutions"}
    assert all(command[-1] == "--reset" for command in sql)
    for script, filename in ci_classroom.CORE_BROWSER:
        calls = script_calls(commands, script)
        expected = (
            2 if script in {"scripts/check_d3_browser.py", "scripts/check_plotly_browser.py"} else 1
        )
        assert len(calls) == expected
        assert all("work/" + filename in call for call in calls)
        assert "--check-persistence" not in calls[0]
        if expected == 2:
            assert "--check-persistence" in calls[1]
    for script in ("scripts/check_scientist_browser.py", "scripts/check_scientific_artifacts.py"):
        calls = script_calls(commands, script)
        assert len(calls) == 2 and "--check-persistence" in calls[1]
    assert any(command[:3] == ["bash", "classroom", "doctor"] for command in commands)
    resumes = [
        command
        for command in commands
        if command[:2] == ["bash", "classroom"] and "doctor" not in command
    ]
    assert len(resumes) == 2 and all("--no-build" in command for command in resumes)
    assert all("--rebuild" not in command for command in commands)
    summary = json.loads((tmp_path / "work/ci-qualification.json").read_text())
    assert summary["complete"] is summary["passed"] is True
    assert summary["revision"] == REVISION
    assert summary["run_id"] == "123" and summary["run_attempt"] == "2"
    assert summary["profiles"] == ["python-core"]
    assert all(item["passed"] and item["name"] for item in summary["checks"])


def test_worker_avoids_repeating_core_corpus_but_preserves_ml_and_scientific_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work, commands = prepared("data-engineering", tmp_path, monkeypatch)
    work.qualify()
    corpus = script_calls(commands, "scripts/check_module_references.py")[0]
    assert corpus[corpus.index("--profiles") + 1] == "data-engineering dbt-duckdb"
    assert not script_calls(commands, "scripts/check_d3_browser.py")
    service = script_calls(commands, "courses/ml-engineering/projects/local-system/check.py")
    assert len(service) == 1 and "ds60sqlpy-worker-data-engineering:1.0.0" in service[0]
    data_product = script_calls(
        commands, "courses/data-ml-engineering/projects/data-product/check_project.py"
    )
    assert len(data_product) == 1
    assert "ds60sqlpy-worker-data-engineering:1.0.0" in data_product[0]
    assert "--confirm-disposable" in data_product[0]
    assert "owned data product HTTP, publication and recovery" in work.completed
    browser = script_calls(commands, "scripts/check_scientist_browser.py")
    assert len(browser) == 2 and "--check-persistence" in browser[1]
    assert "requirements/ci-browser.arm64.lock" in next(
        command for command in commands if "pip" in command
    )


def test_qualification_does_not_inherit_registry_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    secret_keys = (
        "DOCKERHUB_USERNAME",
        "DOCKERHUB_TOKEN",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "DOCKER_CONFIG",
        "DOCKER_DEFAULT_PLATFORM",
        "DS60_LAB_IMAGE",
    )
    for key in secret_keys:
        monkeypatch.setenv(key, "not-public")
    result = ci_classroom.clean_environment("ds60-ci-owned")
    assert all(key not in result for key in secret_keys)
    assert result["COMPOSE_PROJECT_NAME"] == "ds60-ci-owned"
    assert result["DS60_CLASSROOM_PORT"] == result["DS60_POSTGRES_PORT"] == "0"


def test_prepare_checks_native_platform_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work, commands = prepared("cpp", tmp_path, monkeypatch)
    monkeypatch.setattr(work, "output", lambda command: "x86_64")
    with pytest.raises(ValueError, match="native Docker architecture"):
        work.prepare()
    assert not commands


def test_existing_resources_and_wrong_ownership_block_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work, commands = prepared("cpp", tmp_path, monkeypatch)
    monkeypatch.setattr(
        work, "output", lambda command: "aarch64" if "info" in command else "existing-container"
    )
    with pytest.raises(ValueError, match="fresh CI project"):
        work.prepare()
    work.marker.write_text("{}")
    with pytest.raises(ValueError, match="ownership marker"):
        work.cleanup()
    assert not commands


def test_group_registry_rejects_omissions_duplicates_and_gpu_profiles(tmp_path: Path) -> None:
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker/classroom-images.tsv").write_text(
        (ROOT / "docker/classroom-images.tsv").read_text()
    )
    original: dict[str, Any] = json.loads((ROOT / "docker/ci-profile-groups.json").read_text())
    for mutation in ("missing", "duplicate", "gpu"):
        data = json.loads(json.dumps(original))
        if mutation == "missing":
            data["groups"].pop()
        elif mutation == "duplicate":
            data["groups"][1]["profiles"].append("python-core")
        else:
            data["groups"][1]["profiles"].append("cuda-python")
        (tmp_path / "docker/ci-profile-groups.json").write_text(json.dumps(data))
        with pytest.raises(ValueError):
            ci_profiles.groups(tmp_path)


def test_browser_locks_have_matching_versions_and_native_hashes() -> None:
    texts = [(ROOT / ci_classroom.browser_lock(arch)).read_text() for arch in ("amd64", "arm64")]
    versions = [re.findall(r"(?m)^([a-z_]+)==([^ \n]+)", text) for text in texts]
    assert versions[0] == versions[1]
    assert ("playwright", "1.64.1") in versions[0]
    assert all(len(re.findall(r"--hash=sha256:[a-f0-9]{64}", text)) == 4 for text in texts)
    assert texts[0] != texts[1]
    assigned = [name for shard in ("main", "r", "julia") for name in languages(shard)]
    assert len(assigned) == len(set(assigned)) and set(assigned) == set(LANGUAGES)


def test_ci_summary_matches_release_staging_schema_without_publishing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.check_module_references import collect_cases
    from scripts.docker_release import Context, qualification_records

    work, _ = prepared("cpp", tmp_path, monkeypatch)
    work.qualify()
    cases, report = collect_cases(ROOT, ["cpp20"])
    # Synthetic policy evidence only: no compiler, image or registry is invoked.
    report.update(complete=True, passed=True)
    for row in report["results"]:
        row.update(
            status="passed",
            worker_status="succeeded",
            returncode=0,
            truncated=False,
            job_id="b" * 32,
        )
    corpus = tmp_path / "policy-corpus.json"
    corpus.write_text(json.dumps(report))
    context = Context(
        "exampleuser", "exampleuser/ds60sqlpy", "example/classroom", "1.0.0", REVISION, "123", "2"
    )
    records = qualification_records(
        [corpus, tmp_path / "work/ci-qualification.json"], context, "arm64", {"cpp20"}, ROOT
    )
    assert len(records) == 2
    assert records[0]["references"] == len(cases)
    assert records[1]["checks"]


def test_pytorch_requires_real_inference_browser_and_persistence_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work, commands = prepared("pytorch", tmp_path, monkeypatch)
    work.qualify()
    calls = script_calls(commands, "scripts/check_inference_project.py")
    assert len(calls) == 1
    command = calls[0]
    assert command[command.index("--image") + 1] == "ds60sqlpy-worker-llm-torch-cpu:1.0.0"
    assert "--browser-python" in command and "--confirm-disposable" in command
    assert "owned inference lifecycle, SSE and persistent history" in work.completed
    assert not script_calls(commands, "scripts/check_scientist_browser.py")
    assert "requirements/ci-browser.arm64.lock" in next(
        command for command in commands if "pip" in command
    )


@pytest.mark.parametrize("existing", ["container", "network", "volume", "wrong-architecture"])
def test_inference_gate_rejects_existing_resources_or_emulation_before_writing(
    existing: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import check_inference_project as gate

    monkeypatch.setattr(gate, "ROOT", tmp_path)
    calls: list[list[str]] = []

    def output(command: list[str], environment: dict[str, str]) -> str:
        calls.append(command)
        if command[1] == "info":
            return "aarch64"
        if command[1:3] == ["image", "inspect"]:
            architecture = "amd64" if existing == "wrong-architecture" else "arm64"
            return json.dumps(
                [{"Os": "linux", "Architecture": architecture, "Id": "sha256:" + "a" * 64}]
            )
        resource = "container" if command[1] == "ps" else command[1]
        return "owned-elsewhere" if resource == existing else ""

    monkeypatch.setattr(gate, "output", output)
    with pytest.raises(ValueError, match="fresh project|native Linux"):
        gate.qualify("ds60-infer-ci-preflight", "ds60sqlpy-worker-llm-torch-cpu:1.0.0")
    assert not (tmp_path / "work").exists()
    assert not any(
        "build" in command or "compose" in command or "rm" in command for command in calls
    )


def test_inference_gate_keeps_the_prepared_virtual_environment_interpreter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os
    import subprocess
    import venv

    from scripts.check_inference_project import browser_interpreter

    if os.name == "nt":
        pytest.skip("The contributor gate runs in Linux, macOS or WSL 2")
    prepared = tmp_path / "browser-env"
    venv.EnvBuilder(with_pip=False, symlinks=True).create(prepared)
    monkeypatch.chdir(tmp_path)
    interpreter = browser_interpreter(Path("browser-env/bin/python"))
    result = subprocess.check_output(
        [str(interpreter), "-c", "import sys; print(sys.prefix)"], text=True
    ).strip()
    assert Path(result) == prepared


@pytest.mark.parametrize("group", ["data-platforms", "java"])
def test_native_platform_groups_require_real_service_lifecycle_gates(
    group: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work, commands = prepared(group, tmp_path, monkeypatch)
    work.qualify()
    command = script_calls(commands, "courses/apache-data-platforms/authoring/qualify_workshop.py")[
        0
    ]
    if group == "data-platforms":
        assert work.profiles == ["data-platforms-python", "rust-stable"]
        assert "arrow-flight" in command and "--require-ipc" in command
        assert "DS60_PLATFORM_IMAGE=ds60sqlpy-worker-data-platforms-python:1.0.0" in command
    else:
        assert "streaming" in command and "--prepare" in command
        assert "DS60_JAVA_IMAGE=ds60sqlpy-worker-java21:1.0.0" in command
    assert "work/apache-service-receipts.json" in command


def test_python_web_requires_real_services_browser_and_retained_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work, commands = prepared("python-web", tmp_path, monkeypatch)
    work.qualify()
    script = "courses/python-web/projects/web-lab/check_project.py"
    checks = script_calls(commands, script)
    assert len(checks) == 1
    command = checks[0]
    assert command[command.index("--image") + 1] == "ds60sqlpy-worker-python-web:1.0.0"
    assert command[command.index("--browser-python") + 1] == str(
        tmp_path / "work/browser-env/bin/python"
    )
    assert "--confirm-disposable" in command
    assert "owned Python web HTTP, streaming, browser and persistence" in work.completed
    assert set(work.completed) == ci_classroom.required_checks("python-web")
    corpus = script_calls(commands, "scripts/check_module_references.py")
    assert len(corpus) == 1 and corpus[0][corpus[0].index("--profiles") + 1] == "python-web"
    assert not script_calls(commands, "scripts/check_scientist_browser.py")
    assert "requirements/ci-browser.arm64.lock" in next(item for item in commands if "pip" in item)
