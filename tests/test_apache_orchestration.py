"""Owned orchestration policy and real local data-integrity contracts."""

from __future__ import annotations

import json
import os
import runpy
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

BASE = Path(__file__).resolve().parents[1] / "courses/apache-data-platforms"


@pytest.mark.parametrize("number", range(21, 33))
def test_orchestration_units_are_developed_and_project_only(number: int) -> None:
    key = f"apache-{number:03d}"
    prose = (BASE / "authoring/chapters" / (key + ".md")).read_text()
    metadata = json.loads((BASE / "authoring/units" / (key + ".json")).read_text())
    notebook = (BASE / "authoring/programs" / (key + ".md")).read_text()
    assert len(prose.split()) >= 500
    assert prose.count("## Worked case") == 2
    assert "Interview discussion" in prose
    assert "\u2014" not in prose + notebook
    assert metadata["runtime"] == "reading" and metadata["language"] == "markdown"
    assert len(metadata["sources"]) >= 2 and "bash run.sh" in notebook


def fake_docker(tmp_path: Path, script: str) -> tuple[Path, dict[str, str]]:
    tools = tmp_path / "tools"
    tools.mkdir()
    docker = tools / "docker"
    docker.write_text('#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$DOCKER_CALL_LOG"\n' + script)
    docker.chmod(0o755)
    log = tmp_path / "calls"
    env = os.environ | {
        "PATH": str(tools) + os.pathsep + os.environ["PATH"],
        "DOCKER_CALL_LOG": str(log),
        "DOCKER_HOST": "unix:///fixture/docker.sock",
        "DOCKER_CONTEXT": "",
    }
    return log, env


