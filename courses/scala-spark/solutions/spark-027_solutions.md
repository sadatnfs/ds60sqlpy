# spark-027: Explained paired reference solutions

Read the [guide](../guides/spark-027.md) and attempt one language first. The [Scala reference](spark-027_solution.scala) and [PySpark reference](spark-027_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Transform without collapsing occurrences or unknowns

Keep rows whose amount is nonnegative or NULL, then return entity_id, segment, doubled=amount*2. Preserve duplicate occurrences and unknown values.

**Expected:** Seven rows, known total 130 and oneNULL doubled value. The negative entity 6 row is excluded.

```scala
def transform(source: DataFrame): DataFrame = {
  source.filter(col("amount") >= 0L || col("amount").isNull).select(col("entity_id"),col("segment"),(col("amount") * 2L).as("doubled"))
}
```

```python
def transform(source):
    return source.filter((F.col("amount")>=0)|F.col("amount").isNull()).select("entity_id","segment",(F.col("amount")*2).alias("doubled"))
```

The predicate makes unknown-amount retention a policy rather than an accident of three-valued logic. Arithmetic preservesNULL instead of manufacturing zero. No deduplication is requested, so identical source occurrences remain identical output occurrences. Aggregate checks provide a readable first diagnostic while the later bag oracle checks every occurrence.

**Verification evidence:** Assert population, total and unknown count, then compare with the literal golden relation in later tasks.

### Exercise 2: Define an ordered field/type contract

Return ordered(name, simple_type) pairs from the result schema. Compare with entity_id bigint, segment string, doubled bigint.

**Expected:** Exactly those three fields in that order. Casting entity_id to string changes the contract even when printed values look alike.

```scala
def schemaContract(frame: DataFrame): Seq[(String,String)] = {
  frame.schema.fields.toSeq.map(field => (field.name,field.dataType.simpleString))
}
```

```python
def schema_contract(frame):
    return [(field.name,field.dataType.simpleString()) for field in frame.schema.fields]
```

The contract is explicit about names, order and data types. This fixture compares nullability semantics through actual values rather than demanding an identical optimizer-derived nullable flag. A different product could include stricter nullability metadata, but it should state that requirement separately rather than confusing values with schema annotations.

**Verification evidence:** Assert the correct type list and a different list after the deliberate cast.

### Exercise 3: Compare schemas before duplicate-sensitive values

Reject a schema mismatch first, then require both exceptAll differences to be empty. Accept a repartitioned correct result and reject the deliberate string-ID result.

**Expected:** Correct result passes in different physical layouts; string-ID candidate fails with a named schema contract error.

```scala
def assertSameBag(actual: DataFrame, expected: DataFrame): Unit = {
  require(schemaContract(actual) == schemaContract(expected),"schema contract mismatch")
  require(actual.exceptAll(expected).count() == 0L && expected.exceptAll(actual).count() == 0L,"bag contract mismatch")
}
```

```python
def assert_same_bag(actual, expected):
    if schema_contract(actual) != schema_contract(expected):
        raise ValueError("schema contract mismatch")
    if actual.exceptAll(expected).count() or expected.exceptAll(actual).count():
        raise ValueError("bag contract mismatch")
```

Checking schema first prevents a set operation from silently finding a common coerced type. The two directional bag differences preserve multiplicity and NULL equality semantics while ignoring arrival order. A repartitioned correct relation therefore passes, and a visually similar but type-incompatible relation fails for the right reason.

**Verification evidence:** Assert acceptance for golden/repartitioned values and explicit schema rejection before a coercing bag comparison.

### Exercise 4: Register, materialize, reuse and release one cached relation

Persist the supplied transformed relation with MEMORY_AND_DISK, materialize via count, reuse for a total and inspect a filtered consumer plan. Unpersist with blocking cleanup in finally.

**Expected:** Count 7, total 130, an InMemoryTableScan reuse marker, and no registered storage level after return.

```scala
def cachedSummary(frame: DataFrame): (Long,Long,String) = {
  frame.persist(StorageLevel.MEMORY_AND_DISK)
  try {
   require(frame.storageLevel != StorageLevel.NONE,"cache not registered")
   val rows = frame.count()
   val total = frame.agg(sum("doubled")).first().getLong(0)
   val plan = frame.filter(col("doubled") >= 0L).queryExecution.executedPlan.toString
   (rows,total,plan)
  } finally frame.unpersist(blocking=true)
}
```

```python
def cached_summary(frame):
    frame.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        assert frame.storageLevel != StorageLevel.NONE
        rows = frame.count()
        total = frame.agg(F.sum("doubled")).first()[0]
        plan = frame.filter(F.col("doubled")>=0)._jdf.queryExecution().executedPlan().toString()
        return rows,total,plan
    finally:
        frame.unpersist(blocking=True)
```

The sequence distinguishes marking a relation for persistence from computing and reusing it. The captured plan belongs to a consumer while the cache is active. Finally-based blocking unpersist makes cleanup observable after the helper returns. This teaches a lifecycle contract without asserting that caching a seven-row relation is faster or representative of production economics.

**Verification evidence:** Assert result values, cache-scan evidence and post-returnStorageLevel.NONE. Do not use a timing threshold.

### Exercise 5: Release persistence when a consumer fails

Persist and materialize the relation, then raise an injected failure before a later consumer. Unpersist in finally and verify the original error reaches the caller.

**Expected:** The injected_after_materialize error is observed and storage level isNONE afterward. Correct uncached output still passes the golden oracle.

```scala
def failingReuse(frame: DataFrame): Unit = {
  frame.persist(StorageLevel.MEMORY_AND_DISK)
  try {
   frame.count()
   throw new IllegalStateException("injected_after_materialize")
  } finally frame.unpersist(blocking=true)
}
```

```python
def failing_reuse(frame):
    frame.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        frame.count()
        raise RuntimeError("injected_after_materialize")
    finally:
        frame.unpersist(blocking=True)
```

The deliberate failure tests the resource boundary rather than only a happy-path value. Recomputing the correct relation afterward shows that cleanup did not corrupt source data or require a hidden cached result. Persistence remains an optimization inside this application; it is not durable state that the next run must inherit.

**Verification evidence:** Assert the named failure, post-failure release and full golden equality on a subsequent computation.

### Exercise 6: Demonstrate why set equality misses duplicate loss

Return directional exceptAll row counts after schema validation. Compare transformed.distinct with golden and require the golden validator to reject it.

**Expected:** Distinct has 5 rows; unexpected occurrences 0 and missing expected occurrences 2. The bag validator raises a named bag contract mismatch.

```scala
def differenceCounts(actual: DataFrame, expected: DataFrame): (Long,Long) = {
  require(schemaContract(actual) == schemaContract(expected),"schema contract mismatch")
  (actual.exceptAll(expected).count(),expected.exceptAll(actual).count())
}
```

```python
def difference_counts(actual, expected):
    if schema_contract(actual) != schema_contract(expected):
        raise ValueError("schema contract mismatch")
    return actual.exceptAll(expected).count(),expected.exceptAll(actual).count()
```

The negative control proves that the oracle protects occurrence multiplicity rather than only value membership. There are no new distinct values, so a set comparator would miss the error. Directional bag counts explain the failure as two missing occurrences, which is more useful than a generic mismatch message when diagnosing an accidentalDISTINCT or deduplication step.

**Verification evidence:** Assert(0,2), count 5 and the explicit negative-control rejection.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
