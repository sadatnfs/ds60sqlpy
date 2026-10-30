"""Bounded real Spark job for the explicitly prepared Kubernetes image."""

import json
import os
import socket

from pyspark import TaskContext
from pyspark.sql import SparkSession


def summarize(rows):
    count = total = 0
    for row in rows:
        count += 1
        total += row.id
    context = TaskContext.get()
    yield {
        "partition": context.partitionId(),
        "attempt": context.attemptNumber(),
        "host": socket.gethostname(),
        "python_pid": os.getpid(),
        "count": count,
        "sum": total,
    }


spark = SparkSession.builder.appName("ds60-kubernetes-partition-proof").getOrCreate()
try:
    if spark.version != "4.0.1":
        raise RuntimeError("Expected Spark 4.0.1")
    records = spark.range(100_000, numPartitions=8).rdd.mapPartitions(summarize).collect()
    assert sorted(row["partition"] for row in records) == list(range(8))
    assert sum(row["count"] for row in records) == 100_000
    assert sum(row["sum"] for row in records) == 4_999_950_000
    print(
        json.dumps(
            {
                "application_id": spark.sparkContext.applicationId,
                "driver": socket.gethostname(),
                "partitions": records,
            },
            sort_keys=True,
        )
    )
finally:
    spark.stop()
