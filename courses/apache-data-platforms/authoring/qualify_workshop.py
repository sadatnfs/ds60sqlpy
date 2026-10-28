#!/usr/bin/env python3
"""Qualify one copied owned workshop, then remove only its synthetic resources.

Contributor/CI helper. Learners use the workshop's Bash launcher without host
Python. Library, service and architecture evidence stay explicitly separate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import runpy
import shutil
import signal
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

BASE = Path(__file__).resolve().parents[1]


def safe_diagnostic(value: str) -> str:
    """Do not persist transient signed download-query credentials in failures."""

    def strip_query(match: re.Match[str]) -> str:
        parts = urlsplit(match.group(0))
        return urlunsplit((parts.scheme, parts.netloc.rsplit("@", 1)[-1], parts.path, "", ""))

    return re.sub(r"https?://[^\s<>\"']+", strip_query, value)


def command(args: list[str], directory: Path, *, timeout: float = 240) -> str:
    process = subprocess.Popen(
        args,
        cwd=directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        lock = directory / ".workshop-lock"
        pid = lock / "pid"
        # This helper launched and reaped this exact process. It never takes
        # ownership of another process's lock or an uncertain prior action.
        if (
            not lock.is_symlink()
            and pid.is_file()
            and not pid.is_symlink()
            and pid.read_text().strip() == str(process.pid)
        ):
            pid.unlink()
            lock.rmdir()
        raise RuntimeError("Owned workshop action exceeded its deadline") from None
    if process.returncode:
        raise RuntimeError(
            f"Workshop action failed ({process.returncode}): "
            + safe_diagnostic((stderr + stdout)[-6000:])
        )
    return stdout.strip()


def study_identity(name: str, result: dict[str, Any], workspace: Path) -> dict[str, Any]:
    """Compare stable study-source semantics, not incidental diagnostic fields."""
    if result.get("passed") is not True:
        raise ValueError("The actual study check did not pass")
    if name == "arrow-flight":
        expected = {
            "schema_version": 1,
            "transport": "actual-arrow-flight",
            "rows": 3,
            "east_total": 11,
            "invalid_tickets_rejected": 3,
        }
        for key, value in expected.items():
            if result.get(key) != value:
                raise ValueError("Arrow semantic fixture changed: " + key)
        rows = [
            {"id": 1, "region": "east", "amount": 4},
            {"id": 2, "region": "west", "amount": 9},
            {"id": 3, "region": "east", "amount": 7},
        ]
        expected["logical_sha256"] = hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if result.get("logical_sha256") != expected["logical_sha256"]:
            raise ValueError("Arrow source identity changed")
        return expected
    expected = {
        "schema_version": 1,
        "product": "Apache Kafka",
        "records": 3,
        "partitions": 2,
        "exact_keyed_payloads": True,
        "invalid_replication_rejected": True,
        "missing_topic_rejected": True,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise ValueError("Noncompacted Kafka fixture changed: " + key)
    digest = hashlib.sha256((workspace / "events.txt").read_bytes()).hexdigest()
    if result.get("source_sha256") != digest:
        raise ValueError("Noncompacted Kafka source identity changed")
    offsets = result.get("partition_end_offsets")
    if (
        not isinstance(offsets, dict)
        or set(offsets) != {"0", "1"}
        or any(type(value) is not int or value < 0 for value in offsets.values())
        or sum(offsets.values()) != 3
    ):
        raise ValueError("Noncompacted Kafka partition positions changed")
    return expected | {"source_sha256": digest, "partition_end_offsets": offsets}


def retention_identity(result: dict[str, Any], workspace: Path) -> dict[str, Any]:
    """An obsolete compacted record may disappear; latest state/positions may not."""
    expected_state = {"acct-1": "v2", "acct-2": "v3"}
    expected_digest = hashlib.sha256((workspace / "retention-events.txt").read_bytes()).hexdigest()
    if (
        result.get("schema_version") != 1
        or result.get("passed") is not True
        or result.get("configured_cleanup_policy") != "compact"
        or result.get("source_sha256") != expected_digest
        or result.get("source_end_offset") != 3
        or result.get("latest_key_state") != expected_state
        or result.get("physical_compaction_demonstrated") is not False
    ):
        raise ValueError("Compacted fixture source/latest-key state contract changed")
    offsets = result.get("retained_offsets")
    if (
        not isinstance(offsets, list)
        or any(type(value) is not int for value in offsets)
        or offsets != sorted(set(offsets))
        or not {1, 2} <= set(offsets) <= {0, 1, 2}
        or result.get("observed_log_records") != len(offsets)
    ):
        raise ValueError("Compacted fixture retained offsets violate the allowed history")
    return {
        "source_sha256": expected_digest,
        "source_end_offset": 3,
        "configured_cleanup_policy": "compact",
        "latest_key_state": expected_state,
    }


def transaction_identity(result: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version": 1,
        "passed": True,
        "committed_records": 3,
        "uncommitted_records": 4,
        "aborted_hidden": True,
        "separate_duplicate_send_calls_retained": 2,
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise ValueError("Transaction visibility changed; it is not a compacted-history fixture")
    return expected


def qualify(
    name: str,
    workspace: Path,
    *,
    prepare: bool,
    require_ipc: bool,
    binary: bool = False,
    mirror: bool = False,
) -> dict[str, Any]:
    if mirror and name != "hive":
        raise ValueError("The digest-identical mirror route belongs to Hive")
    if binary and name not in {"pinot", "streaming"}:
        raise ValueError("The explicit binary route belongs to Pinot or Kafka")
    if name in {"pinot", "hive"}:
        if require_ipc:
            raise ValueError("IPC qualification belongs to Arrow Flight")
        helper = runpy.run_path(str(BASE / "authoring/qualify_serving.py"))
        return helper["qualify"](
            BASE,
            name,
            workspace,
            prepare=prepare,
            binary=binary,
            mirror=mirror,
            command=command,
            diagnostic=safe_diagnostic,
        )
    if name in {"cassandra", "cassandra-replicated"}:
        if require_ipc:
            raise ValueError("IPC qualification belongs to the Arrow Flight project")
        helper = runpy.run_path(str(BASE / "authoring/qualify_cassandra.py"))
        return helper["qualify"](
            BASE,
            workspace,
            prepare=prepare,
            replicated=name == "cassandra-replicated",
            command=command,
            diagnostic=safe_diagnostic,
        )
    source = BASE / "projects" / name
    if workspace.exists() or workspace.is_symlink():
        raise ValueError("Use a new absent disposable workspace; no existing data is replaced")
    if require_ipc and name != "arrow-flight":
        raise ValueError("IPC qualification belongs to the Arrow Flight project")
    if prepare and name != "streaming":
        raise ValueError("Prepare Flight's classroom images through the main launcher first")
    files = sorted(path for path in source.rglob("*") if path.is_file())
    if any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("Workshop sources cannot contain symbolic links")
    hashes = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in files
        if path.name != ".env" and ".workshop" not in str(path)
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
        "source_sha256": hashes,
        "checks": [],
        "cleanup": False,
    }

    def action(label: str, *arguments: str) -> str:
        output = command(["bash", "run.sh", *arguments], workspace)
        (workspace / (label + ".log")).write_text(output + "\n")
        return output

    try:
        report["engine"] = command(
            [docker, "info", "--format", "{{.OSType}}/{{.Architecture}}"], workspace
        )
        if prepare:
            action("prepare", "prepare", "--binary")
        action("start", "start", *(["--binary"] if name == "streaming" else []))
        fields = dict(line.split("=", 1) for line in (workspace / ".env").read_text().splitlines())
        project = fields["DS60_WORKSHOP_PROJECT"]
        compose = [docker, "compose", "--env-file", ".env", "-p", project, "-f", "compose.yaml"]
        if name == "streaming":
            compose += ["-f", "compose.binary.yaml"]
        service = "server" if name == "arrow-flight" else "kafka"
        first = command([*compose, "ps", "-aq", service], workspace)
        if len(first) != 64 or any(char not in "0123456789abcdef" for char in first):
            raise AssertionError("Expected one exact Docker container identity")
        server_image = command([docker, "inspect", "--format", "{{.Image}}", first], workspace)
        report["server_image"] = {
            "id": server_image,
            "native_platform": command(
                [docker, "image", "inspect", "--format", "{{.Os}}/{{.Architecture}}", server_image],
                workspace,
            ),
        }
        if require_ipc:
            rust_image = (
                "ds60sqlpy-worker-rust-stable:" + fields["DS60_PLATFORM_IMAGE"].rsplit(":", 1)[1]
            )
            report["rust_image_id"] = command(
                [docker, "image", "inspect", "--format", "{{.Id}}", rust_image], workspace
            )
        initial = json.loads(action("initial", "check"))
        initial_identity = study_identity(name, initial, workspace)
        compacted_identity: dict[str, Any] | None = None
        transaction_state: dict[str, Any] | None = None
        report["checks"].append({"name": "actual_semantic_read", "result": initial})
        if name == "arrow-flight":
            network = json.loads(action("network", "network-check"))
            if (
                network.get("service_dns_read_passed") is not True
                or network.get("client_loopback_rejected") is not True
            ):
                raise AssertionError("Namespace diagnostic did not establish both paths")
            report["checks"].append({"name": "actual_namespace", "result": network})
            if require_ipc:
                output = action("ipc", "ipc-check")
                if "exact schema, values and nulls passed" not in output:
                    raise AssertionError("Cross-language semantic oracle did not pass")
                report["checks"].append({"name": "compiled_rust_python_ipc", "passed": True})
        else:
            for label in ["transactions", "consumers", "retention"]:
                result = json.loads(action(label, "check-" + label))
                if result.get("passed") is not True:
                    raise AssertionError(f"Actual {label} check failed")
                if label == "retention":
                    compacted_identity = retention_identity(result, workspace)
                elif label == "transactions":
                    transaction_state = transaction_identity(result)
                report["checks"].append({"name": label, "result": result})
            action("schema", "check-schema")
            report["checks"].append(
                {"name": "local_schema_validator", "passed": True, "is_registry_service": False}
            )
        if (
            study_identity(name, json.loads(action("repeat", "check")), workspace)
            != initial_identity
        ):
            raise AssertionError("Repeated fixture initialization changed source/result")
        if name == "streaming":
            repeated = json.loads(action("repeat_retention", "check-retention"))
            if retention_identity(repeated, workspace) != compacted_identity:
                raise AssertionError("Latest compacted state changed on repeated observation")
        action("stop", "stop")
        action("resume", "resume")
        if command([*compose, "ps", "-aq", service], workspace) != first:
            raise AssertionError("Resume replaced the retained container")
        if (
            study_identity(name, json.loads(action("resumed", "check")), workspace)
            != initial_identity
        ):
            raise AssertionError("Semantic result changed after exact resume")
        if name == "streaming":
            resumed = json.loads(action("resumed_retention", "check-retention"))
            if retention_identity(resumed, workspace) != compacted_identity:
                raise AssertionError("Latest compacted state changed after exact resume")
        report["checks"].append({"name": "exact_container_resume", "passed": True})
        action("down", "down")
        action("replace", "start")
        replacement = command([*compose, "ps", "-aq", service], workspace)
        if replacement == first or len(replacement) != 64:
            raise AssertionError("Expected a replacement container over retained state")
        if (
            command([docker, "inspect", "--format", "{{.Image}}", replacement], workspace)
            != server_image
        ):
            raise AssertionError(
                "The image tag changed during qualification; retry with stable prepared images"
            )
        if (
            study_identity(name, json.loads(action("replaced", "check")), workspace)
            != initial_identity
        ):
            raise AssertionError("Semantic result changed after replacement")
        if name == "streaming":
            retained = json.loads(action("retained_transactions", "check-transactions"))
            if transaction_identity(retained) != transaction_state:
                raise AssertionError("Retained transaction isolation state changed")
            replaced = json.loads(action("replaced_retention", "check-retention"))
            if retention_identity(replaced, workspace) != compacted_identity:
                raise AssertionError("Latest compacted state changed after replacement")
            report["checks"].append({"name": "compacted_state_across_lifecycle", "passed": True})
        report["checks"].append({"name": "retained_volume_replacement", "passed": True})
        report["passed"] = True
    except Exception as error:
        report["error"] = safe_diagnostic(str(error))
    finally:
        if (workspace / ".env").is_file():
            try:
                action("destroy", "destroy", "--confirm-owned-data-loss")
                report["cleanup"] = True
            except Exception as error:
                report["cleanup_error"] = safe_diagnostic(str(error))
                report["passed"] = False
        else:
            report["cleanup"] = True
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workshop",
        choices=["arrow-flight", "streaming", "cassandra", "cassandra-replicated", "pinot", "hive"],
    )
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument(
        "--binary", action="store_true", help="Explicit checksum-binary Pinot route"
    )
    parser.add_argument(
        "--mirror", action="store_true", help="Explicit digest-identical Hive mirror"
    )
    parser.add_argument("--require-ipc", action="store_true")
    args = parser.parse_args()
    if args.workshop == "hive" and not args.prepare:
        parser.error(
            "Hive requires --prepare for its per-copy JDBC and compiled metadata artifacts"
        )
    if args.mirror and args.workshop != "hive":
        parser.error("--mirror is the explicit Hive download route")
    if args.evidence.exists() or args.evidence.is_symlink():
        parser.error("Evidence output must be absent; historical receipts are retained")
    if args.workspace.is_symlink():
        parser.error("Workspace cannot be a symbolic link")
    report = qualify(
        args.workshop,
        args.workspace.resolve(),
        prepare=args.prepare,
        require_ipc=args.require_ipc,
        binary=args.binary,
        mirror=args.mirror,
    )
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "passed": report["passed"],
                "workshop": args.workshop,
                "checks": len(report["checks"]),
                "cleanup": report["cleanup"],
            }
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
