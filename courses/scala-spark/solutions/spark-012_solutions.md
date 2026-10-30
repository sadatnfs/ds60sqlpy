# spark-012: Explained paired reference solutions

Read the [guide](../guides/spark-012.md) and attempt one language first. The [Scala reference](spark-012_solution.scala) and [PySpark reference](spark-012_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Inspect the complete schema contract

Return ordered field triples(name, simpleString, nullable) for a DataFrame. Check the fixture rather than inferring correctness from a printed schema alone.

**Expected:** The triples are(event_id, bigint, false),(team, string, true),(amount_cents, bigint, true).

```scala
def schemaFields(frame: DataFrame): Seq[(String, String, Boolean)] = {
  frame.schema.fields.map(field => (field.name, field.dataType.simpleString, field.nullable)).toSeq
}
```

```python
def schema_fields(frame):
    return [
        (field.name, field.dataType.simpleString(), field.nullable) for field in frame.schema.fields
    ]
```

Field type and nullability are independent parts of the declared schema. A sample with only small integers does not justify inferring Int when the contract requires Long, and a missing amount must not force an approximate numeric representation. Comparing the complete field list also catches accidental column reordering or renamed fields before downstream positional Row access can misinterpret them.

**Verification evidence:** Compare the complete triples with literals in both languages, including all nullability flags.

### Exercise 2: Keep a transformation separate from its action

Return a DataFrame plan selecting team A without collecting or counting inside the function. At the call site, request a count and verify IDs 1 and 3. Preserve raw.

**Expected:** The returned frame contains two rows when evaluated; raw still has four. The function body contains only a filter transformation.

```scala
def teamA(frame: DataFrame): DataFrame = {
  frame.filter(col("team") === lit("A"))
}
```

```python
def team_a(frame):
    return frame.filter(F.col("team") == F.lit("A"))
```

The source function describes the relation while the caller controls when results are requested. This makes evaluation boundaries visible and avoids a hidden collect inside a reusable transformation. The raw count check confirms immutable-plan behavior for the fixture. It is not a timing-based claim that every possible planning operation is free of metadata or engine work.

**Verification evidence:** Assert returned count 2, ordered IDs[1,3] and raw count 4 at explicit action sites.

### Exercise 3: Bound the driver result and detect overflow of the budget

Return ordered event IDs while collecting at most limit+1 rows, with 0<=limit<=20. Reject a result larger than limit and invalid limits. Empty data with limit 0 is valid. Do not collect the full frame before checking length.

**Expected:** The four-row fixture passes limit 4 and rejects limit 3. An empty filter with limit 0 returns empty; limit 21 is rejected before collection.

```scala
def boundedIds(frame: DataFrame, limit: Int): Seq[Long] = {
  require(limit >= 0 && limit <= 20, "driver ID budget outside 0..20")
  val rows =
    frame.select("event_id").orderBy("event_id").limit(limit + 1).collect().map(_.getLong(0)).toSeq
  require(rows.size <= limit, "driver ID result exceeds budget")
  rows
}
```

```python
def bounded_ids(frame, limit):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= 20:
        raise ValueError("driver ID budget outside 0..20")
    rows = [
        row.event_id
        for row in frame.select("event_id").orderBy("event_id").limit(limit + 1).collect()
    ]
    if len(rows) > limit:
        raise ValueError("driver ID result exceeds budget")
    return rows
```

Checking after an unbounded collect would be too late to protect driver memory. Limiting the action to one row beyond the budget supplies a concrete rejection witness. The operation bounds returned payload, not every byte of source scanning or sorting work. The explicit small fixture and fixed worker budget provide the broader execution bound for this lesson.

**Verification evidence:** Assert exact IDs, catch the oversize and invalid-budget errors, and inspect the bounded limit before the action.

### Exercise 4: Retain observed zero while isolating unknown amounts

Return rows with nonnull amount_cents, keeping all columns and identities. Do not replace NULL with zero or filter out observed zero.

**Expected:** IDs 1,3,4 remain with amounts 0,25,40, total 65. Raw still has one NULL amount at ID 2.

```scala
def observedRows(frame: DataFrame): DataFrame = {
  frame.filter(col("amount_cents").isNotNull)
}
```

```python
def observed_rows(frame):
    return frame.filter(F.col("amount_cents").isNotNull())
```

The observation filter answers which amounts are known, not which are positive. Keeping zero preserves an event and its denominator contribution. The sum alone would not expose zero loss, so the exact ID list is also checked. Raw remains the full relation with its unknown value available for separate data-quality reporting.

**Verification evidence:** Assert exact IDs and sum 65, and independently count the unchanged raw NULL row.

### Exercise 5: Canonicalize content across physical repartitioning

Return ordered triples(event_id, optional team, optional amount) for this bounded fixture. Compare raw, repartition(1) and repartition(3) against the same literal content, not raw collect order.

**Expected:** Every version yields (1, A,0),(2, B, NULL),(3, A,25),(4, B,40). Physical placement does not change identity, NULL state or value.

```scala
def canonical(frame: DataFrame): Seq[(Long, Option[String], Option[Long])] = {
  frame.select("event_id", "team", "amount_cents").orderBy("event_id").collect().toSeq.map { row =>
    (
      row.getLong(0),
      if (row.isNullAt(1)) None else Some(row.getString(1)),
      if (row.isNullAt(2)) None else Some(row.getLong(2))
    )
  }
}
```

```python
def canonical(frame):
    return [
        tuple(row)
        for row in frame.select("event_id", "team", "amount_cents").orderBy("event_id").collect()
    ]
```

Repartitioning changes physical organization and can change arrival order, so raw collection order is not the invariant. The unique event ID supplies a complete canonical order for this tiny result. Scala checks NULL before typed extraction; Python receives None through the Row interface. This establishes logical parity across the tested local partition changes without claiming any performance improvement.

**Verification evidence:** Assert all three canonical outputs and keep the final event_id ordering explicit.

### Exercise 6: Read back the actual local session contract

Return master, timezone, shuffle-partition, ANSI, AQE, UI, driver-binding and Spark-version settings from the active session. Compare them with this prepared profile and rely on finally for owned stop. Do not substitute a hardcoded target string for version readback.

**Expected:** Master local[2], UTC, two shuffle partitions, ANSI true, AQE false, UI false, both driver addresses 127.0.0.1, and Spark version 4.0.1.

```scala
def settings(spark: SparkSession): Map[String, String] = {
  Map(
    "master" -> spark.sparkContext.master,
    "timezone" -> spark.conf.get("spark.sql.session.timeZone"),
    "shuffle" -> spark.conf.get("spark.sql.shuffle.partitions"),
    "ansi" -> spark.conf.get("spark.sql.ansi.enabled"),
    "adaptive" -> spark.conf.get("spark.sql.adaptive.enabled"),
    "ui" -> spark.sparkContext.getConf.get("spark.ui.enabled"),
    "driver_host" -> spark.sparkContext.getConf.get("spark.driver.host"),
    "driver_bind" -> spark.sparkContext.getConf.get("spark.driver.bindAddress"),
    "spark_version" -> spark.version
  )
}
```

```python
def settings(spark):
    context = spark.sparkContext.getConf()
    return {
        "master": spark.sparkContext.master,
        "timezone": spark.conf.get("spark.sql.session.timeZone"),
        "shuffle": spark.conf.get("spark.sql.shuffle.partitions"),
        "ansi": spark.conf.get("spark.sql.ansi.enabled"),
        "adaptive": spark.conf.get("spark.sql.adaptive.enabled"),
        "ui": context.get("spark.ui.enabled"),
        "driver_host": context.get("spark.driver.host"),
        "driver_bind": context.get("spark.driver.bindAddress"),
        "spark_version": spark.version,
    }
```

Actual readback can detect an unexpected reused or differently configured session, while source builder text only states intent. The version assertion deliberately targets the prepared worker rather than the older design proposal. The finally block stops this owned session after checks or failures; process and descendant cleanup remain separately observed worker responsibilities. Matching settings does not replace any of the row and schema assertions.

**Verification evidence:** Assert the complete settings map; record actual version output and distinguish it from worker cleanup evidence.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
