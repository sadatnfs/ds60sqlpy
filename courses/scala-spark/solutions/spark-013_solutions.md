# spark-013 solutions: one row, one event

Review this after attempting the [pilot guide](../guides/spark-013.md), or after
explicitly requesting an answer. This is an authored beta Scala/Spark lesson. The
scripts below target proposed local profiles; no Scala compilation or Spark
execution acceptance is implied. The seven-row arithmetic and the independent
plain-Python oracle can be checked without Spark.

## Reasoning before implementation

The paid events are 1, 2, 3, 4, 6 and 7. Their observed amounts are 100, 0, 50
and 100 cents. Therefore six retained events contain four observed amounts and
total 250 cents. Prediction choice **2**, `(6, 4, 250)`, is correct. Keeping the
void event would add ID 5 and 150 cents, giving raw metrics `(7, 5, 400)`.

IDs 1 and 6 have equal team and amount values but are distinct events. After
projecting away event identity, `distinct` can no longer tell that their equal
pairs represent separate events. The incorrect result has five rows and totals
150 cents. This is a grain error, not a partitioning error.

Expected canonical paid summary:

| team | rows | valued | total_cents |
| --- | ---: | ---: | ---: |
| A | 3 | 2 | 200 |
| B | 1 | 1 | 0 |
| C | 1 | 0 | NULL |
| NULL | 1 | 1 | 50 |

