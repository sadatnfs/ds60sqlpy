"""Actual disposable Docker acceptance; uses only host Python's standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import urllib.error
from pathlib import Path
from typing import Any
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

SOURCE = Path(__file__).resolve().parent


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        raise ValueError("The private acceptance client refuses redirects")


def qualify(workspace: Path, image: str) -> dict[str, Any]:
    workspace = workspace.absolute()
    if workspace.exists() or workspace.is_symlink():
        raise ValueError("Use a new disposable workspace; previous state and evidence are retained")
    docker = shutil.which("docker") or str(Path.home() / ".rd/bin/docker")
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("DS60_", "WORKSHOP_", "COMPOSE_"))
        and key
        not in {
            "DOCKERHUB_USERNAME",
            "DOCKERHUB_TOKEN",
            "GH_TOKEN",
            "GITHUB_TOKEN",
            "DOCKER_CONFIG",
            "DOCKER_DEFAULT_PLATFORM",
        }
    }
    actual = json.loads(subprocess.check_output([docker, "image", "inspect", image], env=env))[0]
    architecture = subprocess.check_output(
        [docker, "info", "--format", "{{.Architecture}}"], env=env, text=True
    ).strip()
    native = {"aarch64": "arm64", "x86_64": "amd64", "arm64": "arm64", "amd64": "amd64"}.get(
        architecture
    )
    if native not in {"amd64", "arm64"} or (actual["Os"], actual["Architecture"]) != (
        "linux",
        native,
    ):
        raise ValueError("Use an existing image that matches the native Linux engine")
    if any(path.is_symlink() for path in SOURCE.rglob("*") if ".workshop" not in path.parts):
        raise ValueError("Maintained workshop source cannot contain symbolic links")
    shutil.copytree(
        SOURCE,
        workspace,
        ignore=shutil.ignore_patterns(
            ".workshop", "__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache", ".DS_Store"
        ),
    )
    evidence = workspace / "evidence"
    evidence.mkdir()
    hashes = {
        str(path.relative_to(workspace)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in workspace.rglob("*")
        if path.is_file() and "evidence" not in path.relative_to(workspace).parts
    }
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env.update(DS60_PRODUCT_PORT=str(port), DS60_PRODUCT_IMAGE=image)

    def run(name: str, args: list[str], expected: int = 0) -> dict[str, Any] | None:
        result = subprocess.run(
            ["bash", "run.sh", *args],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        (evidence / (name + ".stdout")).write_text(result.stdout)
        (evidence / (name + ".stderr")).write_text(result.stderr)
        if result.returncode != expected:
            raise ValueError(
                f"Owned acceptance step {name} returned {result.returncode}, expected {expected}"
            )
        if args[0] in {
            "ingest",
            "publish",
            "recover",
            "history",
            "rollback",
            "product",
            "snapshots",
            "snapshot",
        } and result.stdout.strip().startswith("{"):
            document: dict[str, Any] = json.loads(result.stdout)
            return document
        return None

    settings: dict[str, str] = {}
    token = ""
    origin = f"http://127.0.0.1:{port}"
    opener = build_opener(ProxyHandler({}), NoRedirect())

    def http(
        path: str, body: bytes | None = None, expected: int = 200, *, bad_token: bool = False
    ) -> dict[str, Any]:
        request = Request(
            origin + path,
            data=body,
            headers={
                "Origin": origin,
                "Content-Type": "application/json",
                "X-DS60-Product-Token": "invalid" if bad_token else token,
            },
        )
        try:
            response = opener.open(request, timeout=10)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            if response.status != expected:
                raise ValueError(f"HTTP acceptance received {response.status}, expected {expected}")
            value: dict[str, Any] = json.loads(response.read(65_537))
            return value

    def files() -> dict[str, str]:
        directory = workspace / ".workshop/published/versions"
        return {
            str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in directory.rglob("*")
            if path.is_file()
        }

    def identity() -> dict[str, str]:
        ids = subprocess.check_output(
            [
                docker,
                "ps",
                "-aq",
                "--filter",
                "label=com.docker.compose.project=" + settings["DS60_PRODUCT_PROJECT"],
            ],
            text=True,
            env=env,
        ).split()
        rows = json.loads(subprocess.check_output([docker, "inspect", *ids], env=env))
        if (
            len(rows) != 1
            or rows[0]["Config"]["Labels"].get("ds60.workshop.owner")
            != settings["DS60_PRODUCT_OWNER"]
        ):
            raise ValueError("Owned API container identity does not match")
        return {"container_id": rows[0]["Id"], "image_id": rows[0]["Image"]}

    started = False
    try:
        run("reject-extra-start-argument", ["start", "--unknown"], 2)
        if (workspace / ".workshop").exists():
            raise ValueError("Invalid action arguments created private state")
        started = True
        run("start", ["start"])
        settings = dict(
            line.split("=", 1)
            for line in (workspace / ".workshop/settings.env").read_text().splitlines()
        )
        if settings["DS60_PRODUCT_IMAGE_ID"] != actual["Id"]:
            raise ValueError("The initial image selection changed during acceptance")
        token = (workspace / ".workshop/private/token").read_text().strip()
        http("/api/status", bad_token=True, expected=403)
        run("ingest-baseline", ["ingest", "baseline.json"])
        raw_baseline = http("/api/snapshots")
        baseline_data = json.loads((workspace / "fixtures/baseline.json").read_text())
        changed = json.loads(json.dumps(baseline_data))
        changed["records"][0]["packages"] = 4
        http("/api/snapshots", json.dumps(changed).encode(), expected=409)
        boolean = json.loads(json.dumps(baseline_data))
        boolean["records"][0]["packages"] = True
        http("/api/snapshots", json.dumps(boolean).encode(), expected=400)
        wrong_count = {**baseline_data, "expected_rows": 2}
        http("/api/snapshots", json.dumps(wrong_count).encode(), expected=400)
        duplicate = json.dumps(baseline_data).replace(
            '"generation": 1', '"generation": 1, "generation": 1', 1
        )
        http("/api/snapshots", duplicate.encode(), expected=400)
        if http("/api/snapshots") != raw_baseline:
            raise ValueError("Rejected requests modified the accepted raw population")
        replay = run("exact-replay", ["ingest", "baseline.json"])
        if replay is None or replay["created"] is not False:
            raise ValueError("Exact HTTP replay created another snapshot")
        run("publish-baseline", ["publish", "baseline"])
        baseline = http("/api/product")
        expected_baseline = [
            {"route_id": 10, "deliveries": 2, "packages": 5},
            {"route_id": 20, "deliveries": 1, "packages": 1},
        ]
        if baseline["rows"] != expected_baseline:
            raise ValueError("Actual published baseline differs from the independent oracle")
        baseline_version = baseline["pointer"]["version_id"]
        pointer_path = workspace / ".workshop/published/active.json"
        baseline_pointer = pointer_path.read_bytes()
        run("ingest-corrected", ["ingest", "corrected.json"])
        run("before-pointer-exit", ["publish", "corrected", "--failpoint", "before-pointer"], 71)
        prepared_files = files()
        recovery = run("before-pointer-recovery", ["recover"])
        if (
            recovery is None
            or len(recovery["prepared_not_active"]) != 1
            or pointer_path.read_bytes() != baseline_pointer
            or http("/api/product")["rows"] != expected_baseline
        ):
            raise ValueError("Recovery silently activated a prepared product")
        prepared_version = recovery["prepared_not_active"][0]["version_id"]
        prepared_manifest = (
            workspace / ".workshop/published/versions" / prepared_version / "manifest.json"
        )
        prepared_bytes = prepared_manifest.read_bytes()
        try:
            prepared_manifest.write_bytes(prepared_bytes + b"\n")
            run("changed-prepared-manifest-refusal", ["publish", "corrected"], 3)
            if pointer_path.read_bytes() != baseline_pointer:
                raise ValueError("Changed prepared manifest was activated before verification")
        finally:
            prepared_manifest.write_bytes(prepared_bytes)
        run("explicit-prepared-activation", ["publish", "corrected"])
        if files() != prepared_files or http("/api/product")["rows"][0]["packages"] != 7:
            raise ValueError(
                "Prepared activation rewrote data or produced the wrong corrected value"
            )
        run("ingest-invalid-candidate", ["ingest", "unknown-route.json"])
        before_rejection = pointer_path.read_bytes()
        run("quality-rejection", ["publish", "unknown-route"], 2)
        if pointer_path.read_bytes() != before_rejection:
            raise ValueError("Invalid analytical candidate changed the accepted pointer")
        run("ingest-later", ["ingest", "later.json"])
        raw = http("/api/snapshots")
        run("after-pointer-exit", ["publish", "later", "--failpoint", "after-pointer"], 72)
        if http("/api/product")["rows"][0]["packages"] != 9:
            raise ValueError("A valid activated pointer was mistaken for no execution")
        retained_files = files()
        recovery = run("after-pointer-recovery", ["recover"])
        if (
            recovery is None
            or recovery["observation"]["receipt"]["completion_observation"]
            != "recovered_after_pointer"
            or recovery["observation"]["receipt"]["raw_reingested"]
        ):
            raise ValueError("Pointer recovery did not reconcile the actual operation")
        if files() != retained_files or http("/api/snapshots") != raw:
            raise ValueError("Reconciliation replayed or rewrote existing evidence")
        history = run("history-before-restart", ["history"])
        pointer = pointer_path.read_bytes()
        first = identity()
        run("stop", ["stop"])
        run("exact-resume", ["resume"])
        resumed = identity()
        if resumed != first:
            raise ValueError("Resume replaced an existing container or image")
        if (
            run("history-after-resume", ["history"]) != history
            or http("/api/snapshots") != raw
            or files() != retained_files
            or pointer_path.read_bytes() != pointer
        ):
            raise ValueError("Exact resume changed retained state")
        run("replace", ["replace"])
        replaced = identity()
        if (
            replaced["container_id"] == first["container_id"]
            or replaced["image_id"] != first["image_id"]
        ):
            raise ValueError("Replacement did not retain the saved image")
        if (
            run("history-after-replacement", ["history"]) != history
            or http("/api/snapshots") != raw
            or files() != retained_files
            or pointer_path.read_bytes() != pointer
        ):
            raise ValueError("Replacement changed retained state")
        run(
            "explicit-rollback",
            ["rollback", baseline_version, "--reason", "Review the retained synthetic baseline"],
        )
        active = http("/api/product")
        if active["rows"] != expected_baseline or active["pointer"]["high_water_generation"] != 4:
            raise ValueError("Rollback lost the accepted high-water generation")
        pointer = pointer_path.read_bytes()
        run("stale-publication-refusal", ["publish", "corrected"], 2)
        if pointer_path.read_bytes() != pointer:
            raise ValueError("A stale publication changed the rollback selection")
        parquet = workspace / ".workshop/published/versions" / baseline_version / "routes.parquet"
        original = parquet.read_bytes()
        try:
            changed_bytes = bytearray(original)
            changed_bytes[len(changed_bytes) // 2] ^= 1
            parquet.write_bytes(changed_bytes)
            http("/api/product", expected=503)
        finally:
            parquet.write_bytes(original)
        if http("/api/product")["rows"] != expected_baseline:
            raise ValueError("Owned corruption-fixture restoration failed")
        for relative, expected in hashes.items():
            if hashlib.sha256((workspace / relative).read_bytes()).hexdigest() != expected:
                raise ValueError("Maintained source changed during acceptance")
        report = {
            "passed": True,
            "platform": "linux/" + str(native),
            "image_id": actual["Id"],
            "project": settings["DS60_PRODUCT_PROJECT"],
            "source_sha256": hashes,
            "first": first,
            "resumed": resumed,
            "replaced": replaced,
            "actual_process_exit_codes": [71, 72],
            "raw_receipts_unchanged": True,
            "immutable_versions_unchanged_through_restarts": True,
            "explicit_rollback_high_water": 4,
            "corruption_rejected": True,
        }
        (evidence / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")
        return report
    finally:
        if started and (workspace / ".workshop/settings.env").is_file():
            run("cleanup-owned-containers", ["down"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--confirm-disposable", action="store_true", required=True)
    args = parser.parse_args()
    report = qualify(args.workspace, args.image)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("Native HTTP, publication, process recovery and exact persistence passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
