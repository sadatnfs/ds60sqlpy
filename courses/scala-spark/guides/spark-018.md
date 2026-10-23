# spark-018: Timestamp types, time zones and interval boundaries

Authored paired Scala/PySpark teaching content. The default fixtures are tiny,local and deterministic. Runtime acceptance,logical correctness and learner understanding remain separate evidence.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct design prerequisites: `spark-017`. The prepared baseline is Spark 4.0.1,Scala binary2.13,JDK 17 and Python 3.12. Read the [execution baseline](../execution-baseline.md); a proposed future tuple is not a runtime receipt.

## How to run this lesson

Open `spark-018` in the classroom and choose the Scala or PySpark implementation you understand. Prepare only its fixed `spark-local-scala` or `spark-local-python` profile,save your pad and run the complete source. Scala stages as `Main.scala` with `object Main`; Python stages as `main.py` with a main guard. Each program creates its own local[2] session,disables the UI,binds the driver to loopback and stops the session in finally. No external dataset,package download,JDBC connection or cloud service is requested.

The [Scala learner](../lessons/spark-018.scala) and [PySpark learner](../lessons/spark-018.py) run two complete demonstrations and retain six explicit task stubs. Use the [explained solutions](../solutions/spark-018_solutions.md) only after an attempt or an explicit worked comparison; the [Scala reference](../solutions/spark-018_solution.scala) and [PySpark reference](../solutions/spark-018_solution.py) contain complete assertions. A bounded collect is used only for the declared tiny fixture; do not copy it onto an unbounded or large production table.

## Learning objectives

- Distinguish an instant from a local timestamp and define event windows with explicit time-zone policy.
- State the input and output grain,schema,NULL policy and ordering before executing a transformation.
- Compare each language implementation with independent literal expectations,not only with the other implementation.

## Vocabulary and concepts

- **Instant:** A point on the time line that can be rendered in different local clocks without changing its epoch value.

- **Timestamp with local time-zone semantics:** Spark TIMESTAMP_LTZ stores an instant and applies the session zone for local parsing or rendering; it does not preserve the original textual offset.

- **Timestamp without time zone:** TIMESTAMP_NTZ represents local calendar and clock fields without declaring which instant they denote.

- **Half-open interval:** A range including its lower boundary and excluding its upper boundary, allowing adjacent periods without double counting.

- **Fold ambiguity:** A repeated local-clock time during a backward daylight-saving transition; resolving it requires an offset or an explicit policy.

A timestamp can answer two different questions: when did an event occur on a global timeline, or what local clock reading was written on a schedule? Treating these as interchangeable causes silent shifts. The lesson declares TIMESTAMP_LTZ for offset-bearing event strings and uses TIMESTAMP_NTZ only for a clock value whose instant has not been identified. The session zone is UTC except inside a tightly scoped rendering demonstration that restores its previous setting.

The input contains two different textual encodings of the same instant. Event 2 is 2024-11-03T01:30:00-07:00 and event 5 is 2024-11-03T08:30:00Z. Their epoch values must match after parsing. Event 3 is 2024-11-03T01:30:00-08:00, one hour later even though the local clock fields match event 2. An offset is part of the evidence identifying the instant; stripping it before parsing destroys that distinction.

America/Los_Angeles repeats the hour beginning 01:00 at the November 2024 backward transition. Both event 2 and event 3 therefore render as 01:30 in that zone, but they remain distinct instants. Converting a timestamp to a formatted string is a presentation step that may lose information. Joining or deduplicating on the displayed minute can merge independent events. The fixture deliberately includes equal local labels to make this information loss observable.

A local calendar day need not last 24 elapsed hours. The Los Angeles day 2024-11-03 starts at 07:00Z and ends at 08:00Z the next day, making 25 hours. The interval contract uses those explicit instant boundaries and retains event IDs 1,2,3,5. Event 6 is one second before the lower boundary and event 4 exactly equals the upper boundary. The lower event is included and the upper event excluded. Reusing this half-open convention for the next day avoids counting an event in both days.

The reference computes both lower and upper boundary instants from the supplied offset-bearing values. It does not infer daylight-saving policy from the host operating system or the Python datetime representation returned by collect. Epoch-second comparisons and Spark-side formatting keep the evidence tied to the declared Spark session. In a real application, calendar boundaries should be constructed from the business zone and date, with tested handling for historical zone rules and any unusual midnight transitions.

TIMESTAMP_NTZ is useful when local fields themselves are the data, such as an unresolved appointment request. It is not a portable shortcut for UTC. The local value 2024-11-03 01:30:00 stays the same clock string when rendered under UTC or Los Angeles, because no zone conversion is requested for NTZ. This stability does not identify which of the two Los Angeles instants was intended. Assigning a zone later requires an explicit ambiguity policy or additional offset evidence.

