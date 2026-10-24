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


def parse_instants(raw):
    return raw.withColumn("event_time", F.to_timestamp("text", "yyyy-MM-dd'T'HH:mm:ssXXX"))


def render_clock(events, zone):
    spark = events.sparkSession
    previous = spark.conf.get("spark.sql.session.timeZone")
    try:
        spark.conf.set("spark.sql.session.timeZone", zone)
        return [
            tuple(r)
            for r in events.select(
                "event_id", F.date_format("event_time", "yyyy-MM-dd HH:mm:ss").alias("clock")
            )
            .orderBy("event_id")
            .collect()
        ]
    finally:
        spark.conf.set("spark.sql.session.timeZone", previous)


def local_day(events):
    lower = F.to_timestamp(F.lit("2024-11-03T07:00:00Z"))
    upper = F.to_timestamp(F.lit("2024-11-04T08:00:00Z"))
    return events.filter((F.col("event_time") >= lower) & (F.col("event_time") < upper))


def local_fields(spark):
    previous = spark.conf.get("spark.sql.session.timeZone")
    try:
        results = []
        for zone in ["UTC", "America/Los_Angeles"]:
            spark.conf.set("spark.sql.session.timeZone", zone)
            frame = spark.sql("SELECT CAST('2024-11-03 01:30:00' AS TIMESTAMP_NTZ) AS local_time")
            assert frame.schema["local_time"].dataType.typeName() == "timestamp_ntz"
            results.append(frame.select(F.col("local_time").cast("string")).first()[0])
        return results
    finally:
        spark.conf.set("spark.sql.session.timeZone", previous)


def fold_evidence(events):
    fold = events.filter(F.col("event_id").isin(2, 3))
    labels = {label for _, label in render_clock(fold, "America/Los_Angeles")}
    instants = {r[0] for r in fold.select(F.unix_timestamp("event_time")).collect()}
    return len(labels), len(instants)


def parse_ledger(spark):
    source = spark.sql(
        "SELECT * FROM VALUES (1,'2024-01-01T00:00:00Z'),(2,'bad'),(3,CAST(NULL AS STRING)) AS v(id,text)"
    )
    return source.withColumn(
        "parsed", F.try_to_timestamp("text", F.lit("yyyy-MM-dd'T'HH:mm:ssXXX"))
    ).withColumn(
        "reason",
        F.when(F.col("text").isNull(), "missing_timestamp")
        .when(F.col("parsed").isNull(), "malformed_timestamp")
        .otherwise("accepted"),
    )


