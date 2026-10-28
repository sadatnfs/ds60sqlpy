"""Course admission and actual Arrow workshop data-integrity contracts."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

import pytest

BASE = Path(__file__).resolve().parents[1] / "courses/apache-data-platforms"


def test_complete_plan_preserves_product_scope_and_distinct_cases() -> None:
    plan = json.loads((BASE / "authoring/chapter-map.json").read_text())["units"]
    assert [unit["id"] for unit in plan] == [f"apache-{index:03d}" for index in range(1, 89)]
    assert len({unit["title"] for unit in plan}) == 88
    for unit in plan:
        assert len(set(unit["worked_cases"])) == 2
        assert unit["outcome"]
    sections = {unit["section"] for unit in plan}
    assert {
        "Arrow",
        "DataFusion",
        "Ballista",
        "Airflow",
        "Kafka",
        "Iceberg",
        "Flink",
        "Cassandra",
        "Pinot",
        "Hive and Metastore",
        "Atlas",
        "Delta Sharing",
    } <= sections
    assert "Delta Lake/Linux Foundation" in (BASE / "DESIGN.md").read_text()


def test_incremental_authoring_cannot_admit_incomplete_course() -> None:
    builder = runpy.run_path(str(BASE / "authoring/build.py"))
    admitted_before = (BASE / "track.json").is_file()
    outputs = builder["outputs"](admit=admitted_before)
    assert (BASE / "track.json" in outputs) is admitted_before
    for path, text in outputs.items():
        assert path.read_text() == text
    # Complete authoring can now be reviewed for explicit admission. Removing
    # even one developed unit must still refuse a partial route.
    from unittest.mock import patch

    missing = BASE / "authoring/units/apache-088.json"
    original_exists = Path.exists
    with (
        patch.object(Path, "exists", lambda path: path != missing and original_exists(path)),
        pytest.raises(ValueError, match="apache-088 is not complete"),
    ):
        builder["outputs"](admit=True)
    admitted = builder["outputs"](admit=True)
    assert len(json.loads(admitted[BASE / "track.json"])["lessons"]) == 88
    assert len(json.loads(admitted[BASE / "lessons.json"])["lessons"]) == 88


@pytest.mark.parametrize("number", range(9, 14))
def test_arrow_chapter_embeds_exact_executable_source(number: int) -> None:
    key = f"apache-{number:03d}"
    guide = (BASE / "guides" / f"{key}.md").read_text()
    source = (BASE / "examples" / f"{key}.py").read_text()
    assert "```python\n" + source.rstrip() + "\n```" in guide
    assert guide.count("## Worked case") == 2
    assert "## Interview discussion" in guide
    assert "\u2014" not in guide


@pytest.fixture
def flight_source() -> dict[str, Any]:
    pytest.importorskip("pyarrow", reason="Optional real Arrow workshop API")
    return runpy.run_path(str(BASE / "projects/arrow-flight/service.py"))


def test_flight_fixture_survives_reinitialization_without_byte_replacement(
    tmp_path: Path, flight_source: dict[str, Any]
) -> None:
    state = tmp_path / "fixture"
    flight_source["initialize"](state)
    before = {path.name: path.read_bytes() for path in state.iterdir()}
    flight_source["initialize"](state)
    assert {path.name: path.read_bytes() for path in state.iterdir()} == before
    table = flight_source["read_fixture"](state)
    assert table.to_pylist() == [
        {"id": 1, "region": "east", "amount": 4},
        {"id": 2, "region": "west", "amount": 9},
        {"id": 3, "region": "east", "amount": 7},
    ]


def test_flight_partial_state_is_rejected_without_reset(
    tmp_path: Path, flight_source: dict[str, Any]
) -> None:
    state = tmp_path / "fixture"
    state.mkdir()
    retained = state / "manifest.json"
    retained.write_text("retained learner evidence")
    with pytest.raises(ValueError, match="regular"):
        flight_source["initialize"](state)
    assert retained.read_text() == "retained learner evidence"
    assert not (state / "events.parquet").exists()


def test_flight_manifest_corruption_does_not_mutate_data(
    tmp_path: Path, flight_source: dict[str, Any]
) -> None:
    state = tmp_path / "fixture"
    flight_source["initialize"](state)
    original = (state / "events.parquet").read_bytes()
    (state / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "logical_sha256": "0" * 64})
    )
    with pytest.raises(ValueError, match="identity"):
        flight_source["initialize"](state)
    assert (state / "events.parquet").read_bytes() == original


def test_flight_rejects_symlink_and_oversized_fixture(
    tmp_path: Path, flight_source: dict[str, Any]
) -> None:
    state = tmp_path / "fixture"
    flight_source["initialize"](state)
    manifest = state / "manifest.json"
    target = tmp_path / "external.json"
    target.write_bytes(manifest.read_bytes())
    manifest.unlink()
    manifest.symlink_to(target)
    with pytest.raises(ValueError, match="regular"):
        flight_source["read_fixture"](state)
    manifest.unlink()
    manifest.write_text(" " * 4097)
    with pytest.raises(ValueError, match="bounds"):
        flight_source["read_fixture"](state)
    assert target.read_text().startswith('{"schema_version": 1')


def test_flight_rejects_extra_rows_before_materialization(
    tmp_path: Path, flight_source: dict[str, Any]
) -> None:
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")

    state = tmp_path / "fixture"
    flight_source["initialize"](state)
    pq.write_table(
        pa.Table.from_pylist([{"id": i, "region": "east", "amount": 1} for i in range(4)]),
        state / "events.parquet",
    )
    with pytest.raises(ValueError, match="exactly three"):
        flight_source["read_fixture"](state)


@pytest.mark.parametrize("workshop", ["arrow-flight", "streaming", "cassandra"])
def test_workshop_invalid_action_has_no_docker_calls_or_state(
    tmp_path: Path, workshop: str
) -> None:
    import os
    import shutil
    import subprocess

    project = tmp_path / "owned workshop"
    project.mkdir()
    shutil.copy2(BASE / "projects" / workshop / "run.sh", project / "run.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "docker"
    fake.write_text('#!/bin/sh\necho called >> "$DOCKER_CALL_LOG"\nexit 99\n')
    fake.chmod(0o755)
    log = tmp_path / "calls"
    result = subprocess.run(
        ["bash", str(project / "run.sh"), "start", "--unknown"],
        env=os.environ
        | {"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "DOCKER_CALL_LOG": str(log)},
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert not log.exists() and not (project / ".env").exists()


@pytest.mark.parametrize("workshop", ["arrow-flight", "streaming", "cassandra"])
def test_workshop_refuses_cross_architecture_before_state_creation(
    tmp_path: Path, workshop: str
) -> None:
    import os
    import shutil
    import subprocess

    project = tmp_path / "owned workshop"
    project.mkdir()
    shutil.copy2(BASE / "projects" / workshop / "run.sh", project / "run.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "docker"
    fake.write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$DOCKER_CALL_LOG"
case "$1 $2" in
  'context inspect') echo unix:///fixture/docker.sock ;;
  'info --format') echo 'linux|aarch64' ;;
  'image inspect') echo 'linux|amd64' ;;
  *) exit 99 ;;
esac
""")
    fake.chmod(0o755)
    log = tmp_path / "calls"
    result = subprocess.run(
        ["bash", str(project / "run.sh"), "start"],
        env=os.environ
        | {
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "DOCKER_CALL_LOG": str(log),
            "DOCKER_HOST": "unix:///fixture/docker.sock",
            "DOCKER_CONTEXT": "",
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2 and "automatic emulation is disabled" in result.stderr.lower()
    assert not (project / ".env").exists() and not (project / ".workshop-lock").exists()
    assert all(
        line.startswith(("info ", "image inspect ")) for line in log.read_text().splitlines()
    )


@pytest.mark.parametrize("unsafe", [False, True])
def test_binary_installer_verifies_checksum_and_safe_members_before_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unsafe: bool
) -> None:
    import hashlib
    import io
    import tarfile
    import urllib.request

    namespace = runpy.run_path(str(BASE / "projects/streaming/binary-image/install.py"))
    installer = namespace["install"]
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w:gz") as archive:
        entry = tarfile.TarInfo("kafka_2.13-4.4.0/../../escaped")
        entry.size = 1
        archive.addfile(entry, io.BytesIO(b"x"))
    payload = data.getvalue()

    class Response(io.BytesIO):
        def geturl(self) -> str:
            return str(namespace["URL"])

    def download(url: str, *, timeout: int) -> Response:
        assert url == namespace["URL"] and timeout > 0
        return Response(payload)

    monkeypatch.setattr(urllib.request, "urlopen", download)
    if unsafe:
        monkeypatch.setitem(installer.__globals__, "SHA512", hashlib.sha512(payload).hexdigest())
    destination = tmp_path / "kafka"
    with pytest.raises(
        ValueError, match="Unsafe distribution path" if unsafe else "SHA512 mismatch"
    ):
        installer(destination)
    assert not destination.exists() and not (tmp_path / "escaped").exists()


@pytest.mark.parametrize("workshop", ["arrow-flight", "streaming", "cassandra"])
def test_resume_uses_exact_container_without_image_lookup_or_new_compose_flags(
    tmp_path: Path, workshop: str
) -> None:
    import os
    import shutil
    import subprocess

    owner = "0123456789abcdef0123456789abcdef"
    kind = {
        "arrow-flight": "apache-arrow-flight",
        "streaming": "apache-streaming",
        "cassandra": "apache-cassandra",
    }[workshop]
    prefix = {
        "arrow-flight": "ds60-apache-flight-",
        "streaming": "ds60-apache-stream-",
        "cassandra": "ds60-apache-cassandra-",
    }[workshop]
    container = "a" * 64
    project = tmp_path / "owned workshop"
    project.mkdir()
    shutil.copy2(BASE / "projects" / workshop / "run.sh", project / "run.sh")
    settings = [f"DS60_WORKSHOP_OWNER={owner}", f"DS60_WORKSHOP_PROJECT={prefix}{owner[:12]}"]
    if workshop == "arrow-flight":
        settings += [
            "DS60_PLATFORM_IMAGE=ds60sqlpy-worker-data-platforms-python:1.0.0",
        ]
    elif workshop == "cassandra":
        settings += ["DS60_CASSANDRA_IMAGE=ds60-apache-cassandra-binary:5.0.9"]
    else:
        settings += ["DS60_KAFKA_CLUSTER_ID=Q2xhc3Nyb29tS2Fma2ExMg", "DS60_KAFKA_ROUTE=binary"]
    (project / ".env").write_text("\n".join(settings) + "\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "docker"
    fake.write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$DOCKER_CALL_LOG"
case "$1 $2" in
  'info --format') echo 'linux|aarch64'; exit 0 ;;
  'ps -aq') echo "$TEST_CONTAINER"; exit 0 ;;
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
      ps) echo "$TEST_CONTAINER"; exit 0 ;;
      start) exit 0 ;;
      port) echo '127.0.0.1:18815'; exit 0 ;;
    esac
  done
