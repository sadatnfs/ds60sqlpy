"""Foreground Compose services using an explicit offline wheel and prepared image."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


def main():
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
    Path("/work/evidence").mkdir(parents=True, exist_ok=True)
    wheels = list(Path("/wheels").glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Mount exactly one explicit prepared package wheel")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--no-compile",
            "--target",
            "/work/python",
            str(wheels[0]),
        ],
        check=True,
    )
    host = args.host or args.role
    # Prepared single-container bases can pin loopback. Standalone services must
    # advertise their own internal Compose DNS/IP, including executor processes.
    os.environ["SPARK_LOCAL_IP"] = socket.gethostbyname(host)
    os.environ["SPARK_LOCAL_HOSTNAME"] = host
    os.environ["PYTHONPATH"] = "/work/python"
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
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
            "768M",
            "--work-dir",
            "/work/executors",
            "spark://master:7077",
        ]
    else:
        jars = ["/probe/probe.jar"]
        if os.environ["INTEGRATION_PACKAGE"] == "spark-tmbad":
            jars.append("/opt/spark-tmbad/spark-tmbad.jar")
        command = [
            str(home / "bin/spark-submit"),
            "--master",
            "spark://master:7077",
            "--deploy-mode",
            "client",
            "--driver-memory",
            "768m",
            "--jars",
            ",".join(jars),
        ]
        settings = {
            "spark.driver.host": "driver",
            "spark.driver.bindAddress": "0.0.0.0",
            "spark.driver.port": "7079",
            "spark.blockManager.port": "7080",
            "spark.driver.maxResultSize": "128k",
            "spark.executor.memory": "512m",
            "spark.executor.cores": "1",
            "spark.cores.max": "2",
            "spark.task.cpus": "1",
            "spark.task.maxFailures": "4",
            "spark.sql.shuffle.partitions": "8",
            "spark.default.parallelism": "8",
            "spark.sql.adaptive.enabled": "false",
            "spark.dynamicAllocation.enabled": "false",
            "spark.ui.enabled": "false",
            "spark.network.timeout": "60s",
            "spark.executor.heartbeatInterval": "10s",
            "spark.rpc.askTimeout": "60s",
            "spark.scheduler.barrier.maxConcurrentTasksCheck.interval": "5s",
            "spark.scheduler.barrier.maxConcurrentTasksCheck.maxFailures": "24",
            "spark.executorEnv.PYTHONPATH": "/work/python",
            "spark.executorEnv.OPENBLAS_NUM_THREADS": "1",
            "spark.executorEnv.OMP_NUM_THREADS": "1",
        }
        for name, value in settings.items():
            command += ["--conf", name + "=" + value]
        command += ["/integration/driver.py"]
        status = subprocess.run(command, check=False).returncode
        (Path("/work") / "exit.json").write_text(json.dumps({"returncode": status}))
        # Keep tmpfs evidence readable until the bounded host collector removes
        # this exact owned project. No service survives the host timeout cleanup.
        time.sleep(180)
        raise SystemExit(status)
    os.execv(command[0], command)


if __name__ == "__main__":
    main()
