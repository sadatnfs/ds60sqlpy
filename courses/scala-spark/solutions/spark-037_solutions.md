# spark-037: Explained paired reference solutions

Read the [guide](../guides/spark-037.md) and attempt one language first. The [Scala reference](spark-037_solution.scala) and [PySpark reference](spark-037_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations;matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Establish a finite restart baseline

Run the restart scenario with two supplied records and retain progress plus exact sink values.

**Expected:** 2 input rows and bag 1:100,2:200.

```scala
def baseline(spark: SparkSession, paths: (Path, Path, Path)): RunReceipt = {
  runScenario(spark, paths._1, paths._2, paths._3, "restart")
}
```

```python
def baseline(spark, paths):
    return run_scenario(spark, *paths, "restart")
```

The fixture exists before the finite query starts, so there is no timing guess about arrival. Completion must come from the query API. The literal bag detects wrong values or missing rows that a progress count alone could not catch.

**Verification evidence:** Assert the literal bag, input count 2 and inactive query.

### Exercise 2: Prove no-input recovery without a sleep

Restart the compatible baseline with its existing checkpoint and no new file.

**Expected:** Same query ID, new run ID, zero new rows and unchanged sink.

```scala
def restartEmpty(spark: SparkSession, paths: (Path, Path, Path)): RunReceipt = {
  runScenario(spark, paths._1, paths._2, paths._3, "restart")
}
```

```python
def restart_empty(spark, paths):
    return run_scenario(spark, *paths, "restart")
```

The source checkpoint is retained during this case. A new checkpoint would answer a different replay question. The test accepts the documented no-work shape and still verifies that the old committed product was not duplicated.

**Verification evidence:** Compare identities, input sum and exact bag;allow empty progress entries.

### Exercise 3: Test real streaming duplicate suppression

Use native streaming dropDuplicates on the id key for two identical occurrences of 1:100.

**Expected:** 2 source rows,1 committed row 1:100.

```scala
def duplicateCase(spark: SparkSession, paths: (Path, Path, Path)): RunReceipt = {
  runScenario(spark, paths._1, paths._2, paths._3, "duplicates")
}
```

```python
def duplicate_case(spark, paths):
    return run_scenario(spark, *paths, "duplicates")
```

This case runs a stateful Spark deduplication operator, not only a local Python set. Equal duplicate payloads avoid an unspecified winner problem. There is no eviction policy here, so a production unbounded stream would require a separate state-bound design rather than copying this tiny test unchanged.

**Verification evidence:** Compare input count 2 and the one-row bag.

### Exercise 4: Test the exact event-time boundary

Apply the explicitly declared admission cutoff event_second>=90 to rows at 80,90 and 110.

**Expected:** 3 source rows;accepted IDs 2,3 with cents 200,300.

```scala
def lateCase(spark: SparkSession, paths: (Path, Path, Path)): RunReceipt = {
  runScenario(spark, paths._1, paths._2, paths._3, "late")
}
```

```python
def late_case(spark, paths):
    return run_scenario(spark, *paths, "late")
```

Event seconds are integer seconds on a declared synthetic UTC timeline. The policy cutoff is fixed and inclusive, so the boundary can be checked independently of scheduling. Native watermark/state eviction was taught separately and must not be inferred from this ordinary filter.

**Verification evidence:** Compare exact two-row bag and explain why 90 is retained.

### Exercise 5: Keep invalid rows visible in the case ledger

Reject a NULL identity and a negative amount while retaining valid 3:300.

**Expected:** 3 input occurrences,2 invalid,1 accepted.

```scala
def invalidCase(spark: SparkSession, paths: (Path, Path, Path)): RunReceipt = {
  runScenario(spark, paths._1, paths._2, paths._3, "invalid")
}
```

```python
def invalid_case(spark, paths):
    return run_scenario(spark, *paths, "invalid")
```

The invalid count is established against the supplied raw fixture rather than disappearing from the report. The sum accepted+invalid=source occurrences is a conservation check. Invalid JSON syntax would be a different FAILFAST source error and is not relabeled as an ordinary valid-schema row rejection.

**Verification evidence:** Compare raw source count 3, actual progress, sink bag 3:300 and static predicate count 2.

### Exercise 6: Prove the oracle rejects a plausible regression

Compare the correct duplicate-case bag with an unsafe two-copy append result and reject the mismatch. Confirm every owned query is inactive before cleanup.

**Expected:** Correct bag passes;duplicated bag raises an assertion-contract error;all owned queries are inactive.

```scala
def requireBag(actual: Seq[String], expected: Seq[String]): Unit = {
  require(actual == expected, "Canonical bag mismatch")
}
```

```python
def require_bag(actual, expected):
    if actual != expected:
        raise ValueError("Canonical bag mismatch")
```

The negative control demonstrates that the case oracle would reject a duplicate-preserving or repeated-append shortcut. It does not rely on a randomly occurring failure. Inactive-query checks are a precondition for deleting the fresh scratch root;cleanup must not race active stream work or target another test directory.

**Verification evidence:** Catch the specific mismatch and compare the exact offending rows.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration;they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
