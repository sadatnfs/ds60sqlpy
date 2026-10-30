"""Prepared-route safety and semantic oracles, not service acceptance receipts."""

from __future__ import annotations

import json
import os
import runpy
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy import __version__

BASE = Path(__file__).resolve().parents[1] / "courses/apache-data-platforms"


def test_every_unit_has_developed_distinct_cases_and_no_false_run_surface() -> None:
    plan = json.loads((BASE / "authoring/chapter-map.json").read_text())["units"]
    assert len(plan) == 88
    for row in plan:
        key = row["id"]
        meta = json.loads((BASE / "authoring/units" / (key + ".json")).read_text())
        prose = (BASE / "authoring/chapters" / (key + ".md")).read_text()
        assert len(prose.split()) >= 500, key
        assert prose.count("## Worked case") == 2, key
        assert "Interview discussion" in prose, key
        assert "\u2014" not in prose, key
        assert len(meta["sources"]) >= 2
        if row["surface"] == "reading":
            assert (meta["language"], meta["runtime"]) == ("markdown", "reading"), key
        assert key not in meta["prerequisites"], key


def test_cassandra_retained_identity_rejects_same_count_wrong_business_rows() -> None:
    helper = runpy.run_path(str(BASE / "authoring/qualify_cassandra.py"))["identity"]
    with pytest.raises(ValueError, match="order identities"):
        helper(
            {
                "host_id": "01234567-0123-0123-0123-0123456789ab",
                "cluster_name": "DS60 local Cassandra",
                "read_only_no_initialization": True,
                "orders": [{"order_id": 1, "amount": 20}] * 3,
            },
            replicated=False,
        )
    with pytest.raises(ValueError, match="read-only"):
        helper({"read_only_no_initialization": False}, replicated=False)


def test_cassandra_rf3_oracle_rejects_a_wrong_replication_policy() -> None:
    helper = runpy.run_path(str(BASE / "authoring/qualify_cassandra.py"))["identity"]
    value = {
        "read_only_no_initialization": True,
        "host_ids": [f"01234567-0123-0123-0123-0123456789a{i}" for i in range(3)],
        "value": {"value": "three-replica-known-value"},
        "replication": {
            "class": "org.apache.cassandra.locator.NetworkTopologyStrategy",
            "datacenter1": "1",
        },
    }
    with pytest.raises(ValueError, match="replication policy"):
        helper(value, replicated=True)


def test_atlas_plan_has_owned_identity_and_intentionally_absent_lineage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = "0123456789abcdef0123456789abcdef"
    monkeypatch.setenv("DS60_ATLAS_OWNER", owner)
    module = runpy.run_path(str(BASE / "projects/atlas/client.py"))
    plan = module["payloads"]()
    entities = plan["entities"]["entities"]
    assert len(entities) == 4
    assert all(owner in row["attributes"]["qualifiedName"] for row in entities)
    process = entities[-1]["attributes"]
    assert process["inputs"][0]["guid"] == "-1"
    assert process["outputs"][0]["guid"] == "-2"
    assert "-3" not in {row["guid"] for row in process["inputs"] + process["outputs"]}


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://unowned.example",
        "https://user:secret@example.test",  # secret-scan: allow-fixture
        "https://example.test/?token=secret",
    ],
)
def test_atlas_credentials_cannot_be_sent_to_an_unapproved_origin(
    monkeypatch: pytest.MonkeyPatch, endpoint: str
) -> None:
    monkeypatch.setenv("DS60_ATLAS_OWNER", "a" * 32)
    monkeypatch.setenv("DS60_ATLAS_ENDPOINT", endpoint)
    module = runpy.run_path(str(BASE / "projects/atlas/client.py"))
    with pytest.raises(ValueError):
        module["Client"]()


