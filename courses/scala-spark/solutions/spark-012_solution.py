from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType




def schema_fields(frame):
    return [(field.name, field.dataType.simpleString(), field.nullable) for field in frame.schema.fields]

def team_a(frame):
    return frame.filter(F.col("team") == F.lit("A"))

def bounded_ids(frame, limit):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= 20:
        raise ValueError("driver ID budget outside 0..20")
    rows = [row.event_id for row in frame.select("event_id").orderBy("event_id").limit(limit + 1).collect()]
    if len(rows) > limit:
        raise ValueError("driver ID result exceeds budget")
    return rows

def observed_rows(frame):
    return frame.filter(F.col("amount_cents").isNotNull())

def canonical(frame):
    return [tuple(row) for row in frame.select("event_id", "team", "amount_cents").orderBy("event_id").collect()]

def settings(spark):
    context = spark.sparkContext.getConf()
    return {"master": spark.sparkContext.master, "timezone": spark.conf.get("spark.sql.session.timeZone"),
            "shuffle": spark.conf.get("spark.sql.shuffle.partitions"), "ansi": spark.conf.get("spark.sql.ansi.enabled"),
            "adaptive": spark.conf.get("spark.sql.adaptive.enabled"), "ui": context.get("spark.ui.enabled"),
            "driver_host": context.get("spark.driver.host"), "driver_bind": context.get("spark.driver.bindAddress"),
            "spark_version": spark.version}

def main():
    spark = (SparkSession.builder.appName("ds60-spark-012").master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC").getOrCreate())
    try:
        assert spark.sparkContext.master == "local[2]"
        spark.sparkContext.setLogLevel("ERROR")
        schema = StructType([
            StructField("event_id", LongType(), False),
            StructField("team", StringType(), True),
            StructField("amount_cents", LongType(), True),
        ])
        raw = spark.createDataFrame([(1, "A", 0), (2, "B", None), (3, "A", 25), (4, "B", 40)], schema=schema)
        # Exercise 1: Inspect the complete schema contract
        assert schema_fields(raw) == [("event_id", "bigint", False), ("team", "string", True), ("amount_cents", "bigint", True)]
        # Exercise 2: Keep a transformation separate from its action
        a = team_a(raw)
        assert a.count() == 2 and raw.count() == 4
        assert [row.event_id for row in a.select("event_id").orderBy("event_id").collect()] == [1, 3]
        # Exercise 3: Bound the driver result and detect overflow of the budget
        assert bounded_ids(raw, 4) == [1, 2, 3, 4]
        for limit in [3, 21]:
            try:
                bounded_ids(raw, limit)
            except ValueError:
                pass
            else:
                raise AssertionError("oversize or invalid budget must fail")
        assert bounded_ids(raw.filter(F.lit(False)), 0) == []
        # Exercise 4: Retain observed zero while isolating unknown amounts
        observed = observed_rows(raw)
        assert bounded_ids(observed, 4) == [1, 3, 4]
        assert observed.agg(F.sum("amount_cents")).first()[0] == 65
        assert raw.filter(F.col("amount_cents").isNull()).count() == 1
        # Exercise 5: Canonicalize content across physical repartitioning
        golden = [(1, "A", 0), (2, "B", None), (3, "A", 25), (4, "B", 40)]
        assert canonical(raw) == golden
        assert canonical(raw.repartition(1)) == golden
        assert canonical(raw.repartition(3)) == golden
        # Exercise 6: Read back the actual local session contract
        assert settings(spark) == {"master": "local[2]", "timezone": "UTC", "shuffle": "2", "ansi": "true", "adaptive": "false", "ui": "false", "driver_host": "127.0.0.1", "driver_bind": "127.0.0.1", "spark_version": "4.0.1"}
        print("spark-012: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Inspect the complete schema contract. Inputs/task: Return ordered field triples(name, simpleString, nullable) for a DataFrame. Check the fixture rather than inferring correctness from a printed schema alone. Expected: The triples are(event_id, bigint, false),(team, string, true),(amount_cents, bigint, true). Verify: Compare the complete triples with literals in both languages, including all nullability flags.
# Exercise 2: Keep a transformation separate from its action. Inputs/task: Return a DataFrame plan selecting team A without collecting or counting inside the function. At the call site, request a count and verify IDs 1 and 3. Preserve raw. Expected: The returned frame contains two rows when evaluated;raw still has four. The function body contains only a filter transformation. Verify: Assert returned count 2, ordered IDs[1,3] and raw count 4 at explicit action sites.
# Exercise 3: Bound the driver result and detect overflow of the budget. Inputs/task: Return ordered event IDs while collecting at most limit+1 rows, with 0<=limit<=20. Reject a result larger than limit and invalid limits. Empty data with limit 0 is valid. Do not collect the full frame before checking length. Expected: The four-row fixture passes limit 4 and rejects limit 3. An empty filter with limit 0 returns empty;limit 21 is rejected before collection. Verify: Assert exact IDs, catch the oversize and invalid-budget errors, and inspect the bounded limit before the action.
# Exercise 4: Retain observed zero while isolating unknown amounts. Inputs/task: Return rows with nonnull amount_cents, keeping all columns and identities. Do not replace NULL with zero or filter out observed zero. Expected: IDs 1,3,4 remain with amounts 0,25,40, total 65. Raw still has one NULL amount at ID 2. Verify: Assert exact IDs and sum 65, and independently count the unchanged raw NULL row.
# Exercise 5: Canonicalize content across physical repartitioning. Inputs/task: Return ordered triples(event_id, optional team, optional amount) for this bounded fixture. Compare raw, repartition(1) and repartition(3) against the same literal content, not raw collect order. Expected: Every version yields (1, A,0),(2, B, NULL),(3, A,25),(4, B,40). Physical placement does not change identity, NULL state or value. Verify: Assert all three canonical outputs and keep the final event_id ordering explicit.
# Exercise 6: Read back the actual local session contract. Inputs/task: Return master, timezone, shuffle-partition, ANSI, AQE, UI, driver-binding and Spark-version settings from the active session. Compare them with this prepared profile and rely on finally for owned stop. Do not substitute a hardcoded target string for version readback. Expected: Master local[2], UTC, two shuffle partitions, ANSI true, AQE false, UI false, both driver addresses 127.0.0.1, and Spark version 4.0.1. Verify: Assert the complete settings map;record actual version output and distinguish it from worker cleanup evidence.
