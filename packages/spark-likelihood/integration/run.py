"""Qualify a copied package in an owned four-container Spark Compose environment.

The image and wheel must already exist. This program never pulls, builds an
image, contacts a registry, publishes ports, mounts an engine socket or deletes
volumes. It compiles the small original probe offline in the selected image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import tomllib
import uuid
from pathlib import Path

from evidence import collect_driver_evidence
from inputs import container_identity, image_identity, native_identity, wheel_identity
from validate import recovery, two_workers

HERE = Path(__file__).resolve().parent
PACKAGE = json.loads((HERE / "package.json").read_text())["package"]
IMPORT = "ds60_spark_tmbad" if PACKAGE == "spark-tmbad" else "ds60_spark_likelihood"
OWNER = "ds60-isolated-spark-integration"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(command, *, environment, check=True, timeout=30):
    result = subprocess.run(
        command, env=environment, capture_output=True, text=True, timeout=timeout
    )
    if check and result.returncode:
        raise RuntimeError(
            "Command failed: " + " ".join(command[:5]) + "\n" + result.stderr[-5000:]
        )
    return result


def owned_state(identifier, project, environment):
    values = json.loads(call(["docker", "inspect", identifier], environment=environment).stdout)
    value = container_identity(values, identifier, project, OWNER)
    return {
        "id": value["Id"],
        "name": value["Name"],
        "hostname": value["Config"]["Hostname"],
        "image_id": value["Image"],
        "state": value["State"],
        "mounts": value["Mounts"],
        "memory_limit": value["HostConfig"]["Memory"],
        "pid_limit": value["HostConfig"]["PidsLimit"],
        "published_ports": value["HostConfig"].get("PortBindings"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        required=True,
        help="Prepared native local image with Spark/JDK/Python and numerical dependencies",
    )
    parser.add_argument(
        "--wheel",
        type=Path,
        required=True,
        help="Noneditable package wheel built from this exact copied package",
    )
    parser.add_argument(
        "--native-install",
        type=Path,
        help="Prepared native installation; mounted only in driver, distributed by SparkFiles",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Fresh private evidence directory outside package source",
    )
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()
    if not 120 <= args.timeout <= 3600:
        raise ValueError("Choose a bounded 120..3600-second whole environment deadline")
    if PACKAGE not in {"spark-tmbad", "spark-likelihood"}:
        raise ValueError("Unknown integration package configuration")
    if args.output.exists() or args.output.is_symlink():
        raise ValueError("Preserve prior evidence: choose a fresh output directory")
    if not args.wheel.is_file() or args.wheel.suffix != ".whl":
        raise ValueError("Prepare the wheel explicitly first")
    if PACKAGE == "spark-tmbad" and (
        args.native_install is None or not (args.native_install / "artifact.json").is_file()
    ):
        raise ValueError("The native package requires its independently prepared installation")
    if PACKAGE != "spark-tmbad" and args.native_install is not None:
        raise ValueError("Torch integration does not take a native/R dependency")
    output = args.output.resolve()
    if output.is_relative_to(HERE.parent):
        raise ValueError("Keep generated evidence outside the copied package")
    project_metadata = HERE.parent / (
        "python/pyproject.toml" if PACKAGE == "spark-tmbad" else "pyproject.toml"
    )
    version = tomllib.loads(project_metadata.read_text())["project"]["version"]
    source = HERE.parent / ("python/src" if PACKAGE == "spark-tmbad" else "src") / IMPORT
    identity = wheel_identity(args.wheel, source, IMPORT, version)
    environment = dict(os.environ)
    for key in [
        "DOCKER_DEFAULT_PLATFORM",
        "COMPOSE_FILE",
        "COMPOSE_PROJECT_NAME",
        "COMPOSE_PROFILES",
    ]:
        environment.pop(key, None)
    image = json.loads(
        call(["docker", "image", "inspect", args.image], environment=environment).stdout
    )[0]
    engine = json.loads(
        call(["docker", "info", "--format", "{{json .}}"], environment=environment).stdout
    )
    architecture = image_identity(image, engine)
    native = (
        native_identity(args.native_install, HERE.parent, architecture, version)
        if args.native_install
        else None
    )
    before_volumes = call(
        ["docker", "volume", "ls", "--format", "{{.Name}}"], environment=environment
    ).stdout.splitlines()
    output.mkdir(parents=True)
    probe_dir, wheel_dir = output / "probe", output / "wheel"
    probe_dir.mkdir()
    wheel_dir.mkdir()
    shutil.copyfile(args.wheel, wheel_dir / args.wheel.name)
    (probe_dir / "source-identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    project = "ds60-it-" + uuid.uuid4().hex[:14]
    compiler = project + "-compiler"
    environment.update(
        {
            "INTEGRATION_IMAGE": image["Id"],
            "INTEGRATION_DIRECTORY": str(HERE),
            "INTEGRATION_PACKAGE": PACKAGE,
            "PROBE_DIRECTORY": str(probe_dir),
            "WHEEL_DIRECTORY": str(wheel_dir),
            "INTEGRATION_PLATFORM": "linux/" + architecture,
        }
    )
    if args.native_install:
        environment["NATIVE_INSTALL_DIRECTORY"] = str(args.native_install.resolve())
    compose = ["docker", "compose", "--project-name", project, "--file", str(HERE / "compose.yaml")]
    report = {
        "schema_version": 1,
        "accepted": False,
        "project": project,
        "package": PACKAGE,
        "image_id": image["Id"],
        "platform": "linux/" + architecture,
        "source_identity": identity,
        "native_artifact_identity": native,
        "integration_source_sha256": {
            str(p.relative_to(HERE)): digest(p)
            for p in sorted(HERE.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts
        },
        "volumes_before": sorted(before_volumes),
    }
    started = time.monotonic()
    identifiers = {}
    killed = None
    restored = False
    compose_attempted = False
    last_resource_sample = 0.0
    try:
        command = [
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
            "--env",
            "JAVA_TOOL_OPTIONS=-Duser.home=/tmp -XX:ActiveProcessorCount=2",
            "--mount",
            f"type=bind,src={HERE},dst=/integration,readonly",
            "--mount",
            f"type=bind,src={probe_dir},dst=/probe",
            "--entrypoint",
            "python3",
            image["Id"],
            "/integration/build_probe.py",
            "--output",
            "/probe/probe.jar",
        ]
        compile_result = call(command, environment=environment, check=False, timeout=240)
        (output / "compiler.log").write_text(compile_result.stdout + compile_result.stderr)
        if compile_result.returncode:
            raise RuntimeError("Offline probe compilation failed; see compiler.log")
        call(["docker", "rm", compiler], environment=environment)
        compose_attempted = True
        call(
            compose + ["up", "--detach", "--no-build", "--pull", "never"],
            environment=environment,
            timeout=180,
        )
        for service in ["master", "worker1", "worker2", "driver"]:
            identifier = call(
                compose + ["ps", "--all", "--quiet", service], environment=environment
            ).stdout.strip()
            if not re.fullmatch(r"[0-9a-f]{64}", identifier):
                raise AssertionError("Missing unique container for " + service)
            identifiers[service] = identifier
        report["containers_before"] = {
            name: owned_state(identifier, project, environment)
            for name, identifier in identifiers.items()
        }
        for item in report["containers_before"].values():
            if item["published_ports"] or any(
                mount["Type"] == "volume" or mount["Destination"].endswith("docker.sock")
                for mount in item["mounts"]
            ):
                raise AssertionError(
                    "Integration services cannot publish ports or mount volumes/engine sockets"
                )
        network = json.loads(
            call(
                ["docker", "network", "inspect", project + "_isolated"], environment=environment
            ).stdout
        )[0]
        if (
            not network["Internal"]
            or network["Labels"].get("com.docker.compose.project") != project
        ):
            raise AssertionError("Expected this project's owned internal-only network")
        report["network"] = {key: network[key] for key in ["Id", "Name", "Internal", "Driver"]}
        driver = identifiers["driver"]
        while time.monotonic() - started < args.timeout:
            if time.monotonic() - last_resource_sample >= 10:
                sample = {"elapsed_seconds": round(time.monotonic() - started, 3), "containers": {}}

                for name, identifier in identifiers.items():
                    resources = call(
                        ["docker", "exec", identifier, "python3", "/integration/resources.py"],
                        environment=environment,
                        check=False,
                    )
                    if resources.returncode == 0:
                        sample["containers"][name] = json.loads(resources.stdout)
                report.setdefault("resource_samples", []).append(sample)
                last_resource_sample = time.monotonic()
            status_result = call(
                ["docker", "exec", driver, "python3", "/integration/control.py", "status"],
                environment=environment,
                check=False,
            )
            state = json.loads(status_result.stdout) if status_result.returncode == 0 else {}
            if not killed and state.get("phase") == "loss_fit":
                waiters = state.get("waiters", [])
                hosts = {entry["host"] for entry in waiters}
                if hosts == {"worker1", "worker2"}:
                    interrupted = next(entry for entry in waiters if entry["host"] == "worker2")
                    owned_state(identifiers["worker2"], project, environment)
                    call(
                        ["docker", "stop", "--time", "0", identifiers["worker2"]],
                        environment=environment,
                    )
                    killed = {
                        "container_id": identifiers["worker2"],
                        "interrupted": interrupted,
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                        "stopped_state": owned_state(identifiers["worker2"], project, environment),
                    }
                    report["fault"] = killed
                    call(
                        ["docker", "exec", driver, "python3", "/integration/control.py", "release"],
                        environment=environment,
                    )
            if killed and not restored and state.get("phase") == "recovery_fit_complete":
                owned_state(identifiers["worker2"], project, environment)
                call(["docker", "start", identifiers["worker2"]], environment=environment)
                call(
                    ["docker", "exec", driver, "python3", "/integration/control.py", "restored"],
                    environment=environment,
                )
                restored = True
            exit_result = call(
                ["docker", "exec", driver, "cat", "/work/exit.json"],
                environment=environment,
                check=False,
            )
            if exit_result.returncode == 0:
                report["driver_exit"] = json.loads(exit_result.stdout)
                break
            time.sleep(1)
        else:
            raise TimeoutError("Whole Compose environment exceeded its deadline")
        (output / "driver").mkdir(exist_ok=True)
        collect_driver_evidence(driver, output / "driver", environment, required=True)
        result = json.loads((output / "driver/driver.json").read_text())
        if report["driver_exit"]["returncode"] != 0 or result["status"] != "passed":
            raise AssertionError(
                "Driver computation failed; inspect driver/driver.json and service logs"
            )
        if killed is None or not restored:
            raise AssertionError("Controlled worker-container loss and restart did not occur")
        report["recovery"] = recovery(result["spark_tasks"], killed["interrupted"])
        before = two_workers(result["executors_before"])
        after = two_workers(result["executors_after"])
        lost_id = killed["interrupted"]["executor_id"]
        if lost_id in {entry["executor_id"] for entry in after}:
            raise AssertionError("Stopped worker's lost executor ID was not replaced")
        report["executors_before"], report["executors_after"] = before, after
        report["accepted"] = True
    except BaseException as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)[:5000]}
    finally:
        if compose_attempted:
            for name in ["master", "worker1", "worker2", "driver"]:
                if name in identifiers:
                    continue
                discovered = call(
                    compose + ["ps", "--all", "--quiet", name], environment=environment, check=False
                )
                identifier = discovered.stdout.strip()
                if re.fullmatch(r"[0-9a-f]{64}", identifier):
                    identifiers[name] = identifier
        if "driver" in identifiers and not (output / "driver/driver.json").is_file():
            (output / "driver").mkdir(exist_ok=True)
            try:
                collect_driver_evidence(
                    identifiers["driver"], output / "driver", environment, required=False
                )
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                report.setdefault("collection_errors", []).append(str(error)[:500])
        for name, identifier in identifiers.items():
            try:
                logs = call(["docker", "logs", identifier], environment=environment, check=False)
                (output / (name + ".log")).write_text(logs.stdout + logs.stderr)
                report.setdefault("containers_after", {})[name] = owned_state(
                    identifier, project, environment
                )
            except Exception as error:
                report.setdefault("collection_errors", []).append(name + ": " + str(error)[:500])
        if compose_attempted:
            cleanup = call(
                compose + ["down", "--timeout", "5"],
                environment=environment,
                check=False,
                timeout=90,
            )
            report["cleanup_exit"] = cleanup.returncode
        call(["docker", "rm", "--force", compiler], environment=environment, check=False)
        after_volumes = call(
            ["docker", "volume", "ls", "--format", "{{.Name}}"], environment=environment
        ).stdout.splitlines()
        report["volumes_after"] = sorted(after_volumes)
        if not set(before_volumes).issubset(after_volumes):
            report["accepted"] = False
            report["volume_preservation_failure"] = True
        for sample in report.get("resource_samples", []):
            for name, resources in sample["containers"].items():
                memory = dict(
                    line.split() for line in resources.get("memory.events", "").splitlines()
                )
                pids = dict(line.split() for line in resources.get("pids.events", "").splitlines())
                if any(int(memory.get(key, "0")) for key in ["oom", "oom_kill"]) or int(
                    pids.get("max", "0")
                ):
                    report["accepted"] = False
                    report.setdefault("resource_limit_failures", []).append(
                        {"container": name, "resources": resources}
                    )
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
        if report.get("cleanup_exit", 0) or report.get("collection_errors"):
            report["accepted"] = False
        for name, item in report.get("containers_after", {}).items():
            if item["state"].get("OOMKilled"):
                report["accepted"] = False
                report.setdefault("oom_failures", []).append(name)
        (output / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "accepted": report["accepted"],
                "evidence": str(output),
                "elapsed_seconds": report["elapsed_seconds"],
                "error": report.get("error"),
            }
        )
    )
    if not report["accepted"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
