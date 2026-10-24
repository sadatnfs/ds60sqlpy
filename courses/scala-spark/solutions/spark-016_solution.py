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


def fact_ids(frame):
    return [row.fact_id for row in frame.select("fact_id").orderBy("fact_id").collect()]


def pair_ids(frame):
    return [
        tuple(row)
        for row in frame.select("fact_id", "dimension_row")
        .orderBy("fact_id", "dimension_row")
        .collect()
    ]


def multiplicity(facts, dimension):
    f = facts.groupBy("key").agg(F.count(F.lit(1)).alias("fact_rows")).alias("f")
    d = dimension.groupBy("key").agg(F.count(F.lit(1)).alias("dimension_rows")).alias("d")
    joined = f.join(d, F.col("f.key").eqNullSafe(F.col("d.key")), "full").select(
        F.coalesce(F.col("f.key"), F.col("d.key")).alias("key"),
        F.coalesce("fact_rows", F.lit(0)).alias("fact_rows"),
        F.coalesce("dimension_rows", F.lit(0)).alias("dimension_rows"),
    )
    return joined.withColumn(
        "predicted_inner",
        F.when(F.col("key").isNull(), F.lit(0)).otherwise(
            F.col("fact_rows") * F.col("dimension_rows")
        ),
    )


def equality_join(facts, dimension):
    return (
        facts.alias("f")
        .join(dimension.alias("d"), F.col("f.key") == F.col("d.key"), "inner")
        .select("f.fact_id", "d.dimension_row", "f.amount_cents")
    )


def left_join(facts, dimension):
    return (
        facts.alias("f")
        .join(dimension.alias("d"), F.col("f.key") == F.col("d.key"), "left")
        .select("f.fact_id", "d.dimension_row")
    )


def membership(facts, dimension):
    return facts.join(dimension, on="key", how="left_semi"), facts.join(
        dimension, on="key", how="left_anti"
    )


def null_safe_join(facts, dimension):
    return (
        facts.alias("f")
        .join(dimension.alias("d"), F.col("f.key").eqNullSafe(F.col("d.key")), "inner")
        .select("f.fact_id", "d.dimension_row")
    )


def safe_enrichment(facts, dimension):
    keys = dimension.agg(F.count(F.lit(1)), F.countDistinct("key")).first()
    if keys[0] != keys[1]:
        raise ValueError("dimension keys must be nonnull and unique")
    return facts.join(dimension.select("key", "label"), on="key", how="left").select(
        "fact_id", "amount_cents", "label"
    )


