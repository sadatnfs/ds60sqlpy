"""Offline prepared-image Spark service for the integrated one-wheel candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import stat
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_wheel(wheel: Path, target: Path) -> dict:
    with zipfile.ZipFile(wheel) as archive:
        members = archive.infolist()
        if len(members) > 512 or sum(member.file_size for member in members) > 64 * 1024 * 1024:
            raise RuntimeError("Wheel member/expanded-byte budget exceeded")
        for member in members:
            name = PurePosixPath(member.filename)
            if (
                name.is_absolute()
                or ".." in name.parts
                or not name.parts
                or member.file_size > 8 * 1024 * 1024
                or stat.S_ISLNK(member.external_attr >> 16)
            ):
                raise RuntimeError("Unsafe or oversized wheel member")
            if member.is_dir():
                continue
            destination = target.joinpath(*name.parts)
            if destination.exists():
                raise RuntimeError("Wheel member collision")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, destination.open("xb") as output:
                copied = 0
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    copied += len(chunk)
                    if copied > 8 * 1024 * 1024:
                        raise RuntimeError("Wheel extraction exceeds member bound")
                    output.write(chunk)
    return {"name": wheel.name, "sha256": _sha(wheel)}


def _prepare_python() -> None:
    wheels = sorted(Path("/wheels").glob("*.whl"))
    if len(wheels) != 1 or not wheels[0].name.startswith("ds60_spark_likelihood-0.2.0-"):
        raise RuntimeError("Mount exactly one source-bound integrated 0.2.0 wheel")
    target = Path("/work/python")
    target.mkdir(mode=0o700)
    identity = [_extract_wheel(wheel, target) for wheel in wheels]
    Path("/work/wheels.json").write_text(json.dumps(identity, sort_keys=True) + "\n")
    spark_home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    pyspark_zip = spark_home / "python/lib/pyspark.zip"
    py4j = sorted((spark_home / "python/lib").glob("py4j-*-src.zip"))
    if not pyspark_zip.is_file() or len(py4j) != 1:
        raise RuntimeError("Prepared Spark Python zip/py4j source paths are absent")
    os.environ["PYTHONPATH"] = ":".join(
        (str(target), "/opt/spark-torch", str(pyspark_zip), str(py4j[0]))
    )
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=["master", "worker", "driver", "health"])
    parser.add_argument("--host", default="")
    args = parser.parse_args()
    if args.role == "health":
        with socket.create_connection(
            (args.host, 7077 if args.host == "master" else 7078), timeout=2
        ):
            pass
        return
    _prepare_python()
    host = args.host or args.role
    os.environ["SPARK_LOCAL_IP"] = socket.gethostbyname(host)
    os.environ["SPARK_LOCAL_HOSTNAME"] = host
    home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    if args.role == "master":
        command = [
            str(home / "bin/spark-class"),
            "org.apache.spark.deploy.master.Master",
            "--host",
            "master",
            "--port",
            "7077",
            "--webui-port",
            "8080",
        ]
    elif args.role == "worker":
        command = [
            str(home / "bin/spark-class"),
            "org.apache.spark.deploy.worker.Worker",
            "--host",
            args.host,
            "--port",
            "7078",
            "--webui-port",
            "8081",
            "--cores",
            "1",
            "--memory",
            "512M",
            "--work-dir",
            "/work/executors",
            "spark://master:7077",
        ]
    else:
        case = json.loads(Path("/shared/current-case.json").read_text())
        if case.get("case") not in {
            "single",
            "reference",
            "fault",
            "resume",
            "dataframe",
        }:
            raise RuntimeError("Unknown explicitly selected training case")
        gate_token = case.get("token")
        if case["case"] == "fault":
            if type(gate_token) is not str or len(gate_token) != 32:
                raise RuntimeError("Fault case needs an exact gate token")
        elif gate_token is not None:
            raise RuntimeError("Only the fault case may set a gate token")
        command = [
            str(home / "bin/spark-submit"),
            "--master",
            "spark://master:7077",
            "--deploy-mode",
            "client",
            "--driver-memory",
            "512m",
            "--jars",
            "/probe/probe.jar",
        ]
        settings = {
            "spark.driver.host": "driver",
            "spark.driver.bindAddress": "0.0.0.0",
            "spark.driver.port": "7079",
            "spark.blockManager.port": "7080",
            "spark.driver.maxResultSize": "512k",
            "spark.executor.memory": "512m",
            "spark.executor.cores": "1",
            "spark.cores.max": "2",
            "spark.task.cpus": "1",
            "spark.task.maxFailures": "1",
            "spark.speculation": "false",
            "spark.sql.shuffle.partitions": "2",
            "spark.default.parallelism": "2",
            "spark.sql.adaptive.enabled": "false",
            "spark.dynamicAllocation.enabled": "false",
            "spark.ui.enabled": "false",
            "spark.network.timeout": "60s",
            "spark.executor.heartbeatInterval": "10s",
            "spark.rpc.askTimeout": "60s",
            "spark.scheduler.barrier.maxConcurrentTasksCheck.interval": "5s",
            "spark.scheduler.barrier.maxConcurrentTasksCheck.maxFailures": "24",
            "spark.executorEnv.PYTHONPATH": os.environ["PYTHONPATH"],
            "spark.executorEnv.OMP_NUM_THREADS": "1",
            "spark.executorEnv.OPENBLAS_NUM_THREADS": "1",
            "spark.executorEnv.MKL_NUM_THREADS": "1",
            "spark.executorEnv.DS60_TORCH_TEST_GATE_DIR": "/shared/gates",
            "spark.executorEnv.DS60_TORCH_TEST_GATE_TOKEN": gate_token or "",
        }
        for name, value in settings.items():
            command += ["--conf", name + "=" + value]
        command += ["/integration/driver.py"]
        status = subprocess.run(command, check=False).returncode
        exit_path = Path("/shared") / (case["case"] + "-driver-exit.json")
        pending = exit_path.with_suffix(".pending")
        pending.write_text(json.dumps({"returncode": status}) + "\n")
        pending.replace(exit_path)
        time.sleep(180)
        raise SystemExit(status)
    os.execv(command[0], command)


if __name__ == "__main__":
    main()
