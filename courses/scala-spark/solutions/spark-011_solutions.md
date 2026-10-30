# spark-011: Explained paired reference solutions

Read the [guide](../guides/spark-011.md) and attempt one language first. The [Scala reference](spark-011_solution.scala) and [PySpark reference](spark-011_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Construct a predicate without collapsing it to a driver Boolean

Implement aboveTen/above_ten returning a Spark Column for amount_cents>10. Do not collect values or return a Python/Scala scalar Boolean.

**Expected:** Passing the predicate to raw.filter retains IDs 2 and 4. In Python, bool(predicate) raises ValueError rather than choosing one row's truth value.

```scala
def aboveTen(): Column = {
  col("amount_cents") > lit(10L)
}
```

```python
def above_ten():
    return F.col("amount_cents") > F.lit(10)
```

The function returns a plan expression that can be reused inside an engine transformation. No single truth value exists until the expression is evaluated for particular rows. The explicit Python failure check rejects the common use of scalar control-flow operators on a Column. The Scala return type Column makes the same boundary visible at compile time.

**Verification evidence:** Assert the exact filtered IDs and, in the PySpark reference, catch the scalar-Boolean conversion failure.

### Exercise 2: Apply the predicate and preserve event identity

Return the ordered event IDs selected by aboveTen from this tiny fixture. Preserve both equal-valued 20-cent events and leave raw unchanged.

**Expected:** The result is[2,4], and raw still contains IDs[1,2,3,4]. Projecting amount and calling distinct is not an acceptable implementation.

```scala
def selectedIds(frame: DataFrame): Seq[Long] = {
  ids(frame.filter(aboveTen()))
}
```

```python
def selected_ids(frame):
    return ids(frame.filter(above_ten()))
```

A DataFrame transformation creates another plan and does not remove rows from the raw DataFrame object. Keeping event_id preserves the event grain even when amounts repeat. The final ordering creates a deterministic driver-side comparison; without it, raw collect order would be an invalid general contract. Collection is permitted only because the fixture is explicitly tiny.

**Verification evidence:** Compare the selected IDs with literals and independently check all four raw IDs.

### Exercise 3: Select missingness explicitly

Return ordered IDs whose amount_cents is SQL NULL. Do not compare the Column to JVM null/Python None using driver identity logic, and do not treat zero as missing.

**Expected:** Only ID 3 is returned. The observed-zero ID 1 is absent from the missingness result.

```scala
def missingIds(frame: DataFrame): Seq[Long] = {
  ids(frame.filter(col("amount_cents").isNull))
}
```

```python
def missing_ids(frame):
    return ids(frame.filter(F.col("amount_cents").isNull()))
```

SQL NULL expresses unknown row data and is tested with an engine missingness operator. Equality to a null literal generally produces unknown rather than true, and a driver identity test does not inspect rows at all. The zero counterexample confirms that the implementation preserves a valid observed amount instead of collapsing it with absence.

**Verification evidence:** Assert[3] and separately assert that the zero-amount filter returns [1].

### Exercise 4: Combine conditions with engine operators

Return ordered IDs with a known amount at least 10 and event_id less than 4. Combine parenthesized Column comparisons with engine Boolean operators in each language.

**Expected:** Only ID 2 qualifies. ID 4 fails the ID bound, ID 3 is missing, and ID 1 is below the amount threshold.

```scala
def combinedIds(frame: DataFrame): Seq[Long] = {
  ids(
    frame.filter(
      col("amount_cents").isNotNull && (col("amount_cents") >= lit(10L)) && (col("event_id") < lit(
        4L
      ))
    )
  )
}
```

```python
def combined_ids(frame):
    return ids(
        frame.filter(
            F.col("amount_cents").isNotNull()
            & (F.col("amount_cents") >= F.lit(10))
            & (F.col("event_id") < F.lit(4))
        )
    )
```

The condition remains one composite engine expression rather than several driver-side decisions. Parentheses make comparison boundaries explicit in Python, avoiding precedence errors. Each excluded row challenges a different part of the predicate, so the singleton result is more informative than a test containing only positive qualifying rows.

**Verification evidence:** Assert the exact singleton and explain one exclusion reason for each other ID.

### Exercise 5: Preserve NULL through a derived column

Return a DataFrame with event_id and amount_plus_one=amount_cents+1, without filling NULL or dropping identity. Keep a Long-compatible integer result.

**Expected:** Ordered rows are(1,1),(2,21),(3, NULL),(4,21). The two 21 values remain separate events and unknown remains unknown.

```scala
def projected(frame: DataFrame): DataFrame = {
  frame.select(col("event_id"), (col("amount_cents") + lit(1L)).as("amount_plus_one"))
}
```

```python
def projected(frame):
    return frame.select("event_id", (F.col("amount_cents") + F.lit(1)).alias("amount_plus_one"))
```

Arithmetic with an unknown input remains unknown under SQL semantics. An alias names the derived field for downstream contracts instead of exposing an implementation-generated expression name. Retaining event_id keeps repeated numerical outputs attached to their distinct source events. A coalesce-to-zero operation would represent a separate imputation decision and change the third result.

**Verification evidence:** Compare every ordered row with literal expected values, including the NULL position.

### Exercise 6: Compare SQL and Columns with an independent expectation

Register a session-local temporary view and return ordered IDs from SQL SELECT/WHERE amount_cents>10. Compare SQL and DataFrame paths to the literal expected IDs rather than only to one another.

**Expected:** Both paths return [2,4]. The temporary view exists only in this owned session and no external database connection is opened.

```scala
def sqlIds(spark: SparkSession, frame: DataFrame): Seq[Long] = {
  frame.createOrReplaceTempView("ds60_spark_011_events")
  ids(
    spark.sql(
      "SELECT event_id FROM ds60_spark_011_events WHERE amount_cents > 10 ORDER BY event_id"
    )
  )
}
```

```python
def sql_ids(spark, frame):
    frame.createOrReplaceTempView("ds60_spark_011_events")
    return ids(
        spark.sql(
            "SELECT event_id FROM ds60_spark_011_events WHERE amount_cents > 10 ORDER BY event_id"
        )
    )
```

The temporary view provides a name for the same local DataFrame plan inside this SparkSession. SQL WHERE retains only true predicate rows and ORDER BY defines deterministic output. Both implementations can share a conceptual mistake, so each is checked against independent literal identities. This exercises Spark SQL syntax without opening PostgreSQL, JDBC or another service.

**Verification evidence:** Assert SQL IDs and selectedIds against [2,4] independently, then let the complete program stop its session in finally.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