fi
exit 99
""")
    fake.chmod(0o755)
    log = tmp_path / "calls"
    result = subprocess.run(
        ["bash", str(project / "run.sh"), "resume"],
        env=os.environ
        | {
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "DOCKER_CALL_LOG": str(log),
            "DOCKER_HOST": "unix:///fixture/docker.sock",
            "DOCKER_CONTEXT": "",
            "TEST_CONTAINER": container,
            "TEST_OWNER": owner,
            "TEST_KIND": kind,
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    calls = log.read_text().splitlines()
    assert any(" start " in call for call in calls)
    assert not any(
        "--wait" in call or call.startswith(("image ", "pull ", "build ")) for call in calls
    )
    assert not (project / ".workshop-lock").exists()


@pytest.mark.parametrize("workshop", ["arrow-flight", "streaming", "cassandra"])
def test_compose_tmpfs_entries_remain_complete_absolute_mount_specs(workshop: str) -> None:
    yaml = pytest.importorskip("yaml")
    config = yaml.safe_load((BASE / "projects" / workshop / "compose.yaml").read_text())
    for service in config["services"].values():
        mounts = service["tmpfs"]
        assert isinstance(mounts, list) and mounts
        assert all(
            isinstance(mount, str) and mount.startswith("/") and ":" in mount for mount in mounts
        )
        assert any(mount.startswith("/tmp:") and "size=" in mount for mount in mounts)


def test_every_developed_unit_has_exact_source_and_explicit_execution_boundary() -> None:
    """A reading notebook must never silently acquire an executable pad profile."""
    for metadata in sorted((BASE / "authoring/units").glob("apache-*.json")):
        key = metadata.stem
        meta = json.loads(metadata.read_text())
        suffix = ".py" if meta["language"] == "python" else ".md"
        source = (BASE / "authoring/programs" / (key + suffix)).read_text()
        guide = (BASE / "guides" / (key + ".md")).read_text()
        assert (BASE / "examples" / (key + suffix)).read_text() == source
        assert source.rstrip() in guide
        assert guide.count("## Worked case") == 2
        assert "Interview discussion" in guide
        assert len(meta["sources"]) >= 2
        if suffix == ".md":
            assert meta["runtime"] == "reading"
            assert "The classroom does not execute these service commands." in guide
        else:
            assert meta["runtime"] == "data-platforms-python"


@pytest.mark.parametrize("rows", [0, 4])
def test_crosslanguage_fixture_rejects_wrong_row_count(rows: int) -> None:
    import io
    import subprocess
    import sys

    pa = pytest.importorskip("pyarrow")
    ipc = pytest.importorskip("pyarrow.ipc")
    table = pa.table(
        {
            "id": pa.array(list(range(rows)), type=pa.int64()),
            "region": pa.array(["east"] * rows, type=pa.string()),
            "amount": pa.array([4] * rows, type=pa.int64()),
        }
    )
    buffer = io.BytesIO()
    with ipc.new_stream(buffer, table.schema) as writer:
        writer.write_table(table)
    result = subprocess.run(
        [sys.executable, str(BASE / "projects/arrow-flight/ipc_fixture.py"), "read"],
        input=buffer.getvalue(),
        capture_output=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert b"exact schema, values and nulls passed" not in result.stdout


def test_qualification_refuses_existing_workspace_before_docker(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(BASE / "authoring/qualify_workshop.py"))
    retained = tmp_path / "retained"
    retained.mkdir()
    marker = retained / "draft.txt"
    marker.write_text("retained learner draft")
    with pytest.raises(ValueError, match="no existing data is replaced"):
        namespace["qualify"]("arrow-flight", retained, prepare=False, require_ipc=False)
    assert marker.read_text() == "retained learner draft"
    assert list(retained.iterdir()) == [marker]


def test_qualification_reaps_own_timed_out_action_and_releases_only_its_lock(
    tmp_path: Path,
) -> None:
    import sys

    namespace = runpy.run_path(str(BASE / "authoring/qualify_workshop.py"))
    source = (
        "import os,time; from pathlib import Path; "
        "lock=Path('.workshop-lock'); lock.mkdir(); "
        "(lock/'pid').write_text(str(os.getpid())); time.sleep(10)"
    )
    with pytest.raises(RuntimeError, match="exceeded its deadline"):
        namespace["command"]([sys.executable, "-c", source], tmp_path, timeout=0.25)
    assert not (tmp_path / ".workshop-lock").exists()


def test_qualification_diagnostics_remove_transient_download_credentials() -> None:
    namespace = runpy.run_path(str(BASE / "authoring/qualify_workshop.py"))
    message = (
        # secret-scan: allow-fixture
        "Failed https://user:temporary-secret@example.test/blob?signature=temporary-token#fragment"
    )
    cleaned = namespace["safe_diagnostic"](message)
    assert cleaned == "Failed https://example.test/blob"
    assert "temporary-secret" not in cleaned and "temporary-token" not in cleaned


def test_backup_receipt_is_atomic_and_never_replaces_evidence(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(BASE / "projects/cassandra/backup_receipts.py"))
    directory = tmp_path / "evidence"
    identity = "restore_0123456789abcdef"
    namespace["save_receipt"](directory, identity, {"passed": True, "rows": 3})
    target = directory / (identity + ".json")
    original = target.read_bytes()
    with pytest.raises(FileExistsError):
        namespace["save_receipt"](directory, identity, {"passed": False})
    assert target.read_bytes() == original
    assert list(directory.iterdir()) == [target]


def test_failed_backup_receipt_save_leaves_no_partial_final_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    namespace = runpy.run_path(str(BASE / "projects/cassandra/backup_receipts.py"))
    directory = tmp_path / "evidence"
    execution = {"passed": True, "actual_sstable_import": True}

    def disk_full(*args: Any, **kwargs: Any) -> None:
        raise OSError("Synthetic full evidence filesystem")

    monkeypatch.setattr(namespace["json"], "dump", disk_full)
    with pytest.raises(OSError, match="full evidence"):
        namespace["save_receipt"](directory, "restore_0123456789abcdef", execution)
    assert execution == {"passed": True, "actual_sstable_import": True}
    assert not list(directory.iterdir())


def test_backup_receipt_rejects_linked_directory_and_path_identity(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(BASE / "projects/cassandra/backup_receipts.py"))
    outside = tmp_path / "retained"
    outside.mkdir()
    linked = tmp_path / "link"
    linked.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic link"):
        namespace["save_receipt"](linked, "restore_0123456789abcdef", {"passed": True})
    with pytest.raises(ValueError, match="identity"):
        namespace["save_receipt"](outside, "../escaped", {"passed": True})
    assert not list(outside.iterdir())


def test_replicated_cassandra_refuses_small_engine_before_saved_state(tmp_path: Path) -> None:
    import os
    import shutil
    import subprocess

    project = tmp_path / "owned"
    project.mkdir()
    shutil.copy2(BASE / "projects/cassandra/run.sh", project / "run.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "docker"
    fake.write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$DOCKER_CALL_LOG"
case "$1 $2" in
  'info --format')
    case "$3" in *MemTotal*) echo 1073741824 ;; *) echo 'linux|arm64' ;; esac ;;
  'image inspect') echo 'linux|arm64' ;;
  *) exit 99 ;;
esac
""")
    fake.chmod(0o755)
    log = tmp_path / "calls"
    result = subprocess.run(
        ["bash", str(project / "run.sh"), "start", "--replicated"],
        env=os.environ
        | {
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "DOCKER_CALL_LOG": str(log),
            "DOCKER_HOST": "unix:///fixture.sock",
            "DOCKER_CONTEXT": "",
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2 and "8 GiB" in result.stderr
    assert not (project / ".env").exists() and not (project / ".workshop-lock").exists()
    assert all(
        line.startswith(("info ", "image inspect ")) for line in log.read_text().splitlines()
    )


def test_cassandra_never_changes_a_saved_single_node_topology_implicitly(tmp_path: Path) -> None:
    import os
    import shutil
    import subprocess

    project = tmp_path / "owned"
    project.mkdir()
    shutil.copy2(BASE / "projects/cassandra/run.sh", project / "run.sh")
    owner = "0123456789abcdef0123456789abcdef"
    settings = (
        f"DS60_WORKSHOP_OWNER={owner}\n"
        f"DS60_WORKSHOP_PROJECT=ds60-apache-cassandra-{owner[:12]}\n"
        "DS60_CASSANDRA_IMAGE=ds60-apache-cassandra-binary:5.0.9\n"
    )
    (project / ".env").write_text(settings)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls"
    fake = bin_dir / "docker"
    fake.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$DOCKER_CALL_LOG"\nexit 99\n')
    fake.chmod(0o755)
    result = subprocess.run(
        ["bash", str(project / "run.sh"), "start", "--replicated"],
        env=os.environ
        | {
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "DOCKER_CALL_LOG": str(log),
            "DOCKER_HOST": "unix:///fixture.sock",
            "DOCKER_CONTEXT": "",
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2 and "differs from saved state" in result.stderr
    assert (project / ".env").read_text() == settings
    assert not log.exists() and not (project / ".workshop-lock").exists()


def test_compaction_preserves_latest_state_identity_while_obsolete_history_shrinks(
    tmp_path: Path,
) -> None:
    import hashlib

    namespace = runpy.run_path(str(BASE / "authoring/qualify_workshop.py"))
    source = b"acct-1|v1\nacct-1|v2\nacct-2|v3\n"
    (tmp_path / "retention-events.txt").write_bytes(source)
    full = {
        "schema_version": 1,
        "passed": True,
        "configured_cleanup_policy": "compact",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "source_end_offset": 3,
        "observed_log_records": 3,
        "retained_offsets": [0, 1, 2],
        "latest_key_state": {"acct-1": "v2", "acct-2": "v3"},
        "physical_compaction_demonstrated": False,
    }
    compacted = full | {"observed_log_records": 2, "retained_offsets": [1, 2]}
    assert namespace["retention_identity"](full, tmp_path) == namespace["retention_identity"](
        compacted, tmp_path
    )
    assert full["observed_log_records"] == 3 and compacted["observed_log_records"] == 2
    invalid_states: list[dict[str, object]] = [
        {"source_end_offset": 4},
        {"source_sha256": "0" * 64},
        {"observed_log_records": 2, "retained_offsets": [0, 2]},
        {"observed_log_records": 2, "retained_offsets": [1, 1]},
        {"latest_key_state": {"acct-1": "v1", "acct-2": "v3"}},
        {"observed_log_records": 1},
    ]
    for changed in invalid_states:
        with pytest.raises(ValueError):
            namespace["retention_identity"](full | changed, tmp_path)


@pytest.mark.parametrize(
    "changed",
    [
        {"committed_records": 2},
        {"uncommitted_records": 3},
        {"aborted_hidden": False},
        {"separate_duplicate_send_calls_retained": 1},
    ],
)
def test_transaction_visibility_cannot_use_the_compacted_history_exception(
    changed: dict[str, Any],
) -> None:
    namespace = runpy.run_path(str(BASE / "authoring/qualify_workshop.py"))
    baseline = {
        "schema_version": 1,
        "passed": True,
        "committed_records": 3,
        "uncommitted_records": 4,
        "aborted_hidden": True,
        "separate_duplicate_send_calls_retained": 2,
    }
    assert namespace["transaction_identity"](baseline) == baseline
    with pytest.raises(ValueError, match="not a compacted-history"):
        namespace["transaction_identity"](baseline | changed)
