# spark-014: Explained paired reference solutions

Read the [guide](../guides/spark-014.md) and attempt one language first. The [Scala reference](spark-014_solution.scala) and [PySpark reference](spark-014_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Classify defects without dropping source occurrences

Add a nullable rejection_reason Column using the declared precedence: missing_id, invalid_id, unknown_status, negative_amount. Keep every source field and row. Unknown amounts are allowed; unknown statuses are not.

**Expected:** Source row 11 has unknown_status, row 12 has missing_id, and the other 10 reasons are NULL. All 12 source_row identities remain.

```scala
def classified(frame: DataFrame): DataFrame = {
  val reason = when(col("event_id").isNull, lit("missing_id"))
    .when(col("event_id") <= lit(0L), lit("invalid_id"))
    .when(col("status").isNull || !col("status").isin("paid", "void"), lit("unknown_status"))
    .when(col("amount_cents") < lit(0L), lit("negative_amount"))
    .otherwise(lit(null).cast(StringType))
  frame.withColumn("rejection_reason", reason)
}
```

```python
def classified(frame):
    reason = (
        F.when(F.col("event_id").isNull(), F.lit("missing_id"))
        .when(F.col("event_id") <= F.lit(0), F.lit("invalid_id"))
        .when(
            F.col("status").isNull() | ~F.col("status").isin("paid", "void"),
            F.lit("unknown_status"),
        )
        .when(F.col("amount_cents") < F.lit(0), F.lit("negative_amount"))
        .otherwise(F.lit(None).cast("string"))
    )
    return frame.withColumn("rejection_reason", reason)
```

Classification adds evidence while preserving the source relation. The explicit NULL-status test prevents three-valued logic from letting an unknown status fall through as valid. The chain defines one reproducible first reason when defects overlap. Unknown amount is not a negative amount and remains permitted, so the classifier does not invent a value merely to simplify aggregation.

**Verification evidence:** Assert the exact two(source_row, reason) pairs and the unchanged source count 12.

### Exercise 2: Create the accepted event relation

Return source_row, event_id, team, amount_cents, status only for rows with no rejection reason. Preserve the valid void event and all accepted zero/NULL amounts.

**Expected:** Accepted event IDs are 1 through 10, with 10 rows. Event 5 remains accepted as void; IDs 2 and 7 remain accepted with unknown amounts.

```scala
def accepted(frame: DataFrame): DataFrame = {
  classified(frame)
    .filter(col("rejection_reason").isNull)
    .select("source_row", "event_id", "team", "amount_cents", "status")
}
```

```python
def accepted(frame):
    return (
        classified(frame)
        .filter(F.col("rejection_reason").isNull())
        .select("source_row", "event_id", "team", "amount_cents", "status")
    )
```

The accepted relation represents source validity, not paid-revenue eligibility. Keeping the void event allows the later report to reconcile why one accepted event contributes no paid revenue. NULL and zero remain distinct observations. The exact IDs guard against a classifier that happens to produce ten rows after losing one valid event and admitting one invalid event.

**Verification evidence:** Assert the complete accepted ID list, count 10, one void row and two NULL-amount rows.

### Exercise 3: Retain a complete quarantine row

Return source_row, event_id, team, amount_cents, status, rejection_reason for rejected records, ordered by source_row when inspected. Keep the original values, including the missing event ID.

**Expected:** Rows are(11,11, A,10, mystery, unknown_status) and (12, NULL, A,5, paid, missing_id). Accepted and quarantined counts sum to 12.

```scala
def quarantine(frame: DataFrame): DataFrame = {
  classified(frame)
    .filter(col("rejection_reason").isNotNull)
    .select("source_row", "event_id", "team", "amount_cents", "status", "rejection_reason")
}
```

```python
def quarantine(frame):
    return (
        classified(frame)
        .filter(F.col("rejection_reason").isNotNull())
        .select("source_row", "event_id", "team", "amount_cents", "status", "rejection_reason")
    )
```

A reason without the original record is often insufficient for diagnosis. The quarantine preserves both source occurrence identity and all relevant raw fields, including the malformed status or missing business ID. Complementary filters over one classification support count conservation, while exact row comparisons verify that rejected content was not rewritten. No record is silently repaired or assigned a made-up ID.

**Verification evidence:** Compare every quarantined field with literal expected rows and check count conservation independently.

### Exercise 4: Publish a NULL-aware paid summary

From accepted records, filter paid and group by team into team, rows, valued, total_cents. Count every event, only nonnull amounts, and the exact Long sum. Preserve a NULL team group and a NULL-only amount group.

**Expected:** Groups are A:(3,2,200), B:(2,2,25), C:(1,0, NULL), D:(1,1,200), E:(1,1,0), NULL:(1,1,50). Paid metrics are 9 rows,7 valued,475 cents.

```scala
def summarizePaid(frame: DataFrame): DataFrame = {
  frame
    .filter(col("status") === lit("paid"))
    .groupBy("team")
    .agg(
      count(lit(1)).as("rows"),
      count(col("amount_cents")).as("valued"),
      sum(col("amount_cents")).as("total_cents")
    )
}
```

```python
def summarize_paid(frame):
    return (
        frame.filter(F.col("status") == F.lit("paid"))
        .groupBy("team")
        .agg(
            F.count(F.lit(1)).alias("rows"),
            F.count("amount_cents").alias("valued"),
            F.sum("amount_cents").alias("total_cents"),
        )
    )
```

The three measures answer different questions: event volume, observed-value volume and measured cents. Group C has no observed amounts and therefore no known sum, while E has a real measured zero. The NULL team remains a group instead of disappearing through a key filter. Typed canonical comparison verifies schema and values as well as counts.

**Verification evidence:** Assert the full typed canonical group list and the global paid metrics against independent literals.

### Exercise 5: Expose projection-plus-distinct loss

Return a paid row-level projection retaining event_id, team, amount_cents. Compare it with the deliberately wrong team/amount distinct projection and explain the lost 100-cent event.

**Expected:** The correct projection has metrics(9,7,475); the wrong projection has(8,6,375). IDs 1 and 6 must both remain despite equal team/amount values.

```scala
def paidProjection(frame: DataFrame): DataFrame = {
  frame.filter(col("status") === lit("paid")).select("event_id", "team", "amount_cents")
}
```

```python
def paid_projection(frame):
    return frame.filter(F.col("status") == F.lit("paid")).select("event_id", "team", "amount_cents")
```

The wrong projection erases the field distinguishing two real events, then distinct collapses their equal remaining values. This is not duplicate-delivery handling; it is information loss created by the projection. The incorrect totals are explicitly computed and checked so the lesson proves its oracle detects a realistic mistake rather than only confirming a good implementation.

**Verification evidence:** Assert both metric tuples and verify that correct event IDs include 1 and 6 separately.

### Exercise 6: Gate the SQL report on identity and conservation

Validate at most 100 unique nonmissing source_row occurrences, unique positive accepted event IDs, and accepted-plus-quarantine conservation before returning a SQL paid summary. Reject a duplicate accepted event ID. Compare SQL output to the same literal groups.

**Expected:** The base 12-row batch passes and matches all six golden groups. Appending source_row13 with a second event_id1 rejects publication instead of choosing a winner.

```scala
def auditedSqlReport(spark: SparkSession, frame: DataFrame): DataFrame = {
  val source =
    frame.agg(count(lit(1)), countDistinct(col("source_row")), count(col("source_row"))).first()
  require(
    source.getLong(0) <= 100L && source.getLong(0) == source.getLong(1) && source.getLong(
      0
    ) == source.getLong(2),
    "invalid or oversized source identity"
  )
  val valid = accepted(frame)
  val keys = valid.agg(count(lit(1)), countDistinct(col("event_id")), min(col("event_id"))).first()
  require(
    keys.getLong(0) == keys.getLong(1) && (keys.getLong(0) == 0L || keys.getLong(2) > 0L),
    "accepted event IDs must be positive and unique"
  )
  require(
    valid.count() + quarantine(frame).count() == source.getLong(0),
    "source count does not reconcile"
  )
  valid.filter(col("status") === lit("paid")).createOrReplaceTempView("ds60_spark_014_paid")
  spark.sql(
    "SELECT team,COUNT(*) AS rows,COUNT(amount_cents) AS valued,SUM(amount_cents) AS total_cents FROM ds60_spark_014_paid GROUP BY team"
  )
}
```

```python
def audited_sql_report(spark, frame):
    source = frame.agg(
        F.count(F.lit(1)), F.countDistinct("source_row"), F.count("source_row")
    ).first()
    if not (source[0] <= 100 and source[0] == source[1] == source[2]):
        raise ValueError("invalid or oversized source identity")
    valid = accepted(frame)
    keys = valid.agg(F.count(F.lit(1)), F.countDistinct("event_id"), F.min("event_id")).first()
    if not (keys[0] == keys[1] and (keys[0] == 0 or keys[2] > 0)):
        raise ValueError("accepted event IDs must be positive and unique")
    if valid.count() + quarantine(frame).count() != source[0]:
        raise ValueError("source count does not reconcile")
    valid.filter(F.col("status") == F.lit("paid")).createOrReplaceTempView("ds60_spark_014_paid")
    return spark.sql(
        "SELECT team,COUNT(*) AS rows,COUNT(amount_cents) AS valued,SUM(amount_cents) AS total_cents FROM ds60_spark_014_paid GROUP BY team"
    )
```

The final gate validates the occurrence and event grains before presenting a report. CountDistinct ignores NULL, so equality with total count also detects missing IDs; the positive minimum adds the domain restriction. A duplicate accepted event rejects the whole report rather than being arbitrarily resolved. SQL aggregation is then checked against independent literal groups, not merely a second implementation that could share the same mistake.

**Verification evidence:** Assert base SQL parity and a real failure for the duplicate-ID extension; retain the validation failure rather than publishing a partial report.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
