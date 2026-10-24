from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    IntegerType,
    StringType,
    DoubleType,
    BooleanType,
    ArrayType,
    MapType,
    TimestampType,
    DecimalType,
)
from pathlib import Path
import tempfile
import shutil
import json
import uuid

EVENT_SCHEMA = StructType(
    [StructField("id", LongType(), True), StructField("cents", LongType(), True)]
)
OWNED_QUERIES = []


def publish_file(root, input_path, name, lines):
    import re, os

    if (
        re.fullmatch(r"batch-[0-9]{2}\.json", name) is None
        or len(lines) > 8
        or any(len(line) > 256 for line in lines)
    ):
        raise ValueError("Fixed finite file contract required")
    input_path.mkdir(exist_ok=True)
    staged = root / ("pending-" + uuid.uuid4().hex + ".json")
    try:
        with staged.open("x", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        if (input_path / name).exists():
            raise ValueError("Input file identity already exists")
        os.rename(staged, input_path / name)
    finally:
        staged.unlink(missing_ok=True)


def run_parquet(spark, input_path, checkpoint, output):
    source = (
        spark.readStream.schema(EVENT_SCHEMA)
        .option("maxFilesPerTrigger", 1)
        .option("mode", "FAILFAST")
        .json(str(input_path))
    )
    query = (
        source.writeStream.format("parquet")
        .outputMode("append")
        .option("checkpointLocation", str(checkpoint))
        .trigger(availableNow=True)
        .start(str(output))
    )
    OWNED_QUERIES.append(query)
    try:
        if not query.awaitTermination(45):
            raise TimeoutError("Finite query exceeded45-second deadline")
        if query.exception() is not None:
            raise RuntimeError(str(query.exception()))
        progress = query.recentProgress
        return {
            "id": str(query.id),
            "run_id": str(query.runId),
            "input_rows": sum(p["numInputRows"] for p in progress),
            "batches": [p["batchId"] for p in progress],
        }
    finally:
        if query.isActive:
            query.stop()


def bag(spark, path):
    frame = spark.read.parquet(str(path))
    if [(f.name, f.dataType.simpleString()) for f in frame.schema.fields] != [
        ("id", "bigint"),
        ("cents", "bigint"),
    ]:
        raise ValueError("Result schema mismatch")
    if frame.count() > 8:
        raise ValueError("Tiny result bound exceeded")
    return [f"{r.id}:{r.cents}" for r in frame.orderBy("id", "cents").collect()]


def all_metrics(frame):
    result = []
    pending = [frame._jdf.queryExecution().executedPlan()]
    while pending:
        node = pending.pop()
        metrics = {}
        items = node.metrics().iterator()
        while items.hasNext():
            item = items.next()
            metrics[str(item._1())] = int(item._2().value())
        result.append((str(node.nodeName()), metrics))
        children = node.children().iterator()
        while children.hasNext():
            pending.append(children.next())
    return result


def metric(report, key):
    values = [values[key] for _, values in report["metrics"] if key in values]
    return sum(values) if values else None


def retained_stages(spark, group):
    tracker = spark.sparkContext.statusTracker()
    ids = set()
    for job_id in tracker.getJobIdsForGroup(group):
        job = tracker.getJobInfo(job_id)
        if job is not None:
            ids.update(job.stageIds)
    rows = []
    for stage_id in sorted(ids):
        value = tracker.getStageInfo(stage_id)
        if value is not None:
            rows.append((stage_id, value.numTasks, value.numCompletedTasks, value.numFailedTasks))
    return rows


def measured(spark, source, partitions, root):
    import time

    if type(partitions) is not int or not 1 <= partitions <= 8:
        raise ValueError("Partition budget1..8")
    group = f"budget-{partitions}-{uuid.uuid4().hex}"
    previous = spark.conf.get("spark.sql.shuffle.partitions")
    spark.conf.set("spark.sql.shuffle.partitions", str(partitions))
    try:
        shuffled = source.repartition(partitions, F.col("key"))
        grouped = shuffled.groupBy("key").agg(F.count(F.lit(1)).alias("n"))
        begin = time.monotonic_ns()
        spark.sparkContext.setJobGroup(group, "Bounded budget comparison", interruptOnCancel=True)
        try:
            rows = sorted((r[0], r[1]) for r in grouped.collect())
        finally:
            for key in (
                "spark.jobGroup.id",
                "spark.job.description",
                "spark.job.interruptOnCancel",
            ):
                spark.sparkContext.setLocalProperty(key, None)
        elapsed = time.monotonic_ns() - begin
        metrics = all_metrics(grouped)
        stages = retained_stages(spark, group)
        counts = {
            r[0]: r[1]
            for r in shuffled.select(F.spark_partition_id().alias("partition"))
            .groupBy("partition")
            .count()
            .collect()
        }
        bucket_rows = [counts.get(index, 0) for index in range(partitions)]
        output = root / f"product-{partitions}"
        grouped.write.mode("errorifexists").parquet(str(output))
        readback = sorted((r[0], r[1]) for r in spark.read.parquet(str(output)).collect())
        if readback != rows:
            raise ValueError("Persisted product differs")
        files = len(list(output.glob("*.parquet")))
        return {
            "rows": rows,
            "partitions": partitions,
            "bucket_rows": bucket_rows,
            "files": files,
            "elapsed_ns": elapsed,
            "metrics": metrics,
            "stages": stages,
        }
    finally:
        spark.conf.set("spark.sql.shuffle.partitions", previous)


def fixture_metrics(source):
    return tuple(
        source.agg(
            F.count(F.lit(1)), F.countDistinct("id"), F.countDistinct("key"), F.sum("id")
        ).first()
    )


def measure_two(spark, source, root):
    return measured(spark, source, 2, root)


def measure_four(spark, source, root):
    return measured(spark, source, 4, root)


def imbalance(counts):
    if not counts or any(value < 0 for value in counts) or sum(counts) <= 0:
        raise ValueError("Positive bounded work counts required")
    return max(counts) / (sum(counts) / len(counts))


def estimated_cost(vcpu, seconds, gib, days):
    import math

    if any(not math.isfinite(value) or value < 0 for value in (vcpu, seconds, gib, days)):
        raise ValueError("Finite nonnegative model inputs required")
    return vcpu * (seconds / 3600) * 0.05 + gib * (days / 30) * 0.02


def within_budget(rows, partitions):
    return (
        type(rows) is int
        and type(partitions) is int
        and 1 <= rows <= 20000
        and 1 <= partitions <= 8
    )


def main():
    owned_root = None
    spark = (
        SparkSession.builder.appName("ds60-spark-039")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    try:
        assert spark.sparkContext.master == "local[2]"
        spark.sparkContext.setLogLevel("ERROR")
        if spark.version != "4.0.1":
            raise ValueError("Prepared Spark4.0.1 required")
        spark.conf.set("spark.sql.streaming.stopTimeout", "5000")
        owned_root = Path(tempfile.mkdtemp(prefix="spark-039-", dir=Path.cwd()))
        source = spark.range(0, 20000, 1, 4).withColumn(
            "key", F.when(F.col("id") < 16000, F.lit(0).cast("long")).otherwise(F.col("id") % 100)
        )
        # Exercise 1: Validate the generated skewed fixture
        assert fixture_metrics(source) == (20000, 20000, 100, 199990000)
        assert source.filter(F.col("key") == 0).count() == 16040
        # Exercise 2: Measure the two-partition configuration
        two = measure_two(spark, source, owned_root)
        expected = [(key, 16040 if key == 0 else 40) for key in range(100)]
        assert (
            two["rows"] == expected
            and sum(two["bucket_rows"]) == 20000
            and 1 <= two["files"] <= 2
            and two["stages"]
        )
        assert metric(two, "dataSize") is not None and metric(two, "dataSize") > 0
        # Exercise 3: Compare four partitions without assuming a speedup
        four = measure_four(spark, source, owned_root)
        assert (
            four["rows"] == expected
            and four["rows"] == two["rows"]
            and sum(four["bucket_rows"]) == 20000
            and 1 <= four["files"] <= 4
        )
        assert metric(four, "dataSize") is not None and metric(four, "dataSize") > 0
        # Exercise 4: Interpret work imbalance and spill honestly
        assert imbalance(two["bucket_rows"]) > 1 and imbalance(four["bucket_rows"]) > 1
        for report in (two, four):
            print(
                {
                    "partitions": report["partitions"],
                    "bucket_rows": report["bucket_rows"],
                    "work_ratio": imbalance(report["bucket_rows"]),
                    "files": report["files"],
                    "elapsed_ns": report["elapsed_ns"],
                    "dataSize": metric(report, "dataSize"),
                    "shuffleBytesWritten": metric(report, "shuffleBytesWritten"),
                    "spillSize": metric(report, "spillSize"),
                    "stages": report["stages"],
                }
            )
        # Exercise 5: Compute a separate hypothetical cost model
        assert abs(estimated_cost(2, 3600, 2, 30) - 0.14) < 1e-12
        try:
            estimated_cost(2, -1, 2, 30)
        except ValueError:
            pass
        else:
            raise AssertionError("Negative modeled duration accepted")
        # Exercise 6: Enforce the stop budget before scaling data
        assert (
            within_budget(20000, 4) and not within_budget(20001, 4) and not within_budget(20000, 9)
        )
        assert spark.conf.get("spark.sql.shuffle.partitions") == "2"
        print("spark-039: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        try:
            for query in OWNED_QUERIES:
                if query.isActive:
                    query.stop()
            if any(query.isActive for query in OWNED_QUERIES):
                raise RuntimeError("Do not remove scratch while an owned query is active")
            if owned_root is not None:
                if owned_root.parent != Path.cwd() or not owned_root.name.startswith("spark-"):
                    raise ValueError("Owned cleanup boundary mismatch")
                shutil.rmtree(owned_root)
        finally:
            spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Validate the generated skewed fixture. Inputs/task: Require 20000 rows, IDs 0..19999,100 keys and total ID sum 199990000. Explain key 0 occurs 16040 times. Expected: Exact population tuple 20000,20000,100,199990000;key 0 count 16040, other keys 40. Verify: Compare aggregate counts and the independent formula 16000+4000/100.
# Exercise 2: Measure the two-partition configuration. Inputs/task: Execute the bounded grouped query under a unique job group, read actual executed metrics, measure partition row counts and persist/read back the product. Expected: 100 exact key/count pairs, total 20000;nonempty retained stage evidence;one or two data files. Verify: Compare all rows with the literal formula before accepting any work/time report.
# Exercise 3: Compare four partitions without assuming a speedup. Inputs/task: Repeat with 4 partitions and a separate output directory. Expected: All 100 result tuples match the same oracle;four buckets sum 20000 and one to four files are observed. Verify: Assert parity and print actual elapsed time/file/metric values without an ordering claim.
# Exercise 4: Interpret work imbalance and spill honestly. Inputs/task: Compute maximum bucket rows divided by mean bucket rows;report available dataSize, shuffleBytesWritten and spillSize metrics without inventing missing values. Expected: Both observed work ratios exceed 1;unavailable metrics remain None/None-equivalent. Verify: Assert row conservation and positive ratio, then print exact available metric maps and stage receipts.
# Exercise 5: Compute a separate hypothetical cost model. Inputs/task: Use a hypothetical rate 0.05 currency units per vCPU-hour and 0.02 per GiB-month. Evaluate 2 vCPUs for 1 hour plus 2 GiB retained for 30 days under a30-day month. Expected: Estimated 0.14 currency units, not an actual cloud bill or a price recommendation. Verify: Check each unit conversion and reject negative durations/resources.
# Exercise 6: Enforce the stop budget before scaling data. Inputs/task: Accept only row counts 1..20000 and partition counts 1..8 for this local exercise. Reject an attempted larger fixture before constructing it. Expected: 20000/4 accepted;20001/4 and 20000/9 rejected. Verify: Assert both refusals and confirm the session shuffle setting restored to 2.
