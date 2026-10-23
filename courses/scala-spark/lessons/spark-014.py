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
    raise NotImplementedError("Complete classified")

def accepted(frame):
    raise NotImplementedError("Complete accepted")

def quarantine(frame):
    raise NotImplementedError("Complete quarantine")

def summarize_paid(frame):
    raise NotImplementedError("Complete summarize_paid")

def paid_projection(frame):
    raise NotImplementedError("Complete paid_projection")

def audited_sql_report(spark, frame):
    raise NotImplementedError("Complete audited_sql_report")

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
        assert raw.count() == 12
        assert raw.select("source_row").distinct().count() == 12
        assert raw.filter(F.col("event_id").isNull()).select("source_row").first()[0] == 12
        print("Source occurrence identity survives a missing business ID")
        unknown = [row.event_id for row in raw.filter(F.col("amount_cents").isNull()).select("event_id").orderBy("event_id").collect()]
        zero = [row.event_id for row in raw.filter(F.col("amount_cents") == F.lit(0)).select("event_id").orderBy("event_id").collect()]
        assert unknown == [2, 7] and zero == [3, 9]
        print("Unknown amounts and observed zeros have different identities")
        print("spark-014: worked examples passed; six task implementations remain")
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