@pytest.mark.parametrize("workshop", ["ballista", "airflow"])
def test_unknown_flag_has_no_state_or_docker_calls(tmp_path: Path, workshop: str) -> None:
    project = tmp_path / "project"
    project.mkdir()
    shutil.copy2(BASE / "projects" / workshop / "run.sh", project / "run.sh")
    log, env = fake_docker(tmp_path, "exit 99\n")
    result = subprocess.run(
        ["bash", "run.sh", "start", "--unknown"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert not log.exists() and not (project / ".env").exists()


@pytest.mark.parametrize(
    "workshop,flag", [("ballista", "--reuse-swift"), ("airflow", "--reuse-core")]
)
def test_wrong_native_base_is_rejected_before_build_or_state(
    tmp_path: Path, workshop: str, flag: str
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    shutil.copy2(BASE / "projects" / workshop / "run.sh", project / "run.sh")
    log, env = fake_docker(
        tmp_path,
        """case "$1 $2" in
'info --format') echo 'linux|aarch64' ;;
'image inspect') echo 'linux|amd64' ;;
*) exit 99 ;;
esac
""",
    )
    result = subprocess.run(
        ["bash", "run.sh", "prepare", flag],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert not (project / ".env").exists() and not (project / ".workshop-lock").exists()
    assert all(
        line.startswith(("info ", "image inspect ")) for line in log.read_text().splitlines()
    )


@pytest.mark.parametrize("workshop", ["ballista", "airflow"])
def test_resume_reuses_exact_container_without_image_preparation(
    tmp_path: Path, workshop: str
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    shutil.copy2(BASE / "projects" / workshop / "run.sh", project / "run.sh")
    owner = "0123456789abcdef0123456789abcdef"
    kind = "apache-" + workshop
    image = (
        "ds60-apache-ballista-swift:54.1.0"
        if workshop == "ballista"
        else "ds60-apache-airflow-core:3.3.2"
    )
    fields = [
        f"DS60_WORKSHOP_OWNER={owner}",
        f"DS60_WORKSHOP_PROJECT=ds60-apache-{workshop}-{owner[:12]}",
        f"DS60_{workshop.upper()}_IMAGE={image}",
    ]
    if workshop == "airflow":
        fields.append("DS60_AIRFLOW_PORT=18880")
    (project / ".env").write_text("\n".join(fields) + "\n")
    log, env = fake_docker(
        tmp_path,
        """case "$1 $2" in
'ps -aq') echo aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; exit 0 ;;
'network ls' | 'volume ls') exit 0 ;;
'inspect --format')
  case "$3" in
    *State.Status*) echo 'running|healthy' ;;
    *) echo "$TEST_OWNER|$TEST_KIND" ;;
  esac
  exit 0 ;;
esac
if [ "$1" = compose ]; then
  for value in "$@"; do
    case "$value" in
      ps) echo aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; exit 0 ;;
      start) exit 0 ;;
    esac
  done
fi
exit 99
""",
    )
    result = subprocess.run(
        ["bash", "run.sh", "resume"],
        cwd=project,
        env=env | {"TEST_OWNER": owner, "TEST_KIND": kind},
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    calls = log.read_text().splitlines()
    assert any(" start " in line for line in calls)
    assert not any(
        "--wait" in line or line.startswith(("image ", "pull ", "build ")) for line in calls
    )
    assert not (project / ".workshop-lock").exists()


@pytest.fixture
def airflow_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    namespace = runpy.run_path(str(BASE / "projects/airflow/project_data.py"))
    root = tmp_path / "state"
    root.mkdir()
    monkeypatch.setitem(namespace["initialize"].__globals__, "ROOT", root)
    namespace["initialize"]()
    return namespace


def test_airflow_partition_retry_is_byte_idempotent_and_correction_is_scoped(
    airflow_data: dict[str, Any],
) -> None:
    write = airflow_data["write_partition"]
    read = airflow_data["read_partition"]
    root = write.__globals__["ROOT"]
    write("2026-01-01", 0, "first-run")
    write("2026-01-02", 0, "second-run")
    first = (root / "outputs/2026-01-01.json").read_bytes()
    second = (root / "outputs/2026-01-02.json").read_bytes()
    write("2026-01-01", 0, "repeat-run")
    assert (root / "outputs/2026-01-01.json").read_bytes() == first
    assert len(list((root / "write-receipts").iterdir())) == 2
    write("2026-01-01", 1, "correction-run")
    assert read("2026-01-01")["amount_total"] == 15
    assert (root / "outputs/2026-01-02.json").read_bytes() == second
    with pytest.raises(ValueError, match="downgrade"):
        write("2026-01-01", 0, "invalid-downgrade")
    assert read("2026-01-01")["revision"] == 1


def test_airflow_corrupt_output_is_not_replaced(airflow_data: dict[str, Any]) -> None:
    write = airflow_data["write_partition"]
    root = write.__globals__["ROOT"]
    write("2026-01-01", 0, "first-run")
    path = root / "outputs/2026-01-01.json"
    record = json.loads(path.read_text())
    record["amount_total"] = 999
    path.write_text(json.dumps(record))
    retained = path.read_bytes()
    with pytest.raises(ValueError, match="identity"):
        write("2026-01-01", 0, "retry")
    assert path.read_bytes() == retained


def test_airflow_rejects_symlink_output_directory(
    airflow_data: dict[str, Any], tmp_path: Path
) -> None:
    write = airflow_data["write_partition"]
    root = write.__globals__["ROOT"]
    (root / "outputs").rmdir()
    external = tmp_path / "external"
    external.mkdir()
    (root / "outputs").symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match="owned output"):
        write("2026-01-01", 0, "attempt")
    assert not list(external.iterdir())


def test_airflow_unidentified_existing_state_is_never_reset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    namespace = runpy.run_path(str(BASE / "projects/airflow/project_data.py"))
    root = tmp_path / "state"
    root.mkdir()
    (root / "valuable.txt").write_text("retained")
    monkeypatch.setitem(namespace["initialize"].__globals__, "ROOT", root)
    with pytest.raises(ValueError, match="Unidentified"):
        namespace["initialize"]()
    assert (root / "valuable.txt").read_text() == "retained"
    assert not (root / "identity.json").exists()


@pytest.mark.parametrize("workshop", ["ballista", "airflow"])
def test_compose_limits_and_ownership_do_not_expose_an_engine_socket(workshop: str) -> None:
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load((BASE / "projects" / workshop / "compose.yaml").read_text())
    for service in data["services"].values():
        assert service["read_only"] is True
        assert service["cpus"] <= 2 and service["pids_limit"] <= 384
        assert service["labels"]["org.ds60.workshop.kind"] == "apache-" + workshop
        assert not any("docker.sock" in str(value) for value in service["volumes"])
        for port in service.get("ports", []):
            assert port.startswith("127.0.0.1:")


def test_ballista_disconnected_health_observer_does_not_end_supervisor() -> None:
    namespace = runpy.run_path(str(BASE / "projects/ballista/supervisor.py"))

    class Disconnected:
        def sendall(self, value: bytes) -> None:
            raise BrokenPipeError("observer deadline ended")

    assert namespace["respond"](Disconnected(), {"passed": True}) is False


def test_ballista_control_keeps_exact_role_ownership_during_reconfiguration() -> None:
    source = (BASE / "projects/ballista/supervisor.py").read_text()
    assert "child.terminate()" in source and "child.wait(timeout=10)" in source
    assert "child.kill()" in source and "children.pop(name, None)" in source
    assert "pkill" not in source and "os.kill" not in source


def test_airflow_saved_summary_uses_its_observed_versions_not_current_output(
    airflow_data: dict[str, Any],
) -> None:
    import hashlib

    canonical = airflow_data["canonical"]
    rows_for = airflow_data["rows_for"]
    validate = airflow_data["validate_summary"]
    versions = {
        day: hashlib.sha256(canonical(rows_for(day, 0))).hexdigest() for day in airflow_data["DAYS"]
    }
    prior = {
        "run_id": "asset-run",
        "region": "east",
        "source_versions": versions,
        "rows": 2,
        "amount_total": 11,
    }
    validate(prior)
    airflow_data["write_partition"]("2026-01-01", 1, "later-correction")
    validate(prior)
    with pytest.raises(ValueError, match="independent"):
        validate(prior | {"amount_total": 13})
    with pytest.raises(ValueError, match="source identity"):
        validate(prior | {"source_versions": {"2026-01-01": "0" * 64}})


def test_ballista_fixture_rejects_forged_extra_rows_before_materialization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import hashlib

    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    namespace = runpy.run_path(str(BASE / "projects/ballista/fixture.py"))
    root = tmp_path / "fixture"
    root.mkdir()
    monkeypatch.setitem(namespace["initialize"].__globals__, "ROOT", root)
    namespace["initialize"]()
    original = (root / "orders.parquet").read_bytes()
    namespace["initialize"]()
    assert (root / "orders.parquet").read_bytes() == original
    pq.write_table(
        pa.Table.from_pylist(namespace["ROWS"] + [namespace["ROWS"][0]]), root / "orders.parquet"
    )
    manifest = root / "manifest.json"
    record = json.loads(manifest.read_text())
    record["file_sha256"] = hashlib.sha256((root / "orders.parquet").read_bytes()).hexdigest()
    manifest.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="exactly200|exactly 200"):
        namespace["read"]()


def test_airflow_mapped_regions_share_an_immutable_run_source(airflow_data: dict[str, Any]) -> None:
    write = airflow_data["write_partition"]
    capture = airflow_data["capture_source"]
    read = airflow_data["read_snapshot"]
    write("2026-01-01", 0, "first-day")
    write("2026-01-02", 0, "second-day")
    initial = capture("asset-run-before-correction")
    before = Path(initial["path"]).read_bytes()
    assert sum(row["amount"] for row in read(initial)["rows"]) == 20
    write("2026-01-01", 1, "correction")
    assert capture("asset-run-before-correction") == initial
    assert Path(initial["path"]).read_bytes() == before
    assert sum(row["amount"] for row in read(initial)["rows"]) == 20
    fresh = capture("asset-run-after-correction")
    assert sum(row["amount"] for row in read(fresh)["rows"]) == 22


@pytest.mark.parametrize(
    "end", ["2026-01-01T00:00:00+00:00", "2026-01-01T12:00:00+00:00", "2026-01-03T00:00:00+00:00"]
)
def test_airflow_rejects_zero_partial_or_multiple_day_intervals(
    airflow_data: dict[str, Any], end: str
) -> None:
    with pytest.raises(ValueError, match="one full UTC day"):
        airflow_data["validate_interval"]("2026-01-01T00:00:00+00:00", end)
    assert (
        airflow_data["validate_interval"]("2026-01-01T00:00:00+00:00", "2026-01-02T00:00:00+00:00")
        == "2026-01-01"
    )


def test_ballista_receipt_failure_keeps_actual_success_visible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import io

    namespace = runpy.run_path(str(BASE / "projects/ballista/receipts.py"))
    report = {"passed": True, "rows": [{"total": 11}], "request_id": "fixture"}
    target = tmp_path / "result.json"
    original = Path.open

    def no_pending(self: Path, *args: Any, **kwargs: Any) -> Any:
        if self.suffix == ".pending":
            raise OSError("fixture storage failure")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", no_pending)
    output = io.StringIO()
    assert namespace["emit_report"](report, target, output) is False
    shown = json.loads(output.getvalue())
    assert shown["passed"] is True and shown["rows"] == [{"total": 11}]
    assert "storage_warning" in shown and report == {
        "passed": True,
        "rows": [{"total": 11}],
        "request_id": "fixture",
    }
    assert not target.exists()


def test_ballista_atomic_receipt_never_overwrites_retained_result(tmp_path: Path) -> None:
    import io

    namespace = runpy.run_path(str(BASE / "projects/ballista/receipts.py"))
    target = tmp_path / "result.json"
    target.write_text("retained existing outcome")
    output = io.StringIO()
    assert (
        namespace["emit_report"]({"passed": False, "error": "new failed attempt"}, target, output)
        is False
    )
    assert target.read_text() == "retained existing outcome"
    assert json.loads(output.getvalue())["passed"] is False
    assert not target.with_suffix(".pending").exists()


def test_ballista_commits_exact_complete_receipt(tmp_path: Path) -> None:
    import io

    namespace = runpy.run_path(str(BASE / "projects/ballista/receipts.py"))
    target = tmp_path / "result.json"
    report = {"passed": True, "rows": [1, 2, 3]}
    output = io.StringIO()
    assert namespace["emit_report"](report, target, output) is True
    assert json.loads(target.read_text()) == json.loads(output.getvalue()) == report
    assert not target.with_suffix(".pending").exists()


def test_ballista_preexisting_pending_outcome_is_not_deleted(tmp_path: Path) -> None:
    import io

    namespace = runpy.run_path(str(BASE / "projects/ballista/receipts.py"))
    target = tmp_path / "result.json"
    pending = target.with_suffix(".pending")
    pending.write_text("prior uncertain outcome")
    output = io.StringIO()
    assert namespace["emit_report"]({"passed": True}, target, output) is False
    assert pending.read_text() == "prior uncertain outcome"
    assert not target.exists()
