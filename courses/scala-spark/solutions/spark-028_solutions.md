# spark-028: Explained paired reference solutions

Read the [guide](../guides/spark-028.md) and attempt one language first. The [Scala reference](spark-028_solution.scala) and [PySpark reference](spark-028_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Classify facts and reconcile the whole source population

Add reason using missing fact identity, negative known amount, then accepted precedence. Retain all source records; acceptedNULL amounts remain unknown.

**Expected:** Accepted 2000, rejected 2 with source 2001 missing_identity and 2002 negative_amount. Accepted unique fact IDs 2000 and known amounts 1800.

```scala
def classifyFacts(raw: DataFrame): DataFrame = {
  raw.withColumn("reason",when(col("fact_id").isNull,"missing_identity").when(col("amount") < 0L,"negative_amount").otherwise("accepted"))
}
```

```python
def classify_facts(raw):
    return raw.withColumn("reason",F.when(F.col("fact_id").isNull(),"missing_identity").when(F.col("amount")<0,"negative_amount").otherwise("accepted"))
```

The row-preserving ledger makes rejected records visible instead of dropping them inside a later join or filter. Its precedence produces one interpretable reason per source occurrence. Known-amount counts remain separate from accepted row counts, so allowingNULL measurements cannot silently be presented as complete observed revenue.

**Verification evidence:** Assert every rejection identity/reason, source reconciliation and accepted uniqueness/completeness counts.

### Exercise 2: Select an approved unique dimension before tuning

Keep approved dimension rows, require at most 100 rows and known unique keys, then return key, factor. Reject a candidate with a second approved key 0 row.

**Expected:** Reviewed keys 0..5, factors 2..7, six rows. The conflicting approved candidate fails before joining.

```scala
def reviewDimension(raw: DataFrame): DataFrame = {
  val reviewed = raw.filter(col("approved")).select("key","factor")
  val rows = reviewed.limit(101).count()
  require(rows <= 100L && reviewed.agg(countDistinct("key")).first().getLong(0) == rows,"Approved keys must be known,unique and bounded")
  reviewed
}
```

```python
def review_dimension(raw):
    reviewed = raw.filter(F.col("approved")).select("key","factor")
    rows = reviewed.limit(101).count()
    if rows > 100 or reviewed.agg(F.countDistinct("key")).first()[0] != rows:
        raise ValueError("Approved keys must be known,unique and bounded")
    return reviewed
```

Review establishes the build-side grain before either join strategy is evaluated. The row budget keeps the candidate bounded, and countDistinct excludesNULL keys as well as detecting multiplicity. The rejected negative control prevents a later optimization from hiding an unresolved business-version conflict.

**Verification evidence:** Assert all six key/factor rows and the explicit duplicate-approved rejection.

### Exercise 3: Produce the correct baseline and independent key summary

Build the ordinary equality join over accepted facts and reviewed dimension, projecting source_id, fact_id, key, amount, factor. Summarize per key with rows, known amounts, total amount and weighted total.

**Expected:** Key 0:(1600,1440,5755,11510);1:(100,100,401,1203);2:(100,80,321,1284);3:(100,100,398,1990);4:(100,80,321,1926).

```scala
def baselineProduct(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts.join(dimension,Seq("key"),"inner").select("source_id","fact_id","key","amount","factor")
}
```

```python
def baseline_product(facts, dimension):
    return facts.join(dimension,on="key",how="inner").select("source_id","fact_id","key","amount","factor")
```

The per-key oracle checks more than the grand total. It detects a wrong factor mapping or shifted group population that could be obscured by compensating totals. Known counts expose the NULL measurement population, and the full accepted-identity count verifies one product row per accepted fact under the reviewed dimension contract.

**Verification evidence:** Assert all five summary tuples and aggregate metrics 2000,2000,1800,7196,17913.

### Exercise 4: Compare a bounded broadcast strategy with the same business contract

Broadcast the reviewed dimension for the same equality join and projection. Preserve all output occurrences using exceptAll in both directions against baseline.

**Expected:** Identical metrics and empty directional bag differences. The candidate plan containsBroadcastHashJoin.

```scala
def broadcastProduct(facts: DataFrame, dimension: DataFrame): DataFrame = {
  facts.join(broadcast(dimension),Seq("key"),"inner").select("source_id","fact_id","key","amount","factor")
}
```

```python
def broadcast_product(facts, dimension):
    return facts.join(F.broadcast(dimension),on="key",how="inner").select("source_id","fact_id","key","amount","factor")
```

The candidate changes physical execution while retaining the same selected inputs, join condition and output fields. The symmetric bag comparison avoids a large driver collect and protects duplicate-sensitive identity semantics. A successful plan marker is meaningful only after these correctness checks; it does not certify safe memory use for an arbitrary larger dimension.

**Verification evidence:** Assert the full metric map, both distributed bag differences and the observed strategy marker.

### Exercise 5: Assemble an honest bounded comparison receipt

Return version, master, AQE and automatic broadcast threshold as named fields. Attach key frequencies, the baseline/candidate plans and each observed summary-query exchange metric map.

**Expected:** Spark 4.0.1, local[2], AQEfalse, threshold-1; key 0 frequency 1600 and others 100. Both runs expose actual nonempty exchange observations. No peak-memory or throughput value is invented.

```scala
def configurationReceipt(spark: SparkSession): Map[String,String] = {
  Map("version"->spark.version,"master"->spark.sparkContext.master,"aqe"->spark.conf.get("spark.sql.adaptive.enabled"),"automatic_broadcast"->spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
}
```

```python
def configuration_receipt(spark):
    return {"version":spark.version,"master":spark.sparkContext.master,"aqe":spark.conf.get("spark.sql.adaptive.enabled"),"automatic_broadcast":spark.conf.get("spark.sql.autoBroadcastJoinThreshold")}
```

The packet makes configuration, skew, logical results and measured operator counters separately inspectable. The exchange maps belong to summary queries that actually ran; they are not counters read from an unexecuted fresh plan. The report deliberately leaves unmeasured peak memory and production throughput unspecified instead of filling them with guesses or local timing folklore.

**Verification evidence:** Assert controlled settings and frequency ledger, then print plans and separately labeled actual metric maps.

### Exercise 6: Roll back execution policy without rolling back data quality

Choose baseline or broadcast using an explicit Boolean switch over the same accepted facts and reviewed dimension. Switch back to baseline and revalidate the complete product.

**Expected:** Both switch positions satisfy the same metric map and bag contract. The disabled position has no BroadcastHashJoin under the controlled configuration.

```scala
def chooseProduct(facts: DataFrame, dimension: DataFrame, useBroadcast: Boolean): DataFrame = {
  if(useBroadcast) broadcastProduct(facts,dimension) else baselineProduct(facts,dimension)
}
```

```python
def choose_product(facts, dimension, use_broadcast):
    if not isinstance(use_broadcast,bool):
        raise ValueError("Explicit Boolean strategy switch required")
    return broadcast_product(facts,dimension) if use_broadcast else baseline_product(facts,dimension)
```

The rollback boundary is deliberately narrower than the business-data contract. It restores a known correct strategy while retaining acceptance and approved-dimension decisions. This makes an optimization reversible without reintroducing the data-quality defects that originally prevented trustworthy metrics. Production rollout would add representative resource and reliability qualification beyond this local capstone.

**Verification evidence:** Assert golden metrics and bag equality after rollback, and inspect the restored baseline plan.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
