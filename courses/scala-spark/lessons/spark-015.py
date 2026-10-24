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


def amount_rows(frame):
    return [
        tuple(row) for row in frame.select("event_id", "amount_cents").orderBy("event_id").collect()
    ]


def with_parsed(frame):
    raise NotImplementedError("Complete with_parsed")


def parse_ledger(frame):
    raise NotImplementedError("Complete parse_ledger")


def accepted_projection(frame):
    raise NotImplementedError("Complete accepted_projection")


def sql_projection(spark, frame):
    raise NotImplementedError("Complete sql_projection")


def strict_projection(frame):
    raise NotImplementedError("Complete strict_projection")


def nonnegative_amounts(frame):
    raise NotImplementedError("Complete nonnegative_amounts")


def main():
    spark = (
        SparkSession.builder.appName("ds60-spark-015")
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
                StructField("amount_text", StringType(), True),
            ]
        )
        raw = spark.createDataFrame(
            [
                (1, "100"),
                (2, "0"),
                (3, " 25 "),
                (4, None),
                (5, "bad"),
                (6, "9223372036854775808"),
                (7, "-5"),
                (8, "50"),
            ],
            schema=schema,
        )
        tolerant = raw.select(
            "event_id", F.expr("try_cast(trim(amount_text) AS BIGINT)").alias("parsed_amount")
        )
        assert [
            row.event_id
            for row in tolerant.filter(F.col("parsed_amount").isNull())
            .select("event_id")
            .orderBy("event_id")
            .collect()
        ] == [4, 5, 6]
        print("Parse NULLs include both source missingness and rejected text")
        signed = raw.filter(F.col("event_id") == F.lit(7)).select(
            F.expr("try_cast(amount_text AS BIGINT)").alias("amount")
        )
        assert signed.first()[0] == -5
        assert spark.conf.get("spark.sql.ansi.enabled") == "true"
        print("A signed integer can be cast-valid while domain-invalid")
        print("spark-015: worked examples passed; six task implementations remain")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Add an explicit tolerant parse column. Inputs/task: Return all source columns plus parsed_amount from try_cast(trim(amount_text) AS BIGINT). Preserve eight rows and distinguish this nullable parse result from a final validity decision. Expected: Ordered parsed values are 100,0,25, NULL, NULL, NULL,-5,50. The output parsed type is bigint. Verify: Compare all eight(event_id, parsed_amount) pairs and the field type with literals.
# Exercise 2: Classify missing versus rejected tokens. Inputs/task: Add parse_status with missing for source NULL, rejected for a nonnull source that parsed to NULL, and valid otherwise. Keep all original rows and parsed values. Expected: IDs 1,2,3,7,8 are valid, ID 4 missing, and IDs 5,6 rejected. Counts are 5,1,2 and sum to 8. Verify: Assert the ordered status list and the exact two rejected IDs.
# Exercise 3: Project the six parse-accepted events. Inputs/task: Retain valid and missing statuses, then return event_id and parsed_amount aliased as amount_cents. Reject only malformed/overflowing nonnull tokens at this stage. Expected: IDs[1,2,3,4,7,8] remain with amounts[100,0,25, NULL,-5,50]. There are 6 rows,5 known values and total 170. Verify: Assert the exact rows and independent count/known/sum metrics.
# Exercise 4: Express the same parse contract in SQL. Inputs/task: Register the raw frame as a session-local view and produce the same six event_id, amount_cents rows using a SQL parse CTE and explicit missing-or-success filter. Compare with literals rather than only with the DataFrame result. Expected: The SQL ordered rows are exactly the six rows from Exercise 3, including the NULL amount and signed-5. Verify: Assert the SQL result against the full literal row list and separately compare the DataFrame path to that list.
# Exercise 5: Observe strict ANSI failure at evaluation. Inputs/task: Return a strict trimmed BIGINT cast projection. Evaluate a valid subset successfully, then intentionally evaluate the bad token at ID 5 under ANSI mode and require a CAST_INVALID_INPUT diagnostic. Do not count an unrelated exception as success. Expected: The valid subset has the same six rows. ID 5 fails when collected, and the reference records the expected failure code before continuing. Verify: Assert ANSI readback true, valid-row results, and a caught diagnostic containing CAST_INVALID_INPUT.
# Exercise 6: Apply a separate nonnegative domain policy. Inputs/task: From parse-accepted rows, retain unknown amounts and known nonnegative amounts. Return event_id, amount_cents and report the separate negative-domain rejection at ID 7 in the checks. Expected: Final IDs[1,2,3,4,8] have 5 rows,4 known values, total 175. The full source reconciles as 5 final accepted+2 parse rejected+1 negative-domain rejected. Verify: Assert final rows/metrics, negative ID 7 and the 8-row conservation equation.