@pytest.mark.parametrize("project", ["pinot", "hive", "atlas", "delta-sharing"])
def test_unknown_action_cannot_contact_docker_or_write_owner(tmp_path: Path, project: str) -> None:
    copied = tmp_path / "owned project"
    copied.mkdir()
    shutil.copy2(BASE / "projects" / project / "run.sh", copied / "run.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    call_log = tmp_path / "calls"
    docker = bin_dir / "docker"
    docker.write_text('#!/bin/sh\necho called >> "$DOCKER_CALL_LOG"\nexit 99\n')
    docker.chmod(0o755)
    result = subprocess.run(
        ["bash", str(copied / "run.sh"), "start", "--unknown"],
        env=os.environ
        | {
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "DOCKER_CALL_LOG": str(call_log),
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert not call_log.exists()
    assert not (copied / ".env").exists()
    assert not (copied / ".workshop-owner").exists()


def test_sharing_unsupported_protocol_stops_before_any_data_download(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pytest.importorskip("pyarrow", reason="Real portable Parquet client dependency")
    module = runpy.run_path(str(BASE / "projects/delta-sharing/client.py"))
    check = module["check"]
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps({"share": "ds60_fixture", "schema": "tutorial", "table": "orders", "version": 0})
    )
    monkeypatch.setitem(
        check.__globals__,
        "read_profile",
        lambda: {
            "endpoint": "https://fixture.example/sharing",
            "bearerToken": "synthetic-test-token",
        },
    )
    monkeypatch.setitem(check.__globals__, "Path", lambda _: contract)
    calls: list[str] = []

    def policy_fixture(url: str, **kwargs: Any) -> tuple[int, dict[str, str], bytes]:
        calls.append(url)
        if url.endswith("/query"):
            return (
                200,
                {"Delta-Table-Version": "0"},
                b'{"protocol":{"minReaderVersion":2}}\n{"file":{"url":"https://data.example/private"}}',
            )
        if url.endswith("/metadata"):
            return 200, {}, b"{}"
        name = (
            "ds60_fixture" if "/shares?" in url else "tutorial" if "/schemas?" in url else "orders"
        )
        return 200, {}, json.dumps({"items": [{"name": name}]}).encode()

    monkeypatch.setitem(check.__globals__, "fetch", policy_fixture)
    with pytest.raises(ValueError, match="Unsupported protocol"):
        check()
    assert len(calls) == 5 and not any("data.example" in call for call in calls)


def test_prepared_server_routes_never_claim_local_atlas_or_sharing_acceptance() -> None:
    atlas = (BASE / "projects/atlas/README.md").read_text()
    sharing = (BASE / "projects/delta-sharing/README.md").read_text()
    assert "Default local Atlas server execution is omitted" in atlas
    assert "No local server or advanced client feature" in sharing
    assert "Delta Lake/Linux Foundation" in sharing


def test_atlas_redirect_is_rejected_before_authorization_can_be_forwarded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DS60_ATLAS_OWNER", "a" * 32)
    module = runpy.run_path(str(BASE / "projects/atlas/client.py"))
    with pytest.raises(ValueError, match="before credential forwarding"):
        module["NoRedirect"]().redirect_request(
            None, None, 302, "redirect", {}, "https://different.example/"
        )


@pytest.mark.parametrize("partitioned", [False, True])
def test_sharing_rejects_partitioned_or_oversized_footer_before_materialization(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, partitioned: bool
) -> None:
    pa = pytest.importorskip("pyarrow", reason="Real portable Parquet client dependency")
    pq = pytest.importorskip("pyarrow.parquet")
    module = runpy.run_path(str(BASE / "projects/delta-sharing/client.py"))
    check = module["check"]
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps({"share": "ds60_fixture", "schema": "tutorial", "table": "orders", "version": 0})
    )
    monkeypatch.setitem(
        check.__globals__,
        "read_profile",
        lambda: {"endpoint": "https://fixture.example/sharing", "bearerToken": "synthetic"},
    )
    monkeypatch.setitem(check.__globals__, "Path", lambda _: contract)
    monkeypatch.setenv("DS60_SHARING_DATA_HOSTS", "data.example")
    buffer = pa.BufferOutputStream()
    pq.write_table(
        pa.table({"id": range(1001), "region": ["east"] * 1001, "amount": [4] * 1001}), buffer
    )
    parquet_bytes = buffer.getvalue().to_pybytes()
    data_requests: list[dict[str, Any]] = []

    def policy_fixture(url: str, **kwargs: Any) -> tuple[int, dict[str, str], bytes]:
        if "data.example" in url:
            data_requests.append(kwargs)
            return 200, {}, parquet_bytes
        if url.endswith("/query"):
            file = {
                "url": "https://data.example/object",
                "partitionValues": {"day": "2026-01-01"} if partitioned else {},
            }
            body = (
                json.dumps({"protocol": {"minReaderVersion": 1}})
                + "\n"
                + json.dumps({"file": file})
            )
            return 200, {"Delta-Table-Version": "0"}, body.encode()
        if url.endswith("/metadata"):
            return 200, {}, b"{}"
        name = (
            "ds60_fixture" if "/shares?" in url else "tutorial" if "/schemas?" in url else "orders"
        )
        return 200, {}, json.dumps({"items": [{"name": name}]}).encode()

    monkeypatch.setitem(check.__globals__, "fetch", policy_fixture)
    with pytest.raises(
        ValueError, match="unpartitioned table" if partitioned else "footer exceeds"
    ):
        check()
    assert len(data_requests) == (0 if partitioned else 1)
    assert all("token" not in request for request in data_requests)


@pytest.mark.parametrize(
    "project,action,envname",
    [("atlas", "apply", "atlas.env"), ("delta-sharing", "check", "sharing.env")],
)
def test_private_environment_cannot_override_saved_workshop_owner(
    tmp_path: Path,
    project: str,
    action: str,
    envname: str,
) -> None:
    copied = tmp_path / "owned"
    copied.mkdir()
    shutil.copy2(BASE / "projects" / project / "run.sh", copied / "run.sh")
    state = copied / ".workshop"
    state.mkdir()
    (state / "owner").write_text("a" * 32)
    (state / envname).write_text("DS60_ATLAS_OWNER=" + "b" * 32 + "\n")
    (state / "recipient.share").write_text("{}")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    contact = tmp_path / "contact"
    docker = binaries / "docker"
    docker.write_text("""#!/bin/sh
case "$1 $2" in
 'context inspect') echo unix:///fixture/docker.sock ;;
 'info --format') echo 'linux|aarch64' ;;
 'image inspect') echo 'linux|arm64' ;;
 'run --rm') echo contacted >> "$CONTACT_LOG" ;;
 *) exit 99 ;;
esac
""")
    docker.chmod(0o755)
    result = subprocess.run(
        ["bash", str(copied / "run.sh"), action],
        env=os.environ
        | {
            "PATH": str(binaries) + os.pathsep + os.environ["PATH"],
            "DOCKER_HOST": "unix:///fixture/docker.sock",
            "DOCKER_CONTEXT": "",
            "CONTACT_LOG": str(contact),
        },
        text=True,
        capture_output=True,
        timeout=5,
    )
    assert result.returncode == 2 and "Unexpected private environment field" in result.stderr
    assert not contact.exists()
    assert (state / "owner").read_text() == "a" * 32


def test_portable_client_private_files_use_existing_payload_exclusion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = BASE.parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    payload = runpy.run_path(str(root / "scripts/course_payload.py"))
    assert payload["ignore_private_files"](str(tmp_path), [".workshop", "client.py"]) == {
        ".workshop"
    }
    sharing = (BASE / "projects/delta-sharing/client.py").read_text()
    assert "/project/.workshop/recipient.share" in sharing
    for project in ["atlas", "delta-sharing"]:
        launcher = (BASE / "projects" / project / "run.sh").read_text()
        assert ".workshop/owner" in launcher
        assert ".workshop/lock" in launcher
        assert "source=$PWD,target=/project" not in launcher


@pytest.mark.parametrize(
    "project,wrong_image",
    [
        ("pinot", f"ds60sqlpy-worker-data-platforms-python:{__version__}"),
        ("hive", "ds60-apache-hive-postgres:17.6"),
    ],
)
def test_auxiliary_wrong_architecture_refuses_initial_state_and_compose(
    tmp_path: Path,
    project: str,
    wrong_image: str,
) -> None:
    copied = tmp_path / "owned"
    copied.mkdir()
    shutil.copy2(BASE / "projects" / project / "run.sh", copied / "run.sh")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    calls = tmp_path / "calls"
    docker = binaries / "docker"
    docker.write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$CALL_LOG"
case "$1 $2" in
 'context inspect') echo unix:///fixture/docker.sock ;;
 'info --format') echo 'linux|aarch64' ;;
 'image inspect')
   for argument in "$@"; do
     if [ "$argument" = "$WRONG_IMAGE" ]; then echo 'linux|amd64'; exit 0; fi
   done
   echo 'linux|arm64' ;;
 *) exit 99 ;;
