"""Supervise one isolated, bounded four-container Torch training qualification.

The selected local image and integrated wheel must already exist. This script never
builds or pulls an image, contacts a registry, publishes ports, or uses volumes.
It only stops or recreates containers bearing this run's Compose project label.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import time
import uuid
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
OWNER = "ds60-work-only-torch-integration"
SERVICES = ("master", "worker1", "worker2", "driver")
CASES = ("single", "reference", "fault", "resume")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def package_identity(wheel: Path) -> dict:
    """Bind this copied package source to one wheel's exact RECORD members."""
    if not wheel.name.startswith("ds60_spark_likelihood-0.2.0-"):
        raise RuntimeError("Require the integrated 0.2.0 wheel")
    source = PACKAGE / "src"
    files = sorted(source.rglob("*.py"))
    if len(files) < 40 or len(list((source / "ds60_torch_training").glob("*.py"))) < 11:
        raise RuntimeError("Copied package source inventory is incomplete")
    expected_members = {path.relative_to(source).as_posix(): path for path in files}
    with ZipFile(wheel) as archive:
        members = archive.infolist()
        names = [member.filename for member in members]
        if len(names) != len(set(names)):
            raise RuntimeError("Duplicate wheel members")
        if len(members) > 512 or sum(member.file_size for member in members) > 64 * 1024 * 1024:
            raise RuntimeError("Integrated wheel member/expanded-byte budget exceeded")
        for member in members:
            path = PurePosixPath(member.filename)
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in member.filename
                or stat.S_ISLNK(member.external_attr >> 16)
            ):
                raise RuntimeError("Unsafe integrated wheel member")
        records = [name for name in names if name.endswith(".dist-info/RECORD")]
        if len(records) != 1:
            raise RuntimeError("Require one wheel RECORD")
        metadata_name = records[0].removesuffix("RECORD") + "METADATA"
        metadata = BytesParser().parsebytes(archive.read(metadata_name))
        if (
            metadata["Name"].replace("-", "_").lower() != "ds60_spark_likelihood"
            or metadata["Version"] != "0.2.0"
        ):
            raise RuntimeError("Integrated wheel metadata differs from candidate version")
        rows = list(csv.reader(io.StringIO(archive.read(records[0]).decode("utf-8"))))
        if any(len(row) != 3 for row in rows):
            raise RuntimeError("Malformed wheel RECORD")
        record = {row[0]: row[1] for row in rows}
        if len(record) != len(rows):
            raise RuntimeError("Duplicate wheel RECORD path")
        module_members = {
            name
            for name in names
            if name.endswith(".py")
            and name.startswith(("ds60_spark_likelihood/", "ds60_torch_training/"))
        }
        if module_members != set(expected_members):
            raise RuntimeError("Wheel Python source set differs from copied package")
        identities = {}
        for member, path in expected_members.items():
            if path.stat().st_size > 1024 * 1024:
                raise RuntimeError("Copied source module exceeds bound")
            raw = archive.read(member)
            encoded = (
                base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).rstrip(b"=").decode("ascii")
            )
            if raw != path.read_bytes() or record.get(member) != "sha256=" + encoded:
                raise RuntimeError("Copied source/wheel RECORD differs: " + member)
            identities[member] = hashlib.sha256(raw).hexdigest()
    return {"wheel_sha256": sha(wheel), "package_source_sha256": identities}


def call(argv: list[str], env: dict, *, timeout: int = 30, check: bool = True):
    result = subprocess.run(
        argv, env=env, text=True, capture_output=True, timeout=timeout, check=False
    )
    if check and result.returncode:
        raise RuntimeError("Command failed: " + " ".join(argv[:5]) + "\n" + result.stderr[-2000:])
    return result


