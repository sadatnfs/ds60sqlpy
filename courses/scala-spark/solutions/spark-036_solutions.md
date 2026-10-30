# spark-036: Explained paired reference solutions

Read the [guide](../guides/spark-036.md) and attempt one language first. The [Scala reference](spark-036_solution.scala) and [PySpark reference](spark-036_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations;matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Define canonical bounded microbatch content

Validate the explicit bigint schema, nonnegative cents, positive IDs and at most 8 rows;return sorted id, cents newline records preserving multiplicity.

**Expected:** Exact text 1,100 newline 2,200 newline, with a stable SHA256 after repartitioning.

```scala
def encodeBatch(frame: DataFrame): String = {
  canonicalBatch(frame)
}
```

```python
def encode_batch(frame):
    return canonical_batch(frame)
```

Canonical bytes make a retry comparison independent of task order. Validation and a fixed eight-row limit make the driver collection deliberate. A digest is computed only after the schema and domain contract holds. Repeated equal rows remain repeated source occurrences, so canonicalization does not secretly implement business-event deduplication.

**Verification evidence:** Compare exact bytes and reject NULL cents before publication.

### Exercise 2: Publish one logical batch idempotently

Publish the same canonical content twice under identity manual-v1 and batch 7. Compare the existing receipt instead of appending.

**Expected:** First call publishes true;second returns false;exactly 2 logical rows remain.

```scala
def publishOnce(root: Path, identity: String, batchId: Long, text: String): Boolean = {
  publishBatch(root, identity, batchId, text, false)
}
```

```python
def publish_once(root, identity, batch_id, text):
    return publish_batch(root, identity, batch_id, text, False)
```

The local commit file contains both data and the batch identity, digest together. Its atomic rename is the visibility boundary. A repeated call with identical content is a no-op;the sink does not add a second copy. This assumes a single writer and the prepared same-filesystem rename semantics, not distributed transaction coordination or power-loss durability.

**Verification evidence:** Assert return values, unchanged receipt bytes and one batch file.

### Exercise 3: Inject a real callback failure before publication

Run the actual foreachBatch query with failure after staging and before rename. Retain the wrapped streaming exception and attempted batch ID.

**Expected:** The query fails with injected_before_publication;no stream-v1 batch is visible and the attempted batch ID is 0.

```scala
def failCallback(spark: SparkSession, input: Path, checkpoint: Path, sink: Path): Unit = {
  var observed = false
  try runForeach(spark, input, checkpoint, sink, "stream-v1", true)
  catch {
    case e: org.apache.spark.sql.streaming.StreamingQueryException
        if e.toString.contains("injected_before_publication") =>
      observed = true
  }
  require(observed, "Expected injected streaming failure")
}
```

```python
def fail_callback(spark, input_path, checkpoint, sink):
    from pyspark.errors import StreamingQueryException

    try:
        run_foreach(spark, input_path, checkpoint, sink, "stream-v1", True)
    except StreamingQueryException as error:
        if "injected_before_publication" not in str(error):
            raise
    else:
        raise AssertionError("Expected injected streaming failure")
```

This is an actual streaming callback failure, not only a direct helper exception. The staged file never becomes a visible batch file, and cleanup removes its unpublished temporary file. The source offset may have been recorded before failure, while completion has not been committed. Letting the exception escape is essential so the compatible restart retries the batch.

**Verification evidence:** Check the exception marker, empty published rows and inactive query.

### Exercise 4: Recover the same checkpoint and observe replay

Restart the same source/checkpoint/query namespace without failure. Compare attempts and logical query/run IDs.

**Expected:** Batch 0 is attempted again and publishes 2 rows once. Query ID persists;run ID changes.

```scala
def recoverCallback(spark: SparkSession, input: Path, checkpoint: Path, sink: Path): RunReceipt = {
  runForeach(spark, input, checkpoint, sink, "stream-v1", false)
}
```

```python
def recover_callback(spark, input_path, checkpoint, sink):
    return run_foreach(spark, input_path, checkpoint, sink, "stream-v1", False)
```

The repeated batch ID is direct evidence that callback delivery can repeat. The sink key is stable across runs, so replay refers to the same logical work. A key based on runId would change after restart and defeat this protection. The application-defined namespace is also bound to its source/checkpoint/schema contract to reject accidental reuse for an unrelated query.

**Verification evidence:** Assert attempt sequence 0,0, exact rows and corresponding identities.

### Exercise 5: Expose a non-idempotent append counterexample

Append the same canonical batch text twice to a separate unsafe-demo file, then compare it with the idempotent published batch.

**Expected:** Unsafe append has 4 row occurrences;the committed batch remains 2.

```scala
def unsafeAppend(path: Path, text: String): Unit = {
  Files.writeString(
    path,
    text,
    StandardCharsets.UTF_8,
    StandardOpenOption.CREATE,
    StandardOpenOption.APPEND
  )
  ()
}
```

```python
def unsafe_append(path, text):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)
```

This intentionally unsafe local side effect is isolated from the real sink. Its duplicate result does not depend on a race or random timing;two deliveries visibly append two copies. The counterexample shows why a successful callback or checkpoint configuration cannot magically make a non-idempotent external operation exactly once.

**Verification evidence:** Compare exact repeated lines and preserve the unsafe file as a separate diagnostic until owned cleanup.

### Exercise 6: Reject identity collisions and admit the next batch

Reject different content under an existing batch key, then publish a new source file 3:300 and resume the real query.

**Expected:** The conflicting key fails without replacing its receipt. Stream batch 1 adds one row, leaving IDs 1,2,3 and total 600 across two batch files.

```scala
def rejectCollision(root: Path, text: String): Unit = {
  var rejected = false
  try publishBatch(root, "manual-v1", 7L, text + "9,999\n", false)
  catch { case _: IllegalArgumentException => rejected = true }
  require(rejected)
}
```

```python
def reject_collision(root, text):
    try:
        publish_batch(root, "manual-v1", 7, text + "9,999\n", False)
    except ValueError:
        pass
    else:
        raise AssertionError("Changed content reused a committed batch key")
```

Idempotency is a content-aware identity rule, not unconditional suppression of anything with a repeated number. A collision signals incompatible reuse or corruption and must not silently overwrite the committed result. The subsequent real microbatch demonstrates that the sink can accept new logical work while maintaining replay safety for old work.

**Verification evidence:** Assert collision rejection, old receipt equality, attempt sequence 0,0,1 and exact 3-row sink.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration;they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
