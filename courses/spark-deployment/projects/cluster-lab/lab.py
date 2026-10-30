"""Own one local Spark workshop. Never pull images or remove saved state."""

import argparse
import json
import os
import platform
import re
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVICES = {"master", "worker-a", "worker-b", "driver", "history", "notebook", "ui"}


def run(args, *, env=None, capture=False, timeout=120):
    return subprocess.run(
        args, check=True, text=True, capture_output=capture, env=env, timeout=timeout
    )


def require_local_engine():
    endpoint = os.environ.get("DOCKER_HOST")
    if not endpoint or os.environ.get("DOCKER_CONTEXT"):
        endpoint = run(
            ["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"],
            capture=True,
        ).stdout.strip()
    if not endpoint.startswith("unix://"):
        raise ValueError("Select an explicitly local Unix-socket Docker engine")


def local_image(reference):
    require_local_engine()
    result = run(["docker", "image", "inspect", reference], capture=True)
    data = json.loads(result.stdout)
    if len(data) != 1 or data[0]["Os"] != "linux":
        raise ValueError("Select one existing Linux image")
    expected = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "amd64", "AMD64": "amd64"}.get(
        platform.machine()
    )
    if data[0]["Architecture"] != expected:
        raise ValueError("Only the host's native architecture is supported")
    return {"id": data[0]["Id"], "architecture": data[0]["Architecture"], "reference": reference}


def initialize(state, image, notebook_image):
    if state.exists():
        raise ValueError(
            "State already exists. Use status/resume or a different new owned directory"
        )
    runtime = local_image(image)
    notebook = local_image(notebook_image) if notebook_image else None
    owner = "ds60-spark-deploy-" + secrets.token_hex(6)
    state.mkdir(mode=0o700, parents=True)
    for name in ("events", "results", "notebooks", "artifacts"):
        target = state / name
        target.mkdir(mode=0o777)
        target.chmod(0o777)  # The parent remains private to the host user.
    private = state / "private"
    private.mkdir(mode=0o755)
    token = private / "notebook-token"
    token.write_text(secrets.token_urlsafe(32) + "\n")
    token.chmod(0o444)  # Readable to container UID 65534; private parent is 0700.
    record = {
        "schema_version": 1,
        "owner": owner,
        "source": str(ROOT),
        "state": str(state),
        "runtime": runtime,
        "notebook": notebook,
    }
    (state / "owner.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Created owned state. Existing images were inspected locally; no pull occurred.")


def load(state):
    if state.is_symlink() or not state.is_dir():
        raise ValueError("Use an existing real owned state directory")
    record = json.loads((state / "owner.json").read_text())
    if (
        record.get("schema_version") != 1
        or record.get("source") != str(ROOT)
        or record.get("state") != str(state)
    ):
        raise ValueError("Workshop owner/source/state binding differs")
    if not re.fullmatch(r"ds60-spark-deploy-[0-9a-f]{12}", record.get("owner", "")):
        raise ValueError("Malformed owner identity")
    for kind in ("runtime", "notebook"):
        if record.get(kind) and local_image(record[kind]["id"])["id"] != record[kind]["id"]:
            raise ValueError("Saved immutable image is unavailable")
    return record


def compose(record):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("COMPOSE_") and not key.startswith("DS60_")
    }
    env.update(
        {
            "DS60_SPARK_IMAGE": record["runtime"]["id"],
            "DS60_SPARK_OWNER": record["owner"],
            "DS60_SPARK_STATE": record["state"],
        }
    )
    if record.get("notebook"):
        env["DS60_NOTEBOOK_IMAGE"] = record["notebook"]["id"]
    command = [
        "docker",
        "compose",
        "--profile",
        "notebook",
        "--project-name",
        record["owner"],
        "--project-directory",
        str(ROOT),
        "--file",
        str(ROOT / "compose.yaml"),
    ]
    return command, env


