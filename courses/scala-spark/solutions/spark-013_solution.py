from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType


def ids(df):
    return [row["event_id"] for row in df.select("event_id")
            .orderBy("event_id").collect()]


def metrics(df):
    row = df.agg(
        F.count(F.lit(1)).alias("rows"),
        F.count("amount_cents").alias("valued"),
        F.sum("amount_cents").alias("total_cents"),
    ).first()
    return (row["rows"], row["valued"], row["total_cents"])


def summarize(df):
    return df.groupBy("team").agg(
        F.count(F.lit(1)).alias("rows"),
        F.count("amount_cents").alias("valued"),
        F.sum("amount_cents").alias("total_cents"),
    )


def canonical(df):
    assert [(field.name, field.dataType.simpleString())
            for field in df.schema.fields] == [
        ("team", "string"), ("rows", "bigint"),
        ("valued", "bigint"), ("total_cents", "bigint"),
    ]
    return [tuple(row) for row in
            df.orderBy(F.col("team").asc_nulls_last()).collect()]



def paid_events(raw):
    return raw.filter(F.col("status") == F.lit("paid"))

def main():
    spark = (
        SparkSession.builder.appName("ds60-spark-013-solution")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    try:
        assert spark.sparkContext.master == "local[2]"
        schema = StructType([
            StructField("event_id", LongType(), False),
            StructField("team", StringType(), True),
            StructField("amount_cents", LongType(), True),
            StructField("status", StringType(), False),
        ])
        rows = [
            (1, "A", 100, "paid"), (2, "A", None, "paid"),
            (3, "B", 0, "paid"), (4, None, 50, "paid"),
            (5, "B", 150, "void"), (6, "A", 100, "paid"),
            (7, "C", None, "paid"),
        ]
        raw = spark.createDataFrame(rows, schema=schema)
        paid = paid_events(raw)
        golden = [
            ("A", 3, 2, 200), ("B", 1, 1, 0),
            ("C", 1, 0, None), (None, 1, 1, 50),
        ]

        # Exercise 1: grain and the exact paid/excluded IDs.
        assert ids(raw) == [1, 2, 3, 4, 5, 6, 7]
        assert raw.filter(F.col("event_id").isNull()).count() == 0
        assert raw.count() == 7
        assert raw.select("event_id").distinct().count() == 7
        assert ids(paid) == [1, 2, 3, 4, 6, 7]
        assert ids(raw.filter(F.col("status") != F.lit("paid"))) == [5]
        assert paid.count() == 6
        assert "event_id" in paid.columns

        # Exercise 2: distinguish events from observed amounts.
        assert metrics(raw) == (7, 5, 400)
        assert metrics(paid) == (6, 4, 250)

        # Exercise 3: all four groups, NULLs and zero included.
        assert canonical(summarize(paid)) == golden

        # Exercise 4: SQL NULL semantics expressed with Columns.
        assert ids(paid.filter(F.col("amount_cents").isNull())) == [2, 7]
        assert ids(paid.filter(F.col("amount_cents") == F.lit(0))) == [3]
        assert ids(paid.filter(F.col("team").isNull())) == [4]
        assert ids(paid.filter(F.col("team") == F.lit(None))) == []
        assert ids(paid.filter(F.col("team").eqNullSafe(F.lit(None)))) == [4]

        # Exercise 5: deliberately incorrect projection, then correct repartition.
        wrong = paid.select("team", "amount_cents").distinct()
        assert metrics(wrong) == (5, 3, 150)
        assert metrics(paid) == (6, 4, 250)
        assert canonical(summarize(paid.repartition(3))) == golden

        # Exercise 6: compare SQL to literals, not only to another implementation.
        paid.createOrReplaceTempView("ds60_spark_013_paid")
        sql_result = spark.sql("""
            SELECT team, COUNT(*) AS rows,
                   COUNT(amount_cents) AS valued,
                   SUM(amount_cents) AS total_cents
            FROM ds60_spark_013_paid
            GROUP BY team
            ORDER BY team ASC NULLS LAST
        """)
        assert canonical(sql_result) == golden
        assert raw.count() == paid.count() + 1
        assert metrics(paid)[2] == 250
        print("PySpark checks passed: 7 raw, 6 paid, 4 observed, 250 cents.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
