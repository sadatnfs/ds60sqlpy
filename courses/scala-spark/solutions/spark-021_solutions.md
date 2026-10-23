# spark-021: Explained paired reference solutions

Read the [guide](../guides/spark-021.md) and attempt one language first. The [Scala reference](spark-021_solution.scala) and [PySpark reference](spark-021_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Check the query meaning before its execution plan

Execute the projection query and return ordered(id, doubled) tuples. Compare all nine rows with the literal rule id 3..11, doubled=20*id.

**Expected:** Nine tuples from(3,60) through(11,220), with no missing or extra identities.

```scala
def projectionResult(spark: SparkSession, query: String): Seq[(Long,Long)] = {
  spark.sql(query).orderBy("id").collect().toSeq.map(r => (r.getLong(0),r.getLong(1)))
}
```

```python
def projection_result(spark, query):
    return [tuple(r) for r in spark.sql(query).orderBy("id").collect()]
```

This result is the semantic anchor for every later plan observation. Comparing every projected identity and measure detects missing rows, wrong filters and wrong expressions independently of operator selection. A plan parser or normalization helper cannot make an incorrect query acceptable by producing convincing-looking text.

**Verification evidence:** Assert the complete tuple list, not only the first/last rows or a printed plan.

### Exercise 2: Capture each extended planning stage

Return EXPLAIN EXTENDED text for the supplied query. Permit only EXTENDED or FORMATTED as the mode and reject another mode.

**Expected:** Text includes Parsed Logical Plan, Analyzed Logical Plan, Optimized Logical Plan and Physical Plan sections. An invalid mode is rejected.

```scala
def explainText(spark: SparkSession, query: String, mode: String): String = {
  require(Set("EXTENDED","FORMATTED").contains(mode),"Unsupported evidence mode")
  spark.sql("EXPLAIN " + mode + " " + query).collect().map(_.getString(0)).mkString("\n")
}
```

```python
def explain_text(spark, query, mode):
    if mode not in {"EXTENDED","FORMATTED"}:
        raise ValueError("Unsupported evidence mode")
    return "\n".join(r[0] for r in spark.sql("EXPLAIN "+mode+" "+query).collect())
```

The helper captures a versioned observation of the supplied fixed query and constrains its evidence mode. Parsed, analyzed and optimized trees can differ without changing the query result. A missing relation or type error belongs at a different diagnostic layer from an unwanted physical exchange, so retaining stage labels improves the precision of a review.

**Verification evidence:** Assert all four section labels and an explicit invalid-mode exception.

### Exercise 3: Inspect the scan scope for column pruning

Capture FORMATTED output and extract lines containing ReadSchema. Verify that the projection scan requests id and amount but not group_id or unused_payload. Also locate Filter and Project operators.

**Expected:** ReadSchema includes id: bigint and amount: bigint only among the four stored fields. Filter and Project evidence are present.

```scala
def readSchemaEvidence(formatted: String): String = {
  formatted.linesIterator.filter(_.contains("ReadSchema")).mkString("\n")
}
```

```python
def read_schema_evidence(formatted):
    return "\n".join(line for line in formatted.splitlines() if "ReadSchema" in line)
```

The check targets the file-scan field requirement, which is where pruning is observable. It does not mistake unused columns appearing in a parsed table schema for columns actually requested by the scan. Likewise, a pushed filter and a residual Filter can coexist. Neither a pruned schema nor a pushed predicate alone measures actual bytes avoided.

**Verification evidence:** Assert needed/excluded fields in the extracted scan lines rather than in the entire extended plan.

### Exercise 4: Connect grouped output to a redistribution boundary

Execute the grouped aggregate and capture its FORMATTED plan. Return group_id, n, total and locate aggregate plus Exchange operators under the fixed AQE-disabled configuration.

**Expected:** Groups 0,1,2 each have n3 with totals 180,210,240. The plan shows aggregation and an Exchange.

```scala
def aggregateResult(spark: SparkSession, query: String): Seq[(Long,Long,Long)] = {
  spark.sql(query).orderBy("group_id").collect().toSeq.map(r => (r.getLong(0),r.getLong(1),r.getLong(2)))
}
```

```python
def aggregate_result(spark, query):
    return [tuple(r) for r in spark.sql(query).orderBy("group_id").collect()]
```

Each group result is checked against its three accepted source amounts. The Exchange is a physical distribution requirement in this prepared setup, not part of the logical definition of SUM. If a future layout or optimizer removes that boundary, the semantic oracle should remain while the plan claim is reviewed against the changed configuration instead of blindly updating an exact snapshot.

**Verification evidence:** Assert all group tuples independently, then assert the relevant operator markers and recorded AQE setting.

### Exercise 5: Normalize incidental identifiers without erasing semantics

Replace expression-number suffixes such as#123 with#ID and the exact owned root path with<owned-root> in plan text. Preserve operators, field names, predicates and partitioning descriptions.

**Expected:** A synthetic Project id#123L becomes Project id#IDL; the current temporary root is absent from normalized actual plan text.

```scala
def normalizeEvidence(plan: String, root: String): String = {
  plan.replace(root,"<owned-root>").replaceAll("#[0-9]+","#ID")
}
```

```python
def normalize_evidence(plan, root):
    return re.sub(r"#[0-9]+","#ID",plan.replace(root,"<owned-root>"))
```

Expression IDs and scratch paths identify this execution but are not the relational policy being taught. Removing just those fragments makes evidence easier to compare while retaining important distinctions. The normalized text is still not a universal plan contract: optimizer versions and settings can legitimately change operator structure.

**Verification evidence:** Assert the synthetic replacement and required semantic tokens after normalizing the actual plan.

### Exercise 6: Compare equivalent query forms with separate semantic and plan evidence

Execute a nested projection/filter form of the direct query and compare its exact rows. Capture its extended plan and return a bounded receipt containing Spark version, ANSI, AQE and shuffle partition settings.

**Expected:** The nested query has the same nine tuples. Receipt shows Spark 4.0.1, ANSItrue, AQEfalse, shuffle partitions 2. Both extended plans expose an optimized stage.

```scala
def configurationReceipt(spark: SparkSession): Map[String,String] = {
  Map("spark_version"->spark.version,"ansi"->spark.conf.get("spark.sql.ansi.enabled"),"aqe"->spark.conf.get("spark.sql.adaptive.enabled"),"shuffle_partitions"->spark.conf.get("spark.sql.shuffle.partitions"))
}
```

```python
def configuration_receipt(spark):
    return {"spark_version":spark.version,"ansi":spark.conf.get("spark.sql.ansi.enabled"),"aqe":spark.conf.get("spark.sql.adaptive.enabled"),"shuffle_partitions":spark.conf.get("spark.sql.shuffle.partitions")}
```

Semantic equality is established with concrete rows, and configuration is attached to the physical observation. The optimizer is allowed to simplify different source expressions into related plans, but exact text is not the acceptance rule. No action timing or task metric is measured here, so the receipt does not claim a performance improvement.

**Verification evidence:** Assert full output parity with the literal oracle and exact controlled settings; do not assert whole-plan byte equality or faster execution.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
