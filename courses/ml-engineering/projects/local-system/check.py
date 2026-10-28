#!/usr/bin/env python3
"""Qualify only a fresh, explicitly disposable local Docker workshop project."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
OWNER_LABEL = "org.ds60.workshop.owner"


def command(
    arguments: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 180,
) -> str:
    result = subprocess.run(
        arguments, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {arguments[0]} {arguments[1:3]}\n"
            + (result.stdout + result.stderr)[-6000:]
        )
    return result.stdout


def resources(docker: str, project: str) -> dict[str, list[str]]:
    query = "label=com.docker.compose.project=" + project
    return {
        "containers": command([docker, "ps", "-aq", "--filter", query]).split(),
        "networks": command([docker, "network", "ls", "-q", "--filter", query]).split(),
        "volumes": command([docker, "volume", "ls", "-q", "--filter", query]).split(),
    }


def owned(docker: str, project: str, owner: str) -> dict[str, list[str]]:
    result = resources(docker, project)
    for kind, identifiers in result.items():
        if not identifiers:
            continue
        prefix = [docker, "inspect"] if kind == "containers" else [docker, kind[:-1], "inspect"]
        for row in json.loads(command([*prefix, *identifiers])):
            labels = (
                row.get("Config", {}).get("Labels") if kind == "containers" else row.get("Labels")
            )
            if not isinstance(labels, dict) or labels.get(OWNER_LABEL) != owner:
                raise RuntimeError("Refusing cleanup: project resources no longer match ownership")
    return result


def request(
    origin: str, route: str, payload: dict[str, Any] | None = None, expected: int = 200
) -> Any:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    raw = None if payload is None else json.dumps(payload, allow_nan=False).encode()
    query = urllib.request.Request(
        origin + route, data=raw, headers={"Content-Type": "application/json"}
    )
    try:
        response = opener.open(query, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        status = response.status
        body = response.read(100_001)
    if len(body) > 100_000:
        raise ValueError("Workshop response exceeded its limit")
    value = json.loads(body)
    if status != expected:
        raise AssertionError(
            f"Unexpected {route} status {status}; expected {expected}: {str(value)[:500]}"
        )
    return value


def await_ready(origin: str, owner: str, seconds: float = 60) -> dict[str, Any]:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            health = request(origin, "/health")
            if health.get("ready") is True and health.get("owner") == owner:
                return dict(health)
        except (OSError, ValueError, AssertionError):
            pass
        time.sleep(0.2)
    raise RuntimeError("Owned workshop service did not become ready")


def run_checks(docker: str, project: str, image: str, report_path: Path) -> dict[str, Any]:
    if re.fullmatch(r"ds60-mle-[a-z0-9][a-z0-9-]{0,45}", project) is None:
        raise ValueError("Use a fresh project name beginning ds60-mle-")
    if not image or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/:@-]{0,240}", image) is None:
        raise ValueError("Use an explicit local image reference")
    if any(resources(docker, project).values()):
        raise ValueError("The project already owns resources; choose a new disposable name")
    context = os.environ.get("DOCKER_CONTEXT", "")
    endpoint = os.environ.get("DOCKER_HOST", "")
    if context or not endpoint:
        arguments = [docker, "context", "inspect"] + ([context] if context else [])
        endpoint = command(
            [*arguments, "--format", "{{.Endpoints.docker.Host}}"], timeout=20
        ).strip()
    if not endpoint.startswith("unix://"):
        raise ValueError(
            "This bind-mounted loopback workshop requires a local Unix-socket Docker context"
        )
    image_info = json.loads(command([docker, "image", "inspect", image]))[0]
    owner = uuid.uuid4().hex
    directory = Path(tempfile.mkdtemp(prefix=project + "-"))
    state = directory / "state"
    state.mkdir(mode=0o700)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in {".py", ".yaml", ".html"}:
            shutil.copyfile(path, directory / path.name)
    (directory / "workshop-owner.json").write_text(json.dumps({"owner": owner, "project": project}))
    env = dict(
        os.environ,
        DS60_DATA_IMAGE=image,
        DS60_WORKSHOP_OWNER=owner,
        DS60_WORKSHOP_UID=str(os.getuid()),
        DS60_WORKSHOP_GID=str(os.getgid()),
        DS60_WORKSHOP_PORT="0",
    )
    compose = [docker, "compose", "-p", project, "-f", str(directory / "compose.yaml")]
    report: dict[str, Any] = {
        "schema_version": 1,
        "project": project,
        "owner": owner,
        "image": image,
        "image_id": image_info["Id"],
        "passed": False,
        "checks": [],
        "sources": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in HERE.iterdir()
            if p.is_file() and p.suffix in {".py", ".yaml", ".html"}
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        created = True
        command(
            [
                *compose,
                "up",
                "-d",
                "--no-build",
                "--pull",
                "never",
                "--wait",
                "--wait-timeout",
                "150",
                "predictor",
            ],
            cwd=directory,
            env=env,
            timeout=210,
        )
        owned(docker, project, owner)
        port_text = command([*compose, "port", "predictor", "8080"], cwd=directory, env=env).strip()
        match = re.fullmatch(r"127\.0\.0\.1:([0-9]+)", port_text)
        if match is None:
            container = command([*compose, "ps", "-q", "predictor"], cwd=directory, env=env).strip()
            inspected = json.loads(command([docker, "inspect", container]))[0]
            report["port_diagnostic"] = {
                "reported": port_text,
                "bindings": inspected["HostConfig"]["PortBindings"],
                "published": inspected["NetworkSettings"]["Ports"],
            }
            raise ValueError(f"Workshop port is not loopback-only: {port_text!r}")
        origin = "http://127.0.0.1:" + match[1]
        report["origin"] = origin
        health = await_ready(origin, owner)
        assert health["version"] == "v1"
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(origin + "/", timeout=15) as response:
            page = response.read(30_001)
            assert response.status == 200 and len(page) <= 30_000
            assert response.headers.get_content_type() == "text/html"
            assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert b'id="prediction-form"' in page and b"https://" not in page
        report["checks"].append("Offline prediction form served over the owned loopback endpoint")
        training = json.loads((state / "training.json").read_text())
        assert (
            training["training_rows"] == 77
            and training["validation_rows"] == 40
            and training["feature_rows"] == 120
        )
        assert all(row["accepted_for_synthetic_demo"] for row in training["models"].values())
        first = request(origin, "/predict", {"customer_id": 1})
        assert first["model_version"] == "v1" and 0 <= first["probability"] <= 1
        assert 0 <= first["feature_age_seconds"] <= 48 * 3600
        report["checks"].append(
            "Real Polars/Feast training, MLflow artifacts and loopback HTTP inference"
        )
        request(origin, "/predict", {"customer_id": -1}, expected=422)
        request(origin, "/predict", {"customer_id": 1, "label": 1}, expected=422)
        metrics = request(origin, "/metrics")
        assert metrics["counts"].get("422", 0) >= 2 and metrics["counts"].get("predictions", 0) >= 1
        assert metrics["p95_ms"] is not None and metrics["p95_ms"] >= 0
        report["checks"].append("Input rejection and bounded process monitoring")
        command(
            [
                *compose,
                "run",
                "--rm",
                "--pull",
                "never",
                "--no-deps",
                "-T",
                "control",
                "activate",
                "--version",
                "v2",
            ],
            cwd=directory,
            env=env,
        )
        second = request(origin, "/predict", {"customer_id": 1})
        assert (
            second["model_version"] == "v2"
            and abs(second["probability"] - first["probability"]) > 1e-8
        )
        command(
            [
                *compose,
                "run",
                "--rm",
                "--pull",
                "never",
                "--no-deps",
                "-T",
                "control",
                "activate",
                "--version",
                "v1",
            ],
            cwd=directory,
            env=env,
        )
        restored = request(origin, "/predict", {"customer_id": 1})
        assert restored["model_version"] == "v1" and math.isclose(
            restored["probability"], first["probability"], abs_tol=1e-12
        )
        report["checks"].append("Validated version activation and exact prediction rollback")
        command(
            [
                *compose,
                "run",
                "--rm",
                "--pull",
                "never",
                "--no-deps",
                "-T",
                "control",
                "inject-stale",
            ],
            cwd=directory,
            env=env,
        )
        stale = request(origin, "/predict", {"customer_id": 1}, expected=503)
        assert "freshness" in stale["detail"].lower()
        command(
            [
                *compose,
                "run",
                "--rm",
                "--pull",
                "never",
                "--no-deps",
                "-T",
                "control",
                "restore-features",
            ],
            cwd=directory,
            env=env,
        )
        fresh = request(origin, "/predict", {"customer_id": 1})
        assert math.isclose(fresh["probability"], first["probability"], abs_tol=1e-12)
        report["checks"].append("Actual stale online-feature rejection and controlled restoration")
        model_path = state / "models/v1/model.json"
        original = model_path.read_bytes()
        model_path.write_bytes(original + b" ")
        corrupt = request(origin, "/predict", {"customer_id": 1}, expected=503)
        assert "integrity" in corrupt["detail"].lower()
        model_path.write_bytes(original)
        assert request(origin, "/health")["ready"] is True
        report["checks"].append("Model-byte corruption fails closed before inference")
        before = {
            str(p.relative_to(state)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in state.rglob("*")
            if p.is_file()
        }
        command([*compose, "stop", "predictor"], cwd=directory, env=env)
        command(
            [
                *compose,
                "up",
                "-d",
                "--no-deps",
                "--force-recreate",
                "--no-build",
                "--pull",
                "never",
                "--wait",
                "--wait-timeout",
                "90",
                "predictor",
            ],
            cwd=directory,
            env=env,
        )
        port_text = command([*compose, "port", "predictor", "8080"], cwd=directory, env=env).strip()
        match = re.fullmatch(r"127\.0\.0\.1:([0-9]+)", port_text)
        assert match is not None
        origin = "http://127.0.0.1:" + match[1]
        await_ready(origin, owner)
        again = request(origin, "/predict", {"customer_id": 1})
        after = {
            str(p.relative_to(state)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in state.rglob("*")
            if p.is_file()
        }
        assert before == after and math.isclose(
            again["probability"], first["probability"], abs_tol=1e-12
        )
        report["checks"].append(
            "Prediction and exact durable state survive predictor replacement without retraining"
        )
        report["passed"] = True
        report["predictions"] = {
            "v1": first["probability"],
            "v2": second["probability"],
            "rolled_back": again["probability"],
        }
        report["training"] = training
    except Exception as error:
        report["failure"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        if created:
            try:
                owned(docker, project, owner)
                report["service_logs"] = command(
                    [*compose, "logs", "--no-color", "--tail", "80"], cwd=directory, env=env
                )[-12_000:]
                command([*compose, "down", "--remove-orphans"], cwd=directory, env=env)
                report["owned_resources_removed"] = not any(resources(docker, project).values())
                if report["owned_resources_removed"]:
                    marker = json.loads((directory / "workshop-owner.json").read_text())
                    if marker == {"owner": owner, "project": project}:
                        shutil.rmtree(directory)
                else:
                    report["retained_work_directory"] = str(directory)
            except Exception as cleanup_error:
                report["cleanup_failure"] = str(cleanup_error)
                report["retained_work_directory"] = str(directory)
                report["passed"] = False
        report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--image", default="ds60sqlpy-worker-data-engineering:1.0.0")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--confirm-disposable", action="store_true")
    args = parser.parse_args()
    if not args.confirm_disposable:
        parser.error("This checker creates owned test state; supply --confirm-disposable")
    docker = shutil.which("docker")
    if docker is None:
        parser.error("Start a local Docker engine and make its CLI available")
    try:
        report = run_checks(docker, args.project, args.image, args.report.resolve())
    except (OSError, ValueError, RuntimeError, AssertionError, subprocess.SubprocessError) as error:
        print(f"Workshop qualification failed: {error}")
        return 1
    for item in report["checks"]:
        print("PASS: " + item)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
