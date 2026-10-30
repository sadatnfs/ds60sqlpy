"""A real Spark reduction with bounded driver results and independent oracles."""

import argparse
import json
import os
import socket
import time
import urllib.request
from pathlib import Path

from pyspark import TaskContext
from pyspark.sql import SparkSession


def partition_summary(rows, pause_seconds):
    context = TaskContext.get()
    n = sx = sxx = sy = sxy = 0
    for row in rows:
        x = int(row.id)
        y = 3 + 2 * x
        n += 1
        sx += x
        sxx += x * x
        sy += y
        sxy += x * y
    time.sleep(pause_seconds)
    yield {
        "partition": context.partitionId(),
        "attempt": context.attemptNumber(),
        "host": socket.gethostname(),
        "python_pid": os.getpid(),
        "n": n,
        "sx": sx,
        "sxx": sxx,
        "sy": sy,
        "sxy": sxy,
    }


def executor_inventory(spark):
    ui = spark.sparkContext.uiWebUrl
    if not ui or not ui.startswith("http://"):
        raise RuntimeError("Expected the current application's explicit local HTTP UI")
    url = f"{ui}/api/v1/applications/{spark.sparkContext.applicationId}/executors"
    with urllib.request.urlopen(url, timeout=5) as response:
        payload = response.read(1_048_577)
    if len(payload) > 1_048_576:
        raise ValueError("Executor inventory exceeds its bounded response contract")
    rows = json.loads(payload)
    return [
        {key: row.get(key) for key in ("id", "hostPort", "isActive", "totalTasks", "failedTasks")}
        for row in rows
        if row["id"] != "driver"
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hold-seconds", type=int, default=0)
    parser.add_argument("--partition-seconds", type=int, default=0)
    parser.add_argument("--allow-one-worker", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.hold_seconds <= 120 or not 0 <= args.partition_seconds <= 15:
        parser.error("Hold must be 0..120 seconds and partition delay 0..15 seconds")
    spark = SparkSession.builder.appName("ds60-deployment-bounded-fit").getOrCreate()
    try:
        if spark.version != "4.0.1":
            raise RuntimeError("This workshop targets Spark 4.0.1")
        if spark.sparkContext.getConf().get("spark.driver.maxResultSize") != "1m":
            raise RuntimeError("The driver result bound must remain 1m")
        wanted = 1 if args.allow_one_worker else 2
        deadline = time.monotonic() + 60
        while True:
            executors = executor_inventory(spark)
            if sum(bool(x["isActive"]) for x in executors) >= wanted:
                break
            if time.monotonic() > deadline:
                raise RuntimeError("Required executors did not register within 60 seconds")
            time.sleep(0.5)
        # Data remain on executors. Only eight small sufficient-statistic records return.
        records = (
            spark.range(0, 100_000, numPartitions=8)
            .rdd.mapPartitions(lambda rows: partition_summary(rows, args.partition_seconds))
            .collect()
        )
        if sorted(x["partition"] for x in records) != list(range(8)):
            raise RuntimeError("Incomplete or duplicate partition coverage")
        totals = {key: sum(row[key] for row in records) for key in ("n", "sx", "sxx", "sy", "sxy")}
        n = totals["n"]
        if (
            n != 100_000
            or totals["sx"] != n * (n - 1) // 2
            or totals["sxx"] != n * (n - 1) * (2 * n - 1) // 6
        ):
            raise RuntimeError("Independent count and moment oracles failed")
        denominator = n * totals["sxx"] - totals["sx"] ** 2
        slope = (n * totals["sxy"] - totals["sx"] * totals["sy"]) / denominator
        intercept = (totals["sy"] - slope * totals["sx"]) / n
        if abs(slope - 2.0) > 1e-12 or abs(intercept - 3.0) > 1e-9:
            raise RuntimeError("Independent linear-model coefficient oracle failed")
        hosts = sorted({row["host"] for row in records})
        if not args.allow_one_worker and hosts != ["worker-a", "worker-b"]:
            raise RuntimeError("Baseline did not execute partitions on both named workers")
        result = {
            "application_id": spark.sparkContext.applicationId,
            "spark": spark.version,
            "driver_host": socket.gethostname(),
            "driver_max_result_size": "1m",
            "partitions": records,
            "totals": totals,
            "coefficients": {"intercept": intercept, "slope": slope},
            "future_covariate_predictions": [
                {"x": x, "prediction": intercept + slope * x} for x in (100_000, 100_001)
            ],
            "forecast_semantics": (
                "Deterministic future-covariate linear extrapolation, "
                "not a conditional-history time-series model"
            ),
            "executors": executor_inventory(spark),
            "worker_loss_observed": False,
        }
        data = json.dumps(result, indent=2) + "\n"
        if len(data.encode()) > 32_768:
            raise RuntimeError("Report exceeds the 32 KiB evidence budget")
        output = Path("/results") / f"{spark.sparkContext.applicationId}.json"
        output.write_text(data)
        print(data, flush=True)
        time.sleep(args.hold_seconds)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
