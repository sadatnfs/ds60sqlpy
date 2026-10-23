from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType


def ids(frame):
    return [row.event_id for row in frame.select("event_id").orderBy("event_id").collect()]

def metrics(frame):
    row = frame.agg(F.count(F.lit(1)), F.count("amount_cents"), F.sum("amount_cents")).first()
    return tuple(row)

def canonical(frame):
    assert [(field.name, field.dataType.simpleString()) for field in frame.schema.fields] == [
        ("team", "string"), ("rows", "bigint"), ("valued", "bigint"), ("total_cents", "bigint")]
    return [tuple(row) for row in frame.orderBy(F.col("team").asc_nulls_last()).collect()]

def classified(frame):
    reason = (F.when(F.col("event_id").isNull(), F.lit("missing_id"))
        .when(F.col("event_id") <= F.lit(0), F.lit("invalid_id"))
        .when(F.col("status").isNull() | ~F.col("status").isin("paid", "void"), F.lit("unknown_status"))
        .when(F.col("amount_cents") < F.lit(0), F.lit("negative_amount"))
        .otherwise(F.lit(None).cast("string")))
    return frame.withColumn("rejection_reason", reason)

def accepted(frame):
    return classified(frame).filter(F.col("rejection_reason").isNull()).select("source_row", "event_id", "team", "amount_cents", "status")

def quarantine(frame):
    return classified(frame).filter(F.col("rejection_reason").isNotNull()).select("source_row", "event_id", "team", "amount_cents", "status", "rejection_reason")

def summarize_paid(frame):
    return frame.filter(F.col("status") == F.lit("paid")).groupBy("team").agg(F.count(F.lit(1)).alias("rows"), F.count("amount_cents").alias("valued"), F.sum("amount_cents").alias("total_cents"))

def paid_projection(frame):
    return frame.filter(F.col("status") == F.lit("paid")).select("event_id", "team", "amount_cents")

def audited_sql_report(spark, frame):
    source = frame.agg(F.count(F.lit(1)), F.countDistinct("source_row"), F.count("source_row")).first()
    if not (source[0] <= 100 and source[0] == source[1] == source[2]):
        raise ValueError("invalid or oversized source identity")
    valid = accepted(frame)
    keys = valid.agg(F.count(F.lit(1)), F.countDistinct("event_id"), F.min("event_id")).first()
    if not (keys[0] == keys[1] and (keys[0] == 0 or keys[2] > 0)):
        raise ValueError("accepted event IDs must be positive and unique")
    if valid.count() + quarantine(frame).count() != source[0]:
        raise ValueError("source count does not reconcile")
    valid.filter(F.col("status") == F.lit("paid")).createOrReplaceTempView("ds60_spark_014_paid")
    return spark.sql("SELECT team,COUNT(*) AS rows,COUNT(amount_cents) AS valued,SUM(amount_cents) AS total_cents FROM ds60_spark_014_paid GROUP BY team")

