# spark-025: Parquet, column pruning and file layout

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-024`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-025` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-025.scala) and [PySpark learner](../lessons/spark-025.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-025_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-025_solution.scala) and [PySpark reference](../solutions/spark-025_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Use a columnar local file layout and verify that schema and logical results survive round trips.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Parquet:** A column-oriented file format whose metadata describes field types and can support selective reading.

- **Directory partition:** A storage path segment such as day=even that represents a partition-column value; it is distinct from an execution partition.

- **Partition pruning:** Excluding storage partitions using their directory metadata before reading their row data.

- **Predicate pushdown:** Passing a supported row predicate to the data source so it can use available metadata or reader capabilities; actual savings require measurement.

- **Small-file layout:** A product split across many tiny files whose listing, opening and scheduling costs may be large relative to useful data.

- **Round-trip contract:** A declared comparison of field types, values and occurrence multiplicity after writing and reading a product.

The fixture creates 2000 explicit-schema rows with a unique long id, a string partition value even or odd, an amount equal to seven times id, and a32-character payload. The round-trip contract concerns every field and occurrence. It does not require Parquet to preserve the original execution partitions, row arrival order or writer-side nonnull flags. Spark can mark read fields nullable for compatibility even though this particular file contains no nulls.

The compact layout repartitions by the day field before writing partitionBy(day) into a fresh owned directory. Equal day values therefore reach one writer partition in this controlled setup, while separate output directories represent day=even and day=odd. The larger-file-count comparison repartitions the same rows into 12 round-robin execution partitions before the same directory partitioning. Several writers can then create a file for each day. Both layouts must read back the same logical bag.

A storage directory partition is not an executor partition. A file is also not necessarily a scan partition: Spark can combine small files into fewer scan tasks or split larger files according to reader rules and configuration. The fifth exercise reports all three quantities separately. The fact that this example has two day directories does not imply two files, two executors or two tasks in every subsequent stage.

The selected query asks for id and amount only, with day=even and id>=1990. Its exact IDs are 1990,1992,1994,1996,1998. The day predicate can be represented in PartitionFilters because day comes from directory structure. The id predicate can appear in DataFilters and PushedFilters, and the scan ReadSchema can omit payload. These are separate mechanisms: directory pruning chooses storage partitions, column pruning chooses fields, and predicate pushdown communicates a row-level condition to the reader.

Plan evidence establishes what Spark requested from the reader. It does not establish a specific byte saving without runtime metrics. A file can satisfy a pushed predicate description while its statistics are too broad to skip much data. A residual Filter can remain necessary for exact semantics. The lesson therefore asserts the requested fields, predicate markers and exact output, while avoiding a fabricated percentage improvement.

The inventory counts only files ending in.parquet as data files. Success markers, checksum sidecars and directories are not counted as data records. Total data bytes are measured from those files, not inferred from row count. Both layouts stay well inside the worker scratch budget. The many-file layout should have more data files than the compact layout for this fixture, but no exact file-count or compression-ratio promise is generalized to every writer, version or configuration.

A duplicate-sensitive exceptAll comparison in both directions checks the round trip. A count or total alone could hide a missing occurrence paired with a duplicate. The compared columns are selected in a common order because a partition column can be reconstructed at a different position on read. Type checks use the field-to-type mapping, while the guide explains why writer/read nullability is not a byte-identical schema assertion.

The final task exercises error-if-exists on the already owned compact path. The second write must fail, and the original data must remain readable with the same bag. This is a write-mode boundary, not transactional publication or a complete concurrent-writer protocol. A later chapter introduces staging and a publication manifest. Here each run creates a new outer scratch root, so the deliberate existing-path error concerns only data created by that run.

All cleanup is scoped to that fresh root. The program does not delete a user-selected directory, replace an existing checkpoint or change a remote table. The scan and write plans remain local, and the owned session stops in finally. Tiny-file observations explain mechanisms; they do not measure a distributed object store's metadata latency or establish a production file-size recommendation.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files,Path,Paths}
import scala.jdk.CollectionConverters._

ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(),".ds60-spark-025-")
val schema = StructType(Seq(StructField("id",LongType,false),StructField("day",StringType,false),StructField("amount",LongType,false),StructField("payload",StringType,false)))
val source = spark.createDataFrame(spark.sparkContext.parallelize((0L until 2000L).map(id => Row(id,if(id%2L==0L) "even" else "odd",id*7L,"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")),4),schema)
val compactPath = ownedRoot.resolve("compact").toString
val manyPath = ownedRoot.resolve("many").toString
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
from pyspark.errors import AnalysisException

owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-025-",dir=".")).resolve()
schema = StructType([StructField("id",LongType(),False),StructField("day",StringType(),False),StructField("amount",LongType(),False),StructField("payload",StringType(),False)])
source = spark.createDataFrame([(i,"even" if i%2==0 else "odd",i*7,"x"*32) for i in range(2000)],schema=schema)
compact_path = str(owned_root/"compact")
many_path = str(owned_root/"many")
```

## Worked example / walkthrough

### Worked example 1

```scala
assert(source.schema("id").dataType == LongType && source.count() == 2000L)
assert(source.agg(sum("amount")).first().getLong(0) == 13993000L)
println("Explicit-schema source:2000 rows,total13993000")
```

```python
assert isinstance(source.schema["id"].dataType,LongType) and source.count() == 2000
assert source.agg(F.sum("amount")).first()[0] == 13993000
print("Explicit-schema source:2000 rows,total13993000")
```

The declared long type and arithmetic total provide an input contract before any file layout is chosen. File format, writer task count and directory partitioning are downstream physical decisions that must preserve these values and occurrence identities.

### Worked example 2

```scala
val ids = (1990L until 2000L).filter(_%2L==0L)
assert(ids == Seq(1990L,1992L,1994L,1996L,1998L))
println("Independent filtered identity oracle=" + ids)
```

```python
ids = [i for i in range(1990,2000) if i%2==0]
assert ids == [1990,1992,1994,1996,1998]
print("Independent filtered identity oracle=",ids)
```

The expected filtered population comes directly from the declared even/odd rule and lower bound. It does not depend on the same Spark scan or predicate implementation later used to produce the result.

## Exercises

### Exercise 1: Write and validate a compact partitioned round trip

Repartition source by day into 2 execution partitions, write Parquet with error-if-exists and partitionBy(day), then read it back. Compare field types and the complete duplicate-sensitive bag.

**Expected result/shape:** 2000 rows and total 13993000 survive. Types remain id/amount bigints and day/payload strings; read nullability may differ.

**Verify:** Assert type mapping and exceptAll emptiness in both directions, plus row count and amount total.

**Progressive hint:** Project columns into the same order before comparing; partition columns can move during readback.

### Exercise 2: Read a narrow filtered projection with an independent oracle

Select only id and amount for day=even and id>=1990. Return the five ordered tuples.

**Expected result/shape:** (1990,13930),(1992,13944),(1994,13958),(1996,13972),(1998,13986). No payload column is requested.

**Verify:** Assert every projected identity and amount and exact two-column output schema.

**Progressive hint:** Keep the partition predicate before projecting away day; column selection does not remove its filtering role.

### Exercise 3: Locate partition, column and predicate evidence in the scan

Capture a FORMATTED plan for the selected query on the owned Parquet view. Extract ReadSchema, PartitionFilters and PushedFilters lines and interpret each scope.

**Expected result/shape:** ReadSchema has id and amount but not payload; PartitionFilters mentions day/even; PushedFilters includes the id lower bound.

**Verify:** Assert the relevant field/predicate markers and retain the exact five-row output oracle; do not claim bytes skipped from the plan alone.

**Progressive hint:** Different scan-detail lines describe different pruning and pushdown mechanisms.

### Exercise 4: Compare a deliberately larger file count without changing data

Write the same source after repartition 12 using the same day directory partitioning. Inventory only.parquet data files and their actual byte sizes for both layouts.

**Expected result/shape:** Both round trips match the source bag. The many layout has more data files than compact; both byte totals are positive and below 32 MiB.

**Verify:** Assert bag parity, file-count inequality and measured data-byte bounds. Ignore checksum and success-marker files in data counts.

**Progressive hint:** Use a filesystem walk only under the fresh owned root and count files by the data suffix.

### Exercise 5: Report storage partitions, files and scan partitions separately

Return a receipt with the number of day= directories, the data-file count and the read DataFrame execution-partition count for each layout.

**Expected result/shape:** Both layouts have 2 day directories. Data-file counts are the measured inventory values. Scan partitions are positive observed values and need not equal either other count.

**Verify:** Assert two directory partitions and independent file-count consistency; print actual scan partition counts without imposing equality.

**Progressive hint:** A file reader can group files into scan tasks; the directory hierarchy describes data values.

### Exercise 6: Reject an existing target and preserve its product

Attempt a second error-if-exists write to the already owned compact path. Require the expected analysis error, then read the original product and reconcile its bag.

**Expected result/shape:** The second write fails with an existing-path analysis exception; the original 2000-row product remains unchanged.

**Verify:** Assert the exception and full original bag after the failed write. Do not delete or overwrite the target to make the retry succeed.

**Progressive hint:** This tests a write-mode boundary; it does not establish a transactional publication protocol.

## Common pitfalls

Do not count all filesystem entries as data files or assume one file per storage partition. Do not assert read nullability must equal writer nullability. Do not equate a PushedFilters line with measured bytes skipped. Preserve duplicate occurrences when validating a round trip. An overwrite mode is not a transaction protocol. This lesson cleans only its newly created outer root, and never removes an arbitrary user dataset or existing checkpoint.

## Self-check

Explain the contract of `writeCompact` / `write_compact` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 Parquet data source and partition discovery](https://spark.apache.org/docs/4.0.1/sql-data-sources-parquet.html)

- [Spark 4.0.1 file partition configuration](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html)

- [Spark 4.0.1 save modes](https://spark.apache.org/docs/4.0.1/sql-data-sources-load-save-functions.html)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-025: Parquet, column pruning and file layout.
Read courses/scala-spark/guides/spark-025.md and courses/scala-spark/lessons/spark-025.py;the paired sources are courses/scala-spark/lessons/spark-025.scala and courses/scala-spark/lessons/spark-025.py.
Direct prerequisites: spark-024. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
