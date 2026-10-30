# spark-019: Explained paired reference solutions

Read the [guide](../guides/spark-019.md) and attempt one language first. The [Scala reference](spark-019_solution.scala) and [PySpark reference](spark-019_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Validate identities before defining a winner

Reject an input unless event_id is known, positive and unique and entity is known. Allow missing event_time under the declared last-priority policy. Return Unit/None on success.

**Expected:** The eight-event fixture passes; adding another copy of event 1 fails. Missing-time event 7 is allowed.

```scala
def validateCandidates(events: DataFrame): Unit = {
  val metrics = events.agg(count(lit(1)), countDistinct("event_id")).first()
  require(metrics.getLong(0) == metrics.getLong(1), "event IDs must be known and unique")
  require(
    events.filter(col("event_id") <= 0L || col("entity").isNull).count() == 0L,
    "known positive identities required"
  )
}
```

```python
def validate_candidates(events):
    total, unique = events.agg(F.count(F.lit(1)), F.countDistinct("event_id")).first()
    if (
        total != unique
        or events.filter((F.col("event_id") <= 0) | F.col("entity").isNull()).count()
    ):
        raise ValueError("Known positive unique event IDs and known entity keys required")
```

A unique ID makes the final tie-breaker complete across this fixture. The validation does not equate missing time with missing identity: the former has an explicit selection policy while the latter prevents trustworthy attribution. Rejecting duplicate IDs is safer than arbitrarily choosing among contradictory versions whose ordering fields may be identical.

**Verification evidence:** Assert normal acceptance and explicit rejection after unioning a duplicate identity.

### Exercise 2: Rank all candidates with an explicit NULL rule

Add candidate_rank using row_number per entity, descending event_time with NULL last, then descending event_id. Keep all eight rows.

**Expected:** Ranks by event_id are 1:3,2:2,3:1,4:3,5:2,6:1,7:2,8:1.

```scala
def rankCandidates(events: DataFrame): DataFrame = {
  val order =
    Window.partitionBy("entity").orderBy(col("event_time").desc_nulls_last, col("event_id").desc)
  events.withColumn("candidate_rank", row_number().over(order))
}
```

```python
def rank_candidates(events):
    order = Window.partitionBy("entity").orderBy(
        F.col("event_time").desc_nulls_last(), F.col("event_id").desc()
    )
    return events.withColumn("candidate_rank", F.row_number().over(order))
```

Window partitioning keeps entities independent, and the ordering fields express the winner policy directly. NULL-last is deliberate rather than an accidental default. Retaining every ranked candidate creates an auditable explanation of why a row won or lost; filtering immediately would make debugging incorrect tie-breaking harder.

**Verification evidence:** Assert the full ID/rank table and input count 8.

### Exercise 3: Select stable winners across physical layouts

Validate candidates, rank them and retain rank 1. Compare winner IDs after repartitioning to 1,3 and 4 partitions, then compare an equivalentSQL row_number query.

**Expected:** Every case yields event IDs[3,6,8], one per entity. SQL returns the same literal winners.

```scala
def winners(events: DataFrame): DataFrame = {
  validateCandidates(events)
  rankCandidates(events).filter(col("candidate_rank") === 1).drop("candidate_rank")
}
```

```python
def winners(events):
    validate_candidates(events)
    return rank_candidates(events).filter(F.col("candidate_rank") == 1).drop("candidate_rank")
```

The input gate and complete order jointly establish the selection contract. Repartition checks guard against relying on arrival order, while the literal winner list guards against a shared SQL/DataFrame policy error. This is a correctness test on eight rows. It provides no evidence that a particular partition count is faster or appropriate for a production workload.

**Verification evidence:** Assert exact winners in every layout and SQL, not just equal row counts.

### Exercise 4: Prove why timestamp-only ordering is incomplete

Use dense_rank ordered only by descending event_time with NULL last, returning all rank 1 candidates. Report the candidate IDs rather than choosing an arbitrary winner.

**Expected:** Top-time candidates[2,3,5,6,8]. Entities A and B each have two admissible candidates under the incomplete rule.

```scala
def topTimeCandidates(events: DataFrame): DataFrame = {
  val order = Window.partitionBy("entity").orderBy(col("event_time").desc_nulls_last)
  events
    .withColumn("time_rank", dense_rank().over(order))
    .filter(col("time_rank") === 1)
    .drop("time_rank")
}
```

```python
def top_time_candidates(events):
    order = Window.partitionBy("entity").orderBy(F.col("event_time").desc_nulls_last())
    return (
        events.withColumn("time_rank", F.dense_rank().over(order))
        .filter(F.col("time_rank") == 1)
        .drop("time_rank")
    )
```

The candidate relation shows the under-specification directly. Multiple top-time rows are a fact about the input, not a probabilistic claim about how a scheduler will order them today. A repeatable accidental survivor does not strengthen the business contract. A documented tie-breaker or an explicit ambiguity rejection is needed to produce one trusted winner.

**Verification evidence:** Assert the five candidate identities and the two ambiguous entity keys. Do not require unstable executions to change output.

### Exercise 5: Distinguish occurrence totals from time-peer totals

Return event_id, rows_total, peer_total. ROWS uses ascending time NULL last then ID and an unbounded-preceding/current-row frame. RANGE uses only ascending time NULL last over the same cumulative boundary.

**Expected:** By ID:1(10,10),2(30,60),3(60,60),4(40,40),5(90,150),6(150,150),7(150,150),8(80,80).

```scala
def runningTotals(events: DataFrame): DataFrame = {
  val rowsFrame = Window
    .partitionBy("entity")
    .orderBy(col("event_time").asc_nulls_last, col("event_id"))
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
  val peerFrame = Window
    .partitionBy("entity")
    .orderBy(col("event_time").asc_nulls_last)
    .rangeBetween(Window.unboundedPreceding, Window.currentRow)
  events
    .withColumn("rows_total", sum("amount").over(rowsFrame))
    .withColumn("peer_total", sum("amount").over(peerFrame))
    .select("event_id", "rows_total", "peer_total")
}
```

```python
def running_totals(events):
    rows_frame = (
        Window.partitionBy("entity")
        .orderBy(F.col("event_time").asc_nulls_last(), "event_id")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )
    peer_frame = (
        Window.partitionBy("entity")
        .orderBy(F.col("event_time").asc_nulls_last())
        .rangeBetween(Window.unboundedPreceding, Window.currentRow)
    )
    return (
        events.withColumn("rows_total", F.sum("amount").over(rows_frame))
        .withColumn("peer_total", F.sum("amount").over(peer_frame))
        .select("event_id", "rows_total", "peer_total")
    )
```

The two frames use different membership rules. A row frame progresses through ordered occurrences, while the time-only range includes all equal-time peers together. A final event-ID display order does not alter those memberships. The missing-time event is last within entity C under the declared policy and accumulates the known-time event amount before its own.

**Verification evidence:** Assert all eight tuples, especially tied IDs 2/3 and the missing-time event 7.

### Exercise 6: Interpret lag without claiming strict temporal availability

Using ascending time NULL last then event_id, return event_id, previous_id, gap_seconds. Lag the event identity and time, then subtract epoch seconds.

**Expected:** 1(NULL, NULL),2(1,60),3(2,0),4(NULL, NULL),5(4,120),6(5,0),7(8, NULL),8(NULL, NULL).

```scala
def previousEvidence(events: DataFrame): DataFrame = {
  val order =
    Window.partitionBy("entity").orderBy(col("event_time").asc_nulls_last, col("event_id"))
  events
    .withColumn("previous_id", lag(col("event_id"), 1).over(order))
    .withColumn("previous_time", lag(col("event_time"), 1).over(order))
    .withColumn(
      "gap_seconds",
      unix_timestamp(col("event_time")) - unix_timestamp(col("previous_time"))
    )
    .select("event_id", "previous_id", "gap_seconds")
}
```

```python
def previous_evidence(events):
    order = Window.partitionBy("entity").orderBy(F.col("event_time").asc_nulls_last(), "event_id")
    return (
        events.withColumn("previous_id", F.lag("event_id", 1).over(order))
        .withColumn("previous_time", F.lag("event_time", 1).over(order))
        .withColumn(
            "gap_seconds", F.unix_timestamp("event_time") - F.unix_timestamp("previous_time")
        )
        .select("event_id", "previous_id", "gap_seconds")
    )
```

The previous identity proves which occurrence supplied the lagged field. Zero gaps expose tied timestamps rather than pretending the ID order supplies elapsed time. EntityC shows that a known predecessor does not guarantee a known duration. Prediction features would additionally need event-time and availability-time eligibility; this reproducible lag alone does not establish a leakage-free historical feature.

**Verification evidence:** Assert the complete identity/gap rows and explain zero gaps and the known previous ID with unknown duration.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