def _inspect(identifier: str, project: str, env: dict) -> dict:
    value = json.loads(call(["docker", "inspect", identifier], env).stdout)[0]
    labels = value["Config"].get("Labels") or {}
    if (
        value["Id"] != identifier
        or labels.get("com.docker.compose.project") != project
        or labels.get("ds60.owner") != OWNER
    ):
        raise RuntimeError("Refuse an unowned or changed container identity")
    if value["HostConfig"].get("PortBindings") or any(
        mount["Type"] == "volume" or mount["Destination"].endswith("docker.sock")
        for mount in value["Mounts"]
    ):
        raise RuntimeError("Owned topology published a port or mounted a volume/socket")
    return {
        "id": identifier,
        "hostname": value["Config"]["Hostname"],
        "state": value["State"],
        "image_id": value["Image"],
        "memory_limit": value["HostConfig"]["Memory"],
        "pid_limit": value["HostConfig"]["PidsLimit"],
    }


def _identifiers(compose: list[str], project: str, env: dict) -> dict:
    found = {}
    for name in SERVICES:
        identifier = call(compose + ["ps", "--all", "--quiet", name], env).stdout.strip()
        if re.fullmatch(r"[0-9a-f]{64}", identifier) is None:
            raise RuntimeError("Missing unique owned service: " + name)
        _inspect(identifier, project, env)
        found[name] = identifier
    if len(set(found.values())) != len(SERVICES):
        raise RuntimeError("Duplicate owned container ID")
    return found


def _wait_healthy(identifier: str, project: str, env: dict, deadline: float) -> None:
    while time.monotonic() < deadline:
        state = _inspect(identifier, project, env)["state"]
        if state.get("Health", {}).get("Status") == "healthy":
            return
        if not state.get("Running"):
            raise RuntimeError("Replacement worker stopped before health admission")
        time.sleep(0.5)
    raise TimeoutError("Replacement worker did not become healthy")


def _case(shared: Path, name: str, token: str | None) -> None:
    temporary = shared / ".current-case.pending"
    temporary.write_text(json.dumps({"case": name, "token": token}, sort_keys=True) + "\n")
    temporary.replace(shared / "current-case.json")


def _read_shared_json(driver_id: str, relative: str, env: dict, *, limit: int = 1_000_000):
    """Read bounded evidence as its owning container UID on native Linux hosts."""
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("Invalid owned shared evidence path")
    script = (
        "import os,sys;"
        "p='/shared/'+sys.argv[1]; n=int(sys.argv[2]);"
        "fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0));"
        "f=os.fdopen(fd,'rb'); raw=f.read(n+1); f.close();"
        "sys.exit(2) if len(raw)>n else sys.stdout.buffer.write(raw)"
    )
    result = call(
        ["docker", "exec", driver_id, "python3", "-c", script, str(path), str(limit)],
        env,
        timeout=10,
        check=False,
    )
    if result.returncode or not result.stdout:
        raise OSError("Owned shared evidence is not complete")
    return json.loads(result.stdout)


