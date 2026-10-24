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
    return [tuple(r) for r in spark.sql(query).orderBy("id").collect()]


def explain_text(spark, query, mode):
    if mode not in {"EXTENDED", "FORMATTED"}:
        raise ValueError("Unsupported evidence mode")
    return "\n".join(r[0] for r in spark.sql("EXPLAIN " + mode + " " + query).collect())


def read_schema_evidence(formatted):
    return "\n".join(line for line in formatted.splitlines() if "ReadSchema" in line)


def aggregate_result(spark, query):
    return [tuple(r) for r in spark.sql(query).orderBy("group_id").collect()]


def normalize_evidence(plan, root):
    return re.sub(r"#[0-9]+", "#ID", plan.replace(root, "<owned-root>"))


def configuration_receipt(spark):
    return {
        "spark_version": spark.version,
        "ansi": spark.conf.get("spark.sql.ansi.enabled"),
        "aqe": spark.conf.get("spark.sql.adaptive.enabled"),
        "shuffle_partitions": spark.conf.get("spark.sql.shuffle.partitions"),
    }


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
        # Exercise 1: Check the query meaning before its execution plan
        expected = [(i, 20 * i) for i in range(3, 12)]
        assert projection_result(spark, projection_query) == expected
        # Exercise 2: Capture each extended planning stage
        extended = explain_text(spark, projection_query, "EXTENDED")
        assert all(
            label in extended
            for label in [
                "Parsed Logical Plan",
                "Analyzed Logical Plan",
                "Optimized Logical Plan",
                "Physical Plan",
            ]
        )
        try:
            explain_text(spark, projection_query, "UNSUPPORTED")
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid evidence mode accepted")
        # Exercise 3: Inspect the scan scope for column pruning
        formatted = explain_text(spark, projection_query, "FORMATTED")
        read_schema = read_schema_evidence(formatted)
        assert "id:bigint" in read_schema and "amount:bigint" in read_schema
        assert "unused_payload" not in read_schema and "group_id" not in read_schema
        assert "Filter" in formatted and "Project" in formatted
        print(read_schema)
        # Exercise 4: Connect grouped output to a redistribution boundary
        assert aggregate_result(spark, aggregate_query) == [(0, 3, 180), (1, 3, 210), (2, 3, 240)]
        aggregate_plan = explain_text(spark, aggregate_query, "FORMATTED")
        assert "Aggregate" in aggregate_plan and "Exchange" in aggregate_plan
        assert spark.conf.get("spark.sql.adaptive.enabled") == "false"
        print(aggregate_plan)
        # Exercise 5: Normalize incidental identifiers without erasing semantics
        assert (
            normalize_evidence("Project id#123L at " + str(owned_root), str(owned_root))
            == "Project id#IDL at <owned-root>"
        )
        normalized = normalize_evidence(formatted, str(owned_root))
        assert (
            str(owned_root) not in normalized and "Filter" in normalized and "amount" in normalized
        )
        # Exercise 6: Compare equivalent query forms with separate semantic and plan evidence
        nested = "SELECT id,doubled FROM (SELECT id,amount,amount*2 AS doubled FROM ds60_spark_021_input) WHERE amount>=30"
        assert projection_result(spark, nested) == expected
        assert "Optimized Logical Plan" in explain_text(spark, nested, "EXTENDED")
        receipt = configuration_receipt(spark)
        assert receipt == {
            "spark_version": "4.0.1",
            "ansi": "true",
            "aqe": "false",
            "shuffle_partitions": "2",
        }
        print(receipt)
        print("spark-021: six PySpark reference contracts passed; Spark=" + spark.version)
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
