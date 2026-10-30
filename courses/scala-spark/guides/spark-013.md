# spark-013: One row, one event

A NULL-aware aggregate lesson in Scala, PySpark and Spark SQL.

Open this lesson from the Scala and Apache Spark path in the unified
`/classroom`. Its Scala and PySpark variants use the separately prepared
`spark-local-scala` and `spark-local-python` workers. The classroom capability
notice reports actual runtime readiness. Reading a guide does not install a
JVM or prove that a worker is ready. Keep the
[solutions](../solutions/spark-013_solutions.md) separate while you predict
and attempt the work.

## Level and prerequisites

Beginner, about 90 minutes after a local profile is available. Complete
`spark-012` and demonstrate either the Scala foundations through `spark-010`,
or the PySpark bridge `spark-011` with existing `python-10` skills. Neither path
requires the historical SQL course: the small amount of SQL below is explained
here. Existing `sql-02` offers optional extra aggregate practice.

The classroom worker configuration uses Spark 4.0.1, the Scala 2.13 binary
line, Java 17 and Python 3.12. Read the actual worker version report when
reproducing a run, especially after an explicit image override. Apache's
[versioned environment requirements](https://spark.apache.org/docs/4.0.1/)
explain the compatible language lines. The earlier expansion design discussed
a newer candidate tuple; that historical plan is not the installed image.

## Learning objectives

- State the grain of a table and preserve distinct events with equal values.
- Distinguish retained rows, observed amounts, zero amounts and missing amounts.
- Predict the behavior of grouping, `count`, `sum` and NULL comparisons.
- Separate a result's logical content from its physical partition layout.
- Compare Scala, PySpark and SQL against an independent, ordered golden result.

## Vocabulary and concepts

- **Grain** means what one row represents. Here one row is one event identified
  by `event_id`; it is not one unique `(team, amount_cents)` combination.
- A **bag**, also called a multiset, permits equal-valued rows to occur more
  than once. Distinct event IDs can carry the same amount and team.
- A **schema** states field names, types and nullability. Explicit schemas avoid
  guessing the type of a column whose current values are all missing.
- **NULL** is an unknown or absent value at the SQL boundary. A zero amount is
  an observed number. A missing team is a grouping key with unknown identity.
- A **Column expression** describes work Spark will evaluate. It is not a
  Python Boolean or an already computed Scala value.
- A **transformation** constructs another query; an **action**, such as `count`
  or `collect`, requests a result. Collecting these seven rows is bounded;
  collecting an unknown production table is a different decision.
- A **canonical result** is a deliberately normalized representation for
  comparison, including the requested column order and a complete row order.
  It is not proof that Spark's underlying storage has a permanent order.

`count(*)` counts all retained rows. In the APIs, `count(lit(1))` has that effect
because the literal is non-null for every retained row. `count(amount_cents)`
counts rows with an observed amount. `sum(amount_cents)` adds observed amounts;
if a group has no observed amounts, its sum remains NULL. Replacing that NULL
with zero is a business rule that the report must name, not an automatic repair.

An ordinary comparison with NULL produces an unknown condition, so it does not
pass a filter that keeps only TRUE. Use `isNull` for missingness. Use
`eqNullSafe` in PySpark, `<=>` in Scala, or `<=>` in Spark SQL when you intend
NULL-safe equality. `GROUP BY` collects NULL keys into a group. Finally, specify
`NULLS LAST` when that is the desired presentation policy. These are Spark SQL
semantics shared by the DataFrame expressions.
[Spark NULL semantics](https://spark.apache.org/docs/4.2.0/sql-ref-null-semantics.html).

## Runtime boundary and setup

This pilot uses only inline rows, has no database connection, writes no dataset
and needs no network dataset. A future accepted profile should create a fresh
owned `SparkSession` with `local[2]`, UTC time zone, two shuffle partitions and
Spark UI disabled. Its process controller must bound memory/time and bind local
Spark communication to loopback. It must stop only the session it created.
The snippets below assume that owned session is called `spark`; the learner
scaffolds and solution scripts show its lifecycle explicitly.

Scala uses `Long` values such as `100L`; PySpark's explicit `LongType` receives
Python integers. Money is integer cents to keep arithmetic exact. In the schema,
`false`/`False` means the field cannot be missing in this fixture, and
`true`/`True` permits missing values. Scala `null` and Python `None` become SQL
NULL inside nullable fields. Scala's `Option` is useful in local code, but a
raw `Row` with this schema uses `null` at the boundary.

Before evaluating any code, write your prediction. After a run, inspect values
and assertions, not only a successful exit code. All outputs below are expected
results from a tiny independently calculated fixture. Spark/Scala execution of
this design sample has not been claimed.

## Prediction

After filtering the main fixture to status `paid`, which tuple is correct?
The tuple is `(row count, observed amount count, total cents)`.

1. `(6, 6, 250)`
2. `(6, 4, 250)`
3. `(5, 4, 150)`

Record a choice and a reason before opening the solutions. In particular, decide
whether event IDs 1 and 6 represent one event or two.

## Worked example / walkthrough

### Example 1: one missing amount is not an extra zero

This smaller fixture contains amounts 10, NULL and 0. First count the rows on
paper: there are three. Then count the observed amounts: there are two. Finally
add the observed numbers: the sum is 10. Group `x` has two rows but only one
observed amount; group `y` has one observed zero.

In an owned Scala Spark session:

```scala
import org.apache.spark.sql.Row
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val exampleSchema = StructType(
  Seq(
    StructField("team", StringType, true),
    StructField("amount_cents", LongType, true)
  )
)
val exampleRows = Seq(Row("x", 10L), Row("x", null), Row("y", 0L))
val example = spark.createDataFrame(
  spark.sparkContext.parallelize(exampleRows, 2),
  exampleSchema
)
val metrics = example
  .agg(
    count(lit(1)).as("rows"),
    count(col("amount_cents")).as("valued"),
    sum(col("amount_cents")).as("total_cents")
  )
  .first()
assert(metrics.getLong(0) == 3L)
assert(metrics.getLong(1) == 2L)
assert(metrics.getLong(2) == 10L)
example
  .groupBy("team")
  .agg(
    count(lit(1)).as("rows"),
    count(col("amount_cents")).as("valued"),
    sum(col("amount_cents")).as("total_cents")
  )
  .orderBy(col("team").asc_nulls_last)
  .show()
```

The equivalent PySpark expressions:

```python
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

example_schema = StructType(
    [
        StructField("team", StringType(), True),
        StructField("amount_cents", LongType(), True),
    ]
)
example = spark.createDataFrame([("x", 10), ("x", None), ("y", 0)], schema=example_schema)
metrics = example.agg(
    F.count(F.lit(1)).alias("rows"),
    F.count("amount_cents").alias("valued"),
    F.sum("amount_cents").alias("total_cents"),
).first()
assert tuple(metrics) == (3, 2, 10)
example.groupBy("team").agg(
    F.count(F.lit(1)).alias("rows"),
    F.count("amount_cents").alias("valued"),
    F.sum("amount_cents").alias("total_cents"),
).orderBy(F.col("team").asc_nulls_last()).show()
```

Expected rows, in order:

| team | rows | valued | total_cents |
| --- | ---: | ---: | ---: |
| x | 2 | 1 | 10 |
| y | 1 | 1 | 0 |

The argument to `count` determines what is counted. The alias only names the
result. Changing the alias to `rows` does not turn a count of a nullable field
into a count of every row.

### Example 2: all missing and observed zero remain distinct

Use a new three-row fixture: two missing amounts for `m` and one observed zero
for `n`. Reuse `exampleSchema`/`example_schema` from the first example.

```scala
val missingExample = spark.createDataFrame(
  spark.sparkContext.parallelize(
    Seq(Row("m", null), Row("m", null), Row("n", 0L)),
    2
  ),
  exampleSchema
)
val missingSummary = missingExample
  .groupBy("team")
  .agg(
    count(lit(1)).as("rows"),
    count(col("amount_cents")).as("valued"),
    sum(col("amount_cents")).as("total_cents")
  )
  .orderBy(col("team").asc_nulls_last)
  .collect()
assert(missingSummary(0).getString(0) == "m")
assert(missingSummary(0).getLong(1) == 2L)
assert(missingSummary(0).getLong(2) == 0L)
assert(missingSummary(0).isNullAt(3))
assert(missingSummary(1).getLong(3) == 0L)
```

```python
missing_example = spark.createDataFrame([("m", None), ("m", None), ("n", 0)], schema=example_schema)
missing_summary = (
    missing_example.groupBy("team")
    .agg(
        F.count(F.lit(1)).alias("rows"),
        F.count("amount_cents").alias("valued"),
        F.sum("amount_cents").alias("total_cents"),
    )
    .orderBy(F.col("team").asc_nulls_last())
    .collect()
)
assert [tuple(row) for row in missing_summary] == [
    ("m", 2, 0, None),
    ("n", 1, 1, 0),
]
```

Check the Scala NULL with `isNullAt` before reading a primitive value. Do not let
an unsafe conversion of NULL to a primitive number erase the distinction you
are trying to teach. If a consumer wants a display value of zero, keep the
original observed-count field and document that display policy separately.

## Main fixture and learner scaffolds

The row grain is one event per `event_id`.

| event_id | team | amount_cents | status |
| ---: | --- | ---: | --- |
| 1 | A | 100 | paid |
| 2 | A | NULL | paid |
| 3 | B | 0 | paid |
| 4 | NULL | 50 | paid |
| 5 | B | 150 | void |
| 6 | A | 100 | paid |
| 7 | C | NULL | paid |

`void` means excluded from this report; it does not delete the input event.
IDs 1 and 6 deliberately carry the same team and amount. They are different
paid events. The missing team at ID 4 does not make its observed amount missing.

Save separate Scala and PySpark attempts. Once an optional local profile is
prepared, the following complete skeletons provide an owned session and the
fixture. Add your six exercise results inside `try`, retaining `finally`.
Do not paste a standalone session-owning program into somebody else's shared
Spark shell.

### Scala learner skeleton

```scala
import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-013-attempt")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.session.timeZone", "UTC")
      .getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]")
      val schema = StructType(
        Seq(
          StructField("event_id", LongType, false),
          StructField("team", StringType, true),
          StructField("amount_cents", LongType, true),
          StructField("status", StringType, false)
        )
      )
      val rows = Seq(
        Row(1L, "A", 100L, "paid"),
        Row(2L, "A", null, "paid"),
        Row(3L, "B", 0L, "paid"),
        Row(4L, null, 50L, "paid"),
        Row(5L, "B", 150L, "void"),
        Row(6L, "A", 100L, "paid"),
        Row(7L, "C", null, "paid")
      )
      val raw = spark.createDataFrame(
        spark.sparkContext.parallelize(rows, 2),
        schema
      )
      println(raw.schema.simpleString)
      // Exercise 1: retain event identity and filter status.
      // Exercise 2: inspect row count, observed count and sum.
      // Exercise 3: aggregate by team and order NULL keys last.
      // Exercise 4: distinguish NULL predicates and observed zero.
      // Exercise 5: expose projected-distinct loss; repartition safely.
      // Exercise 6: compare both APIs and SQL to the golden fixture.
    } finally {
      spark.stop()
    }
  }
}
```

### PySpark learner skeleton

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

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
```

## Exercises

### Exercise 1: preserve grain before filtering

Check that all seven IDs are non-null and unique. Derive `paid` by filtering
`status == "paid"` without projecting away `event_id`. Inspect a sorted list of
retained IDs and the separate excluded-ID list.

**Inputs/evidence:** For spark-013 Exercise 1, use the seven-row main fixture,
`raw` and your retained/excluded event-ID lists.

**Expected result/shape:** For spark-013 Exercise 1, input IDs are
`[1, 2, 3, 4, 5, 6, 7]`; paid IDs are `[1, 2, 3, 4, 6, 7]`; excluded IDs are
`[5]`. The raw count and distinct-ID count both equal 7.

**Verify:** For spark-013 Exercise 1, assert the exact sorted ID lists and both
raw counts; assert `paid.count() == 6` and retain `event_id` in the paid schema.

### Exercise 2: count rows and observed amounts separately

Compute `rows`, `valued` and `total_cents` for both `raw` and `paid`. Explain why
counting a nullable field cannot verify how many events survived a filter.

**Inputs/evidence:** For spark-013 Exercise 2, use the raw and paid DataFrames
and named count/sum aggregate fields.

**Expected result/shape:** For spark-013 Exercise 2, raw metrics are
`(7, 5, 400)` and paid metrics are `(6, 4, 250)` in the field order
`(rows, valued, total_cents)`.

**Verify:** For spark-013 Exercise 2, assert both exact tuples and explain the
100-cent contributions of IDs 1 and 6 and the absent contributions of IDs 2 and 7.

### Exercise 3: keep NULL-only, zero and NULL-key groups

Group paid rows by `team`. Return exactly `team`, `rows`, `valued`,
`total_cents`, ordered by team ascending with NULL keys last. Do not replace
missing amounts or group keys before aggregating.

**Inputs/evidence:** For spark-013 Exercise 3, use paid events and a four-column
canonical summary, with an explicit NULL-aware final order.

**Expected result/shape:** For spark-013 Exercise 3, ordered tuples are
`[("A", 3, 2, 200), ("B", 1, 1, 0), ("C", 1, 0, NULL), (NULL, 1, 1, 50)]`.

**Verify:** For spark-013 Exercise 3, compare all four tuples with a hand-written
golden list, checking the NULL sum for C separately from the observed zero for B.

### Exercise 4: choose the right predicate

Find paid rows with missing amounts, paid rows with amount zero, and paid rows
whose team is missing. Compare ordinary equality with a NULL literal against
NULL-safe equality on the team column. Explain which filter retains TRUE.

**Inputs/evidence:** For spark-013 Exercise 4, use paid events and five sorted
ID lists from missing-amount, zero, missing-team, ordinary-NULL-equality and
NULL-safe-team predicates.

**Expected result/shape:** For spark-013 Exercise 4, the lists are `[2, 7]`,
`[3]`, `[4]`, `[]` and `[4]`, respectively.

**Verify:** For spark-013 Exercise 4, assert the five lists exactly; explain
that an unknown ordinary comparison is not TRUE and zero is an observed value.

### Exercise 5: expose an attractive incorrect shortcut

Project paid rows to only `(team, amount_cents)`, then apply `distinct` and
calculate its row count and total. Explain which event identity was lost.
Separately repartition the original paid DataFrame to three partitions and
recompute the correct team summary with its explicit final order.

**Inputs/evidence:** For spark-013 Exercise 5, compare the original paid bag,
the two-column distinct projection and a correctly summarized repartitioned bag.

**Expected result/shape:** For spark-013 Exercise 5, the distinct projection
has 5 rows and totals 150 cents; the original bag has 6 rows and totals 250 cents.
Repartitioning preserves the four golden group tuples from Exercise 3.

**Verify:** For spark-013 Exercise 5, assert both count/total pairs and the full
canonical summary after repartitioning; identify IDs 1 and 6 as the legitimate
pair collapsed by the projection-plus-distinct shortcut.

### Exercise 6: verify across APIs and an independent oracle

Register the paid DataFrame as an owned temporary view. Write a SQL aggregate
using `COUNT(*)`, `COUNT(amount_cents)`, `SUM(amount_cents)`, `GROUP BY team`,
and `ORDER BY team ASC NULLS LAST`. Compare the Scala, PySpark and SQL contracts
against the golden fixture, not merely against each other. Record the input,
retained and excluded event counts as a small reconciliation ledger.

**Inputs/evidence:** For spark-013 Exercise 6, use the four golden group tuples,
a SQL temporary view, paired API results and the raw/paid/excluded ledger.

**Expected result/shape:** For spark-013 Exercise 6, every implementation has
columns `team:string`, `rows:long`, `valued:long`, `total_cents:long`, the same
four canonical tuples, and a count ledger `7 = 6 + 1` with paid total 250 cents.

**Verify:** For spark-013 Exercise 6, assert names, data types, complete tuples
and the ledger against independent literals; keep both language assertions in
the evidence packet and explain why two implementations can share the same bug.

## Progressive hints

1. Keep a ledger of event IDs before comparing values. Equal values do not tell
   you whether two records are the same event.
2. Count a non-null literal and the amount field separately. Inspect team C
   before considering any `coalesce` business rule.
3. Normalize the final summary with an explicit NULL-last order, compare it to
   a literal golden list, and inspect which columns existed immediately before
   `distinct`.

## Retrieval and transfer

Without looking at the code, explain why `count(amount_cents)` differs from
`count(*)`, why an all-missing group's sum is NULL, and why grouping missing
teams does not drop their observed money. Then explain why `repartition(3)`
does not license a fixed order for raw `collect()` results.

For transfer, replace the single C event with two distinct C events whose
amounts are both missing, and add a paid D event worth 25 cents. Predict the new
paid row count, observed count, total and ordered groups before running either
API. State the separate business decision needed if the final display replaces
an unknown amount total with zero.

## Self-check

- Can you identify each event contributing to the 250-cent paid sum and account
  for the two paid events with missing amounts?
- Can you explain a failed assertion in terms of grain, missingness or ordering
  before changing code to match an output?
- Can a peer reproduce your four golden rows in the other language without
  relying on your implementation as the oracle?

## Rubric

Score each criterion 0, 1 or 2: 0 means absent or incorrect, 1 means a correct
result with incomplete evidence/explanation, and 2 means exact evidence plus a
correct explanation. There are six criteria: grain/filter, count/sum distinction,
NULL/zero/group behavior, predicates, bag/partition invariance, and independent
cross-language/SQL parity. Mastery requires 2 on each criterion and a correct
transfer prediction. A successful process exit alone earns no criterion.

## Common pitfalls

Using a set to compare rows can hide duplicate loss. Comparing printed `show`
tables can hide a type mismatch. Filling NULL with zero before thinking about
meaning can erase missingness. Sorting within partitions can leave the overall
result unordered. Scala primitive getters need a NULL guard. PySpark Columns
need `&`/`|` with parentheses rather than Python `and`/`or`. Both implementations
can repeat the same bad assumption, so a hand-written oracle remains necessary.

If a future runtime reports a missing Java/Spark profile, keep your saved
prediction and attempt and show the capability message to the teacher. Do not
install an arbitrary package from a tutor answer. Provisioning and compatibility
are a separate, explicit step.

## Next step

Continue to [spark-014](spark-014.md), the authored twelve-event revenue
capstone. The [course README](../README.md) explains the broader track sequence.
Use the [separate solutions](../solutions/spark-013_solutions.md) to review your
reasoning only after an attempt or an explicit request.

## Durable worker artifacts

The Scala attempt is [spark-013.scala](../lessons/spark-013.scala); the paired Python attempt is [spark-013.py](../lessons/spark-013.py). The worker stages them as Main.scala/object Main or main.py. Both expose paidEvents/paid_events and summarize functions for independent typed checks. The [standard-library oracle](../fixtures/spark013_oracle.py) and [seven-row JSON fixture](../fixtures/spark013.json) are local and require no download. The worker may finish execution without grading when verification_id is null. A registered typed verifier must check identities, schema, NULLs and a changed fixture, not stdout keywords. Review the authored [spark-012](spark-012.md) session and schema lesson before this unit.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning. I am studying authored beta spark-013 from
 courses/scala-spark/guides/spark-013.md and courses/scala-spark/lessons/spark-013.scala.
My chosen route is Scala-first or PySpark-first: <route>.
My prediction and attempted code are: <paste>.
My observed IDs/metrics or exact error are: <paste>.
Help me locate a grain, NULL or ordering mistake. Ask one retrieval question,
then give the smallest next hint. Do not open or reproduce
../solutions/spark-013_solutions.md until I have attempted the work or explicitly
ask for the solution. Check the selected Scala or PySpark runtime readiness
in the current classroom before execution. Do not install dependencies or
claim a successful run without observing its actual result.
```
