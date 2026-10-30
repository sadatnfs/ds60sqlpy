# spark-029: Explained paired reference solutions

Read the [guide](../guides/spark-029.md) and attempt one language first. The [Scala reference](spark-029_solution.scala) and [PySpark reference](spark-029_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Validate the product before computing its digest

Require ordered fieldsid, value with bigint types, exactly 30 known unique IDs 0..29, known values equal to 2*id and total 870. ReturnSHA-256 of sorted SparkJSON lines joined by newline without a trailing newline.

**Expected:** A64-character lowercase digest for the valid product. Wrong values, counts, types or identities are rejected before hashing.

```scala
def productDigest(frame: DataFrame): String = {
  require(
    frame.schema.fields.toSeq
      .map(f => (f.name, f.dataType.simpleString)) == Seq(("id", "bigint"), ("value", "bigint")),
    "Product schema mismatch"
  )
  val metrics =
    frame.agg(count(lit(1)), countDistinct("id"), min("id"), max("id"), sum("value")).first()
  require(metrics.toSeq == Seq(30L, 30L, 0L, 29L, 870L), "Product population mismatch")
  require(
    frame
      .filter(col("id").isNull || col("value").isNull || col("value") =!= col("id") * 2L)
      .count() == 0L,
    "Product value mismatch"
  )
  val canonical = frame.orderBy("id").toJSON.collect().mkString("\n")
  MessageDigest
    .getInstance("SHA-256")
    .digest(canonical.getBytes(StandardCharsets.UTF_8))
    .map(b => f"${b & 0xff}%02x")
    .mkString
}
```

```python
def product_digest(frame):
    if [(f.name, f.dataType.simpleString()) for f in frame.schema.fields] != [
        ("id", "bigint"),
        ("value", "bigint"),
    ]:
        raise ValueError("Product schema mismatch")
    metrics = tuple(
        frame.agg(
            F.count(F.lit(1)), F.countDistinct("id"), F.min("id"), F.max("id"), F.sum("value")
        ).first()
    )
    if metrics != (30, 30, 0, 29, 870):
        raise ValueError("Product population mismatch")
    if frame.filter(
        F.col("id").isNull() | F.col("value").isNull() | (F.col("value") != F.col("id") * 2)
    ).count():
        raise ValueError("Product value mismatch")
    canonical = "\n".join(frame.orderBy("id").toJSON().collect())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

Validation establishes the business product before hashing its canonical representation. Sorting makes the digest independent of execution partition and arrival order. The count check bounds the driver collection to 30 rows. The digest convention is explicit so different implementations cannot silently hash different field orders, newline conventions or number renderings and call the results equivalent.

**Verification evidence:** Assert a64-hex digest and equal digest after repartitioning; reject a 31-row source.

### Exercise 2: Stage a run and validate the persisted readback

Restrict run IDs to 1..32 lowercase letters, digits or hyphens. Validate input, write a fresh run-specific Parquet product, validate readback and save its receipt. If that run already exists, require its validated digest to match instead of appending.

**Expected:** run-a has one 30-row data product and a receipt with the declared schema/count/path/digest. Reusing it never appends another product.

```scala
def stageRun(spark: SparkSession, root: Path, runId: String, source: DataFrame): String = {
  checkRunId(runId)
  val digest = productDigest(source)
  val run = root.resolve("runs").resolve(runId)
  if (Files.exists(run)) {
    val existing = validateStaged(spark, root, runId)
    require(
      mapper.readTree(existing).get("sha256").asText() == digest,
      "Run identity has different content"
    )
    existing
  } else {
    Files.createDirectory(run)
    source.write.mode("errorifexists").parquet(run.resolve("data").toString)
    require(
      productDigest(spark.read.parquet(run.resolve("data").toString)) == digest,
      "Staging readback mismatch"
    )
    val text = receiptText(runId, digest)
    Files.writeString(
      run.resolve("receipt.json"),
      text,
      StandardCharsets.UTF_8,
      StandardOpenOption.CREATE_NEW
    )
    text
  }
}
```

```python
def stage_run(spark, root, run_id, source):
    check_run_id(run_id)
    digest = product_digest(source)
    run = root / "runs" / run_id
    if run.exists():
        existing = validate_staged(spark, root, run_id)
        if json.loads(existing)["sha256"] != digest:
            raise ValueError("Run identity has different content")
        return existing
    run.mkdir()
    source.write.mode("errorifexists").parquet(str(run / "data"))
    if product_digest(spark.read.parquet(str(run / "data"))) != digest:
        raise ValueError("Staging readback mismatch")
    text = receipt_text(run_id, digest)
    with (run / "receipt.json").open("x", encoding="utf-8") as handle:
        handle.write(text)
    return text
```

Staging creates a new data namespace and verifies the actual file product before describing it with a receipt. The existing-run branch is a content-aware retry, not append or overwrite. A partially written run without a valid receipt is rejected by validation rather than guessed complete; cleanup or recovery policy would need an explicit decision for such an orphan.

**Verification evidence:** Assert staged receipt existence and digest equality; all paths remain within the fresh owned root.

### Exercise 3: Validate a receipt against a fixed owned data path

Read a run receipt and require its run_id, data_path, row_count, schema and digest to match the declared contract and actual Parquet readback. Construct the read path from validated runId rather than trusting arbitrary receipt text.

**Expected:** Validrun-a receipt returns unchanged. A traversal-style run ID is rejected before path access.

```scala
def validateStaged(spark: SparkSession, root: Path, runId: String): String = {
  checkRunId(runId)
  val run = root.resolve("runs").resolve(runId)
  val text = Files.readString(run.resolve("receipt.json"), StandardCharsets.UTF_8)
  val node = mapper.readTree(text)
  require(
    node
      .path("run_id")
      .asText() == runId && node.path("data_path").asText() == "runs/" + runId + "/data",
    "Receipt identity/path mismatch"
  )
  require(
    node.path("row_count").asInt() == 30 && node.path("schema").asText() == schemaText,
    "Receipt schema/count mismatch"
  )
  require(
    node.path("sha256").asText() == productDigest(spark.read.parquet(run.resolve("data").toString)),
    "Receipt content mismatch"
  )
  text
}
```

```python
def validate_staged(spark, root, run_id):
    check_run_id(run_id)
    run = root / "runs" / run_id
    text = (run / "receipt.json").read_text(encoding="utf-8")
    node = json.loads(text)
    if node.get("run_id") != run_id or node.get("data_path") != "runs/" + run_id + "/data":
        raise ValueError("Receipt identity/path mismatch")
    if node.get("row_count") != 30 or node.get("schema") != SCHEMA_TEXT:
        raise ValueError("Receipt schema/count mismatch")
    if node.get("sha256") != product_digest(spark.read.parquet(str(run / "data"))):
        raise ValueError("Receipt content mismatch")
    return text
```

The receipt must agree with both the declared metadata policy and current staged bytes. Its relative path is checked against a value constructed from the constrained run identity. This keeps the reader inside the owned namespace and prevents a malformed receipt from redirecting the demonstration to unrelated filesystem state.

**Verification evidence:** Assert receipt equality and explicit rejection of../outside.

### Exercise 4: Publish only a validated run at one explicit visibility point

Validate the staged receipt, write it to a fresh temporary manifest beside current.json, and atomically replace current.json. Support an injected failure before replacement and clean any unpublished temporary manifest in finally.

**Expected:** Publishingrun-a creates current.json selecting its 30-row product. No data is appended or rewritten during publication.

```scala
def publishRun(spark: SparkSession, root: Path, runId: String, failBeforeReplace: Boolean): Unit = {
  val text = validateStaged(spark, root, runId)
  val pending = root.resolve("manifest-pending-" + UUID.randomUUID().toString + ".json")
  try {
    Files.writeString(pending, text, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW)
    if (failBeforeReplace) throw new IllegalStateException("injected_before_publication")
    Files.move(
      pending,
      root.resolve("current.json"),
      StandardCopyOption.ATOMIC_MOVE,
      StandardCopyOption.REPLACE_EXISTING
    )
  } finally Files.deleteIfExists(pending)
}
```

```python
def publish_run(spark, root, run_id, fail_before_replace=False):
    text = validate_staged(spark, root, run_id)
    pending = root / ("manifest-pending-" + uuid.uuid4().hex + ".json")
    try:
        with pending.open("x", encoding="utf-8") as handle:
            handle.write(text)
        if fail_before_replace:
            raise RuntimeError("injected_before_publication")
        os.replace(pending, root / "current.json")
    finally:
        pending.unlink(missing_ok=True)
```

Validation precedes the publication point, so the manifest never intentionally names an unvalidated product. The temporary file sits in the same owned directory to support local atomic replacement. This process-level visibility guarantee is narrower than power-loss durability or distributed multi-writer transactions, which require additional storage-specific protocols.

**Verification evidence:** Assert the current manifest equals the validated receipt and points torun-a.

### Exercise 5: Keep the previous publication readable after an interrupted replacement

Read the current manifest, validate its selected run and return that product. Stage run-b, inject failure before its manifest replacement, and confirm the reader still seesrun-a.

**Expected:** The injected error occurs, current.json bytes remain identical torun-a, and the published product still has 30 rows with the original digest.

```scala
def readPublished(spark: SparkSession, root: Path): DataFrame = {
  val current = Files.readString(root.resolve("current.json"), StandardCharsets.UTF_8)
  val node = mapper.readTree(current)
  val runId = node.path("run_id").asText()
  val validated = validateStaged(spark, root, runId)
  require(mapper.readTree(validated) == node, "Published manifest differs from validated receipt")
  spark.read.parquet(root.resolve("runs").resolve(runId).resolve("data").toString)
}
```

```python
def read_published(spark, root):
    current = (root / "current.json").read_text(encoding="utf-8")
    node = json.loads(current)
    run_id = node.get("run_id")
    validated = validate_staged(spark, root, run_id)
    if json.loads(validated) != node:
        raise ValueError("Published manifest differs from validated receipt")
    return spark.read.parquet(str(root / "runs" / run_id / "data"))
```

The failure leaves a valid but unreferenced staging product. A manifest-based reader ignores it and continues to use the prior selected run. The unchanged manifest bytes and independently revalidated digest prove the precise boundary tested: an interruption before replacement did not publish partial or additional logical rows.

**Verification evidence:** Assert the named exception, unchanged manifest and exact published product digest; run-b staging must not enter the reader population.

### Exercise 6: Replay the same input without appending another product

Compose stage, validate/publish and readback for a repeated run ID. Retryrun-a with a different execution partition layout, then attempt an invalid 31-row product and confirm publication stays intact.

**Expected:** Manifest bytes and data-file count are unchanged by validrun-a replay; published count remains 30. Invalid input fails before changing current.json.

```scala
def retryProduct(spark: SparkSession, root: Path, runId: String, source: DataFrame): String = {
  stageRun(spark, root, runId, source)
  publishRun(spark, root, runId, false)
  productDigest(readPublished(spark, root))
}
```

```python
def retry_product(spark, root, run_id, source):
    stage_run(spark, root, run_id, source)
    publish_run(spark, root, run_id)
    return product_digest(read_published(spark, root))
```

Canonical content identity is stable across physical repartitioning, so the retry can reuse the existing run. Data-file count proves the valid retry did not append another 30-row product. The invalid source is rejected by the product contract before it can replace the current pointer. This is a bounded single-writer local protocol, with its tested failure boundary stated explicitly.

**Verification evidence:** Assert digest, manifest bytes, file-count equality and negative-control rejection.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