Parsing and acceptance are also separate. The final task uses try_to_timestamp to classify a valid offset-bearing value, a missing string and malformed text while ANSI mode remains enabled. A returned NULL can mean missing input or a failed parse, so the raw field determines the diagnostic reason. Quarantined timestamps cannot silently fall out of a WHERE condition and be described as zero events.

The lesson uses exact historical fixtures, not a claim that every business zone has the same daylight-saving transitions. Zone databases and runtime versions are recorded by the worker separately. The technique is to preserve sufficient timestamp evidence, declare types and zones, test boundary membership, and avoid assigning causal or chronological meaning to an ambiguous displayed clock value.

## Supplied local fixture

The complete source creates the owned local session described above, then constructs this explicit fixture. The worked examples below run in that same main function; there is no hidden notebook state.

```scala
import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

spark.conf.set("spark.sql.timestampType","TIMESTAMP_LTZ")
val schema = StructType(Seq(StructField("event_id",LongType,false),StructField("text",StringType,false)))
val raw = spark.createDataFrame(spark.sparkContext.parallelize(Seq(Row(1L,"2024-11-03T07:00:00Z"),Row(2L,"2024-11-03T01:30:00-07:00"),Row(3L,"2024-11-03T01:30:00-08:00"),Row(4L,"2024-11-04T08:00:00Z"),Row(5L,"2024-11-03T08:30:00Z"),Row(6L,"2024-11-03T06:59:59Z")),2),schema)
```

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType

