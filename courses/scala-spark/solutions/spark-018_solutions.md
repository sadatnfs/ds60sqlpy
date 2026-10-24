# spark-018: Explained paired reference solutions

Read the [guide](../guides/spark-018.md) and attempt one language first. The [Scala reference](spark-018_solution.scala) and [PySpark reference](spark-018_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Parse offset evidence into comparable instants

Return event_id, text, event_time by parsing the declared offset pattern yyyy-MM-ddTHH: mm: ss with a literal T and XXX offset. The session timestamp type must be LTZ.

**Expected:** All 6 rows parse. Epoch(event 2)=epoch(event 5), and epoch(event 3)-epoch(event 2)=3600 seconds.

```scala
def parseInstants(raw: DataFrame): DataFrame = {
  raw.withColumn("event_time",to_timestamp(col("text"),"yyyy-MM-dd'T'HH:mm:ssXXX"))
}
```

```python
def parse_instants(raw):
    return raw.withColumn("event_time",F.to_timestamp("text","yyyy-MM-dd'T'HH:mm:ssXXX"))
```

The parser converts each explicit offset into a common instant representation. LTZ affects local rendering and zone-free parsing; it does not retain a different timezone object per row. Epoch equality therefore detects equivalent instants across textual offsets. The adjacent-fold event remains one hour later, preventing a comparison based only on matching local clock fields.

**Verification evidence:** Assert TimestampType, zero null timestamps, exact same-instant equality and the 3600-second separation.

### Exercise 2: Render a zone without changing the underlying instant

Return ordered(event_id, formatted_clock) pairs for a requested zone, formatting yyyy-MM-dd HH: mm: ss. Set the zone only during materialization and restore the previous setting in finally.

**Expected:** Events 2 and 3 render 08:30 and 09:30 underUTC but both 01:30 underAmerica/Los_Angeles. Session zone is UTC afterward.

```scala
def renderClock(events: DataFrame, zone: String): Seq[(Long,String)] = {
  val spark = events.sparkSession
  val previous = spark.conf.get("spark.sql.session.timeZone")
  try {
    spark.conf.set("spark.sql.session.timeZone",zone)
    events.select(col("event_id"),date_format(col("event_time"),"yyyy-MM-dd HH:mm:ss").as("clock")).orderBy("event_id").collect().toSeq.map(r => (r.getLong(0),r.getString(1)))
  } finally { spark.conf.set("spark.sql.session.timeZone",previous) }
}
```

```python
def render_clock(events, zone):
    spark = events.sparkSession
    previous = spark.conf.get("spark.sql.session.timeZone")
    try:
        spark.conf.set("spark.sql.session.timeZone",zone)
        return [tuple(r) for r in events.select("event_id",F.date_format("event_time","yyyy-MM-dd HH:mm:ss").alias("clock")).orderBy("event_id").collect()]
    finally:
        spark.conf.set("spark.sql.session.timeZone",previous)
```

The same instants produce different display labels, and two distinct instants can share a local label during a fold. Materializing while the chosen zone is active makes the observation explicit. Finally-based restoration prevents the demonstration from changing the interpretation of a later query. Display strings should not replace the original instant or event identity.

**Verification evidence:** Assert both full clock strings for IDs 2/3 and the restored session configuration.

### Exercise 3: Filter a complete local day with instant boundaries

Select events in the half-open interval[2024-11-03T07:00:00Z,2024-11-04T08:00:00Z). Return all event columns.

**Expected:** Ordered event IDs[1,2,3,5]. Lower-bound ID 1 included, upper-bound ID 4 excluded and prior-second ID 6 excluded.

```scala
def localDay(events: DataFrame): DataFrame = {
  val lower = to_timestamp(lit("2024-11-03T07:00:00Z"))
  val upper = to_timestamp(lit("2024-11-04T08:00:00Z"))
  events.filter(col("event_time") >= lower && col("event_time") < upper)
}
```

```python
def local_day(events):
    lower = F.to_timestamp(F.lit("2024-11-03T07:00:00Z"))
    upper = F.to_timestamp(F.lit("2024-11-04T08:00:00Z"))
    return events.filter((F.col("event_time")>=lower)&(F.col("event_time")<upper))
```

The condition expresses membership in a reporting interval independently of a displayed timestamp string. Adjacent half-open periods share a boundary instant without sharing an event. Adding a fixed 24-hour duration would end this particular local day too early. The test includes both exact boundaries and a nearby exterior value so an accidental BETWEEN or strict lower comparison fails visibly.

**Verification evidence:** Assert the exact ID set and the 25-hour boundary duration; do not use an inclusive BETWEEN.

### Exercise 4: Keep an unresolved local timestamp as local fields

Under bothUTC and America/Los_Angeles, cast 2024-11-03 01:30:00 explicitly to TIMESTAMP_NTZ, inspect its schema and render it as a string. Restore the prior zone.

**Expected:** Both outputs are 2024-11-03 01:30:00 and the type is timestamp_ntz. No epoch or unique instant is claimed.

```scala
def localFields(spark: SparkSession): Seq[String] = {
  val previous = spark.conf.get("spark.sql.session.timeZone")
  try {
    Seq("UTC","America/Los_Angeles").map { zone =>
      spark.conf.set("spark.sql.session.timeZone",zone)
      val frame = spark.sql("SELECT CAST('2024-11-03 01:30:00' AS TIMESTAMP_NTZ) AS local_time")
      assert(frame.schema("local_time").dataType.typeName == "timestamp_ntz")
      frame.select(col("local_time").cast("string")).first().getString(0)
    }
  } finally { spark.conf.set("spark.sql.session.timeZone",previous) }
}
```

```python
def local_fields(spark):
    previous = spark.conf.get("spark.sql.session.timeZone")
    try:
        results = []
        for zone in ["UTC","America/Los_Angeles"]:
            spark.conf.set("spark.sql.session.timeZone",zone)
            frame = spark.sql("SELECT CAST('2024-11-03 01:30:00' AS TIMESTAMP_NTZ) AS local_time")
            assert frame.schema["local_time"].dataType.typeName() == "timestamp_ntz"
            results.append(frame.select(F.col("local_time").cast("string")).first()[0])
        return results
    finally:
        spark.conf.set("spark.sql.session.timeZone",previous)
```

NTZ deliberately represents local fields without embedding an instant interpretation. Stable rendering across session zones is evidence of that local-field contract, not proof that both zones refer to the same instant. The repeated Los Angeles 01:30 requires an offset or ambiguity policy before conversion to the event timeline. Choosing NTZ merely to avoid timezone bugs would conceal the unresolved decision.

**Verification evidence:** Assert identical local clock strings and explicit type under both zones, then confirm session restoration.

### Exercise 5: Expose the information lost by a local clock key

For the two fold events 2 and 3, compare local formatted labels with their epoch values. Return(label_count, instant_count), retaining original event identity.

**Expected:** One distinct local label but two distinct instants. They must not be deduplicated by the displayed clock.

```scala
def foldEvidence(events: DataFrame): (Int,Int) = {
  val fold = events.filter(col("event_id").isin(2L,3L))
  val labels = renderClock(fold,"America/Los_Angeles").map(_._2).distinct
  val instants = fold.select(unix_timestamp(col("event_time"))).collect().map(_.getLong(0)).distinct
  (labels.size,instants.length)
}
```

```python
def fold_evidence(events):
    fold = events.filter(F.col("event_id").isin(2,3))
    labels = {label for _,label in render_clock(fold,"America/Los_Angeles")}
    instants = {r[0] for r in fold.select(F.unix_timestamp("event_time")).collect()}
    return len(labels),len(instants)
```

A formatted clock is an intentionally lossy projection here. The two-source-ID relation demonstrates the collision directly and rules out the explanation that the source contained a duplicate event. Keeping event identity and the original instant allows correct joins, ordering and replay even when an analyst chooses a local label for display.

**Verification evidence:** Assert(1,2) using separately materialized local labels and original epoch evidence.

### Exercise 6: Quarantine invalid timestamps without confusing missingness

Build an inline source containing a valid offset timestamp, bad text and NULL. Use try_to_timestamp with the declared offset pattern and classify accepted, malformed_timestamp, missing_timestamp.

**Expected:** IDs 1,2,3 have those reasons respectively; only 1 is accepted while ANSI remains true.

```scala
def parseLedger(spark: SparkSession): DataFrame = {
  val source = spark.sql("SELECT * FROM VALUES (1,'2024-01-01T00:00:00Z'),(2,'bad'),(3,CAST(NULL AS STRING)) AS v(id,text)")
  source.withColumn("parsed",try_to_timestamp(col("text"),lit("yyyy-MM-dd'T'HH:mm:ssXXX"))).withColumn("reason",when(col("text").isNull,"missing_timestamp").when(col("parsed").isNull,"malformed_timestamp").otherwise("accepted"))
}
```

```python
def parse_ledger(spark):
    source = spark.sql("SELECT * FROM VALUES (1,'2024-01-01T00:00:00Z'),(2,'bad'),(3,CAST(NULL AS STRING)) AS v(id,text)")
    return source.withColumn("parsed",F.try_to_timestamp("text",F.lit("yyyy-MM-dd'T'HH:mm:ssXXX"))).withColumn("reason",F.when(F.col("text").isNull(),"missing_timestamp").when(F.col("parsed").isNull(),"malformed_timestamp").otherwise("accepted"))
```

Try parsing exposes malformed input as data so a controlled ingestion boundary can retain its reason. RawNULL still needs a separate category because no invalid textual timestamp was supplied. The accepted count and full reason ledger reconcile the population, preventing a downstream time filter from silently discarding rejected records and calling the remaining count complete.

**Verification evidence:** Assert all reason rows, one known timestamp and unchanged ANSI setting.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
