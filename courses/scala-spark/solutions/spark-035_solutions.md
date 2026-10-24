# spark-035: Explained paired reference solutions

Read the [guide](../guides/spark-035.md) and attempt one language first. The [Scala reference](spark-035_solution.scala) and [PySpark reference](spark-035_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations;matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Validate the finite input and output grain

Read a static copy of the two-row schema fixture and require bigint id/cents, known nonnull values and at most 8 rows. Return its canonical ordered bag without removing duplicates.

**Expected:** The first bag is 1:100,2:200. A NULL identity or cents value is rejected.

```scala
def validatedBag(frame: DataFrame): Seq[String] = {
  require(frame.schema.fields.map(f => (f.name,f.dataType.simpleString)).toSeq == Seq(("id","bigint"),("cents","bigint")))
  require(frame.count() <= 8L && frame.filter(col("id").isNull || col("cents").isNull || col("id") <= 0L || col("cents") < 0L).count() == 0L)
  frame.orderBy("id","cents").collect().map(r => s"${r.getLong(0)}:${r.getLong(1)}").toSeq
}
```

```python
def validated_bag(frame):
    if [(f.name,f.dataType.simpleString()) for f in frame.schema.fields]!=[("id","bigint"),("cents","bigint")]:raise ValueError("Schema mismatch")
    if frame.count()>8 or frame.filter(F.col("id").isNull()|F.col("cents").isNull()|(F.col("id")<=0)|(F.col("cents")<0)).count():raise ValueError("Invalid bounded records")
    return [f"{r.id}:{r.cents}" for r in frame.orderBy("id","cents").collect()]
```

The row grain is one input event occurrence, not one distinct business identity. Validating types and missingness before collection makes the tiny oracle meaningful and keeps a null from becoming a string that accidentally looks like a legitimate key. Sorting establishes a comparison order without changing multiplicity.

**Verification evidence:** Compare the exact two-row bag and reject an explicit null-id DataFrame.

### Exercise 2: Run the first finite file stream

Execute the AvailableNow Parquet query with its owned checkpoint/output and retain query ID, run ID, input count and batch IDs.

**Expected:** Two input rows and exactly 1:100,2:200 in the committed sink.

```scala
def firstRun(spark: SparkSession,input: Path,checkpoint: Path,output: Path): RunReceipt = {
  runParquet(spark,input,checkpoint,output)
}
```

```python
def first_run(spark,input_path,checkpoint,output):
    return run_parquet(spark,input_path,checkpoint,output)
```

AvailableNow bounds the available input for this invocation and terminates after processing it. The source offset log and sink commit metadata have different responsibilities. The progress receipt records what this run observed, while actual Parquet readback checks the committed output values. An inactive query alone would not establish those values.

**Verification evidence:** Assert the progress input count is 2, query is terminated, and readback bag is exact.

### Exercise 3: Resume the same checkpoint after a new file

Publish a second file with 2:200 and 3:300, then restart the compatible query with the same checkpoint and sink.

**Expected:** Only 2 new input rows are processed. The sink bag is 1:100,2:200,2:200,3:300. Query ID persists and run ID changes.

```scala
def resumeNewFile(spark: SparkSession,root: Path,input: Path,checkpoint: Path,output: Path): RunReceipt = {
  publishFile(root,input,"batch-02.json",Seq("""{"id":2,"cents":200}""","""{"id":3,"cents":300}"""))
  runParquet(spark,input,checkpoint,output)
}
```

```python
def resume_new_file(spark,root,input_path,checkpoint,output):
    publish_file(root,input_path,"batch-02.json",['{"id":2,"cents":200}','{"id":3,"cents":300}'])
    return run_parquet(spark,input_path,checkpoint,output)
```

The checkpoint retains which immutable source files were processed. The new file has a new source identity even though one row repeats a business ID. The preserved duplicate is intentional evidence separating source-offset recovery from an application deduplication policy. Persistent query ID and fresh run ID show the distinction between a logical query and one execution attempt.

**Verification evidence:** Compare both identities, progress count and all 4 output occurrences.

### Exercise 4: Resume with no new source files

Run the same compatible query again without adding input and compare output before/after.

**Expected:** Zero new input rows and an unchanged 4-row output bag.

```scala
def resumeEmpty(spark: SparkSession,input: Path,checkpoint: Path,output: Path): RunReceipt = {
  runParquet(spark,input,checkpoint,output)
}
```

```python
def resume_empty(spark,input_path,checkpoint,output):
    return run_parquet(spark,input_path,checkpoint,output)
```

No new file offset means no fresh source data to append. An empty progress sequence is compatible with this finite no-work case, so the checker avoids inventing a required microbatch. The before/after output comparison ensures a restart did not duplicate previously committed source occurrences.

**Verification evidence:** Assert zero progress input sum and exact unchanged sink rows.

### Exercise 5: Replay with a separate checkpoint and output

Start from a new checkpoint only when the output namespace is also new. Replay the same source and preserve the old checkpoint/sink.

**Expected:** The separate output has 4 rows, with a new logical query ID. The old output remains 4 rows.

```scala
def separateReplay(spark: SparkSession,input: Path,checkpoint: Path,output: Path,oldCheckpoint: Path,oldOutput: Path): RunReceipt = {
  require(checkpoint!=oldCheckpoint && output!=oldOutput && !Files.exists(checkpoint) && !Files.exists(output))
  runParquet(spark,input,checkpoint,output)
}
```

```python
def separate_replay(spark,input_path,checkpoint,output,old_checkpoint,old_output):
    if checkpoint==old_checkpoint or output==old_output or checkpoint.exists() or output.exists():raise ValueError("Fresh checkpoint and separate sink required")
    return run_parquet(spark,input_path,checkpoint,output)
```

The new checkpoint defines a new source-history namespace and can see all available files again. A separate sink makes that replay inspectable without contaminating the prior committed output. This is a deliberate replay experiment, not a repair that deletes or resets an existing checkpoint.

**Verification evidence:** Assert checkpoint/output paths differ and both independent bags equal the literal 4-row oracle.

### Exercise 6: Write a guarantee ledger from exact counts

Return output row count, distinct business IDs and total cents, then explain why source recovery is not business-ID deduplication or a universal exactly-once guarantee.

**Expected:** 4 occurrences,3 distinct IDs, total 800.

```scala
def guaranteeLedger(frame: DataFrame): Seq[Long] = {
  validatedBag(frame)
  val r=frame.agg(count(lit(1)),countDistinct("id"),sum("cents")).first()
  Seq(r.getLong(0),r.getLong(1),r.getLong(2))
}
```

```python
def guarantee_ledger(frame):
    validated_bag(frame)
    return tuple(frame.agg(F.count(F.lit(1)),F.countDistinct("id"),F.sum("cents")).first())
```

The three-number ledger catches a misleading countDistinct-only success claim. A replay-safe file sink can preserve each source occurrence correctly while still containing repeated business events. Recovery semantics depend jointly on replayable immutable source files, compatible checkpoint state and the selected sink protocol. A process-level local rehearsal does not qualify arbitrary external side effects or distributed storage durability.

**Verification evidence:** Compare all three independent values and preserve the duplicate occurrence.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration;they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