esac
""")
    docker.chmod(0o755)
    result = subprocess.run(
        ["bash", str(copied / "run.sh"), "start"],
        env=os.environ
        | {
            "PATH": str(binaries) + os.pathsep + os.environ["PATH"],
            "DOCKER_HOST": "unix:///fixture/docker.sock",
            "DOCKER_CONTEXT": "",
            "CALL_LOG": str(calls),
            "WRONG_IMAGE": wrong_image,
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2 and "emulation is disabled" in result.stderr
    assert not (copied / ".env").exists()
    assert not any(
        line.startswith(("compose", "run", "pull", "create"))
        for line in calls.read_text().splitlines()
    )


def test_serving_oracle_rejects_correct_count_with_wrong_identity_or_missing_topology() -> None:
    oracle = runpy.run_path(str(BASE / "authoring/qualify_serving.py"))["observation"]
    common = {
        "passed": True,
        "read_only_no_initialization": True,
        "product": "Apache Pinot",
        "rows": [[1, "east", 4], [2, "west", 9], [3, "east", 7]],
        "regional_totals": [["east", 11], ["west", 9]],
        "selective_ids": [3],
        "unknown_column_rejected": True,
        "controller_metadata_observed": True,
        "offline_segment_names": ["owned-segment"],
        "broker_instances": ["Broker_broker_8099"],
        "server_instances": ["Server_server_8098"],
    }
    changed = common | {"rows": [[1, "east", 4], [1, "west", 9], [3, "east", 7]]}
    with pytest.raises(ValueError, match="independent row"):
        oracle("pinot", changed)
    with pytest.raises(ValueError, match="identity missing"):
        oracle("pinot", common | {"server_instances": []})
    assert oracle("pinot", common)["rows"] == common["rows"]


def test_service_observation_parser_rejects_ambiguous_success_records() -> None:
    parser = runpy.run_path(str(BASE / "authoring/qualify_serving.py"))["json_observation"]
    with pytest.raises(ValueError, match="exactly one"):
        parser('{"passed":true}\n{"passed":true}')
    assert parser('tool startup\n{"passed":true}') == {"passed": True}


@pytest.mark.parametrize(
    "project,kind,prefix,image_field,image",
    [
        (
            "arrow-flight",
            "apache-arrow-flight",
            "ds60-apache-flight-",
            "DS60_PLATFORM_IMAGE",
            "ds60sqlpy-worker-data-platforms-python:1.0.0",
        ),
        (
            "cassandra",
            "apache-cassandra",
            "ds60-apache-cassandra-",
            "DS60_CASSANDRA_IMAGE",
            "ds60-apache-cassandra-binary:5.0.9",
        ),
        (
            "pinot",
            "apache-pinot",
            "ds60-apache-pinot-",
            "DS60_PINOT_IMAGE",
            "ds60-apache-pinot-binary:1.5.1",
        ),
        (
            "hive",
            "apache-hive",
            "ds60-apache-hive-",
            "DS60_HIVE_IMAGE",
            "ds60-apache-hive-upstream:4.2.1",
        ),
    ],
)
def test_saved_compose_identity_ignores_ambient_fields_without_rewriting_record(
    tmp_path: Path,
    project: str,
    kind: str,
    prefix: str,
    image_field: str,
    image: str,
) -> None:
    copied = tmp_path / "owned"
    copied.mkdir()
    shutil.copy2(BASE / "projects" / project / "run.sh", copied / "run.sh")
    owner = "0123456789abcdef0123456789abcdef"
    settings = {
        "DS60_WORKSHOP_OWNER": owner,
        "DS60_WORKSHOP_PROJECT": prefix + owner[:12],
        image_field: image,
    }
    if project in {"pinot", "hive"}:
        settings["DS60_PLATFORM_IMAGE"] = "ds60sqlpy-worker-data-platforms-python:1.0.0"
    if project == "hive":
        settings["DS60_POSTGRES_IMAGE"] = "ds60-apache-hive-postgres:17.6"
    record = copied / ".env"
    record.write_text("".join(key + "=" + value + "\n" for key, value in settings.items()))
    before = record.read_bytes()
    binaries = tmp_path / "bin"
    binaries.mkdir()
    snapshot = tmp_path / "environment"
    docker = binaries / "docker"
    docker.write_text("""#!/bin/sh
