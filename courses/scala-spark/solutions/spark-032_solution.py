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
from datetime import datetime, timedelta
import tempfile
import shutil
import os
import uuid
from pyspark.errors import AnalysisException

event_schema = StructType(
    [
        StructField("id", LongType(), True),
        StructField("team", StringType(), True),
        StructField("amount", LongType(), True),
        StructField("event_time", TimestampType(), True),
    ]
)
result_schema = StructType(
    [
        StructField(
            "window",
            StructType(
                [
                    StructField("start", TimestampType(), True),
                    StructField("end", TimestampType(), True),
                ]
            ),
            True,
        ),
        StructField("team", StringType(), True),
        StructField("records", LongType(), True),
        StructField("total", LongType(), True),
    ]
)


def publish(root, index, lines):
    target = root / "input" / f"batch-{index}.json"
    if target.exists():
        raise ValueError("Input filename already published")
    staged = root / "staging" / (uuid.uuid4().hex + ".tmp")
    try:
        with staged.open("x", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        os.replace(staged, target)
    finally:
        staged.unlink(missing_ok=True)


def stream(spark, root):
    return (
        spark.readStream.schema(event_schema)
        .option("maxFilesPerTrigger", 1)
        .option("mode", "FAILFAST")
        .json(str(root / "input"))
    )


def run_phase(spark, root):
    query = (
        windowed(stream(spark, root))
        .writeStream.format("parquet")
        .outputMode("append")
        .option("checkpointLocation", str(root / "checkpoint"))
        .trigger(availableNow=True)
        .start(str(root / "output"))
    )
    try:
        if not query.awaitTermination(30):
            raise TimeoutError("Finite phase timed out")
        if query.exception() is not None or query.isActive:
            raise RuntimeError("Phase did not terminate cleanly")
        return list(query.recentProgress)
    finally:
        query.stop()


def windowed(events):
    return (
        events.withWatermark("event_time", "5 minutes")
        .groupBy(F.window("event_time", "5 minutes"), "team")
        .agg(F.count(F.lit(1)).alias("records"), F.sum("amount").alias("total"))
    )


def watermarks(progress):
    return [
        p["eventTime"]["watermark"]
        for p in progress
        if p.get("eventTime", {}).get("watermark") is not None
    ]


def final_rows(spark, root):
    frame = spark.read.schema(result_schema).parquet(str(root / "output"))
    return [
        tuple(r)
        for r in frame.select(
            F.date_format("window.start", "HH:mm").alias("start"), "team", "records", "total"
        )
        .orderBy("start", "team")
        .collect()
    ]


def dropped_rows(progress):
    operators = [operator for p in progress for operator in p.get("stateOperators", [])]
    if not operators or any("numRowsDroppedByWatermark" not in operator for operator in operators):
        raise ValueError("No complete state-operator evidence")
    return sum(operator["numRowsDroppedByWatermark"] for operator in operators)


def event_ledger(phases, output):
    return (
        sum(p["numInputRows"] for phase in phases for p in phase),
        sum(dropped_rows(phase) for phase in phases),
        sum(row[2] for row in output),
    )


def reject_unsupported(spark, root, kind):
    if kind not in {"update-file", "append-unwatermarked"}:
        raise ValueError("Unknown invalid case")
    relation = (
        windowed(stream(spark, root))
        if kind == "update-file"
        else stream(spark, root).groupBy("team").count()
    )
    mode = "update" if kind == "update-file" else "append"
    query = None
    rejected = False
    try:
        query = (
            relation.writeStream.format("parquet")
            .outputMode(mode)
            .option("checkpointLocation", str(root / (kind + "-checkpoint")))
            .trigger(availableNow=True)
            .start(str(root / (kind + "-output")))
        )
        query.awaitTermination(30)
    except AnalysisException:
        rejected = True
    finally:
        if query is not None:
            query.stop()
    if not rejected:
        raise AssertionError("Unsupported output configuration was accepted")


def main():
    owned_root = None
    spark = (
        SparkSession.builder.appName("ds60-spark-032")
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
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-032-", dir=".")).resolve()
        (owned_root / "input").mkdir()
        (owned_root / "staging").mkdir()
        batches = [
            [
                '{"id":1,"team":"A","amount":10,"event_time":"2024-01-01T00:01:00Z"}',
                '{"id":2,"team":"A","amount":20,"event_time":"2024-01-01T00:04:00Z"}',
            ],
            [
                '{"id":3,"team":"A","amount":5,"event_time":"2024-01-01T00:03:00Z"}',
                '{"id":4,"team":"A","amount":30,"event_time":"2024-01-01T00:12:00Z"}',
            ],
            [
                '{"id":5,"team":"A","amount":999,"event_time":"2024-01-01T00:02:00Z"}',
                '{"id":6,"team":"B","amount":7,"event_time":"2024-01-01T00:13:00Z"}',
            ],
            ['{"id":7,"team":"__advance__","amount":0,"event_time":"2024-01-01T00:30:00Z"}'],
        ]
        # Exercise 1: Define watermark placement and window state
        publish(owned_root, 0, batches[0])
        planned = windowed(stream(spark, owned_root))
        assert planned.isStreaming and planned.columns == ["window", "team", "records", "total"]
        # Exercise 2: Record actual watermark progress after the first phase
        phase1 = run_phase(spark, owned_root)
        assert sum(p["numInputRows"] for p in phase1) == 2
        marks1 = watermarks(phase1)
        assert marks1 and datetime.fromisoformat(
            marks1[-1].replace("Z", "+00:00")
        ) <= datetime.fromisoformat("2024-01-01T00:00:00+00:00")
        print("phase1_watermarks=", marks1)
        # Exercise 3: Accept a retained out-of-order event and observe finalization
        publish(owned_root, 1, batches[1])
        phase2 = run_phase(spark, owned_root)
        assert final_rows(spark, owned_root) == [("00:00", "A", 3, 35)]
        assert any(
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            >= datetime.fromisoformat("2024-01-01T00:07:00+00:00")
            for value in watermarks(phase2)
        )
        # Exercise 4: Observe a far-late drop after the window has closed
        publish(owned_root, 2, batches[2])
        phase3 = run_phase(spark, owned_root)
        assert sum(p["numInputRows"] for p in phase3) == 2 and dropped_rows(phase3) == 1
        assert final_rows(spark, owned_root) == [("00:00", "A", 3, 35)]
        print("phase3_dropped_by_watermark=", dropped_rows(phase3))
        # Exercise 5: Advance event time and distinguish finalized frompending output
        publish(owned_root, 3, batches[3])
        phase4 = run_phase(spark, owned_root)
        output = final_rows(spark, owned_root)
        assert output == [("00:00", "A", 3, 35), ("00:10", "A", 1, 30), ("00:10", "B", 1, 7)]
        assert event_ledger([phase1, phase2, phase3, phase4], output) == (7, 1, 5)
        assert any(
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            >= datetime.fromisoformat("2024-01-01T00:25:00+00:00")
            for value in watermarks(phase4)
        )
        # Exercise 6: Verify output-mode and sink eligibility through explicit failures
        reject_unsupported(spark, owned_root, "update-file")
        reject_unsupported(spark, owned_root, "append-unwatermarked")
        assert not spark.streams.active and final_rows(spark, owned_root) == output
        print("spark-032: six PySpark reference contracts passed; Spark=" + spark.version)
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

# Exercise 1: Define watermark placement and window state. Inputs/task: Apply with Watermark(event_time,5minutes) before grouping by a 5-minute window and team. Aggregate records and total amount, retaining the window struct in the result. Expected: A streaming aggregate with window, team, records, total. The watermark is attached to the same event-time column used by the window. Verify: Assert streaming status and the four output fields before starting the first phase.
# Exercise 2: Record actual watermark progress after the first phase. Inputs/task: Run phase 1 and extract nonmissing watermark strings from retained progress. Parse them as instants rather than wall-clock elapsed duration. Expected: Exactly 2 input rows processed. At least one watermark observation exists;the final observed watermark is no later than 00:00 for this phase. Verify: Assert input count 2 and actual watermark presence/order;do not infer finalization from the file count alone.
# Exercise 3: Accept a retained out-of-order event and observe finalization. Inputs/task: Publish phase 2, run the compatible query again and read finalized sink rows as(start, team, records, total). Verify the 00:03 event contributed before the first window closed. Expected: The finalized sink contains only(00:00, A,3,35) at this point. The actual watermark reaches at least 00:07. Verify: Assert the exact first-window tuple and the observed progress boundary.
# Exercise 4: Observe a far-late drop after the window has closed. Inputs/task: Publish phase 3 after phase 2 has terminated. Read the actual state-operator dropped-by-watermark counters and verify the 999 event does not change the finalized first window. Expected: Two new source rows consumed, one observed watermark drop and unchanged first-window result 35. B at 00:13 remains in pending state. Verify: Assert input 2, drop counter 1 and the unchanged sink tuple. Preserve missing metric evidence as an error rather than guessing zero.
# Exercise 5: Advance event time and distinguish finalized frompending output. Inputs/task: Publish the 00:30 administrative advancer, run phase 4 and return a ledger of total source inputs, observed drops and final business-window records. Expected: Seven total inputs, one observed drop, five finalized business records across three tuples:(00:00, A,3,35),(00:10, A,1,30),(00:10, B,1,7). The advancer window remains pending. Verify: Assert all final tuples, input/drop reconciliation and actual watermark at least 00:25.
# Exercise 6: Verify output-mode and sink eligibility through explicit failures. Inputs/task: Attempt two invalid configurations in separate owned paths:Update mode to Parquet, and Append mode for an unwatermarked team aggregate. Require analysis rejection and stop any unexpectedly created query in finally. Expected: Both configurations raiseAnalysisException;no active query remains. The valid windowed append sink stays intact. Verify: Assert each named analysis failure and the unchanged three-row valid sink after the checks.