def _wait(
    shared: Path,
    case: str,
    *,
    deadline: float,
    env: dict,
    stopped: dict | None = None,
    project: str = "",
    identifiers: dict | None = None,
):
    gate = shared / "gates" / ("ready-" + stopped["token"] + ".json") if stopped else None
    while time.monotonic() < deadline:
        if gate is not None and stopped.get("container_before") is None and gate.is_file():
            try:
                marker = _read_shared_json(
                    identifiers["driver"],
                    "gates/ready-" + stopped["token"] + ".json",
                    env,
                    limit=4096,
                )
                plan = _read_shared_json(identifiers["driver"], "attempts/mlp-fault/plan.json", env)
            except (OSError, ValueError):
                time.sleep(0.1)
                continue
            if (
                marker.get("kind") != "ds60-torch-controlled-worker-loss-gate"
                or marker.get("run_id") != plan["run_id"]
                or marker.get("plan_digest") != plan["plan_digest"]
                or marker.get("rank") != 1
                or marker.get("epoch") != 1
                or marker.get("hostname") not in {"worker1", "worker2"}
            ):
                raise RuntimeError("Fault gate differs from the committed attempt")
            host = marker["hostname"]
            identifier = identifiers[host]
            _inspect(identifier, project, env)
            call(["docker", "stop", "--time", "0", identifier], env, timeout=30)
            stopped.update(
                {
                    "host": host,
                    "marker": marker,
                    "container_before": _inspect(identifier, project, env),
                }
            )
        exit_path = shared / (case + "-driver-exit.json")
        if exit_path.is_file():
            try:
                status = _read_shared_json(
                    identifiers["driver"], case + "-driver-exit.json", env, limit=4096
                )
                receipt = _read_shared_json(identifiers["driver"], case + "-report.json", env)
            except (OSError, ValueError):
                time.sleep(0.1)
                continue
            return status, receipt
        time.sleep(0.1)
    raise TimeoutError("Owned case exceeded its hard host deadline: " + case)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument(
        "--wheel", "--package-wheel", dest="package_wheel", type=Path, required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--case-set", choices=("full", "dataframe"), default="full")
    args = parser.parse_args()
    cases = CASES if args.case_set == "full" else ("dataframe",)
    if not 180 <= args.timeout <= 1800:
        raise ValueError("Whole environment timeout must be 180..1800 seconds")
    output = args.output.absolute()
    if output.exists() or output.is_symlink() or not output.parent.is_dir():
        raise ValueError("Choose a fresh owned output under an existing parent")
    for wheel in (args.package_wheel,):
        if not wheel.is_file() or wheel.suffix != ".whl" or wheel.stat().st_size > 8 * 1024 * 1024:
            raise ValueError("The integrated source-bound wheel must be a bounded regular file")
    frozen_package = package_identity(args.package_wheel)
    env = dict(os.environ)
    for key in (
        "DOCKER_DEFAULT_PLATFORM",
        "COMPOSE_FILE",
        "COMPOSE_PROJECT_NAME",
        "COMPOSE_PROFILES",
    ):
        env.pop(key, None)
    image = json.loads(call(["docker", "image", "inspect", args.image], env).stdout)[0]
    engine = json.loads(call(["docker", "info", "--format", "{{json .}}"], env).stdout)
    native = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64", "amd64": "amd64"}.get(
        engine.get("Architecture")
    )
    architecture = image["Architecture"]
    if image["Os"] != "linux" or architecture not in {"arm64", "amd64"} or architecture != native:
        raise RuntimeError("Require inspected native Linux ARM64 or AMD64 image and engine")
    output.mkdir(mode=0o700)
    shared, wheels, probe = (output / item for item in ("shared", "wheels", "probe"))
    for directory in (shared, wheels, probe, shared / "gates"):
        directory.mkdir(mode=0o700)
    # Docker Desktop maps created bind files back to this host owner. Only this
    # scratch bind and its gate child need traversal by image user 65534.
    shared.chmod(0o777)
    (shared / "gates").chmod(0o777)
    wheels.chmod(0o755)
    probe.chmod(0o755)
    wheel_ids = {}
    for wheel in (args.package_wheel,):
        copied = wheels / wheel.name
        shutil.copyfile(wheel, copied)
        wheel_ids[wheel.name] = sha(copied)
    if len(wheel_ids) != 1 or not next(iter(wheel_ids)).startswith("ds60_spark_likelihood-0.2.0-"):
        raise ValueError("Selected wheel has an unexpected distribution identity")
    volumes_before = call(
        ["docker", "volume", "ls", "--format", "{{.Name}}"], env
    ).stdout.splitlines()
    project = "ds60-torch-" + uuid.uuid4().hex[:12]
    compiler = project + "-probe"
    env.update(
        {
            "TORCH_INTEGRATION_IMAGE": image["Id"],
            "TORCH_INTEGRATION_PLATFORM": "linux/" + architecture,
            "TORCH_INTEGRATION_DIRECTORY": str(HERE),
            "TORCH_PROBE_DIRECTORY": str(probe),
            "TORCH_WHEELS_DIRECTORY": str(wheels),
            "TORCH_SHARED_DIRECTORY": str(shared),
        }
    )
    compose = [
        "docker",
        "compose",
        "--project-name",
        project,
        "--file",
        str(HERE / "compose.yaml"),
    ]
    report = {
        "schema_version": 1,
        "kind": "ds60-torch-compose-attempt",
        "accepted": False,
        "project": project,
        "image_id": image["Id"],
        "platform": "linux/" + architecture,
        "wheel_sha256": wheel_ids,
        "package_source_identity": frozen_package,
        "probe_source_sha256": sha(HERE / "Probe.scala"),
        "integration_source_sha256": {
            p.name: sha(p)
            for p in HERE.iterdir()
            if p.is_file() and p.suffix in {".py", ".yaml", ".scala", ".md"}
        },
        "volumes_before": sorted(volumes_before),
        "cases": {},
    }
    identifiers = {}
    compose_started = False
    began = time.monotonic()
    deadline = began + args.timeout
    try:
        compiler_result = call(
            [
                "docker",
                "run",
                "--name",
                compiler,
                "--pull",
                "never",
                "--network",
                "none",
                "--platform",
                "linux/" + architecture,
                "--memory",
                "1g",
                "--cpus",
                "1",
                "--pids-limit",
                "256",
                "--label",
                "ds60.owner=" + OWNER,
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,exec,nosuid,nodev,size=536870912,mode=1777",
                "--mount",
                f"type=bind,src={HERE},dst=/integration,readonly",
                "--mount",
                f"type=bind,src={probe},dst=/probe",
                "--entrypoint",
                "python3",
                image["Id"],
                "/integration/build_probe.py",
                "--output",
                "/probe/probe.jar",
            ],
            env,
            timeout=240,
            check=False,
        )
        (output / "compiler.log").write_text(compiler_result.stdout + compiler_result.stderr)
        if compiler_result.returncode:
            raise RuntimeError("Offline probe compilation failed")
        metadata = json.loads((probe / "probe.json").read_text())
        if metadata["source_sha256"] != report["probe_source_sha256"] or metadata[
            "jar_sha256"
        ] != sha(probe / "probe.jar"):
            raise RuntimeError("Probe compiler/source/JAR identities disagree")
        _case(shared, cases[0], None)
        compose_started = True
        call(
            compose + ["up", "--detach", "--no-build", "--pull", "never"],
            env,
            timeout=180,
        )
        identifiers = _identifiers(compose, project, env)
        report["containers_initial"] = {
            key: _inspect(value, project, env) for key, value in identifiers.items()
        }
        network = json.loads(
            call(["docker", "network", "inspect", project + "_isolated"], env).stdout
        )[0]
        if (
            not network["Internal"]
            or network["Labels"].get("com.docker.compose.project") != project
        ):
            raise RuntimeError("Expected owned internal-only network")
        report["network"] = {key: network[key] for key in ("Id", "Name", "Internal", "Driver")}
        for index, case in enumerate(cases):
            if index:
                call(compose + ["stop", "--timeout", "5", "driver"], env, timeout=30)
                token = uuid.uuid4().hex if case == "fault" else None
                _case(shared, case, token)
                call(compose + ["start", "driver"], env, timeout=60)
            else:
                token = None
            stopped = {"token": token} if case == "fault" else None
            exit_status, receipt = _wait(
                shared,
                case,
                deadline=deadline,
                env=env,
                stopped=stopped,
                project=project,
                identifiers=identifiers,
            )
            report["cases"][case] = {"driver_exit": exit_status, "report": receipt}
            if case == "fault":
                report["fault"] = stopped
                if (
                    stopped.get("container_before") is None
                    or receipt["status"] != "expected_failure"
                    or exit_status["returncode"] == 0
                ):
                    raise RuntimeError("Controlled worker loss lacked failed driver/task evidence")
                failed = _read_shared_json(
                    identifiers["driver"], "attempts/mlp-fault/result.json", env
                )
                if failed["status"] != "failed":
                    raise RuntimeError("Fault attempt was incorrectly reported successful")
                host = stopped["host"]
                call(compose + ["stop", "--timeout", "5", "driver"], env, timeout=30)
                call(
                    compose
                    + [
                        "up",
                        "--detach",
                        "--no-deps",
                        "--force-recreate",
                        "--no-build",
                        "--pull",
                        "never",
                        host,
                    ],
                    env,
                    timeout=90,
                )
                replacement = _identifiers(compose, project, env)
                if replacement[host] == identifiers[host]:
                    raise RuntimeError("Faulted worker container was not replaced")
                report["fault"]["replacement"] = _inspect(replacement[host], project, env)
                _wait_healthy(replacement[host], project, env, deadline)
                identifiers = replacement
            elif receipt["status"] != "passed" or exit_status["returncode"] != 0:
                raise RuntimeError("Training case did not pass: " + case)
            if case == "resume" and (
                receipt.get("continuation", {}).get("exact_continuation_ranks") != [0, 1]
                or receipt["continuation"]
                .get("heldout_prediction", {})
                .get("exact_reference_resume_equality")
                is not True
            ):
                raise RuntimeError("Resumed tensors or response-free held-out scores differ")
        report["accepted"] = True
    except BaseException as error:  # noqa: BLE001 - preserve interruption and owned failure evidence
        report["error"] = {"type": type(error).__name__, "message": str(error)[:3000]}
    finally:
        try:
            if package_identity(args.package_wheel) != frozen_package or any(
                sha(HERE / name) != expected
                for name, expected in report["integration_source_sha256"].items()
            ):
                report["accepted"] = False
                report["source_drift"] = True
        except Exception as drift_error:  # noqa: BLE001 - retain cleanup route
            report["accepted"] = False
            report["source_drift_error"] = str(drift_error)[:1000]
        if compose_started:
            for name in SERVICES:
                container = call(compose + ["ps", "--all", "--quiet", name], env, check=False)
                identifier = container.stdout.strip()
                if re.fullmatch(r"[0-9a-f]{64}", identifier):
                    logs = call(["docker", "logs", identifier], env, check=False)
                    (output / (name + ".log")).write_text(logs.stdout + logs.stderr)
            master_id = call(
                compose + ["ps", "--all", "--quiet", "master"], env, check=False
            ).stdout.strip()
            if re.fullmatch(r"[0-9a-f]{64}", master_id):
                size_script = (
                    "from pathlib import Path;"
                    "p=Path('/shared');"
                    "print(sum(x.stat().st_size for x in p.rglob('*') if x.is_file()))"
                )
                size_result = call(
                    ["docker", "exec", master_id, "python3", "-c", size_script],
                    env,
                    check=False,
                    timeout=20,
                )
                if (
                    size_result.returncode == 0
                    and size_result.stdout.strip().isdigit()
                    and int(size_result.stdout) <= 128 * 1024 * 1024
                ):
                    collected = output / "shared-collected"
                    collected.mkdir(mode=0o700)
                    copied = call(
                        ["docker", "cp", master_id + ":/shared/.", str(collected)],
                        env,
                        check=False,
                        timeout=90,
                    )
                    report["shared_collection_exit"] = copied.returncode
                    report["shared_collection_bytes"] = int(size_result.stdout)
                    if copied.returncode:
                        report["accepted"] = False
                else:
                    report["shared_collection_error"] = (
                        "Owned shared bytes unavailable or exceed 128 MiB"
                    )
                    report["accepted"] = False
            else:
                report["shared_collection_error"] = "Owned master unavailable for artifact export"
                report["accepted"] = False
            down = call(compose + ["down", "--timeout", "5"], env, check=False, timeout=90)
            report["cleanup_exit"] = down.returncode
            if down.returncode:
                report["accepted"] = False
        call(["docker", "rm", "--force", compiler], env, check=False)
        volumes_after = call(
            ["docker", "volume", "ls", "--format", "{{.Name}}"], env
        ).stdout.splitlines()
        report["volumes_after"] = sorted(volumes_after)
        if not set(volumes_before).issubset(volumes_after):
            report["accepted"] = False
            report["volume_preservation_failure"] = True
        (output / "RESULT.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    if not report["accepted"]:
        raise SystemExit("Torch Compose qualification failed; inspect owned RESULT.json")


if __name__ == "__main__":
    main()