case "$1 $2" in
 'context inspect') echo unix:///fixture/docker.sock; exit 0 ;;
 'info --format') echo 'linux|aarch64'; exit 0 ;;
 'ps -aq') echo "$TEST_CONTAINER"; exit 0 ;;
 'network ls' | 'volume ls') exit 0 ;;
 'inspect --format')
   case "$3" in *State.Status*) echo 'running|healthy';; *) echo "$TEST_OWNER|$TEST_KIND";; esac
   exit 0 ;;
esac
if [ "$1" = compose ]; then
 for value in "$@"; do
  case "$value" in
   ps) echo "$TEST_CONTAINER"; exit 0 ;;
   start)
     for key in $FIELD_KEYS; do
       value=$(printenv "$key")
       printf '%s=%s\\n' "$key" "$value"
     done > "$ENV_SNAPSHOT"
     exit 0 ;;

   port) echo 127.0.0.1:18815; exit 0 ;;
  esac
 done
fi
exit 99
""")
    docker.chmod(0o755)
    ambient = dict.fromkeys(settings, "ambient-conflict")
    result = subprocess.run(
        ["bash", str(copied / "run.sh"), "resume"],
        env=os.environ
        | ambient
        | {
            "PATH": str(binaries) + os.pathsep + os.environ["PATH"],
            "DOCKER_HOST": "unix:///fixture/docker.sock",
            "DOCKER_CONTEXT": "",
            "TEST_CONTAINER": "a" * 64,
            "TEST_OWNER": owner,
            "TEST_KIND": kind,
            "ENV_SNAPSHOT": str(snapshot),
            "FIELD_KEYS": " ".join(settings),
        },
        text=True,
        capture_output=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr
    exported = dict(line.split("=", 1) for line in snapshot.read_text().splitlines() if "=" in line)
    assert all(exported[key] == value for key, value in settings.items())
    assert record.read_bytes() == before


@pytest.mark.parametrize(
    "url,token",
    [
        ("https://fixture.example/", "synthetic-secret\ninvalid"),
        ("https://fixture.example/", "synthetic-secret\u00e9"),
        ("https://fixture.example/object?sig=synthetic-secret\ninvalid", None),
    ],
)
def test_sharing_malformed_url_or_credential_is_withheld_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    url: str,
    token: str | None,
) -> None:
    pytest.importorskip("pyarrow")
    module = runpy.run_path(str(BASE / "projects/delta-sharing/client.py"))

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Malformed private value reached transport")

    monkeypatch.setattr(module["urllib"].request, "build_opener", forbidden)
    with pytest.raises(ValueError, match="withheld") as error:
        module["fetch"](url, token=token)
    assert "synthetic-secret" not in str(error.value)
