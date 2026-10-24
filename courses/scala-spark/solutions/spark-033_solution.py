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
import os
import uuid

event_schema = StructType(
    [
        StructField("delivery_id", LongType(), True),
        StructField("event_id", StringType(), True),
        StructField("amount", LongType(), True),
        StructField("event_time", TimestampType(), True),
    ]
)


def publish(root, index, lines):
    target = root / "input" / f"batch-{index}.json"
    if target.exists():
        raise ValueError("New source filename required")
    staged = root / "staging" / (uuid.uuid4().hex + ".tmp")
    try:
        with staged.open("x", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        os.replace(staged, target)
    finally:
        staged.unlink(missing_ok=True)


def input_stream(spark, root):
    return (
        spark.readStream.schema(event_schema)
        .option("maxFilesPerTrigger", 1)
        .option("mode", "FAILFAST")
        .json(str(root / "input"))
    )


def run_sink(frame, root, name):
    query = (
        frame.writeStream.format("parquet")
        .outputMode("append")
        .option("checkpointLocation", str(root / (name + "-checkpoint")))
        .trigger(availableNow=True)
        .start(str(root / (name + "-output")))
    )
    try:
        if not query.awaitTermination(30):
            raise TimeoutError("Finite sink deadline exceeded")
        if query.isActive or query.exception() is not None:
            raise RuntimeError("Query failed")
        return list(query.recentProgress)
    finally:
        query.stop()


def output_rows(spark, root):
    return [
        tuple(r)
        for r in spark.read.parquet(str(root / "accepted-output"))
        .select("event_id", "delivery_id", "amount")
        .orderBy("event_id", "delivery_id")
        .collect()
    ]


def classify(events):
    return events.withColumn(
        "reason", F.when(F.col("event_id").isNull(), "missing_event_id").otherwise("accepted")
    )


def deduplicated(classified):
    return (
        classified.filter(F.col("reason") == "accepted")
        .drop("reason")
        .withWatermark("event_time", "5 minutes")
        .dropDuplicatesWithinWatermark(["event_id"])
    )


def run_branches(spark, root):
    classified = classify(input_stream(spark, root))
    accepted = run_sink(deduplicated(classified), root, "accepted")
    rejected = run_sink(
        classified.filter(F.col("reason") == "missing_event_id"), root, "quarantine"
    )
    return accepted, rejected


def business_rows(spark, root):
    return [row for row in output_rows(spark, root) if row[0] != "__advance__"]


def removed_state(progress):
    operators = [operator for p in progress for operator in p.get("stateOperators", [])]
    if not operators or any("numRowsRemoved" not in operator for operator in operators):
        raise ValueError("Missing deduplication state evidence")
    return sum(operator["numRowsRemoved"] for operator in operators)


def delivery_ledger(spark, root):
    source = spark.read.schema(event_schema).json(str(root / "input"))
    if source.select("delivery_id").distinct().count() != 6:
        raise ValueError("Delivery identity mismatch")
    return (
        source.count(),
        source.filter(F.col("event_id").isNotNull()).count(),
        spark.read.parquet(str(root / "quarantine-output")).count(),
        spark.read.parquet(str(root / "accepted-output")).count(),
        sum(r[2] for r in business_rows(spark, root)),
    )


def main():
    owned_root = None
    spark = (
        SparkSession.builder.appName("ds60-spark-033")
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
        spark.conf.set("spark.sql.streaming.stopTimeout", "10000")
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-033-", dir=".")).resolve()
        (owned_root / "input").mkdir()
        (owned_root / "staging").mkdir()
        batches = [
            [
                '{"delivery_id":1,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}',
                '{"delivery_id":2,"event_id":"e2","amount":10,"event_time":"2024-01-01T00:02:00Z"}',
                '{"delivery_id":3,"event_id":null,"amount":99,"event_time":"2024-01-01T00:02:00Z"}',
            ],
            [
                '{"delivery_id":4,"event_id":"e1","amount":10,"event_time":"2024-01-01T00:01:00Z"}',
                '{"delivery_id":5,"event_id":"e3","amount":10,"event_time":"2024-01-01T00:03:00Z"}',
            ],
            [
                '{"delivery_id":6,"event_id":"__advance__","amount":0,"event_time":"2024-01-01T00:20:00Z"}'
            ],
        ]
        # Exercise 1: Classify missing event identity before deduplication
        publish(owned_root, 0, batches[0])
        classified = classify(input_stream(spark, owned_root))
        assert classified.isStreaming and "reason" in classified.columns
        # Exercise 2: Define a bounded event-ID stateful operator
        accepted_stream = deduplicated(classified)
        assert accepted_stream.isStreaming and accepted_stream.columns == [
            "delivery_id",
            "event_id",
            "amount",
            "event_time",
        ]
        # Exercise 3: Execute accepted and quarantine branches with separate checkpoints
        first = run_branches(spark, owned_root)
        print(
            "accepted_progress_input=",
            [
                (
                    p["batchId"],
                    p["numInputRows"],
                    [source["numInputRows"] for source in p["sources"]],
                )
                for p in first[0]
            ],
            "quarantine_progress_input=",
            [
                (
                    p["batchId"],
                    p["numInputRows"],
                    [source["numInputRows"] for source in p["sources"]],
                )
                for p in first[1]
            ],
        )
        first_raw = spark.read.schema(event_schema).json(str(owned_root / "input")).count()
        assert (
            first_raw == 3
            and sum(p["numInputRows"] for p in first[0]) == 2
            and sum(p["numInputRows"] for p in first[1]) == 1
        )
        assert output_rows(spark, owned_root) == [("e1", 1, 10), ("e2", 2, 10)]
        quarantine = (
            spark.read.parquet(str(owned_root / "quarantine-output"))
            .select("delivery_id", "event_id", "reason")
            .collect()
        )
        assert [tuple(r) for r in quarantine] == [(3, None, "missing_event_id")]
        # Exercise 4: Suppress a replay while retaining distinct equal-valued events
        publish(owned_root, 1, batches[1])
        second = run_branches(spark, owned_root)
        assert (
            sum(p["numInputRows"] for p in second[0]) == 2
            and sum(p["numInputRows"] for p in second[1]) == 0
        )
        assert (
            spark.read.schema(event_schema).json(str(owned_root / "input")).count() == first_raw + 2
        )
        assert business_rows(spark, owned_root) == [("e1", 1, 10), ("e2", 2, 10), ("e3", 5, 10)]
        assert sum(r[2] for r in business_rows(spark, owned_root)) == 30
        # Exercise 5: Observe state removal and state the retention limit
        publish(owned_root, 2, batches[2])
        third = run_branches(spark, owned_root)
        assert removed_state(third[0]) >= 3
        assert business_rows(spark, owned_root) == [("e1", 1, 10), ("e2", 2, 10), ("e3", 5, 10)]
        assert sum(r[0] == "__advance__" for r in output_rows(spark, owned_root)) == 1
        print(
            "removed_dedup_state=",
            removed_state(third[0]),
            "state_progress=",
            [operator for p in third[0] for operator in p.get("stateOperators", [])],
        )
        # Exercise 6: Reconcile deliveries, quarantine, replay suppression and business totals
        assert delivery_ledger(spark, owned_root) == (6, 5, 1, 4, 30)
        assert not spark.streams.active
        print("spark-033: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        try:
            if spark.streams.active:
                raise RuntimeError("Query still active; preserve scratch")
            if owned_root is not None:
                shutil.rmtree(owned_root)
        finally:
            spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Classify missing event identity before deduplication. Inputs/task: Add reason missing_event_id for NULL event_id and accepted otherwise, retaining delivery_id, amount and event_time. Expected: Delivery 3 is quarantined;known IDs are eligible for the separate deduplication policy. Verify: Construct the first streaming classification with all declared fields and verify the exact quarantine row after the first phase.
# Exercise 2: Define a bounded event-ID stateful operator. Inputs/task: Filter accepted identities, drop the reason field, attach a five-minute watermark to event_time, and deduplicate within that watermark on event_id only. Expected: The result remains streaming and retains delivery_id, event_id, amount, event_time. Equal amounts across distinct IDs remain distinct. Verify: Assert output shape and use the explicit event_id key, then validate all retained identities through later sink checks.
# Exercise 3: Execute accepted and quarantine branches with separate checkpoints. Inputs/task: Run both first-phase branches with AvailableNow:deduplicated records to accepted-output and missing-ID records to quarantine-output. Use distinct checkpoints and bounded await/stop scopes. Expected: Accepted(e1, delivery 1,10),(e2, delivery 2,10);quarantine(delivery 3, NULL, missing_event_id). The raw source has 3 rows;prepared branch input metrics report 2 accepted-eligible rows and 1 quarantine row. Verify: Assert both exact output populations, branch metrics 2/1 and an independent raw batch-source count 3.
# Exercise 4: Suppress a replay while retaining distinct equal-valued events. Inputs/task: Publish the second file after the first phase terminates and run both compatible branches again. Compare the accepted business identities and their total. Expected: Accepted(e1, delivery 1,10),(e2, delivery 2,10),(e3, delivery 5,10);delivery 4 replay contributes no additional row. Business total 30. Verify: Assert all retained event/delivery pairs, sum 30, raw source total 5 and prepared branch metrics 2 accepted-eligible inputs versus 0 quarantined inputs for this phase.
# Exercise 5: Observe state removal and state the retention limit. Inputs/task: Publish the 00:20 advancer and run both branches. Sum actual numRowsRemoved state metrics from the accepted branch and inspect remaining state. Expected: The three old business-key states are removed under the observed watermark progression;accepted output still retains their committed rows plus the advancer. Verify: Assert removed state rows at least 3, unchanged business rows and one advancer output. Print actual state metrics without promising perpetual deduplication.
# Exercise 6: Reconcile deliveries, quarantine, replay suppression and business totals. Inputs/task: Read the six source deliveries once as a bounded batch and compare them with both sinks. Return source deliveries, known-ID deliveries, quarantine rows, accepted rows including advancer, and business total. Expected: Ledger(6,5,1,4,30). One known-ID delivery is suppressed as an in-horizon replay;three distinct equal-valued business events remain. Verify: Assert the complete ledger and six unique delivery IDs;confirm no active queries remain before cleanup.
