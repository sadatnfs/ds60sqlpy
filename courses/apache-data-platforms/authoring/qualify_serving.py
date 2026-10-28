"""Native actual Pinot/Hive acceptance, read-only lifecycle and owned cleanup."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any


def observation(name: str, result: dict[str, Any]) -> dict[str, Any]:
    if result.get("passed") is not True or result.get("read_only_no_initialization") is not True:
        raise ValueError("A passed read-only service observation is required")
    if name == "pinot":
        expected = {
            "product": "Apache Pinot",
            "rows": [[1, "east", 4], [2, "west", 9], [3, "east", 7]],
            "regional_totals": [["east", 11], ["west", 9]],
            "selective_ids": [3],
            "unknown_column_rejected": True,
            "controller_metadata_observed": True,
        }
        if any(result.get(key) != value for key, value in expected.items()):
            raise ValueError("Pinot independent row/query/metadata oracle changed")
        for key in ["offline_segment_names", "broker_instances", "server_instances"]:
            value = result.get(key)
            if (
                not isinstance(value, list)
                or not value
                or any(not isinstance(item, str) or not item for item in value)
            ):
                raise ValueError("Pinot retained segment/role identity missing")
            expected[key] = sorted(value)
        if len(expected["offline_segment_names"]) != 1:
            raise ValueError("Expected one owned offline segment")
        return expected
    expected = {"actual_hive_sql": True, "exact_rows": 3, "invalid_column_rejected": True}
    if any(result.get(key) != value for key, value in expected.items()):
        raise ValueError("Actual Hive SQL/negative oracle changed")
    return expected


def json_observation(output: str) -> dict[str, Any]:
    rows = []
    for line in output.splitlines():
        if line.startswith("{"):
            rows.append(json.loads(line))
    if len(rows) != 1 or not isinstance(rows[0], dict):
        raise ValueError("Expected exactly one bounded service JSON observation")
    return rows[0]


def qualify(
    base: Path,
    name: str,
    workspace: Path,
    *,
    prepare: bool,
    binary: bool = False,
    mirror: bool = False,
    command: Callable[..., str],
    diagnostic: Callable[[str], str],
) -> dict[str, Any]:
    if name == "hive" and not prepare:
        raise ValueError(
            "Hive qualification requires explicit --prepare for its per-copy JDBC/class artifacts"
        )
    source = base / "projects" / name
    if workspace.exists() or workspace.is_symlink():
        raise ValueError("Use an absent disposable workspace; no existing data is replaced")
    if any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("Workshop sources cannot contain symbolic links")
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
        "workshop": name,
        "passed": False,
        "cleanup": False,
        "checks": [],
        "source_sha256": hashes,
    }

    def action(label: str, *args: str) -> str:
        result = command(
            ["bash", "run.sh", *args],
            workspace,
            timeout=1800 if args and args[0] == "prepare" else 420,
        )
        (workspace / (label + ".log")).write_text(diagnostic(result) + "\n")
        return result

    def volumes() -> set[str]:
        return set(
            command([docker, "volume", "ls", "--format", "{{.Name}}"], workspace).splitlines()
        )

    original_volumes = volumes()
    try:
        report["engine"] = command(
            [docker, "info", "--format", "{{.OSType}}/{{.Architecture}}"], workspace
        )
        if prepare:
            action(
                "prepare",
                "prepare",
                *(["--binary"] if binary else []),
                *(["--mirror"] if mirror else []),
            )
        if name == "hive":
            action("start_database", "start-db")
            action("initialize_schema", "initialize-schema")
            action("verify_schema", "verify-schema")
        action("start", "start", *(["--binary"] if binary else []))
        action("initialize", "initialize")
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
        services = (
            ["zookeeper", "controller", "broker", "server"]
            if name == "pinot"
            else ["postgres", "metastore", "hiveserver2"]
        )

        def ids() -> dict[str, str]:
            result = {
                service: command([*compose, "ps", "-aq", service], workspace)
                for service in services
            }
            if any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in result.values()):
                raise ValueError("Expected one exact container per actual service role")
            return result

        def images(containers: dict[str, str]) -> dict[str, str]:
            return {
                service: command(
                    [docker, "inspect", "--format", "{{.Image}}", container], workspace
                )
                for service, container in containers.items()
            }

        def checked(label: str) -> dict[str, Any]:
            result = json_observation(action(label, "check"))
            value = observation(name, result)
            if name == "hive":
                metadata = json_observation(action(label + "_metadata", "metadata"))
                expected = {
                    "passed": True,
                    "actual_thrift_metadata": True,
                    "columns": 3,
                    "partitions": 1,
                    "data_files_read": False,
                    "missing_table_rejected": True,
                    "typed_schema_checked": True,
                    "partition_identity_checked": True,
                }
                if any(metadata.get(key) != item for key, item in expected.items()):
                    raise ValueError("Independent actual Hive Thrift metadata oracle changed")
                value["thrift_metadata"] = expected
            return value

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
        expected = checked("initial_read_only")
        report["checks"].append({"name": "actual_rows_and_typed_negative", "result": expected})
        if checked("repeat_read_only") != expected:
            raise ValueError("Repeated read-only observation changed semantic state")
        action("stop", "stop")
        action("resume", "resume")
        if ids() != first or checked("resumed_read_only") != expected:
            raise ValueError("Exact-container resume changed source/result/role identity")
        report["checks"].append({"name": "exact_container_resume_read_only", "passed": True})
        action("down", "down")
        action("replace", "start")
        replacement = ids()
        if (
            any(replacement[role] == first[role] for role in services)
            or images(replacement) != image_ids
        ):
            raise ValueError(
                "Replacement did not use new containers with unchanged prepared images"
            )
        if checked("replaced_read_only") != expected:
            raise ValueError("Retained-volume replacement changed semantic state")
        report["checks"].append({"name": "retained_volume_replacement_read_only", "passed": True})
        report["first_containers"], report["replacement_containers"] = first, replacement
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
        if (workspace / ".env").is_file():
            try:
                action("destroy", "destroy", "--confirm-owned-data-loss")
                saved = dict(
                    line.split("=", 1) for line in (workspace / ".env").read_text().splitlines()
                )
                project = saved["DS60_WORKSHOP_PROJECT"]
                if re.fullmatch(r"ds60-apache-(?:pinot|hive)-[a-f0-9]{12}", project) is None:
                    raise ValueError("Cannot confirm cleanup for an unreviewed project identity")
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
        else:
            report["cleanup"] = True
        if (workspace / ".workshop/preparation.owner").exists():
            report["cleanup"] = False
            report["passed"] = False
            report["cleanup_error"] = (
                "Owned preparation state requires reconciliation; it was not replayed"
            )
        report["preexisting_volumes_retained"] = original_volumes <= volumes()
        if not report["preexisting_volumes_retained"]:
            report["passed"] = False
    return report
