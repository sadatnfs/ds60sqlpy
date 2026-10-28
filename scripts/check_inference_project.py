"""Qualify a fresh owned inference workshop, preserving its synthetic evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "courses/data-ml-engineering/projects/inference-service"


def environment() -> dict[str, str]:
    excluded = {
        "DOCKERHUB_USERNAME",
        "DOCKERHUB_TOKEN",
        "HUB_USER",
        "HUB_TOKEN",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "DOCKER_CONFIG",
        "DOCKER_DEFAULT_PLATFORM",
    }
    return {
        key: value
        for key, value in os.environ.items()
        if key not in excluded and not key.startswith(("DS60_", "COMPOSE_", "WORKSHOP_"))
    }


def output(command: list[str], env: dict[str, str]) -> str:
    return subprocess.check_output(command, env=env, text=True, timeout=30).strip()


def identities(project: str, env: dict[str, str]) -> dict[str, dict[str, str]]:
    ids = output(
        ["docker", "ps", "-aq", "--filter", "label=com.docker.compose.project=" + project], env
    ).split()
    if len(ids) != 1:
        raise ValueError("The owned inference project must contain exactly one container")
    rows = json.loads(output(["docker", "inspect", *ids], env))
    result = {}
    for row in rows:
        labels = row["Config"]["Labels"]
        if labels.get("ds60.workshop") != "inference-service":
            raise ValueError("Refuse to modify containers without workshop ownership")
        if row["State"]["Status"] != "running" or row["State"]["Health"]["Status"] != "healthy":
            raise ValueError("The owned inference container is not healthy")
        result[row["Id"]] = {"image_id": row["Image"]}
    return result


def browser_interpreter(path: Path) -> Path:
    if not path.is_file():
        raise ValueError("Use an explicitly prepared Playwright Python interpreter")
    # A venv needs its interpreter path, rather than the symlink's bare target,
    # to locate its prepared site-packages after the caller's directory changes.
    return path.absolute()


def qualify(project: str, image: str, browser_python: Path | None = None) -> dict[str, Any]:
    if re.fullmatch(r"ds60-infer-(?:ci|pub)-[a-z0-9][a-z0-9-]{0,30}", project) is None:
        raise ValueError("Use a fresh ds60-infer-ci- or ds60-infer-pub- project")
    if re.fullmatch(r"ds60sqlpy-worker-llm-torch-cpu:[0-9]+\.[0-9]+\.[0-9]+", image) is None:
        raise ValueError("Use the already prepared local versioned Torch CPU classroom image")
    env = environment()
    aliases = {"aarch64": "arm64", "x86_64": "amd64", "arm64": "arm64", "amd64": "amd64"}
    engine_arch = aliases.get(output(["docker", "info", "--format", "{{.Architecture}}"], env))
    base = json.loads(output(["docker", "image", "inspect", image], env))[0]
    if engine_arch not in {"amd64", "arm64"} or (base["Os"], base["Architecture"]) != (
        "linux",
        engine_arch,
    ):
        raise ValueError("The prepared image must match the native Linux engine architecture")
    for command in (
        ["docker", "ps", "-aq"],
        ["docker", "network", "ls", "-q"],
        ["docker", "volume", "ls", "-q"],
    ):
        if output([*command, "--filter", "label=com.docker.compose.project=" + project], env):
            raise ValueError("Choose a fresh project; existing resources will not be touched")
    workspace = ROOT / "work" / "inference-projects" / project
    if workspace.exists() or workspace.is_symlink():
        raise ValueError("Choose a fresh workspace; previous evidence will not be overwritten")
    if browser_python is not None:
        browser_python = browser_interpreter(browser_python)
    workspace.mkdir(parents=True)
    evidence = workspace / "evidence"
    evidence.mkdir()
    hashes = {}
    for path in sorted(SOURCE.iterdir()):
        if path.name in {".workshop", "__pycache__", ".pytest_cache", ".ruff_cache"}:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError("Workshop preparation accepts regular maintained source files only")
        shutil.copy2(path, workspace / path.name)
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env.update(
        WORKSHOP_PROJECT=project,
        WORKSHOP_PORT=str(port),
        WORKSHOP_BASE_IMAGE=image,
        WORKSHOP_PACING="0.02",
    )
    url = f"http://127.0.0.1:{port}"

    def run(name: str, command: list[str], timeout: int = 120) -> None:
        with (evidence / (name + ".log")).open("w") as stream:
            subprocess.run(
                command,
                cwd=workspace,
                env=env,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=timeout,
            )

    def api(name: str, prior: str | None = None) -> None:
        command = [
            sys.executable,
            "check_api.py",
            "--url",
            url,
            "--token-file",
            ".workshop/token",
            "--report",
            str(evidence / (name + ".json")),
        ]
        if prior:
            command.extend(["--verify-persisted", str(evidence / (prior + ".json"))])
        run(name, command)

    started = False
    try:
        run("prepare", ["bash", "workshop", "prepare"], 600)
        # Set before start so a partially created service is also cleaned on failure.
        started = True
        run("start", ["bash", "workshop", "start"])
        first = identities(project, env)
        runtime_names = [path.name for path in SOURCE.glob("serving_*.py")] + [
            "server.py",
            "prepare.py",
            "check_model.py",
            "corpus.txt",
            "index.html",
            "app.js",
            "style.css",
        ]
        probe = (
            "from pathlib import Path;import hashlib,json;print(json.dumps({"
            "p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in "
            + repr(runtime_names)
            + "}))"
        )
        actual_source = json.loads(
            output(["docker", "exec", next(iter(first)), "python", "-c", probe], env)
        )
        if actual_source != {name: hashes[name] for name in runtime_names}:
            raise ValueError("The running image does not match its maintained source")
        api("api")
        if browser_python:
            run(
                "browser",
                [
                    str(browser_python),
                    "check_browser.py",
                    "--url",
                    url,
                    "--output",
                    str(evidence / "browser"),
                ],
            )
        run("stop", ["bash", "workshop", "stop"])
        run("resume", ["bash", "workshop", "resume"])
        resumed = identities(project, env)
        if resumed != first:
            raise ValueError("Resume must retain exact container and image identities")
        api("resumed", "api")
        run("replace", ["bash", "workshop", "replace"])
        replaced = identities(project, env)
        if set(first) & set(replaced) or list(first.values()) != list(replaced.values()):
            raise ValueError("Replacement must change the container and retain the image")
        api("replaced", "api")
        if browser_python:
            run(
                "browser-replaced",
                [
                    str(browser_python),
                    "check_browser.py",
                    "--url",
                    url,
                    "--verify-persisted",
                    str(evidence / "browser/browser.json"),
                    "--output",
                    str(evidence / "browser-replaced"),
                ],
            )
        actual = json.loads(output(["docker", "image", "inspect", image], env))[0]
        if actual["Id"] != base["Id"]:
            raise ValueError("The base image changed during qualification")
        result = {
            "passed": True,
            "project": project,
            "architecture": engine_arch,
            "base_image_id": base["Id"],
            "source_sha256": hashes,
            "running_source_sha256": actual_source,
            "first": first,
            "resumed": resumed,
            "replaced": replaced,
            "browser_qualified": browser_python is not None,
            "persistent_records_unchanged": True,
        }
        (evidence / "qualification.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
    finally:
        if started:
            # The helper validates the same workshop label before stopping.
            run("cleanup-stop", ["bash", "workshop", "stop"])
            run(
                "cleanup-containers",
                [
                    "docker",
                    "compose",
                    "--project-name",
                    project,
                    "--env-file",
                    ".workshop/settings.env",
                    "-f",
                    "compose.yaml",
                    "down",
                ],
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--browser-python", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--confirm-disposable", action="store_true", required=True)
    args = parser.parse_args()
    result = qualify(args.project, args.image, args.browser_python)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print("Owned CPU inference, SSE, exact resume and persistent replacement checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
