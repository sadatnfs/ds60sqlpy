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
import re


def projection_result(spark, query):
    raise NotImplementedError("Complete projection_result")


def explain_text(spark, query, mode):
    raise NotImplementedError("Complete explain_text")


def read_schema_evidence(formatted):
    raise NotImplementedError("Complete read_schema_evidence")


def aggregate_result(spark, query):
    raise NotImplementedError("Complete aggregate_result")


def normalize_evidence(plan, root):
    raise NotImplementedError("Complete normalize_evidence")


def configuration_receipt(spark):
    raise NotImplementedError("Complete configuration_receipt")


def main():
    owned_root = None
    spark = (
        SparkSession.builder.appName("ds60-spark-021")
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
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-021-", dir=".")).resolve()
        fixture = (
            spark.range(0, 12, 1, 2)
            .withColumn("group_id", F.col("id") % 3)
            .withColumn("amount", F.col("id") * 10)
            .withColumn("unused_payload", F.lit("xxxxxxxxxxxxxxxx"))
        )
        data_path = str(owned_root / "data")
        fixture.write.mode("errorifexists").parquet(data_path)
        input_frame = spark.read.parquet(data_path)
        input_frame.createOrReplaceTempView("ds60_spark_021_input")
        projection_query = (
            "SELECT id,amount*2 AS doubled FROM ds60_spark_021_input WHERE amount>=30"
        )
        aggregate_query = "SELECT group_id,COUNT(*) AS n,SUM(amount) AS total FROM ds60_spark_021_input WHERE amount>=30 GROUP BY group_id"
        assert input_frame.count() == 12
        assert input_frame.columns == ["id", "group_id", "amount", "unused_payload"]
        print("Owned Parquet fixture has four stored columns and12 rows")
        rows = spark.sql(projection_query).orderBy("id").collect()
        assert len(rows) == 9 and rows[0][0] == 3 and rows[-1][0] == 11
        spark.sql("EXPLAIN FORMATTED " + projection_query).show(truncate=False)
        print("spark-021: worked examples passed; six task implementations remain")
    finally:
        try:
            if owned_root is not None:
                shutil.rmtree(owned_root)
        finally:
            spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Check the query meaning before its execution plan. Inputs/task: Execute the projection query and return ordered(id, doubled) tuples. Compare all nine rows with the literal rule id 3..11, doubled=20*id. Expected: Nine tuples from(3,60) through(11,220), with no missing or extra identities. Verify: Assert the complete tuple list, not only the first/last rows or a printed plan.
# Exercise 2: Capture each extended planning stage. Inputs/task: Return EXPLAIN EXTENDED text for the supplied query. Permit only EXTENDED or FORMATTED as the mode and reject another mode. Expected: Text includes Parsed Logical Plan, Analyzed Logical Plan, Optimized Logical Plan and Physical Plan sections. An invalid mode is rejected. Verify: Assert all four section labels and an explicit invalid-mode exception.
# Exercise 3: Inspect the scan scope for column pruning. Inputs/task: Capture FORMATTED output and extract lines containing ReadSchema. Verify that the projection scan requests id and amount but not group_id or unused_payload. Also locate Filter and Project operators. Expected: ReadSchema includes id:bigint and amount:bigint only among the four stored fields. Filter and Project evidence are present. Verify: Assert needed/excluded fields in the extracted scan lines rather than in the entire extended plan.
# Exercise 4: Connect grouped output to a redistribution boundary. Inputs/task: Execute the grouped aggregate and capture its FORMATTED plan. Return group_id, n, total and locate aggregate plus Exchange operators under the fixed AQE-disabled configuration. Expected: Groups 0,1,2 each have n3 with totals 180,210,240. The plan shows aggregation and an Exchange. Verify: Assert all group tuples independently, then assert the relevant operator markers and recorded AQE setting.
# Exercise 5: Normalize incidental identifiers without erasing semantics. Inputs/task: Replace expression-number suffixes such as#123 with#ID and the exact owned root path with<owned-root> in plan text. Preserve operators, field names, predicates and partitioning descriptions. Expected: A synthetic Project id#123L becomes Project id#IDL;the current temporary root is absent from normalized actual plan text. Verify: Assert the synthetic replacement and required semantic tokens after normalizing the actual plan.
# Exercise 6: Compare equivalent query forms with separate semantic and plan evidence. Inputs/task: Execute a nested projection/filter form of the direct query and compare its exact rows. Capture its extended plan and return a bounded receipt containing Spark version, ANSI, AQE and shuffle partition settings. Expected: The nested query has the same nine tuples. Receipt shows Spark 4.0.1, ANSItrue, AQEfalse, shuffle partitions 2. Both extended plans expose an optimized stage. Verify: Assert full output parity with the literal oracle and exact controlled settings;do not assert whole-plan byte equality or faster execution.
