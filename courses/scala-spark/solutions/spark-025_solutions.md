# spark-025: Explained paired reference solutions

Read the [guide](../guides/spark-025.md) and attempt one language first. The [Scala reference](spark-025_solution.scala) and [PySpark reference](spark-025_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Write and validate a compact partitioned round trip

Repartition source by day into 2 execution partitions, write Parquet with error-if-exists and partitionBy(day), then read it back. Compare field types and the complete duplicate-sensitive bag.

**Expected:** 2000 rows and total 13993000 survive. Types remain id/amount bigints and day/payload strings; read nullability may differ.

```scala
def writeCompact(source: DataFrame, path: String): DataFrame = {
  source.repartition(2, col("day")).write.mode("errorifexists").partitionBy("day").parquet(path)
  source.sparkSession.read.parquet(path)
}
```

```python
def write_compact(source, path):
    source.repartition(2, "day").write.mode("errorifexists").partitionBy("day").parquet(path)
    return source.sparkSession.read.parquet(path)
```

The comparison preserves semantic field types, values and duplicate occurrences while permitting reader nullability and column-position differences. A symmetric bag difference detects lost or extra rows that a count-only check could miss. The path belongs to this run, so error-if-exists prevents accidental overwrite even within the owned scratch namespace.

**Verification evidence:** Assert type mapping and exceptAll emptiness in both directions, plus row count and amount total.

### Exercise 2: Read a narrow filtered projection with an independent oracle

Select only id and amount for day=even and id>=1990. Return the five ordered tuples.

**Expected:** (1990,13930),(1992,13944),(1994,13958),(1996,13972),(1998,13986). No payload column is requested.

```scala
def filteredProduct(frame: DataFrame): DataFrame = {
  frame.filter(col("day") === "even" && col("id") >= 1990L).select("id", "amount")
}
```

```python
def filtered_product(frame):
    return frame.filter((F.col("day") == "even") & (F.col("id") >= 1990)).select("id", "amount")
```

The query combines a storage-partition value with a row-level numeric predicate but returns only the two requested fields. Its result oracle is independent of how the file reader applies those filters. Projection correctness and pruning evidence are checked separately so a narrow schema cannot conceal a wrong population.

**Verification evidence:** Assert every projected identity and amount and exact two-column output schema.

### Exercise 3: Locate partition, column and predicate evidence in the scan

Capture a FORMATTED plan for the selected query on the owned Parquet view. Extract ReadSchema, PartitionFilters and PushedFilters lines and interpret each scope.

**Expected:** ReadSchema has id and amount but not payload; PartitionFilters mentions day/even; PushedFilters includes the id lower bound.

```scala
def scanEvidence(frame: DataFrame): Map[String, String] = {
  frame.createOrReplaceTempView("ds60_spark_025_read")
  val text = frame.sparkSession
    .sql(
      "EXPLAIN FORMATTED SELECT id,amount FROM ds60_spark_025_read WHERE day='even' AND id>=1990"
    )
    .collect()
    .map(_.getString(0))
    .mkString("\n")
  Seq("ReadSchema", "PartitionFilters", "PushedFilters")
    .map(name => name -> text.linesIterator.filter(_.contains(name)).mkString("\n"))
    .toMap
}
```

```python
def scan_evidence(frame):
    frame.createOrReplaceTempView("ds60_spark_025_read")
    text = "\n".join(
        r[0]
        for r in frame.sparkSession.sql(
            "EXPLAIN FORMATTED SELECT id,amount FROM ds60_spark_025_read WHERE day='even' AND id>=1990"
        ).collect()
    )
    return {
        name: "\n".join(line for line in text.splitlines() if name in line)
        for name in ["ReadSchema", "PartitionFilters", "PushedFilters"]
    }
```

The plan separates directory pruning from column selection and pushed row predicates. Checking each line in its own scope avoids mistaking the original relation schema for the physical scan requirement. These fields show intended reader behavior; actual row-group or byte savings depend on file statistics and runtime measurements that this exercise does not fabricate.

**Verification evidence:** Assert the relevant field/predicate markers and retain the exact five-row output oracle; do not claim bytes skipped from the plan alone.

### Exercise 4: Compare a deliberately larger file count without changing data

Write the same source after repartition 12 using the same day directory partitioning. Inventory only.parquet data files and their actual byte sizes for both layouts.

**Expected:** Both round trips match the source bag. The many layout has more data files than compact; both byte totals are positive and below 32 MiB.

```scala
def fileInventory(path: String): (Int, Long) = {
  val stream = Files.walk(Paths.get(path))
  try {
    val files = stream
      .iterator()
      .asScala
      .filter(p => Files.isRegularFile(p) && p.getFileName.toString.endsWith(".parquet"))
      .toSeq
    (files.size, files.map(p => Files.size(p)).sum)
  } finally stream.close()
}
```

```python
def file_inventory(path):
    files = [p for p in Path(path).rglob("*.parquet") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)
```

The file counts and sizes come from the actual owned output rather than a formula based on writer partitions. Multiple tasks can write within the same directory partition. The larger file count illustrates potential metadata/opening overhead without claiming a universal timing penalty on this tiny local filesystem. Logical bag equality is still required before comparing layouts.

**Verification evidence:** Assert bag parity, file-count inequality and measured data-byte bounds. Ignore checksum and success-marker files in data counts.

### Exercise 5: Report storage partitions, files and scan partitions separately

Return a receipt with the number of day= directories, the data-file count and the read DataFrame execution-partition count for each layout.

**Expected:** Both layouts have 2 day directories. Data-file counts are the measured inventory values. Scan partitions are positive observed values and need not equal either other count.

```scala
def layoutReceipt(frame: DataFrame, path: String): (Int, Int, Int) = {
  val stream = Files.list(Paths.get(path))
  val directories =
    try
      stream
        .iterator()
        .asScala
        .count(p => Files.isDirectory(p) && p.getFileName.toString.startsWith("day="))
    finally stream.close()
  (directories, fileInventory(path)._1, frame.rdd.getNumPartitions)
}
```

```python
def layout_receipt(frame, path):
    directories = sum(p.is_dir() and p.name.startswith("day=") for p in Path(path).iterdir())
    return directories, file_inventory(path)[0], frame.rdd.getNumPartitions()
```

The receipt prevents three different meanings of partitioning from collapsing into one number. Directory partitions encode day values, data files reflect writer output, and scan partitions reflect reader scheduling decisions. Their relationship can change with file sizes, open-cost estimates and runtime configuration while the logical dataset remains identical.

**Verification evidence:** Assert two directory partitions and independent file-count consistency; print actual scan partition counts without imposing equality.

### Exercise 6: Reject an existing target and preserve its product

Attempt a second error-if-exists write to the already owned compact path. Require the expected analysis error, then read the original product and reconcile its bag.

**Expected:** The second write fails with an existing-path analysis exception; the original 2000-row product remains unchanged.

```scala
def rejectExisting(source: DataFrame, path: String): Unit = {
  var rejected = false
  try source.write.mode("errorifexists").parquet(path)
  catch { case _: org.apache.spark.sql.AnalysisException => rejected = true }
  require(rejected, "Existing path unexpectedly accepted")
}
```

```python
def reject_existing(source, path):
    try:
        source.write.mode("errorifexists").parquet(path)
    except AnalysisException:
        return
    raise AssertionError("Existing path unexpectedly accepted")
```

The intentional failure is confined to a path created by this run. The subsequent bag check verifies that the existing product survived. Error-if-exists prevents this overwrite attempt but is not a general atomic publication or concurrent-writer guarantee. The later staging/manifest chapter handles a broader restartable publication contract.

**Verification evidence:** Assert the exception and full original bag after the failed write. Do not delete or overwrite the target to make the retry succeed.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
