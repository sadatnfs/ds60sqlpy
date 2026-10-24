from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType


def paid_events(raw):
    raise NotImplementedError("Complete paid event filter")


def summarize(paid):
    raise NotImplementedError("Complete team summary")


def main():
    spark = (
        SparkSession.builder.appName("ds60-spark-013-attempt")
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
        schema = StructType(
            [
                StructField("event_id", LongType(), False),
                StructField("team", StringType(), True),
                StructField("amount_cents", LongType(), True),
                StructField("status", StringType(), False),
            ]
        )
        rows = [
            (1, "A", 100, "paid"),
            (2, "A", None, "paid"),
            (3, "B", 0, "paid"),
            (4, None, 50, "paid"),
            (5, "B", 150, "void"),
            (6, "A", 100, "paid"),
            (7, "C", None, "paid"),
        ]
        raw = spark.createDataFrame(rows, schema=schema)
        print(raw.schema.simpleString())
        # Exercise 1: retain event identity and filter status.
        # Exercise 2: inspect row count, observed count and sum.
        # Exercise 3: aggregate by team and order NULL keys last.
        # Exercise 4: distinguish NULL predicates and observed zero.
        # Exercise 5: expose projected-distinct loss; repartition safely.
        # Exercise 6: compare both APIs and SQL to the golden fixture.
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
