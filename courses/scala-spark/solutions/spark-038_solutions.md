# spark-038: Explained paired reference solutions

Read the [guide](../guides/spark-038.md) and attempt one language first. The [Scala reference](spark-038_solution.scala) and [PySpark reference](spark-038_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations;matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Capture actual finite streaming progress

Run the supplied three-occurrence stream with ID deduplication and return a bounded observation record.

**Expected:** Input count 3, state rows 2 and exact committed bag 1:100,2:200.

```scala
def capture(spark: SparkSession,input: Path,checkpoint: Path,output: Path): Observation = {
  observe(spark,input,checkpoint,output)
}
```

```python
def capture(spark,input_path,checkpoint,output):
    return observe(spark,input_path,checkpoint,output)
```

The actual query ingests three occurrences and retains two distinct IDs. Its state metric and committed output answer related but different questions. The literal values catch wrong payloads even if state/input counts look reasonable. Termination is observed through the query lifecycle, not an assumed wait duration.

**Verification evidence:** Join the progress record with actual readback and inactive-query evidence.

### Exercise 2: Interpret state and sink metrics with units

Require a state operator and a nonnegative memory-used measurement;preserve unknown or negative sink-row sentinel values as unavailable.

**Expected:** State memory is reported in bytes. A missing or negative sink output count is not converted into zero.

```scala
def knownMetric(value: Option[Long]): Option[Long] = {
  value.filter(_ >= 0L)
}
```

```python
def known_metric(value):
    return value if value is not None and value>=0 else None
```

A state-store memory metric is neither total JVM resident memory nor a cloud bill. A sink may not publish an exact output-row count through progress, so the example retains unavailable rather than making up zero. Actual output values come from the separate file readback.

**Verification evidence:** Check the real state record and explicit None/-1 normalization controls.

### Exercise 3: Observe bounded state growth across restart

Add a new ID 3:300 and restart the same compatible checkpoint.

**Expected:** One new input row, state rows grow 2 to 3, and output gains 3:300.

```scala
def growState(spark: SparkSession,root: Path,input: Path,checkpoint: Path,output: Path): Observation = {
  publishFile(root,input,"batch-02.json",Seq("""{"id":3,"cents":300}"""))
  observe(spark,input,checkpoint,output)
}
```

```python
def grow_state(spark,root,input_path,checkpoint,output):
    publish_file(root,input_path,"batch-02.json",['{"id":3,"cents":300}'])
    return observe(spark,input_path,checkpoint,output)
```

This deduplication query has no eviction policy and adds one new key, so retaining one additional state row is expected. The observation demonstrates how to connect growth to input/key policy. It does not establish a memory leak or prescribe deleting state to reduce the metric.

**Verification evidence:** Compare actual state totals, query identity and exact committed rows.

### Exercise 4: Distinguish empty input from a stuck query

Run a separate AvailableNow query over an empty owned input directory.

**Expected:** Zero admitted rows and a terminated query;state/sink metrics may be absent.

```scala
def emptyObservation(spark: SparkSession,root: Path): Observation = {
  val empty=Files.createDirectory(root.resolve("empty-input"))
  observe(spark,empty,root.resolve("empty-checkpoint"),root.resolve("empty-output"))
}
```

```python
def empty_observation(spark,root):
    empty=root/"empty-input";empty.mkdir()
    return observe(spark,empty,root/"empty-checkpoint",root/"empty-output")
```

A finite empty invocation can finish successfully without producing a readable file dataset. The program therefore does not turn missing output files into an invented zero-row schema. In a running production query, zero input would require checking source discovery, upstream supply and offsets before calling it a compute bottleneck.

**Verification evidence:** Assert zero input and termination without fabricating an output Parquet schema.

### Exercise 5: Diagnose three seeded incident records

For the explicitly synthetic incident fixtures, choose one reversible check for skew, growing state and zero admitted input.

**Expected:** Inspect key/partition distribution;inspect watermark/key-retention policy;inspect source discovery respectively.

```scala
def nextCheck(kind: String): String = {
  kind match { case "skew" => "inspect_partition_keys";case "state" => "inspect_watermark_and_key_growth";case "input" => "inspect_source_discovery";case _ => throw new IllegalArgumentException("Unknown incident") }
}
```

```python
def next_check(kind):
    checks={"skew":"inspect_partition_keys","state":"inspect_watermark_and_key_growth","input":"inspect_source_discovery"}
    if kind not in checks:raise ValueError("Unknown incident")
    return checks[kind]
```

The seeded records are reasoning fixtures, not measurements from the tiny live query. A long-tail task ratio motivates inspecting partition keys but does not prove skew without more evidence. Growing state motivates comparing watermark/key arrival/retention. Zero admitted input motivates checking source discovery before increasing executor resources.

**Verification evidence:** Compare the three exact recommendations and state one success observation for each.

### Exercise 6: Sanitize evidence with an allowlist

Keep only stage_id, task_id, run_ms and input_records from a supplied task-event dictionary containing fake credential fields.

**Expected:** Exact four-field record, with fake token/password absent.

```scala
def sanitize(event: Map[String,String]): Map[String,String] = {
  event.filter { case (key,_) => Set("stage_id","task_id","run_ms","input_records").contains(key) }
}
```

```python
def sanitize(event):
    allowed={"stage_id","task_id","run_ms","input_records"}
    return {key:value for key,value in event.items() if key in allowed}
```

Event logs, plans and configuration can contain paths, SQL text or application data. This small allowlist creates a reviewable sanitized task record and never prints the fake secret input. It is not a universal log-redaction system;new fields need a deliberate data-handling decision before being exported.

**Verification evidence:** Assert field set and values;do not print the unfiltered input.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration;they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
