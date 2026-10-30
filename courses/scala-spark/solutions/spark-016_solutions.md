# spark-016: Explained paired reference solutions

Read the [guide](../guides/spark-016.md) and attempt one language first. The [Scala reference](spark-016_solution.scala) and [PySpark reference](spark-016_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Build a multiplicity ledger before joining facts

Return key, fact_rows, dimension_rows, predicted_inner for the union of key buckets. Merge NULL diagnostic buckets explicitly, but predict zero ordinary-equality pairs for NULL. Order keys with NULL last.

**Expected:** A:(2,3,6), B:(1,1,1), C:(1,0,0), D:(1,0,0), E:(0,1,0), NULL:(1,1,0). Predicted inner rows sum to 7.

```scala
def multiplicity(facts: DataFrame, dimension: DataFrame): DataFrame = {
  val f = facts.groupBy("key").agg(count(lit(1)).as("fact_rows")).as("f")
  val d = dimension.groupBy("key").agg(count(lit(1)).as("dimension_rows")).as("d")
  val joined = f
    .join(d, col("f.key") <=> col("d.key"), "full")
    .select(
      coalesce(col("f.key"), col("d.key")).as("key"),
      coalesce(col("fact_rows"), lit(0L)).as("fact_rows"),
      coalesce(col("dimension_rows"), lit(0L)).as("dimension_rows")
    )
  joined.withColumn(
    "predicted_inner",
    when(col("key").isNull, lit(0L)).otherwise(col("fact_rows") * col("dimension_rows"))
  )
}
```

```python
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
```

Preaggregation makes key multiplicity explicit before any fact measure is repeated. The full join retains keys missing from either side. NULL-safe equality is used only to consolidate diagnostic buckets; the predicted ordinary-equality count still assigns zero to NULL. This separation prevents a convenient diagnostic implementation from silently changing the business join policy.

**Verification evidence:** Assert the full ledger and its summed predicted count, including unmatched right-only E and the NULL bucket.

### Exercise 2: Verify equality pairs and quantify fanout

Return fact_id, dimension_row, amount_cents from an ordinary inner equality join. Compare both DataFrame and SQL pair identities with the seven literal expected pairs.

**Expected:** Facts 1 and 2 each match dimension rows 101,102,103; fact 3 matches 104. There are 7 pairs and the repeated joined amount totals 120, while matched fact amounts total 60.

```scala
def equalityJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts
    .as("f")
    .join(dimension.as("d"), col("f.key") === col("d.key"), "inner")
    .select(col("f.fact_id"), col("d.dimension_row"), col("f.amount_cents"))
}
```

```python
def equality_join(facts, dimension):
    return (
        facts.alias("f")
        .join(dimension.alias("d"), F.col("f.key") == F.col("d.key"), "inner")
        .select("f.fact_id", "d.dimension_row", "f.amount_cents")
    )
```

The output identity is a fact/dimension pair, not a unique fact. Repeated fact amounts are therefore expected in this relation but must not be mistaken for independent revenue. Both APIs and SQL are checked against literal pairs, which detects wrong matches even if their total row count happens to agree. Physical join strategy does not alter these relational semantics.

**Verification evidence:** Assert every pair, count 7 and pair-grain sum 120; compare a SQL join to the same pair list.

### Exercise 3: Count actual matches in a left join

Return fact_id, dimension_row from an ordinary left equality join. Preserve unmatched facts with a NULL right identity and inspect rows ordered by fact_id, dimension_row.

**Expected:** There are 10 output rows but 7 nonnull dimension_row values. Facts 4,5,6 each have one NULL-extended row; all six fact IDs remain represented.

```scala
def leftJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts
    .as("f")
    .join(dimension.as("d"), col("f.key") === col("d.key"), "left")
    .select(col("f.fact_id"), col("d.dimension_row"))
}
```

```python
def left_join(facts, dimension):
    return (
        facts.alias("f")
        .join(dimension.alias("d"), F.col("f.key") == F.col("d.key"), "left")
        .select("f.fact_id", "d.dimension_row")
    )
```

The NULL-extended row preserves an unmatched fact but does not represent a real dimension record. Counting the nonnullable dimension identity distinguishes that placeholder from a match. The NULL-key fact remains unmatched under ordinary equality even though a NULL dimension key exists. The count-distinct fact check verifies population retention separately from the ten-row pair result.

**Verification evidence:** Assert the complete ordered pair/NULL list and distinguish COUNT(*)10 from COUNT(dimension_row)7.

### Exercise 4: Use semi and anti joins for membership

Return a pair of DataFrames containing matched and unmatched facts under ordinary equality, using left_semi and left_anti. Preserve fact rows without right-side fanout.

**Expected:** Semi IDs are[1,2,3], anti IDs[4,5,6]. Key A contributes two semi rows despite three dimension matches. Their bags reconcile to all six facts.

```scala
def membership(facts: DataFrame, dimension: DataFrame): (DataFrame, DataFrame) = {
  (facts.join(dimension, Seq("key"), "left_semi"), facts.join(dimension, Seq("key"), "left_anti"))
}
```

```python
def membership(facts, dimension):
    return facts.join(dimension, on="key", how="left_semi"), facts.join(
        dimension, on="key", how="left_anti"
    )
```

A semi join asks whether a match exists and therefore does not need to emit every matching right row. The anti join is its complementary membership relation under the same equality rule. Using these operators expresses the desired grain directly and avoids an inner-join-plus-distinct repair that could erase legitimate duplicate left occurrences.

**Verification evidence:** Assert both exact ID lists and their combined count 6; do not use distinct to repair an inner join.

### Exercise 5: Make NULL-safe matching an explicit alternative

Return fact_id, dimension_row from an inner join using NULL-safe key equality. Compare with ordinary equality and explain why the extra pair is a policy change.

**Expected:** The ordinary seven pairs plus(5,105) produce eight pairs. No C or D match is invented.

```scala
def nullSafeJoin(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts
    .as("f")
    .join(dimension.as("d"), col("f.key") <=> col("d.key"), "inner")
    .select(col("f.fact_id"), col("d.dimension_row"))
}
```

```python
def null_safe_join(facts, dimension):
    return (
        facts.alias("f")
        .join(dimension.alias("d"), F.col("f.key").eqNullSafe(F.col("d.key")), "inner")
        .select("f.fact_id", "d.dimension_row")
    )
```

The extra pair follows directly from treating two NULL values as equal. This can be appropriate for a meaningful missing-value category, but it is usually not evidence that two unknown entity identifiers belong together. Multiple NULL rows on either side would also multiply. The literal pair difference makes the changed semantic policy visible rather than hiding it inside an optimization rewrite.

**Verification evidence:** Assert all eight ordered pairs and isolate the extra NULL-key pair.

### Exercise 6: Gate enrichment on a reviewed unique dimension

Reject a dimension unless key is nonnull and unique, then left-enrich facts with label while retaining fact_id and amount_cents. The supplied reviewed dimension rows 103,104,106 are the explicit accepted fixture; do not invent an arbitrary duplicate winner.

**Expected:** The raw dimension fails. The reviewed subset yields six facts, total 210, and labels alpha 3, alpha 3, beta, NULL, NULL, NULL for IDs 1..6.

```scala
def safeEnrichment(facts: DataFrame, dimension: DataFrame): DataFrame = {
  val keys = dimension.agg(count(lit(1)), countDistinct(col("key"))).first()
  require(keys.getLong(0) == keys.getLong(1), "dimension keys must be nonnull and unique")
  facts
    .join(dimension.select("key", "label"), Seq("key"), "left")
    .select("fact_id", "amount_cents", "label")
}
```

```python
def safe_enrichment(facts, dimension):
    keys = dimension.agg(F.count(F.lit(1)), F.countDistinct("key")).first()
    if keys[0] != keys[1]:
        raise ValueError("dimension keys must be nonnull and unique")
    return facts.join(dimension.select("key", "label"), on="key", how="left").select(
        "fact_id", "amount_cents", "label"
    )
```

COUNT DISTINCT ignores NULL and collapses duplicates, so equality with total row count establishes the declared nonnull unique-key condition. The reviewed subset is supplied as a business decision for this fixture, not inferred from ingestion order. Once the dimension satisfies that contract, the left enrichment preserves one row per fact and its additive amount. Unmatched labels remain visible for a separate coverage policy.

**Verification evidence:** Catch raw-dimension rejection, assert every enriched row and reconcile count 6, total 210.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