def verify_containers(record):
    ids = run(
        ["docker", "ps", "-aq", "--filter", "label=com.docker.compose.project=" + record["owner"]],
        capture=True,
    ).stdout.split()
    if not ids:
        return
    for container in json.loads(run(["docker", "inspect", *ids], capture=True).stdout):
        labels = container["Config"].get("Labels") or {}
        if (
            labels.get("ds60.owner") != record["owner"]
            or labels.get("com.docker.compose.service") not in SERVICES
        ):
            raise ValueError(
                "Refusing to operate on a container outside the saved workshop ownership contract"
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=ROOT / ".workshop")
    commands = parser.add_subparsers(dest="action", required=True)
    init = commands.add_parser("init")
    init.add_argument("--image", required=True)
    init.add_argument("--notebook-image")
    for action in ("up", "resume", "stop", "down", "status", "urls", "notebook"):
        commands.add_parser(action)
    submit = commands.add_parser("submit")
    submit.add_argument("--hold-seconds", type=int, default=0)
    submit.add_argument("--partition-seconds", type=int, default=0)
    submit.add_argument("--allow-one-worker", action="store_true")
    for action in ("worker-stop", "worker-start"):
        cmd = commands.add_parser(action)
        cmd.add_argument("worker", choices=("worker-a", "worker-b"))
    args = parser.parse_args()
    if args.state.is_symlink():
        parser.error("State directory must not be a symlink")
    state = args.state.absolute()
    if args.action == "init":
        initialize(state, args.image, args.notebook_image)
        return
    record = load(state)
    verify_containers(record)
    cmd, env = compose(record)
    if args.action == "up":
        run(
            [
                *cmd,
                "up",
                "-d",
                "--no-build",
                "--pull",
                "never",
                "master",
                "worker-a",
                "worker-b",
                "driver",
                "history",
                "ui",
            ],
            env=env,
        )
    elif args.action == "resume":
        run([*cmd, "start"], env=env)
    elif args.action == "stop":
        run([*cmd, "stop", "--timeout", "20"], env=env)
    elif args.action == "down":
        run([*cmd, "down", "--timeout", "20"], env=env)
        print("Removed only this project's containers/network. Saved files remain.")
    elif args.action == "status":
        run([*cmd, "ps", "--all"], env=env)
    elif args.action == "urls":
        for service, port in (
            ("master", 8080),
            ("driver", 4040),
            ("history", 18080),
            ("notebook", 8888),
            ("notebook-spark", 14040),
        ):
            result = subprocess.run(
                [*cmd, "port", "ui", str(port)],
                env=env,
                text=True,
                capture_output=True,
                timeout=15,
            )
            if result.returncode == 0 and result.stdout.strip():
                print(f"{service} port {port}: http://{result.stdout.strip()}")
        print(
            "A driver UI exists only during its application. "
            "Notebook login uses the private token file."
        )
    elif args.action == "notebook":
        if not record.get("notebook"):
            raise ValueError("Initialize a fresh lab with an explicitly prepared notebook image")
        run([*cmd, "up", "-d", "--no-build", "--pull", "never", "notebook"], env=env)
    elif args.action in {"worker-stop", "worker-start"}:
        operation = "stop" if args.action == "worker-stop" else "start"
        run([*cmd, operation, args.worker], env=env)
    elif args.action == "submit":
        options = [
            "--hold-seconds",
            str(args.hold_seconds),
            "--partition-seconds",
            str(args.partition_seconds),
        ]
        if args.allow_one_worker:
            options.append("--allow-one-worker")
        run(
            [
                *cmd,
                "exec",
                "-T",
                "driver",
                "/opt/spark/bin/spark-submit",
                "--master",
                "spark://master:7077",
                "--deploy-mode",
                "client",
                "--conf",
                "spark.driver.host=driver",
                "--conf",
                "spark.driver.bindAddress=0.0.0.0",
                "--conf",
                "spark.driver.port=39000",
                "--conf",
                "spark.driver.blockManager.port=39001",
                "/lab/app/bounded_job.py",
                *options,
            ],
            env=env,
            timeout=360,
        )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Workshop stopped: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
