# spark-041: Explained paired reference solutions

Read the [guide](../guides/spark-041.md) and attempt one language first. The [Scala reference](spark-041_solution.scala) and [PySpark reference](spark-041_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations;matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Capture the actual runtime tuple

Record Spark, Scala binary and patch, JDK major and patch, Python version and optional PyArrow distribution version without installing anything.

**Expected:** Spark 4.0.1, Scala 2.13 family, JDK 17;actual patch strings and explicit not-installed Arrow when absent.

```scala
def versionReceipt(spark: SparkSession): Map[String,String] = {
  runtimeVersions(spark)
}
```

```python
def version_receipt(spark):
    return runtime_versions(spark)
```

The receipt describes the runtime actually executing the tests. Scala probes the bundled python 3 with a fixed bounded metadata script;PySpark reads its own interpreter and the actual JVM. An absent Arrow distribution is recorded without fetching it. None of these strings proves a second environment has run the golden suite.

**Verification evidence:** Inspect actual values and reject a claimed target qualification based only on a proposed version string.

### Exercise 2: Run a type, NULL and multiplicity golden suite

Evaluate the supplied four-row bag plus exact decimal and timezone expressions.

**Expected:** 4 rows,3 known amounts, total 200,3 distinct IDs;decimal 12345678.90;instant 19:00UTC.

```scala
def goldenMetrics(frame: DataFrame): Seq[Long] = {
  val r=frame.agg(count(lit(1)),count("cents"),sum("cents"),countDistinct("id")).first()
  Seq(r.getLong(0),r.getLong(1),r.getLong(2),r.getLong(3))
}
```

```python
def golden_metrics(frame):
    return tuple(frame.agg(F.count(F.lit(1)),F.count("cents"),F.sum("cents"),F.countDistinct("id")).first())
```

The fixture catches a migration that drops duplicate occurrences, replaces NULL with zero, changes exact decimals or reinterprets an instant. A successful class load or version line cannot detect those semantic regressions. The small literal expectations are independent of each implementation.

**Verification evidence:** Compare exact metrics and rendered values under the UTC baseline.

### Exercise 3: Preserve baseline state and reject incompatible reuse

Run the baseline ID-only deduplication query, then reject a request to change its state keys to id, cents while retaining that checkpoint.

**Expected:** Baseline output 1:100,2:200;preflight rejects changed keys before starting a new query.

```scala
def requireCompatible(oldKeys: Seq[String],newKeys: Seq[String]): Unit = {
  require(oldKeys==newKeys,"State-key change requires separate checkpoint and output")
}
```

```python
def require_compatible(old_keys,new_keys):
    if old_keys!=new_keys:raise ValueError("State-key change requires separate checkpoint and output")
```

This is an explicit application preflight refusal, not a fabricated Spark engine exception. It protects the old state before launching an incompatible query. Spark documents restrictions on changes to stateful operators and schemas;the safe rehearsal uses a separate recovery namespace rather than deleting or editing checkpoint internals.

**Verification evidence:** Compare owned-query count before/after the refusal and confirm the old checkpoint/output remain present and unchanged.

### Exercise 4: Run the changed query in a separate candidate namespace

Add a new occurrence 1:999 and run id, cents deduplication using a new checkpoint/output.

**Expected:** Candidate bag 1:100,1:999,2:200, which fails the baseline one-row-per-ID product gate.

```scala
def candidateRun(spark: SparkSession,root: Path,input: Path): RunReceipt = {
  publishFile(root,input,"batch-02.json",Seq("""{"id":1,"cents":999}"""))
  runKeys(spark,input,root.resolve("candidate-checkpoint"),root.resolve("candidate-output"),Seq("id","cents"))
}
```

```python
def candidate_run(spark,root,input_path):
    publish_file(root,input_path,"batch-02.json",['{"id":1,"cents":999}'])
    return run_keys(spark,input_path,root/"candidate-checkpoint",root/"candidate-output",["id","cents"])
```

The changed state key admits a second amount for the same ID. That can be a valid new product only if the business contract changes deliberately. Here it violates the existing golden population and is not promoted. A separate namespace makes the comparison reversible without claiming a checkpoint migration occurred.

**Verification evidence:** Compare candidate and baseline exact bags and preserve old checkpoint/output.

### Exercise 5: Rehearse rollback to the preserved compatible query

Resume the original ID-only query with its original checkpoint after the candidate is rejected.

**Expected:** The same baseline query ID resumes;the new occurrence of already-seen ID 1 does not add a row;baseline output stays 1:100,2:200.

```scala
def rollback(spark: SparkSession,input: Path,checkpoint: Path,output: Path): RunReceipt = {
  runKeys(spark,input,checkpoint,output,Seq("id"))
}
```

```python
def rollback(spark,input_path,checkpoint,output):
    return run_keys(spark,input_path,checkpoint,output,["id"])
```

The original state is available because the candidate never reused or reset it. The resumed baseline processes the source under its declared ID-only policy. This is a query-shape rollback within one actual runtime, not proof of cross-version checkpoint portability or a resolution policy for conflicting business events.

**Verification evidence:** Check query identity and exact sink bag without deleting either checkpoint.

### Exercise 6: Gate a proposed runtime change on actual evidence

Require a qualified target profile, golden-suite pass, compatible recovery design and product acceptance before promotion.

**Expected:** The supplied unqualified target or failed candidate is rejected;all four true permits a proposal in this pure decision model.

```scala
def mayPromote(profileQualified: Boolean,goldenPassed: Boolean,recoveryReviewed: Boolean,productPassed: Boolean): Boolean = {
  profileQualified && goldenPassed && recoveryReviewed && productPassed
}
```

```python
def may_promote(profile_qualified,golden_passed,recovery_reviewed,product_passed):
    return profile_qualified and golden_passed and recovery_reviewed and product_passed
```

The gate keeps missing evidence visible. Only the current Spark 4.0.1 stack is executed by this lesson. A future target must run the same golden suite and its own recovery checks with actual version receipts. The Boolean model organizes that decision but cannot create missing runtime evidence.

**Verification evidence:** Check missing-profile and wrong-product negatives, then record that no second runtime was provisioned.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration;they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