def main():
    spark = (
        SparkSession.builder.appName("ds60-spark-018")
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
        spark.conf.set("spark.sql.timestampType", "TIMESTAMP_LTZ")
        schema = StructType(
            [StructField("event_id", LongType(), False), StructField("text", StringType(), False)]
        )
        raw = spark.createDataFrame(
            [
                (1, "2024-11-03T07:00:00Z"),
                (2, "2024-11-03T01:30:00-07:00"),
                (3, "2024-11-03T01:30:00-08:00"),
                (4, "2024-11-04T08:00:00Z"),
                (5, "2024-11-03T08:30:00Z"),
                (6, "2024-11-03T06:59:59Z"),
            ],
            schema=schema,
        )
        # Exercise 1: Parse offset evidence into comparable instants
        events = parse_instants(raw)
        assert (
            isinstance(events.schema["event_time"].dataType, TimestampType)
            and events.filter(F.col("event_time").isNull()).count() == 0
        )
        epochs = {
            r[0]: r[1]
            for r in events.select(
                "event_id", F.unix_timestamp("event_time").alias("epoch")
            ).collect()
        }
        assert epochs[2] == epochs[5] and epochs[3] - epochs[2] == 3600
        # Exercise 2: Render a zone without changing the underlying instant
        utc = dict(render_clock(events, "UTC"))
        local = dict(render_clock(events, "America/Los_Angeles"))
        assert utc[2] == "2024-11-03 08:30:00" and utc[3] == "2024-11-03 09:30:00"
        assert local[2] == local[3] == "2024-11-03 01:30:00"
        assert spark.conf.get("spark.sql.session.timeZone") == "UTC"
        # Exercise 3: Filter a complete local day with instant boundaries
        assert [
            r[0] for r in local_day(events).select("event_id").orderBy("event_id").collect()
        ] == [1, 2, 3, 5]
        assert epochs[4] - epochs[1] == 25 * 3600
        # Exercise 4: Keep an unresolved local timestamp as local fields
        assert local_fields(spark) == ["2024-11-03 01:30:00", "2024-11-03 01:30:00"]
        assert spark.conf.get("spark.sql.session.timeZone") == "UTC"
        # Exercise 5: Expose the information lost by a local clock key
        assert fold_evidence(events) == (1, 2)
        # Exercise 6: Quarantine invalid timestamps without confusing missingness
        ledger = parse_ledger(spark)
        assert [tuple(r) for r in ledger.select("id", "reason").orderBy("id").collect()] == [
            (1, "accepted"),
            (2, "malformed_timestamp"),
            (3, "missing_timestamp"),
        ]
        assert (
            ledger.agg(F.count("parsed")).first()[0] == 1
            and spark.conf.get("spark.sql.ansi.enabled") == "true"
        )
        print("spark-018: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Parse offset evidence into comparable instants. Inputs/task: Return event_id, text, event_time by parsing the declared offset pattern yyyy-MM-ddTHH:mm:ss with a literal T and XXX offset. The session timestamp type must be LTZ. Expected: All 6 rows parse. Epoch(event 2)=epoch(event 5), and epoch(event 3)-epoch(event 2)=3600 seconds. Verify: Assert TimestampType, zero null timestamps, exact same-instant equality and the 3600-second separation.
# Exercise 2: Render a zone without changing the underlying instant. Inputs/task: Return ordered(event_id, formatted_clock) pairs for a requested zone, formatting yyyy-MM-dd HH:mm:ss. Set the zone only during materialization and restore the previous setting in finally. Expected: Events 2 and 3 render 08:30 and 09:30 underUTC but both 01:30 underAmerica/Los_Angeles. Session zone is UTC afterward. Verify: Assert both full clock strings for IDs 2/3 and the restored session configuration.
# Exercise 3: Filter a complete local day with instant boundaries. Inputs/task: Select events in the half-open interval[2024-11-03T07:00:00Z,2024-11-04T08:00:00Z). Return all event columns. Expected: Ordered event IDs[1,2,3,5]. Lower-bound ID 1 included, upper-bound ID 4 excluded and prior-second ID 6 excluded. Verify: Assert the exact ID set and the 25-hour boundary duration; do not use an inclusive BETWEEN.
# Exercise 4: Keep an unresolved local timestamp as local fields. Inputs/task: Under bothUTC andAmerica/Los_Angeles, cast 2024-11-03 01:30:00 explicitly to TIMESTAMP_NTZ, inspect its schema and render it as a string. Restore the prior zone. Expected: Both outputs are 2024-11-03 01:30:00 and the type is timestamp_ntz. No epoch or unique instant is claimed. Verify: Assert identical local clock strings and explicit type under both zones, then confirm session restoration.
# Exercise 5: Expose the information lost by a local clock key. Inputs/task: For the two fold events 2 and 3, compare local formatted labels with their epoch values. Return(label_count, instant_count), retaining original event identity. Expected: One distinct local label but two distinct instants. They must not be deduplicated by the displayed clock. Verify: Assert(1,2) using separately materialized local labels and original epoch evidence.
# Exercise 6: Quarantine invalid timestamps without confusing missingness. Inputs/task: Build an inline source containing a valid offset timestamp, bad text andNULL. Use try_to_timestamp with the declared offset pattern and classify accepted, malformed_timestamp, missing_timestamp. Expected: IDs 1,2,3 have those reasons respectively;only 1 is accepted while ANSI remains true. Verify: Assert all reason rows, one known timestamp and unchanged ANSI setting.
