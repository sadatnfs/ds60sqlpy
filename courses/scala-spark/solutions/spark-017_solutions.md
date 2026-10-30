# spark-017: Explained paired reference solutions

Read the [guide](../guides/spark-017.md) and attempt one language first. The [Scala reference](spark-017_solution.scala) and [PySpark reference](spark-017_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Parse once and retain rejection evidence

Parse raw with the explicit payload schema and PERMISSIVE mode, then add reason using precedence missing_payload, malformed_json, missing_parent, accepted. Preserve source_id and raw.

**Expected:** Sources 1-4 accepted;5 malformed_json;6 missing_parent;7 missing_payload. No source disappears and accepted count is 4.

```scala
def parseRecords(raw: DataFrame): DataFrame = {
  raw
    .withColumn(
      "doc",
      from_json(
        col("raw"),
        payloadSchema,
        Map("mode" -> "PERMISSIVE", "columnNameOfCorruptRecord" -> "_corrupt_record")
      )
    )
    .withColumn(
      "reason",
      when(col("raw").isNull, lit("missing_payload"))
        .when(col("doc._corrupt_record").isNotNull, lit("malformed_json"))
        .when(col("doc.parent_id").isNull, lit("missing_parent"))
        .otherwise(lit("accepted"))
    )
}
```

```python
def parse_records(raw):
    return raw.withColumn(
        "doc",
        F.from_json(
            "raw",
            payload_schema,
            {"mode": "PERMISSIVE", "columnNameOfCorruptRecord": "_corrupt_record"},
        ),
    ).withColumn(
        "reason",
        F.when(F.col("raw").isNull(), "missing_payload")
        .when(F.col("doc._corrupt_record").isNotNull(), "malformed_json")
        .when(F.col("doc.parent_id").isNull(), "missing_parent")
        .otherwise("accepted"),
    )
```

The original source identity and payload remain available for diagnosis. PERMISSIVE parsing is not treated as an acceptance decision: the domain check is separate and ordered after malformed-input evidence. This prevents a malformed record from being mislabeled merely as a missing business key and prevents a missing payload from disappearing into an ordinary null field.

**Verification evidence:** Assert all seven ordered source/reason rows and reconcile accepted 4 plus rejected 3 with input 7.

### Exercise 2: Record collection state before changing grain

For accepted records return source_id, parent_id, items, array_state, with array_state unknown, empty or populated. Keep arrays typed and preserve the two repeated SKU occurrences.

**Expected:** Parent 10 populated,20 empty,30 unknown,40 populated. Parent 10 has size 2; parent 40 size 1.

```scala
def parentLedger(parsed: DataFrame): DataFrame = {
  parsed
    .filter(col("reason") === "accepted")
    .select(col("source_id"), col("doc.parent_id").as("parent_id"), col("doc.items").as("items"))
    .withColumn(
      "array_state",
      when(col("items").isNull, "unknown")
        .when(size(col("items")) === 0, "empty")
        .otherwise("populated")
    )
}
```

```python
def parent_ledger(parsed):
    return (
        parsed.filter(F.col("reason") == "accepted")
        .select(
            "source_id",
            F.col("doc.parent_id").alias("parent_id"),
            F.col("doc.items").alias("items"),
        )
        .withColumn(
            "array_state",
            F.when(F.col("items").isNull(), "unknown")
            .when(F.size("items") == 0, "empty")
            .otherwise("populated"),
        )
    )
```

The ledger is still one row per accepted parent record. Capturing array_state here preserves information that the outer placeholder would otherwise obscure. The array itself remains a typed value, so later generators can retain positions and nested fields without reparsing the JSON or guessing a child schema from a sample.

**Verification evidence:** Assert the four parent/state rows and item lengths independently of any later explode output.

### Exercise 3: Flatten observed child occurrences

Use posexplode to return parent_id, position, sku, qty for actual items. Order by parent_id and position, and retain repeated SKU a.

**Expected:** Rows(10,0, a,2),(10,1, a,3),(40,0, b, NULL). Exactly 3 children; parents 20 and 30 produce none.

```scala
def children(parents: DataFrame): DataFrame = {
  parents
    .select(col("parent_id"), posexplode(col("items")).as(Seq("position", "item")))
    .select(col("parent_id"), col("position"), col("item.sku").as("sku"), col("item.qty").as("qty"))
}
```

```python
def children(parents):
    return parents.select("parent_id", F.posexplode("items").alias("position", "item")).select(
        "parent_id", "position", F.col("item.sku").alias("sku"), F.col("item.qty").alias("qty")
    )
```

The three rows represent actual array elements. Parent 40 remains an observed child even though qty is unknown. Duplicate values for parent 10 are preserved because their positions differ. The bounded literal comparison checks identities and values together; a count-only test would miss an accidental DISTINCT that later happened to be compensated by another duplicated row.

**Verification evidence:** Assert the entire three-row occurrence list and unique(parent_id, position) count 3.

### Exercise 4: Preserve parents without inventing observed children

Use posexplode_outer, preserving parent_id and array_state along with position, sku, qty. Keep null placeholders for empty and unknown arrays.

**Expected:** Five rows: the three observed children plus(20, empty, NULL, NULL, NULL) and (30, unknown, NULL, NULL, NULL).

```scala
def outerChildren(parents: DataFrame): DataFrame = {
  parents
    .select(
      col("parent_id"),
      col("array_state"),
      posexplode_outer(col("items")).as(Seq("position", "item"))
    )
    .select(
      col("parent_id"),
      col("array_state"),
      col("position"),
      col("item.sku").as("sku"),
      col("item.qty").as("qty")
    )
}
```

```python
def outer_children(parents):
    return parents.select(
        "parent_id", "array_state", F.posexplode_outer("items").alias("position", "item")
    ).select(
        "parent_id",
        "array_state",
        "position",
        F.col("item.sku").alias("sku"),
        F.col("item.qty").alias("qty"),
    )
```

Outer generation preserves the reporting population but changes the meaning of a raw row count. The position distinguishes synthetic placeholders from actual elements; checking qty alone would incorrectly discard parent 40. Preserved array_state distinguishes known emptiness from unknown membership, allowing a downstream policy to report them separately.

**Verification evidence:** Assert five rows, four distinct parents and exactly three nonnull generated positions.

### Exercise 5: Reconcile child counts and nullable measures

Aggregate the outer relation to parent_id, array_state, child_count, known_qty_count, total_qty. Count positions for children and preserve SUM NULL when there are no known quantities.

**Expected:** Parent 10:(2,2,5);20:(0,0, NULL);30:(0,0, NULL);40:(1,0, NULL). Empty and unknown collection states remain visible.

```scala
def summarizeChildren(outer: DataFrame): DataFrame = {
  outer
    .groupBy("parent_id", "array_state")
    .agg(
      count("position").as("child_count"),
      count("qty").as("known_qty_count"),
      sum("qty").as("total_qty")
    )
}
```

```python
def summarize_children(outer):
    return outer.groupBy("parent_id", "array_state").agg(
        F.count("position").alias("child_count"),
        F.count("qty").alias("known_qty_count"),
        F.sum("qty").alias("total_qty"),
    )
```

These measures answer separate questions: how many children were observed, how many quantities were known, and what their known sum is. A null total is retained when no quantity is known. An application could deliberately define an empty collection total as zero, but that rule would use array_state and must not also turn an unknown collection or all-missing quantity list into an observed zero.

**Verification evidence:** Assert each parent count tuple and that summed child_count is 3 while known_qty_count is 2.

### Exercise 6: Choose Cartesian or positional array semantics

For one parent with SKUs[a, b] and channels[web, shop, api], return both independent exploded pairs and arrays_zip positional rows. Explain the relationship required for each interpretation.

**Expected:** Independent generators produce 6 pairs; zip produces(a, web),(b, shop),(NULL, api), three rows.

```scala
def arrayRelationships(spark: SparkSession): (DataFrame, DataFrame) = {
  val source = spark.sql("SELECT array('a','b') AS skus, array('web','shop','api') AS channels")
  val cross = source
    .select(explode(col("skus")).as("sku"), col("channels"))
    .select(col("sku"), explode(col("channels")).as("channel"))
  val zipped = source
    .select(posexplode(arrays_zip(col("skus"), col("channels"))).as(Seq("position", "pair")))
    .select(col("position"), col("pair.skus").as("sku"), col("pair.channels").as("channel"))
  (cross, zipped)
}
```

```python
def array_relationships(spark):
    source = spark.sql("SELECT array('a','b') AS skus, array('web','shop','api') AS channels")
    cross = source.select(F.explode("skus").alias("sku"), "channels").select(
        "sku", F.explode("channels").alias("channel")
    )
    zipped = source.select(
        F.posexplode(F.arrays_zip("skus", "channels")).alias("position", "pair")
    ).select("position", F.col("pair.skus").alias("sku"), F.col("pair.channels").alias("channel"))
    return cross, zipped
```

The six-row relation models every independent pairing, while the three-row relation models aligned positions. Padding preserves the third channel without inventing a SKU. Zipping is not a generic cure for explosion and multiplying arrays is not automatically a bug. The data contract must state whether positions correspond before either implementation can be called correct.

**Verification evidence:** Assert the complete Cartesian pair set and all three ordered zipped rows including the paddedNULL.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
