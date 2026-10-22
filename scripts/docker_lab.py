#!/usr/bin/env python3
"""Build/start a local Docker lab, preserve host progress, and open its browser."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "ds60sqlpy-lab:0.3.0"


class LaunchError(RuntimeError):
    """An actionable local-engine or startup problem."""


def docker_executable() -> str:
    candidates = [shutil.which("docker"), str(Path.home() / ".rd/bin/docker")]
    if os.name == "nt":
        candidates.extend(
            [
                str(Path.home() / ".rd/bin/docker.exe"),
                str(
                    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
                    / "Docker/Docker/resources/bin/docker.exe"
                ),
            ]
        )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise LaunchError(
        "Docker CLI was not found. Install/start your local engine, then reopen the terminal."
    )


def output(command: list[str], env: dict[str, str], *, required: bool = True) -> str:
    result = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
    if result.returncode and required:
        raise LaunchError(result.stderr.strip() or "Docker did not complete the requested check.")
    return result.stdout.strip() if result.returncode == 0 else ""


def docker_environment() -> dict[str, str]:
    """Use the same explicit local endpoint for validation and every Docker call."""
    env = dict(os.environ)
    if env.get("DOCKER_HOST"):
        env.pop("DOCKER_CONTEXT", None)
    return env


def local_engine(docker: str, env: dict[str, str]) -> bool:
    """Refuse remote bind mounts; return whether this is a rootless local engine."""
    endpoint = env.get("DOCKER_HOST") or output(
        [docker, "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"], env
    )
    if not endpoint.startswith(("unix://", "npipe://", "tcp://127.0.0.1:", "tcp://localhost:")):
        raise LaunchError(
            "Choose a local Docker context. Host-saved progress cannot use a remote engine path."
        )
    details = output([docker, "info", "--format", "{{json .}}"], env)
    info = json.loads(details)
    if info.get("OSType", "linux") != "linux":
        raise LaunchError(
            "Switch the engine to Linux containers. Windows learners use the WSL 2 backend."
        )
    output([docker, "compose", "version"], env)
    return "rootless" in json.dumps(info.get("SecurityOptions", [])).casefold()


def environment(args: argparse.Namespace, *, rootless: bool) -> dict[str, str]:
    env = docker_environment()
    uid = os.getuid() if hasattr(os, "getuid") else 1000
    gid = os.getgid() if hasattr(os, "getgid") else 1000
    env.update(
        {
            "DS60_UID": str(0 if rootless else uid or 1000),
            "DS60_GID": str(0 if rootless else gid or 1000),
            "DS60_ROOTLESS": "1" if rootless else "0",
            "DS60_LEARNING_DIR": str(args.data_dir.expanduser().resolve()),
            "DS60_LAB_PORT": str(args.port),
            "DS60_POSTGRES_PORT": str(args.database_port),
        }
    )
    return env


def wait_for_lab(url: str, *, timeout: float = 120) -> None:
    deadline = time.monotonic() + timeout
    opener = build_opener(ProxyHandler({}))
    while time.monotonic() < deadline:
        try:
            with opener.open(url, timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(1)
    raise LaunchError(
        "The lab did not become ready. Run status and inspect this project's lab/postgres logs."
    )


def open_browser(url: str) -> None:
    kernel = platform.release().casefold()
    if os.name != "nt" and ("microsoft" in kernel or "wsl" in kernel):
        if shutil.which("wslview"):
            subprocess.Popen(["wslview", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        if shutil.which("cmd.exe"):
            subprocess.Popen(
                ["cmd.exe", "/c", "start", "", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
    if not webbrowser.open(url):
        print("Open the printed URL in your browser.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", nargs="?", default="start", choices=("start", "build", "stop", "status", "doctor")
    )
    parser.add_argument("--build", action="store_true", help="Rebuild before starting.")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=os.environ.get("DS60_LAB_PORT", "8765"))
    parser.add_argument(
        "--database-port", type=int, default=os.environ.get("DS60_POSTGRES_PORT", "55432")
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("DS60_LEARNING_DIR", ROOT / ".learning")),
    )
    parser.add_argument("--project", default="ds60-learning")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,48}", args.project):
        parser.error(
            "Choose a lowercase project name using letters, numbers, hyphens, or underscores."
        )
    if not all(1 <= value <= 65535 for value in (args.port, args.database_port)):
        parser.error("Ports must be between 1 and 65535.")
    if args.port == args.database_port:
        parser.error("The browser and database need different host ports.")
    try:
        docker = docker_executable()
        rootless = local_engine(docker, docker_environment())
        env = environment(args, rootless=rootless)
        command = [
            docker,
            "compose",
            "--project-directory",
            str(ROOT),
            "--project-name",
            args.project,
            "--file",
            str(ROOT / "compose.yaml"),
            "--profile",
            "lab",
        ]
        url = f"http://127.0.0.1:{args.port}/learn"
        print(f"Local lab: {url}\nSaved progress and pads: {env['DS60_LEARNING_DIR']}", flush=True)
        if args.action == "doctor":
            print("Docker engine and Compose are ready (Linux containers).")
            print(f"Rootless engine: {rootless}. No data directory was created.")
            return 0
        if args.action in {"status", "stop"}:
            return subprocess.run(
                command + (["ps"] if args.action == "status" else ["stop"]), env=env, check=False
            ).returncode
        installed = output(
            [docker, "image", "inspect", IMAGE, "--format", "{{.Id}}"], env, required=False
        )
        if args.action == "build" or args.build or not installed:
            print(
                "Building locally. First build downloads packages; nothing is pushed.",
                flush=True,
            )
            build = command + ["build"]
            if env.get("DS60_BASE_IMAGE"):
                build += ["--build-arg", f"DS60_BASE_IMAGE={env['DS60_BASE_IMAGE']}"]
            result = subprocess.run(build + ["lab"], env=env, check=False)
            if result.returncode:
                return result.returncode
        if args.action == "build":
            return 0
        Path(env["DS60_LEARNING_DIR"]).mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            command + ["up", "--wait", "--wait-timeout", "120", "--no-build"], env=env, check=False
        )
        if result.returncode:
            return result.returncode
        wait_for_lab(url)
        print("Ready. Stop keeps your host-saved progress and database volume.", flush=True)
        if not args.no_browser:
            open_browser(url)
        return 0
    except (LaunchError, OSError, ValueError) as exc:
        print(f"DS60 could not start: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
