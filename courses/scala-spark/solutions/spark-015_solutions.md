# spark-015: Explained paired reference solutions

Read the [guide](../guides/spark-015.md) and attempt one language first. The [Scala reference](spark-015_solution.scala) and [PySpark reference](spark-015_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Add an explicit tolerant parse column

Return all source columns plus parsed_amount from try_cast(trim(amount_text) AS BIGINT). Preserve eight rows and distinguish this nullable parse result from a final validity decision.

**Expected:** Ordered parsed values are 100,0,25, NULL, NULL, NULL,-5,50. The output parsed type is bigint.

```scala
def withParsed(frame: DataFrame): DataFrame = {
  frame.withColumn("parsed_amount", expr("try_cast(trim(amount_text) AS BIGINT)"))
}
```

```python
def with_parsed(frame):
    return frame.withColumn("parsed_amount", F.expr("try_cast(trim(amount_text) AS BIGINT)"))
```

try_cast makes conversion failure a data value instead of an exception, which is useful only if the failed rows remain identifiable. The original amount_text is retained alongside the parsed Long. The complete pair list catches whitespace, zero, missingness, malformed text, overflow and signed-value behavior separately. A count-only check would not establish any of those semantics.

**Verification evidence:** Compare all eight(event_id, parsed_amount) pairs and the field type with literals.

### Exercise 2: Classify missing versus rejected tokens

Add parse_status with missing for source NULL, rejected for a nonnull source that parsed to NULL, and valid otherwise. Keep all original rows and parsed values.

**Expected:** IDs 1,2,3,7,8 are valid, ID 4 missing, and IDs 5,6 rejected. Counts are 5,1,2 and sum to 8.

```scala
def parseLedger(frame: DataFrame): DataFrame = {
  withParsed(frame).withColumn(
    "parse_status",
    when(col("amount_text").isNull, lit("missing"))
      .when(col("parsed_amount").isNull, lit("rejected"))
      .otherwise(lit("valid"))
  )
}
```

```python
def parse_ledger(frame):
    return with_parsed(frame).withColumn(
        "parse_status",
        F.when(F.col("amount_text").isNull(), F.lit("missing"))
        .when(F.col("parsed_amount").isNull(), F.lit("rejected"))
        .otherwise(F.lit("valid")),
    )
```

The branch order preserves source provenance. If parsed NULL were checked first, the allowed missing record would be mislabeled as malformed. Every input gets exactly one status, so the ledger can reconcile accepted and rejected populations. This is an explicit source policy; another pipeline may reject missing amounts too, but it must state that different decision.

**Verification evidence:** Assert the ordered status list and the exact two rejected IDs.

### Exercise 3: Project the six parse-accepted events

Retain valid and missing statuses, then return event_id and parsed_amount aliased as amount_cents. Reject only malformed/overflowing nonnull tokens at this stage.

**Expected:** IDs[1,2,3,4,7,8] remain with amounts[100,0,25, NULL,-5,50]. There are 6 rows,5 known values and total 170.

```scala
def acceptedProjection(frame: DataFrame): DataFrame = {
  parseLedger(frame)
    .filter(col("parse_status") =!= lit("rejected"))
    .select(col("event_id"), col("parsed_amount").as("amount_cents"))
}
```

```python
def accepted_projection(frame):
    return (
        parse_ledger(frame)
        .filter(F.col("parse_status") != F.lit("rejected"))
        .select("event_id", F.col("parsed_amount").alias("amount_cents"))
    )
```

The projection changes representation while retaining event identity and allowed missingness. Negative five remains because this stage answers conversion validity, not the later nonnegative-domain question. Separate row and known-value counts prevent a NULL-to-zero replacement from hiding in an unchanged total. The literal rows supply an independent oracle for both language implementations.

**Verification evidence:** Assert the exact rows and independent count/known/sum metrics.

### Exercise 4: Express the same parse contract in SQL

Register the raw frame as a session-local view and produce the same six event_id, amount_cents rows using a SQL parse CTE and explicit missing-or-success filter. Compare with literals rather than only with the DataFrame result.

**Expected:** The SQL ordered rows are exactly the six rows from Exercise 3, including the NULL amount and signed-5.

```scala
def sqlProjection(spark: SparkSession, frame: DataFrame): DataFrame = {
  frame.createOrReplaceTempView("ds60_spark_015_raw")
  spark.sql(
    "WITH parsed AS (SELECT event_id,amount_text,try_cast(trim(amount_text) AS BIGINT) AS amount_cents FROM ds60_spark_015_raw) SELECT event_id,amount_cents FROM parsed WHERE amount_text IS NULL OR amount_cents IS NOT NULL"
  )
}
```

```python
def sql_projection(spark, frame):
    frame.createOrReplaceTempView("ds60_spark_015_raw")
    return spark.sql(
        "WITH parsed AS (SELECT event_id,amount_text,try_cast(trim(amount_text) AS BIGINT) AS amount_cents FROM ds60_spark_015_raw) SELECT event_id,amount_cents FROM parsed WHERE amount_text IS NULL OR amount_cents IS NOT NULL"
    )
```

The CTE names the intermediate parsed relation and retains the original token for the acceptance predicate. OR combines the allowed source-missing case with successful conversion. Dropping amount_text before filtering would make those cases indistinguishable. Final ordering is applied by the bounded canonical helper, so SQL planning order is not mistaken for output order.

**Verification evidence:** Assert the SQL result against the full literal row list and separately compare the DataFrame path to that list.

### Exercise 5: Observe strict ANSI failure at evaluation

Return a strict trimmed BIGINT cast projection. Evaluate a valid subset successfully, then intentionally evaluate the bad token at ID 5 under ANSI mode and require a CAST_INVALID_INPUT diagnostic. Do not count an unrelated exception as success.

**Expected:** The valid subset has the same six rows. ID 5 fails when collected, and the reference records the expected failure code before continuing.

```scala
def strictProjection(frame: DataFrame): DataFrame = {
  frame.select(col("event_id"), trim(col("amount_text")).cast(LongType).as("amount_cents"))
}
```

```python
def strict_projection(frame):
    return frame.select("event_id", F.trim("amount_text").cast("bigint").alias("amount_cents"))
```

The valid subset demonstrates that strict casting is not blanket rejection. The malformed token then triggers the declared ANSI failure at an action site. Checking the diagnostic code prevents a disconnected worker or unrelated error from being mislabeled as a successful negative test. The expected failure is part of the reference evidence, while an unhandled or differently classified failure remains a failed run.

**Verification evidence:** Assert ANSI readback true, valid-row results, and a caught diagnostic containing CAST_INVALID_INPUT.

### Exercise 6: Apply a separate nonnegative domain policy

From parse-accepted rows, retain unknown amounts and known nonnegative amounts. Return event_id, amount_cents and report the separate negative-domain rejection at ID 7 in the checks.

**Expected:** Final IDs[1,2,3,4,8] have 5 rows,4 known values, total 175. The full source reconciles as 5 final accepted+2 parse rejected+1 negative-domain rejected.

```scala
def nonnegativeAmounts(frame: DataFrame): DataFrame = {
  acceptedProjection(frame).filter(col("amount_cents").isNull || (col("amount_cents") >= lit(0L)))
}
```

```python
def nonnegative_amounts(frame):
    return accepted_projection(frame).filter(
        F.col("amount_cents").isNull() | (F.col("amount_cents") >= F.lit(0))
    )
```

The domain rule is applied after conversion and retains its own rejected population. A syntactically valid negative adjustment can therefore be reported as a domain decision rather than a parse error. Keeping source-missing amounts is also explicit. The conservation equation accounts for all eight inputs across the two validation stages, preventing a successful total from hiding unexplained row loss.

**Verification evidence:** Assert final rows/metrics, negative ID 7 and the 8-row conservation equation.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
