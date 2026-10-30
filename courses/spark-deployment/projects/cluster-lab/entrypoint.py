"""Run one explicitly selected role in the isolated teaching topology."""

import os
import signal
import socket
import sys
import time
from pathlib import Path


def wait_for_master() -> None:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("master", 7077), timeout=2):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("The owned master did not listen on master:7077 within 60 seconds")


def main() -> None:
    role = sys.argv[1]
    spark = Path("/opt/spark/bin/spark-class")
    if role == "master":
        args = [
            "org.apache.spark.deploy.master.Master",
            "--host",
            "master",
            "--port",
            "7077",
            "--webui-port",
            "8080",
        ]
    elif role == "worker":
        if sys.argv[2] not in {"worker-a", "worker-b"}:
            raise ValueError("Unknown owned worker")
        wait_for_master()
        args = [
            "org.apache.spark.deploy.worker.Worker",
            "--host",
            sys.argv[2],
            "--cores",
            "1",
            "--memory",
            "1g",
            "--work-dir",
            "/tmp/spark-work",
            "spark://master:7077",
        ]
    elif role == "history":
        os.environ["SPARK_HISTORY_OPTS"] = (
            "-Dspark.history.fs.logDirectory=file:/events -Dspark.history.fs.cleaner.enabled=false"
        )
        args = ["org.apache.spark.deploy.history.HistoryServer"]
    elif role == "idle":
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
        while True:
            signal.pause()
    elif role == "notebook":
        wait_for_master()
        os.execvp("jupyter", ["jupyter", "lab", "--config=/lab/jupyter_config.py"])
    else:
        raise ValueError("Unknown role")
    os.execv(spark, [str(spark), *args])


if __name__ == "__main__":
    main()