spark.conf.set("spark.sql.timestampType","TIMESTAMP_LTZ")
schema = StructType([StructField("event_id",LongType(),False),StructField("text",StringType(),False)])
raw = spark.createDataFrame([(1,"2024-11-03T07:00:00Z"),(2,"2024-11-03T01:30:00-07:00"),(3,"2024-11-03T01:30:00-08:00"),(4,"2024-11-04T08:00:00Z"),(5,"2024-11-03T08:30:00Z"),(6,"2024-11-03T06:59:59Z")],schema=schema)
```

## Worked example / walkthrough

### Worked example 1

```scala
val pair = spark.sql("SELECT unix_timestamp(to_timestamp('2024-11-03T08:30:00Z')) AS utc, unix_timestamp(to_timestamp('2024-11-03T01:30:00-07:00')) AS offset")
val r = pair.first();assert(r.getLong(0) == r.getLong(1))
println("Different text, same instant")
```

```python
pair = spark.sql("SELECT unix_timestamp(to_timestamp('2024-11-03T08:30:00Z')) AS utc, unix_timestamp(to_timestamp('2024-11-03T01:30:00-07:00')) AS offset")
r = pair.first(); assert r[0] == r[1]
print("Different text, same instant")
```

The explicit offset makes both strings unambiguous. Comparing epoch seconds checks the instant rather than comparing their surface spelling. The original text can still be retained for provenance even though the timestamp value does not preserve its formatting.

### Worked example 2

```scala
val r = spark.sql("SELECT timestampdiff(HOUR,to_timestamp('2024-11-03T07:00:00Z'),to_timestamp('2024-11-04T08:00:00Z')) AS hours").first()
assert(r.getLong(0) == 25L)
println("Declared Los Angeles day spans 25 elapsed hours")
```

```python
r = spark.sql("SELECT timestampdiff(HOUR,to_timestamp('2024-11-03T07:00:00Z'),to_timestamp('2024-11-04T08:00:00Z')) AS hours").first()
assert r[0] == 25
print("Declared Los Angeles day spans 25 elapsed hours")
```

The calculation occurs with the session in UTC, so it measures elapsed hours between declared instants. A calendar reporting day is a zone-aware interval, not invariably a duration of 86400 seconds. The explicit boundaries make the exceptional day testable without assuming a host-local timezone.

## Exercises

### Exercise 1: Parse offset evidence into comparable instants

Return event_id, text, event_time by parsing the declared offset pattern yyyy-MM-ddTHH: mm: ss with a literal T and XXX offset. The session timestamp type must be LTZ.

**Expected result/shape:** All 6 rows parse. Epoch(event 2)=epoch(event 5), and epoch(event 3)-epoch(event 2)=3600 seconds.

**Verify:** Assert TimestampType, zero null timestamps, exact same-instant equality and the 3600-second separation.

**Progressive hint:** Use the pattern literal T inside single quotes and XXX for colon-bearing offsets or Z.

### Exercise 2: Render a zone without changing the underlying instant

Return ordered(event_id, formatted_clock) pairs for a requested zone, formatting yyyy-MM-dd HH: mm: ss. Set the zone only during materialization and restore the previous setting in finally.

**Expected result/shape:** Events 2 and 3 render 08:30 and 09:30 underUTC but both 01:30 underAmerica/Los_Angeles. Session zone is UTC afterward.

**Verify:** Assert both full clock strings for IDs 2/3 and the restored session configuration.

**Progressive hint:** Lazy DataFrames are not materialized evidence. Collect the bounded labels inside the scoped zone setting.

### Exercise 3: Filter a complete local day with instant boundaries

Select events in the half-open interval[2024-11-03T07:00:00Z,2024-11-04T08:00:00Z). Return all event columns.

**Expected result/shape:** Ordered event IDs[1,2,3,5]. Lower-bound ID 1 included, upper-bound ID 4 excluded and prior-second ID 6 excluded.

**Verify:** Assert the exact ID set and the 25-hour boundary duration; do not use an inclusive BETWEEN.

**Progressive hint:** Combine event_time>=lower and event_time<upper after parsing both boundaries as instants.

### Exercise 4: Keep an unresolved local timestamp as local fields

Under bothUTC and America/Los_Angeles, cast 2024-11-03 01:30:00 explicitly to TIMESTAMP_NTZ, inspect its schema and render it as a string. Restore the prior zone.

**Expected result/shape:** Both outputs are 2024-11-03 01:30:00 and the type is timestamp_ntz. No epoch or unique instant is claimed.

**Verify:** Assert identical local clock strings and explicit type under both zones, then confirm session restoration.

**Progressive hint:** Use an explicit SQL TIMESTAMP_NTZ cast rather than relying on the session default timestamp type.

### Exercise 5: Expose the information lost by a local clock key

For the two fold events 2 and 3, compare local formatted labels with their epoch values. Return(label_count, instant_count), retaining original event identity.

**Expected result/shape:** One distinct local label but two distinct instants. They must not be deduplicated by the displayed clock.

**Verify:** Assert(1,2) using separately materialized local labels and original epoch evidence.

**Progressive hint:** A rendering can be many-to-one; compare distinct counts without overwriting event_time.

### Exercise 6: Quarantine invalid timestamps without confusing missingness

Build an inline source containing a valid offset timestamp, bad text and NULL. Use try_to_timestamp with the declared offset pattern and classify accepted, malformed_timestamp, missing_timestamp.

**Expected result/shape:** IDs 1,2,3 have those reasons respectively; only 1 is accepted while ANSI remains true.

**Verify:** Assert all reason rows, one known timestamp and unchanged ANSI setting.

**Progressive hint:** Inspect raw missingness before classifying a NULL parsed timestamp as malformed.

## Common pitfalls

Do not confuse a timestamp's displayed timezone with its original textual offset. Do not use a local clock string as a unique event key. Do not add 86400 seconds to represent every local calendar day. Do not assign an arbitrary offset to an ambiguous NTZ value. Restoring a session setting matters even in a tiny demonstration because subsequent lazy analysis can depend on it. Preserve precision deliberately: epoch seconds are sufficient for this second-resolution fixture, but subsecond event ordering requires a higher-resolution representation and its own tests.

## Self-check

Explain the contract of `parseInstants` / `parse_instants` without reading its solution. Trace the specified boundary case,then explain the final exercise's evidence and limitation. Identify where a transformation builds a plan and where an action requests execution. Retain exact values or operator evidence rather than treating a successful process exit as proof of the whole learning objective.

## Next step

Use the [course route](../README.md) to continue. Paired-language agreement is useful only when both outputs also satisfy the independent fixture contract. Keep runtime/profile receipts separate from any cluster-performance or production-recovery claim.

## Primary sources and official APIs

- [Spark 4.0.1 timestamp data types](https://spark.apache.org/docs/4.0.1/sql-ref-datatypes.html)

- [Spark 4.0.1 datetime patterns](https://spark.apache.org/docs/4.0.1/sql-ref-datetime-pattern.html)

- [Spark 4.0.1 session time zone](https://spark.apache.org/docs/4.0.1/configuration.html)

- [Spark 4.0.1 try_to_timestamp](https://spark.apache.org/docs/4.0.1/api/sql/index.html#try_to_timestamp)

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-018: Timestamp types, time zones and interval boundaries.
Read courses/scala-spark/guides/spark-018.md and courses/scala-spark/lessons/spark-018.scala;the paired sources are courses/scala-spark/lessons/spark-018.scala and courses/scala-spark/lessons/spark-018.py.
Direct prerequisites: spark-017. Explain the schema,row grain and new Scala/Python/Spark syntax,ask me to predict a concrete result,then inspect my attempt. Give one hint at a time,review exact result and boundary evidence,and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies,start a remote service,reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