def main():
    spark = (SparkSession.builder.appName("ds60-spark-014").master("local[2]")
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
            StructField("source_row", LongType(), False),StructField("event_id", LongType(), True),
            StructField("team", StringType(), True),StructField("amount_cents", LongType(), True),
            StructField("status", StringType(), True),
        ])
        rows = [
            (1,1,"A",100,"paid"),(2,2,"A",None,"paid"),(3,3,"B",0,"paid"),(4,4,None,50,"paid"),
            (5,5,"B",150,"void"),(6,6,"A",100,"paid"),(7,7,"C",None,"paid"),(8,8,"B",25,"paid"),
            (9,9,"E",0,"paid"),(10,10,"D",200,"paid"),(11,11,"A",10,"mystery"),(12,None,"A",5,"paid"),
        ]
        raw = spark.createDataFrame(rows, schema=schema)
        # Exercise 1: Classify defects without dropping source occurrences
        classification = classified(raw)
        assert classification.count() == 12
        assert [tuple(row) for row in classification.filter(F.col("rejection_reason").isNotNull()).select("source_row", "rejection_reason").orderBy("source_row").collect()] == [(11, "unknown_status"), (12, "missing_id")]
        # Exercise 2: Create the accepted event relation
        valid = accepted(raw)
        assert ids(valid) == list(range(1, 11)) and valid.count() == 10
        assert valid.filter(F.col("status") == F.lit("void")).count() == 1
        assert valid.filter(F.col("amount_cents").isNull()).count() == 2
        # Exercise 3: Retain a complete quarantine row
        rejected = quarantine(raw)
        assert [tuple(row) for row in rejected.orderBy("source_row").collect()] == [(11, 11, "A", 10, "mystery", "unknown_status"), (12, None, "A", 5, "paid", "missing_id")]
        assert valid.count() + rejected.count() == raw.count()
        # Exercise 4: Publish a NULL-aware paid summary
        golden = [("A",3,2,200),("B",2,2,25),("C",1,0,None),("D",1,1,200),("E",1,1,0),(None,1,1,50)]
        assert canonical(summarize_paid(valid)) == golden
        assert metrics(valid.filter(F.col("status") == F.lit("paid"))) == (9, 7, 475)
        # Exercise 5: Expose projection-plus-distinct loss
        paid = paid_projection(valid)
        assert metrics(paid) == (9, 7, 475)
        assert metrics(paid.select("team", "amount_cents").distinct()) == (8, 6, 375)
        assert 1 in ids(paid) and 6 in ids(paid)
        # Exercise 6: Gate the SQL report on identity and conservation
        assert canonical(audited_sql_report(spark, raw)) == golden
        duplicate = spark.createDataFrame([(13, 1, "A", 100, "paid")], schema=schema)
        try:
            audited_sql_report(spark, raw.unionByName(duplicate))
        except ValueError:
            pass
        else:
            raise AssertionError("duplicate accepted identity must reject the report")
        print("spark-014: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Classify defects without dropping source occurrences. Inputs/task: Add a nullable rejection_reason Column using the declared precedence:missing_id, invalid_id, unknown_status, negative_amount. Keep every source field and row. Unknown amounts are allowed;unknown statuses are not. Expected: Source row 11 has unknown_status, row 12 has missing_id, and the other 10 reasons are NULL. All 12 source_row identities remain. Verify: Assert the exact two(source_row, reason) pairs and the unchanged source count 12.
# Exercise 2: Create the accepted event relation. Inputs/task: Return source_row, event_id, team, amount_cents, status only for rows with no rejection reason. Preserve the valid void event and all accepted zero/NULL amounts. Expected: Accepted event IDs are 1 through 10, with 10 rows. Event 5 remains accepted as void;IDs 2 and 7 remain accepted with unknown amounts. Verify: Assert the complete accepted ID list, count 10, one void row and two NULL-amount rows.
# Exercise 3: Retain a complete quarantine row. Inputs/task: Return source_row, event_id, team, amount_cents, status, rejection_reason for rejected records, ordered by source_row when inspected. Keep the original values, including the missing event ID. Expected: Rows are(11,11, A,10, mystery, unknown_status) and (12, NULL, A,5, paid, missing_id). Accepted and quarantined counts sum to 12. Verify: Compare every quarantined field with literal expected rows and check count conservation independently.
# Exercise 4: Publish a NULL-aware paid summary. Inputs/task: From accepted records, filter paid and group by team into team, rows, valued, total_cents. Count every event, only nonnull amounts, and the exact Long sum. Preserve a NULL team group and a NULL-only amount group. Expected: Groups are A:(3,2,200), B:(2,2,25), C:(1,0, NULL), D:(1,1,200), E:(1,1,0), NULL:(1,1,50). Paid metrics are 9 rows,7 valued,475 cents. Verify: Assert the full typed canonical group list and the global paid metrics against independent literals.
# Exercise 5: Expose projection-plus-distinct loss. Inputs/task: Return a paid row-level projection retaining event_id, team, amount_cents. Compare it with the deliberately wrong team/amount distinct projection and explain the lost 100-cent event. Expected: The correct projection has metrics(9,7,475);the wrong projection has(8,6,375). IDs 1 and 6 must both remain despite equal team/amount values. Verify: Assert both metric tuples and verify that correct event IDs include 1 and 6 separately.
# Exercise 6: Gate the SQL report on identity and conservation. Inputs/task: Validate at most 100 unique nonmissing source_row occurrences, unique positive accepted event IDs, and accepted-plus-quarantine conservation before returning a SQL paid summary. Reject a duplicate accepted event ID. Compare SQL output to the same literal groups. Expected: The base 12-row batch passes and matches all six golden groups. Appending source_row13 with a second event_id1 rejects publication instead of choosing a winner. Verify: Assert base SQL parity and a real failure for the duplicate-ID extension;retain the validation failure rather than publishing a partial report.
