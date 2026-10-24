"""Trusted spark-rows-v1 checks; worker stages learner source as main.py."""

import json
from pathlib import Path
import main as learner
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

checks = []


def check(name, passed, detail):
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


spark = (
    SparkSession.builder.appName("ds60-spark-rows-v1")
    .master("local[2]")
    .config("spark.ui.enabled", "false")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
try:
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

    def ids(df):
        return [row[0] for row in df.select("event_id").orderBy("event_id").collect()]

    def canonical(df):
        return [tuple(row) for row in df.orderBy(F.col("team").asc_nulls_last()).collect()]

    expected = [("A", 3, 2, 200), ("B", 1, 1, 0), ("C", 1, 0, None), (None, 1, 1, 50)]
    paid = learner.paid_events(spark.createDataFrame(rows, schema))
    check(
        "paid-identities",
        ids(paid) == [1, 2, 3, 4, 6, 7],
        "Exact event identities preserve legitimate repeated values",
    )
    summary = learner.summarize(paid)
    check(
        "summary-schema",
        [(f.name, f.dataType.simpleString()) for f in summary.schema.fields]
        == [
            ("team", "string"),
            ("rows", "bigint"),
            ("valued", "bigint"),
            ("total_cents", "bigint"),
        ],
        "Four named typed output fields",
    )
    check("summary-values", canonical(summary) == expected, "NULL-aware golden groups")
    check(
        "partition-invariance",
        canonical(learner.summarize(paid.repartition(3))) == expected,
        "Physical redistribution preserves logical content",
    )
    transfer = learner.paid_events(spark.createDataFrame(rows + [(8, "D", 25, "paid")], schema))
    check(
        "transfer-identities",
        ids(transfer) == [1, 2, 3, 4, 6, 7, 8],
        "Changed input remains visible",
    )
    check(
        "transfer-summary",
        canonical(learner.summarize(transfer)) == expected[:3] + [("D", 1, 1, 25)] + expected[3:],
        "Changed fixture defeats a hardcoded result",
    )
except Exception:
    import traceback

    traceback.print_exc()
    check("execution-exception", False, "Learner API raised before typed checks completed")
finally:
    spark.stop()
    Path("checks.json").write_text(json.dumps({"checks": checks}) + "\n", encoding="utf-8")
raise SystemExit(0 if checks and all(c["passed"] for c in checks) else 1)
