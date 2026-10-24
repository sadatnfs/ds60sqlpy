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


def ids(frame):
    return [row.event_id for row in frame.select("event_id").orderBy("event_id").collect()]


def above_ten():
    return F.col("amount_cents") > F.lit(10)


def selected_ids(frame):
    return ids(frame.filter(above_ten()))


def missing_ids(frame):
    return ids(frame.filter(F.col("amount_cents").isNull()))


def combined_ids(frame):
    return ids(
        frame.filter(
            F.col("amount_cents").isNotNull()
            & (F.col("amount_cents") >= F.lit(10))
            & (F.col("event_id") < F.lit(4))
        )
    )


def projected(frame):
    return frame.select("event_id", (F.col("amount_cents") + F.lit(1)).alias("amount_plus_one"))


def sql_ids(spark, frame):
    frame.createOrReplaceTempView("ds60_spark_011_events")
    return ids(
        spark.sql(
            "SELECT event_id FROM ds60_spark_011_events WHERE amount_cents > 10 ORDER BY event_id"
        )
    )


def main():
    spark = (
        SparkSession.builder.appName("ds60-spark-011")
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
        schema = StructType(
            [
                StructField("event_id", LongType(), False),
                StructField("amount_cents", LongType(), True),
            ]
        )
        raw = spark.createDataFrame([(1, 0), (2, 20), (3, None), (4, 20)], schema=schema)
        # Exercise 1: Construct a predicate without collapsing it to a driver Boolean
        predicate = above_ten()
        assert ids(raw.filter(predicate)) == [2, 4]
        try:
            bool(predicate)
        except ValueError:
            pass
        else:
            raise AssertionError("Column must not become a scalar Boolean")
        # Exercise 2: Apply the predicate and preserve event identity
        assert selected_ids(raw) == [2, 4]
        assert ids(raw) == [1, 2, 3, 4]
        # Exercise 3: Select missingness explicitly
        assert missing_ids(raw) == [3]
        assert ids(raw.filter(F.col("amount_cents") == F.lit(0))) == [1]
        # Exercise 4: Combine conditions with engine operators
        assert combined_ids(raw) == [2]
        # Exercise 5: Preserve NULL through a derived column
        assert [tuple(row) for row in projected(raw).orderBy("event_id").collect()] == [
            (1, 1),
            (2, 21),
            (3, None),
            (4, 21),
        ]
        # Exercise 6: Compare SQL and Columns with an independent expectation
        assert sql_ids(spark, raw) == [2, 4]
        assert selected_ids(raw) == [2, 4]
        print("spark-011: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Construct a predicate without collapsing it to a driver Boolean. Inputs/task: Implement aboveTen/above_ten returning a Spark Column for amount_cents>10. Do not collect values or return a Python/Scala scalar Boolean. Expected: Passing the predicate to raw.filter retains IDs 2 and 4. In Python, bool(predicate) raises ValueError rather than choosing one row's truth value. Verify: Assert the exact filtered IDs and, in the PySpark reference, catch the scalar-Boolean conversion failure.
# Exercise 2: Apply the predicate and preserve event identity. Inputs/task: Return the ordered event IDs selected by aboveTen from this tiny fixture. Preserve both equal-valued 20-cent events and leave raw unchanged. Expected: The result is[2,4], and raw still contains IDs[1,2,3,4]. Projecting amount and calling distinct is not an acceptable implementation. Verify: Compare the selected IDs with literals and independently check all four raw IDs.
# Exercise 3: Select missingness explicitly. Inputs/task: Return ordered IDs whose amount_cents is SQL NULL. Do not compare the Column to JVM null/Python None using driver identity logic, and do not treat zero as missing. Expected: Only ID 3 is returned. The observed-zero ID 1 is absent from the missingness result. Verify: Assert[3] and separately assert that the zero-amount filter returns [1].
# Exercise 4: Combine conditions with engine operators. Inputs/task: Return ordered IDs with a known amount at least 10 and event_id less than 4. Combine parenthesized Column comparisons with engine Boolean operators in each language. Expected: Only ID 2 qualifies. ID 4 fails the ID bound, ID 3 is missing, and ID 1 is below the amount threshold. Verify: Assert the exact singleton and explain one exclusion reason for each other ID.
# Exercise 5: Preserve NULL through a derived column. Inputs/task: Return a DataFrame with event_id and amount_plus_one=amount_cents+1, without filling NULL or dropping identity. Keep a Long-compatible integer result. Expected: Ordered rows are(1,1),(2,21),(3, NULL),(4,21). The two 21 values remain separate events and unknown remains unknown. Verify: Compare every ordered row with literal expected values, including the NULL position.
# Exercise 6: Compare SQL and Columns with an independent expectation. Inputs/task: Register a session-local temporary view and return ordered IDs from SQL SELECT/WHERE amount_cents>10. Compare SQL and DataFrame paths to the literal expected IDs rather than only to one another. Expected: Both paths return [2,4]. The temporary view exists only in this owned session and no external database connection is opened. Verify: Assert SQL IDs and selectedIds against [2,4] independently, then let the complete program stop its session in finally.