The C total is unknown because there is no observed amount to sum. B has an
observed zero. The NULL team still has one event with an observed 50 cents.
Grouping does not require replacing the unknown key with a made-up team name.
These are applications of Spark's documented aggregate and NULL rules.
[Spark NULL semantics](https://spark.apache.org/docs/4.2.0/sql-ref-null-semantics.html).

## Independent fixture oracle

This is an intentionally small standard-library reference. It does not call
Spark or borrow the aggregate implementation below. It walks identified events,
retains a separate observed-value list for each team, and compares its output
to literals calculated from the fixture. An empty observed-value list yields
`None`, while a nonempty list containing zero yields zero. Use a fresh local
Python process; this check needs no JDK, Spark, service or package download.

```python
from collections import defaultdict

fixture = [
    (1, "A", 100, "paid"), (2, "A", None, "paid"),
    (3, "B", 0, "paid"), (4, None, 50, "paid"),
    (5, "B", 150, "void"), (6, "A", 100, "paid"),
    (7, "C", None, "paid"),
]
assert len({event[0] for event in fixture}) == 7
paid_fixture = [event for event in fixture if event[3] == "paid"]
assert [event[0] for event in paid_fixture] == [1, 2, 3, 4, 6, 7]

def reference_metrics(events):
    observed = [event[2] for event in events if event[2] is not None]
    return (len(events), len(observed), sum(observed) if observed else None)

def reference_summary(events):
    grouped = defaultdict(list)
    for event in events:
        grouped[event[1]].append(event)
    keys = sorted(grouped, key=lambda team: (team is None, team or ""))
    return [(team, *reference_metrics(grouped[team])) for team in keys]

golden = [
    ("A", 3, 2, 200), ("B", 1, 1, 0),
    ("C", 1, 0, None), (None, 1, 1, 50),
]
assert reference_metrics(fixture) == (7, 5, 400)
assert reference_metrics(paid_fixture) == (6, 4, 250)
assert reference_summary(paid_fixture) == golden
projected_distinct = {(event[1], event[2]) for event in paid_fixture}
assert len(projected_distinct) == 5
assert sum(amount for _, amount in projected_distinct if amount is not None) == 150
assert [event[0] for event in paid_fixture if event[2] is None] == [2, 7]
assert [event[0] for event in paid_fixture if event[2] == 0] == [3]
assert [event[0] for event in paid_fixture if event[1] is None] == [4]
print("Reference checks passed: 7 raw, 6 paid, 4 observed, 250 cents.")
```

The set above is used only to model the deliberately incorrect projected
`distinct`. It is not the mechanism used to verify the correct bag. A set-based
comparison of the real result would hide the very multiplicity defect this
lesson is meant to reveal.

## Complete Scala implementation

Run this only in a future accepted `spark-local-scala` profile as a fresh,
standalone program. It owns its local session and stops it in `finally`. It
uses `isNullAt` before primitive getters, so an unknown total cannot accidentally
turn into a numeric zero during comparison. It never collects more than seven
input rows or four output groups.

```scala
import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Spark013Solution {
  type Summary = Seq[(Option[String], Long, Long, Option[Long])]

  def ids(df: DataFrame): Seq[Long] =
    df.select("event_id").orderBy("event_id").collect()
      .map(_.getLong(0)).toSeq

  def metrics(df: DataFrame): (Long, Long, Option[Long]) = {
    val row = df.agg(
      count(lit(1)).as("rows"),
      count(col("amount_cents")).as("valued"),
      sum(col("amount_cents")).as("total_cents")
    ).first()
    (row.getLong(0), row.getLong(1),
      if (row.isNullAt(2)) None else Some(row.getLong(2)))
  }

  def summarize(df: DataFrame): DataFrame =
    df.groupBy("team").agg(
      count(lit(1)).as("rows"),
      count(col("amount_cents")).as("valued"),
      sum(col("amount_cents")).as("total_cents")
    )

  def canonical(df: DataFrame): Summary = {
    val expectedSchema: Seq[(String, DataType)] = Seq(
      ("team", StringType), ("rows", LongType),
      ("valued", LongType), ("total_cents", LongType)
    )
    assert(df.schema.fields.map(f => (f.name, f.dataType)).toSeq == expectedSchema)
    df.orderBy(col("team").asc_nulls_last).collect().toSeq.map { row =>
      (if (row.isNullAt(0)) None else Some(row.getString(0)),
        row.getLong(1), row.getLong(2),
        if (row.isNullAt(3)) None else Some(row.getLong(3)))
    }
  }

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("ds60-spark-013-solution")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.session.timeZone", "UTC").getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]")
      val schema = StructType(Seq(
        StructField("event_id", LongType, false),
        StructField("team", StringType, true),
        StructField("amount_cents", LongType, true),
        StructField("status", StringType, false)
      ))
      val rows = Seq(
        Row(1L, "A", 100L, "paid"), Row(2L, "A", null, "paid"),
        Row(3L, "B", 0L, "paid"), Row(4L, null, 50L, "paid"),
        Row(5L, "B", 150L, "void"), Row(6L, "A", 100L, "paid"),
        Row(7L, "C", null, "paid")
      )
      val raw = spark.createDataFrame(
        spark.sparkContext.parallelize(rows, 2), schema
      )
      val paid = raw.filter(col("status") === lit("paid"))
      val golden: Summary = Seq(
        (Some("A"), 3L, 2L, Some(200L)),
        (Some("B"), 1L, 1L, Some(0L)),
        (Some("C"), 1L, 0L, None),
        (None, 1L, 1L, Some(50L))
      )

      // Exercise 1: assert grain and retained/excluded identities.
      assert(ids(raw) == Seq(1L, 2L, 3L, 4L, 5L, 6L, 7L))
      assert(raw.filter(col("event_id").isNull).count() == 0L)
      assert(raw.count() == 7L)
      assert(raw.select("event_id").distinct().count() == 7L)
      assert(ids(paid) == Seq(1L, 2L, 3L, 4L, 6L, 7L))
      assert(ids(raw.filter(col("status") =!= lit("paid"))) == Seq(5L))
      assert(paid.count() == 6L)
      assert(paid.columns.contains("event_id"))

      // Exercise 2: counts and exact integer cents are different contracts.
      assert(metrics(raw) == (7L, 5L, Some(400L)))
      assert(metrics(paid) == (6L, 4L, Some(250L)))

      // Exercise 3: preserve NULL, observed zero and the NULL-key group.
      assert(canonical(summarize(paid)) == golden)

      // Exercise 4: use explicit missingness or NULL-safe equality.
      assert(ids(paid.filter(col("amount_cents").isNull)) == Seq(2L, 7L))
      assert(ids(paid.filter(col("amount_cents") === lit(0L))) == Seq(3L))
      assert(ids(paid.filter(col("team").isNull)) == Seq(4L))
      assert(ids(paid.filter(col("team") === lit(null))).isEmpty)
      assert(ids(paid.filter(col("team") <=> lit(null))) == Seq(4L))

      // Exercise 5: show the incorrect shortcut, then preserve the real bag.
      val wrong = paid.select("team", "amount_cents").distinct()
      assert(metrics(wrong) == (5L, 3L, Some(150L)))
      assert(metrics(paid) == (6L, 4L, Some(250L)))
      assert(canonical(summarize(paid.repartition(3))) == golden)

      // Exercise 6: SQL and DataFrames each compare to independent literals.
      paid.createOrReplaceTempView("ds60_spark_013_paid")
      val sqlResult = spark.sql("""
        SELECT team, COUNT(*) AS rows,
               COUNT(amount_cents) AS valued,
               SUM(amount_cents) AS total_cents
        FROM ds60_spark_013_paid
        GROUP BY team
        ORDER BY team ASC NULLS LAST
      """)
      assert(canonical(sqlResult) == golden)
      assert(raw.count() == paid.count() + 1L)
      assert(metrics(paid)._3.contains(250L))
      println("Scala checks passed: 7 raw, 6 paid, 4 observed, 250 cents.")
    } finally {
      spark.stop()
    }
  }
}
```

`wrong` has only three observed amounts: the second A/100 pair disappeared.
Its two remaining missing-amount pairs do not contribute to the field count.
That extra assertion explains why the five-row shortcut's observed count is
three, even though the prediction distractor only needed its wrong row/sum pair.

## Complete PySpark implementation

This is a fresh standalone program for the future `spark-local-python` profile.
The schema is explicit, and `canonical` verifies names and types before values.
The tuple checks preserve multiplicity rather than converting results to sets.
The `None` values in the golden list are intentional expected values.

```python
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
    paid = raw.filter(F.col("status") == F.lit("paid"))
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
```

The schema check intentionally checks names and data types, not every inferred
aggregate-nullability flag or textual plan ID. Those details can differ while
the stated contract is unchanged. The guide calls the integral result type
`long`; Spark's `simpleString()` spells that same type `bigint`.

## Exercise explanations and contracts

### Exercise 1: identity survives filtering

Filtering status removes only ID 5. No projection or deduplication is necessary.
A distinct-ID count verifies this fixture's grain, while a row count verifies
multiplicity; neither replaces the other for arbitrary data. The non-null ID
assertion makes the identity contract explicit instead of trusting a printed
schema as a data-quality test.

**Inputs/evidence:** For spark-013 Exercise 1, use the seven-row main fixture,
`raw` and your retained/excluded event-ID lists.

**Expected result/shape:** For spark-013 Exercise 1, input IDs are
`[1, 2, 3, 4, 5, 6, 7]`; paid IDs are `[1, 2, 3, 4, 6, 7]`; excluded IDs are
`[5]`. The raw count and distinct-ID count both equal 7.

**Verify:** For spark-013 Exercise 1, assert the exact sorted ID lists and both
raw counts; assert `paid.count() == 6` and retain `event_id` in the paid schema.

### Exercise 2: three metrics answer three questions

Rows measure retained events, `valued` measures observed amounts, and the sum
measures observed cents. They cannot be substituted for one another. Raw total
400 includes the void event's 150 cents. The paid total 250 includes both A/100
events. Missing amounts affect `valued` without deleting their events.

**Inputs/evidence:** For spark-013 Exercise 2, use the raw and paid DataFrames
and named count/sum aggregate fields.

**Expected result/shape:** For spark-013 Exercise 2, raw metrics are
`(7, 5, 400)` and paid metrics are `(6, 4, 250)` in the field order
`(rows, valued, total_cents)`.

**Verify:** For spark-013 Exercise 2, assert both exact tuples and explain the
100-cent contributions of IDs 1 and 6 and the absent contributions of IDs 2 and 7.

### Exercise 3: NULL is a meaningful result

The A group contains IDs 1, 2 and 6. B contains ID 3 after filtering, not the
void event. C's only amount is missing, so its sum is NULL. ID 4 contributes
50 cents to the missing-team group. A final sort places that group last and
makes a tuple-by-tuple test meaningful. It does not permanently sort an input
DataFrame or guarantee unrelated future actions share a physical order.

**Inputs/evidence:** For spark-013 Exercise 3, use paid events and a four-column
canonical summary, with an explicit NULL-aware final order.

**Expected result/shape:** For spark-013 Exercise 3, ordered tuples are
`[("A", 3, 2, 200), ("B", 1, 1, 0), ("C", 1, 0, NULL), (NULL, 1, 1, 50)]`.

**Verify:** For spark-013 Exercise 3, compare all four tuples with a hand-written
golden list, checking the NULL sum for C separately from the observed zero for B.

### Exercise 4: filtering keeps TRUE, not unknown

`isNull` asks directly about missingness. Equality to zero asks about an observed
number. Ordinary equality to a NULL literal produces an unknown result for
these rows, so none pass the filter. NULL-safe equality has a defined matching
case for two NULLs, retaining the missing team at ID 4. The ordinary-equality
query is deliberately included as a diagnostic counterexample.

**Inputs/evidence:** For spark-013 Exercise 4, use paid events and five sorted
ID lists from missing-amount, zero, missing-team, ordinary-NULL-equality and
NULL-safe-team predicates.

**Expected result/shape:** For spark-013 Exercise 4, the lists are `[2, 7]`,
`[3]`, `[4]`, `[]` and `[4]`, respectively.

**Verify:** For spark-013 Exercise 4, assert the five lists exactly; explain
that an unknown ordinary comparison is not TRUE and zero is an observed value.

### Exercise 5: projection can erase the evidence needed to deduplicate

A full row includes its unique ID, so a full-row `distinct` would retain all
seven raw events. The bad shortcut first removes `event_id`, making paid events
1 and 6 indistinguishable. That is why it loses exactly 100 cents. In contrast,
repartitioning moves the original rows without changing their logical values or
multiplicities. Only compare its result after the same final ordering contract.

**Inputs/evidence:** For spark-013 Exercise 5, compare the original paid bag,
the two-column distinct projection and a correctly summarized repartitioned bag.

**Expected result/shape:** For spark-013 Exercise 5, the distinct projection
has 5 rows and totals 150 cents; the original bag has 6 rows and totals 250 cents.
Repartitioning preserves the four golden group tuples from Exercise 3.

**Verify:** For spark-013 Exercise 5, assert both count/total pairs and the full
canonical summary after repartitioning; identify IDs 1 and 6 as the legitimate
pair collapsed by the projection-plus-distinct shortcut.

### Exercise 6: implementation agreement is necessary but insufficient

SQL and DataFrame APIs share Spark's engine. Their agreement is useful, but
copying the same bad grain assumption into both would make them agree on an
incorrect answer. The independent literal golden list and plain-Python fixture
walk provide an additional check. The count ledger accounts for all seven
inputs, while the exact type contract prevents a stringified money result from
passing only because its display looks plausible.
[Spark SQL and DataFrames](https://spark.apache.org/docs/4.2.0/sql-programming-guide.html).

**Inputs/evidence:** For spark-013 Exercise 6, use the four golden group tuples,
a SQL temporary view, paired API results and the raw/paid/excluded ledger.

**Expected result/shape:** For spark-013 Exercise 6, every implementation has
columns `team:string`, `rows:long`, `valued:long`, `total_cents:long`, the same
four canonical tuples, and a count ledger `7 = 6 + 1` with paid total 250 cents.

**Verify:** For spark-013 Exercise 6, assert names, data types, complete tuples
and the ledger against independent literals; keep both language assertions in
the evidence packet and explain why two implementations can share the same bug.

## Retrieval answers and transfer check

`count(*)` counts retained events; counting an amount counts only observed
values. NULL-only C is not equivalent to observed-zero B. A missing grouping
key still forms a group and does not erase the observed amount. Repartitioning
changes physical distribution, while final ordering defines display order.

For the transfer fixture, replace ID 7 with two distinct C events, both missing
an amount, and add one D event worth 25 cents. There are now **8 paid rows**,
**5 observed amounts**, and **275 cents**. The ordered summary is
`[("A",3,2,200), ("B",1,1,0), ("C",2,0,NULL), ("D",1,1,25), (NULL,1,1,50)]`.
The raw fixture has 9 rows if the original void event remains. Use distinct new
IDs for the replacement/additional events. If a report displays C as zero, it
must label that as a display/defaulting policy and retain evidence that no C
amount was observed.

## Review rubric and next step

Use the six 0/1/2 criteria from the guide. A score of 2 requires correct values
and an explanation tied to row identity or NULL semantics. A missing or vague
piece of evidence earns at most 1, even if another assertion happens to pass.
Do not make the official answer the only test oracle. Deliberately introduce
the bad distinct projection once and confirm that the canonical contract fails.

Proceed to `spark-014` in the [track plan](../../../docs/expansion/tracks/scala-spark.md), carrying
forward the explicit schema, rejection ledger, golden fixture and session
ownership rules. Spark execution, compiler compatibility, bounded process
cleanup and platform acceptance remain release gates for the future adapters.

Complete worker references: [Scala](spark-013_solution.scala) and [PySpark](spark-013_solution.py). Both use the same schema and seven-row fixture. Execution and typed contract verification are separate receipts; neither grades the retrieval explanation.
