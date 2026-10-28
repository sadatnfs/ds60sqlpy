"""Actual Cassandra CQL/restore/RF3 native qualification with owned cleanup."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any


def identity(value: dict[str, Any], *, replicated: bool) -> dict[str, Any]:
    if value.get("read_only_no_initialization") is not True:
        raise ValueError("Cassandra retained-state readback must be read-only")
    uuid = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"
    if replicated:
        hosts = value.get("host_ids")
        if (
            not isinstance(hosts, list)
            or len(set(hosts)) != 3
            or any(not re.fullmatch(uuid, host) for host in hosts)
        ):
            raise ValueError("Expected the same three actual Cassandra host UUIDs")
        if value.get("value") != {"value": "three-replica-known-value"} or value.get(
            "replication"
        ) != {"class": "org.apache.cassandra.locator.NetworkTopologyStrategy", "datacenter1": "3"}:
            raise ValueError("RF3 source value or replication policy changed")
    else:
        if (
            not re.fullmatch(uuid, value.get("host_id", ""))
            or value.get("cluster_name") != "DS60 local Cassandra"
        ):
            raise ValueError("Single-node Cassandra host/cluster identity changed")
        expected = [
            {
                "customer_id": "alpha",
                "day_bucket": "2026-01-01",
                "ordered_at": "2026-01-01T00:00:00",
                "order_id": 1,
                "amount": 4,
            },
            {
                "customer_id": "beta",
                "day_bucket": "2026-01-01",
                "ordered_at": "2026-01-01T00:30:00",
                "order_id": 2,
                "amount": 9,
            },
            {
                "customer_id": "alpha",
                "day_bucket": "2026-01-01",
                "ordered_at": "2026-01-01T01:00:00",
                "order_id": 3,
                "amount": 7,
            },
        ]
        if value.get("orders") != expected:
            raise ValueError("Retained Cassandra order identities/values changed")
    return value


def qualify(
    base: Path,
    workspace: Path,
    *,
    prepare: bool,
    replicated: bool,
    command: Callable[..., str],
    diagnostic: Callable[[str], str],
) -> dict[str, Any]:
    source = base / "projects/cassandra"
    if workspace.exists() or workspace.is_symlink():
        raise ValueError("Use an absent owned disposable workspace")
    if any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("Workshop source cannot contain symbolic links")
    hashes = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.rglob("*")
        if path.is_file()
        and path.name != ".env"
        and ".workshop" not in str(path.relative_to(source))
        and "__pycache__" not in str(path)
    }
    shutil.copytree(
        source,
        workspace,
        ignore=shutil.ignore_patterns(".env", ".workshop*", "__pycache__", "*.pyc"),
    )
    docker = shutil.which("docker") or str(Path.home() / ".rd/bin/docker")
    report: dict[str, Any] = {
        "schema_version": 1,
        "workshop": "cassandra-replicated" if replicated else "cassandra",
        "passed": False,
        "cleanup": False,
        "source_sha256": hashes,
        "checks": [],
    }
    safe_to_destroy = True

    def action(label: str, *args: str) -> str:
        result = command(["bash", "run.sh", *args], workspace, timeout=720 if replicated else 300)
        (workspace / (label + ".log")).write_text(result + "\n")
        return result

    def volume_names() -> set[str]:
        return set(
            command([docker, "volume", "ls", "--format", "{{.Name}}"], workspace).splitlines()
        )

    original_volumes = volume_names()
    try:
        report["engine"] = command(
            [docker, "info", "--format", "{{.OSType}}/{{.Architecture}}"], workspace
        )
        if prepare:
            action("prepare", "prepare")
        action("start", "start", *(["--replicated"] if replicated else []))
        settings = dict(
            line.split("=", 1) for line in (workspace / ".env").read_text().splitlines()
        )
        compose = [
            docker,
            "compose",
            "--env-file",
            ".env",
            "-p",
            settings["DS60_WORKSHOP_PROJECT"],
            "-f",
            "compose.yaml",
        ]
        if replicated:
            compose += ["-f", "compose.replicated.yaml"]
        services = (
            ["cassandra", "cassandra-two", "cassandra-three"] if replicated else ["cassandra"]
        )

        def ids() -> dict[str, str]:
            result = {
                service: command([*compose, "ps", "-aq", service], workspace)
                for service in services
            }
            if any(not re.fullmatch(r"[0-9a-f]{64}", item) for item in result.values()):
                raise ValueError("Expected one exact container per Cassandra node")
            return result

        def images(containers: dict[str, str]) -> dict[str, str]:
            return {
                service: command(
                    [docker, "inspect", "--format", "{{.Image}}", container], workspace
                )
                for service, container in containers.items()
            }

        def receipts(container: str) -> dict[str, str]:
            code = (
                "import hashlib,json;from pathlib import Path;"
                "print(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() "
                "for p in Path('/state/backup-evidence').glob('*.json')}))"
            )
            return json.loads(
                command([docker, "exec", container, "python3", "-c", code], workspace)
            )

        if replicated:
            actual = json.loads(action("outage", "check-replication"))
            if actual.get("passed") is not True:
                raise ValueError("Actual RF3 outage/recovery did not pass")
            report["checks"].append(
                {"name": "actual_rf3_outage_and_recovered_quorum", "result": actual}
            )
        else:
            actual = json.loads(action("cql", "check"))
            required = [
                "passed",
                "unindexed_filter_rejected",
                "rf1_one_and_quorum_passed",
                "two_replicas_unavailable",
                "cas_success_and_stale_rejection",
                "explicit_timestamp_order",
                "logical_ttl_expiry",
                "logical_delete_observed",
                "actual_storage_attached_index",
            ]
            if (
                any(actual.get(key) is not True for key in required)
                or actual.get("retained_orders") != 3
                or actual.get("alpha_ids_descending_time") != [3, 1]
            ):
                raise ValueError("Actual CQL semantic/negative oracle did not pass")
            report["checks"].append({"name": "actual_cql_sai_cas_ttl_delete", "result": actual})
            safe_to_destroy = False
            backup = json.loads(action("backup", "check-backup"))
            if (
                any(
                    backup.get(key) is not True
                    for key in [
                        "passed",
                        "actual_sstable_import",
                        "receipt_saved",
                        "original_orders_unchanged",
                    ]
                )
                or backup.get("rows") != 3
            ):
                raise ValueError("Actual SSTable restore/evidence oracle did not pass")
            report["checks"].append({"name": "actual_snapshot_sstable_restore", "result": backup})
        first = ids()
        image_ids = images(first)
        report["image_ids"] = image_ids
        report["native_platforms"] = {
            service: command(
                [docker, "image", "inspect", "--format", "{{.Os}}/{{.Architecture}}", image],
                workspace,
            )
            for service, image in image_ids.items()
        }
        observed = identity(
            json.loads(
                action("initial_identity", "replica-identity" if replicated else "identity")
            ),
            replicated=replicated,
        )
        receipt_hashes = {} if replicated else receipts(first["cassandra"])
        if not replicated:
            if not receipt_hashes:
                raise ValueError("Successful restore receipt absent")
            destination = workspace / "exported-receipts"
            destination.mkdir()
            command(
                [docker, "cp", first["cassandra"] + ":/state/backup-evidence/.", str(destination)],
                workspace,
            )
            exported = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in destination.iterdir()
                if path.is_file() and not path.is_symlink()
            }
            if exported != receipt_hashes:
                raise ValueError("Receipt export byte verification failed; owned state retained")
            report["exported_restore_receipt_sha256"] = exported
            safe_to_destroy = True
        action("stop", "stop")
        action("resume", "resume")
        if (
            ids() != first
            or identity(
                json.loads(
                    action("resumed_identity", "replica-identity" if replicated else "identity")
                ),
                replicated=replicated,
            )
            != observed
        ):
            raise ValueError("Exact Cassandra resume changed host/source identity")
        if not replicated and receipts(first["cassandra"]) != receipt_hashes:
            raise ValueError("Stored restore receipt bytes changed after resume")
        report["checks"].append({"name": "exact_container_resume_read_only", "passed": True})
        action("down", "down")
        action("replace", "start")
        replacement = ids()
        if (
            any(replacement[name] == first[name] for name in services)
            or images(replacement) != image_ids
        ):
            raise ValueError("Replacement did not use new containers with the original images")
        if (
            identity(
                json.loads(
                    action("replaced_identity", "replica-identity" if replicated else "identity")
                ),
                replicated=replicated,
            )
            != observed
        ):
            raise ValueError("Replacement changed retained Cassandra host/source identity")
        if not replicated and receipts(replacement["cassandra"]) != receipt_hashes:
            raise ValueError("Stored restore receipt bytes changed after replacement")
        report["checks"].append({"name": "retained_volume_replacement_read_only", "passed": True})
        report["initial_containers"] = first
        report["replacement_containers"] = replacement
        report["retained_identity"] = observed
        report["passed"] = True
    except Exception as error:
        report["error"] = diagnostic(str(error))
        if (workspace / ".env").is_file():
            try:
                action("failure_logs", "logs")
                report["failure_logs_saved"] = True
            except Exception as logs_error:
                report["failure_logs_error"] = diagnostic(str(logs_error))
    finally:
        if (workspace / ".env").is_file() and safe_to_destroy:
            try:
                action("destroy", "destroy", "--confirm-owned-data-loss")
                saved = dict(
                    line.split("=", 1) for line in (workspace / ".env").read_text().splitlines()
                )
                project = saved["DS60_WORKSHOP_PROJECT"]
                if re.fullmatch(r"ds60-apache-cassandra-[a-f0-9]{12}", project) is None:
                    raise ValueError("Unreviewed cleanup project identity")
                remaining = {
                    "containers": command(
                        [
                            docker,
                            "ps",
                            "-aq",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ],
                        workspace,
                    ),
                    "networks": command(
                        [
                            docker,
                            "network",
                            "ls",
                            "-q",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ],
                        workspace,
                    ),
                    "volumes": command(
                        [
                            docker,
                            "volume",
                            "ls",
                            "-q",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ],
                        workspace,
                    ),
                }
                if any(remaining.values()):
                    raise ValueError("Owned resources remain after destroy: " + str(remaining))
                report["cleanup"] = True
                report["owned_resource_absence_confirmed"] = True
            except Exception as error:
                report["cleanup_error"] = diagnostic(str(error))
                report["passed"] = False
        elif not safe_to_destroy:
            report["cleanup_error"] = (
                "Owned Cassandra state retained because restore evidence was not safely exported; "
                "inspect without replay"
            )
            report["passed"] = False
        else:
            report["cleanup"] = True
        report["preexisting_volumes_retained"] = original_volumes <= volume_names()
        if report["preexisting_volumes_retained"] is not True:
            report["passed"] = False
    return report