def main():
    spark = (
        SparkSession.builder.appName("ds60-spark-016")
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
        fact_schema = StructType(
            [
                StructField("fact_id", LongType(), False),
                StructField("key", StringType(), True),
                StructField("amount_cents", LongType(), False),
            ]
        )
        dimension_schema = StructType(
            [
                StructField("dimension_row", LongType(), False),
                StructField("key", StringType(), True),
                StructField("label", StringType(), False),
            ]
        )
        facts = spark.createDataFrame(
            [(1, "A", 10), (2, "A", 20), (3, "B", 30), (4, "C", 40), (5, None, 50), (6, "D", 60)],
            schema=fact_schema,
        )
        dimension = spark.createDataFrame(
            [
                (101, "A", "alpha1"),
                (102, "A", "alpha2"),
                (103, "A", "alpha3"),
                (104, "B", "beta"),
                (105, None, "unknown"),
                (106, "E", "epsilon"),
            ],
            schema=dimension_schema,
        )
        # Exercise 1: Build a multiplicity ledger before joining facts
        ledger = [
            tuple(row)
            for row in multiplicity(facts, dimension)
            .orderBy(F.col("key").asc_nulls_last())
            .collect()
        ]
        assert ledger == [
            ("A", 2, 3, 6),
            ("B", 1, 1, 1),
            ("C", 1, 0, 0),
            ("D", 1, 0, 0),
            ("E", 0, 1, 0),
            (None, 1, 1, 0),
        ]
        assert sum(row[3] for row in ledger) == 7
        # Exercise 2: Verify equality pairs and quantify fanout
        expected_pairs = [(1, 101), (1, 102), (1, 103), (2, 101), (2, 102), (2, 103), (3, 104)]
        inner = equality_join(facts, dimension)
        assert pair_ids(inner) == expected_pairs and inner.count() == 7
        assert inner.agg(F.sum("amount_cents")).first()[0] == 120
        facts.createOrReplaceTempView("ds60_spark_016_facts")
        dimension.createOrReplaceTempView("ds60_spark_016_dimension")
        assert (
            pair_ids(
                spark.sql(
                    "SELECT f.fact_id,d.dimension_row FROM ds60_spark_016_facts f JOIN ds60_spark_016_dimension d ON f.key=d.key"
                )
            )
            == expected_pairs
        )
        # Exercise 3: Count actual matches in a left join
        left = left_join(facts, dimension)
        assert [
            tuple(row)
            for row in left.orderBy(
                F.col("fact_id"), F.col("dimension_row").asc_nulls_last()
            ).collect()
        ] == expected_pairs + [(4, None), (5, None), (6, None)]
        assert tuple(
            left.agg(
                F.count(F.lit(1)), F.count("dimension_row"), F.countDistinct("fact_id")
            ).first()
        ) == (10, 7, 6)
        # Exercise 4: Use semi and anti joins for membership
        semi, anti = membership(facts, dimension)
        assert fact_ids(semi) == [1, 2, 3] and fact_ids(anti) == [4, 5, 6]
        assert semi.count() + anti.count() == 6
        # Exercise 5: Make NULL-safe matching an explicit alternative
        assert pair_ids(null_safe_join(facts, dimension)) == expected_pairs + [(5, 105)]
        # Exercise 6: Gate enrichment on a reviewed unique dimension
        try:
            safe_enrichment(facts, dimension)
        except ValueError:
            pass
        else:
            raise AssertionError("ambiguous dimension must fail")
        reviewed = dimension.filter(F.col("dimension_row").isin(103, 104, 106))
        enriched = safe_enrichment(facts, reviewed)
        assert [tuple(row) for row in enriched.orderBy("fact_id").collect()] == [
            (1, 10, "alpha3"),
            (2, 20, "alpha3"),
            (3, 30, "beta"),
            (4, 40, None),
            (5, 50, None),
            (6, 60, None),
        ]
        assert enriched.count() == 6 and enriched.agg(F.sum("amount_cents")).first()[0] == 210
        print("spark-016: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

# Exercise 1: Build a multiplicity ledger before joining facts. Inputs/task: Return key, fact_rows, dimension_rows, predicted_inner for the union of key buckets. Merge NULL diagnostic buckets explicitly, but predict zero ordinary-equality pairs for NULL. Order keys with NULL last. Expected: A:(2,3,6), B:(1,1,1), C:(1,0,0), D:(1,0,0), E:(0,1,0), NULL:(1,1,0). Predicted inner rows sum to 7. Verify: Assert the full ledger and its summed predicted count, including unmatched right-only E and the NULL bucket.
# Exercise 2: Verify equality pairs and quantify fanout. Inputs/task: Return fact_id, dimension_row, amount_cents from an ordinary inner equality join. Compare both DataFrame and SQL pair identities with the seven literal expected pairs. Expected: Facts 1 and 2 each match dimension rows 101,102,103;fact 3 matches 104. There are 7 pairs and the repeated joined amount totals 120, while matched fact amounts total 60. Verify: Assert every pair, count 7 and pair-grain sum 120;compare a SQL join to the same pair list.
# Exercise 3: Count actual matches in a left join. Inputs/task: Return fact_id, dimension_row from an ordinary left equality join. Preserve unmatched facts with a NULL right identity and inspect rows ordered by fact_id, dimension_row. Expected: There are 10 output rows but 7 nonnull dimension_row values. Facts 4,5,6 each have one NULL-extended row;all six fact IDs remain represented. Verify: Assert the complete ordered pair/NULL list and distinguish COUNT(*)10 from COUNT(dimension_row)7.
# Exercise 4: Use semi and anti joins for membership. Inputs/task: Return a pair of DataFrames containing matched and unmatched facts under ordinary equality, using left_semi and left_anti. Preserve fact rows without right-side fanout. Expected: Semi IDs are[1,2,3], anti IDs[4,5,6]. Key A contributes two semi rows despite three dimension matches. Their bags reconcile to all six facts. Verify: Assert both exact ID lists and their combined count 6;do not use distinct to repair an inner join.
# Exercise 5: Make NULL-safe matching an explicit alternative. Inputs/task: Return fact_id, dimension_row from an inner join using NULL-safe key equality. Compare with ordinary equality and explain why the extra pair is a policy change. Expected: The ordinary seven pairs plus(5,105) produce eight pairs. No C or D match is invented. Verify: Assert all eight ordered pairs and isolate the extra NULL-key pair.
# Exercise 6: Gate enrichment on a reviewed unique dimension. Inputs/task: Reject a dimension unless key is nonnull and unique, then left-enrich facts with label while retaining fact_id and amount_cents. The supplied reviewed dimension rows 103,104,106 are the explicit accepted fixture;do not invent an arbitrary duplicate winner. Expected: The raw dimension fails. The reviewed subset yields six facts, total 210, and labels alpha 3, alpha 3, beta, NULL, NULL, NULL for IDs 1..6. Verify: Catch raw-dimension rejection, assert every enriched row and reconcile count 6, total 210.
