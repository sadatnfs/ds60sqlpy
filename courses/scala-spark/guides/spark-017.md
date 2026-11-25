# spark-017: Nested records, JSON and explode row accounting

Seven raw JSON strings hide four different array shapes: two items, no items, a NULL array and one item, plus three inputs that cannot become a parent record at all. This lesson parses them with an explicit schema and counts rows at every step, because `explode` and `explode_outer` disagree about what an empty array means.

## Level and prerequisites

Intermediate; approximately 90 minutes. Direct prerequisites: `spark-016`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-017.scala) and [PySpark](../lessons/spark-017.py).

Open the [explained solutions](../solutions/spark-017_solutions.md) after an attempt.

The first worked example explodes the two-element array `array(10, 20)` with `posexplode` and prints `Two array occurrences become two child rows`. The second explodes an empty array and a NULL array: `explode` on the empty one yields nothing, `explode_outer` on the NULL one yields a single row, and the program prints `An outer row can be a placeholder, not an item`.

## Learning objectives

- Flatten nested data while preserving parent identity and accounting for empty or missing arrays.
- Parse the seven JSON strings once with an explicit nested schema, accept four parents and reject sources 5, 6 and 7 with the reasons `malformed_json`, `missing_parent` and `missing_payload`.
- Predict that `explode` gives 3 child rows while `explode_outer` gives 5, and explain why the two extra rows are placeholders for parents 20 and 30, not items.

## Vocabulary and concepts

- **Nested schema:** A type tree that describes struct fields, array element types and nullable positions before parsing text.

- **Parse quarantine:** A relation retaining source identity, raw evidence and a declared reason for rejected input.

- **Child grain:** One output occurrence identified by parent identity and its array position; a repeated child value remains a separate occurrence.

- **Outer placeholder:** The synthetic NULL child emitted for an empty or missing array by an outer generator; it is not an observed child.

- **Positional zip:** An alignment of arrays by index that pads a shorter array with NULL; this is a different relationship from a Cartesian product.

A nested record contains two grains at once. The parent has a stable identity, while an array contains ordered child occurrences. Flattening changes the grain: a parent with two items becomes two rows. The two items may even have identical SKU values. Deduplicating by parent and SKU would erase a real occurrence, so this fixture uses parent_id plus array position as child identity.

The input has seven source records. Four satisfy the declared parse and parent-identity contract. Their arrays have lengths two, zero, unknown and one. A malformed JSON string, a syntactically valid object without parent_id, and a missing payload are retained as three different quarantine reasons. A null result field alone cannot distinguish all these cases. The parser schema therefore includes a corrupt-record field and the classification checks raw missingness, parser evidence, then domain identity in a deliberate order.

The schema is a contract for interpreting text, not proof of business validity. A parsed long can still be an invalid business quantity, and a parsed parent ID can be duplicated across records. This lesson validates only the stated required identity and parse conditions. A production boundary would add domain ranges and parent uniqueness before joining other data. Unknown JSON fields are not automatically part of the declared schema; silently ignoring them may be acceptable for compatibility or unacceptable for a strict producer contract.

An ordinary explode emits one row per actual element and emits none for an empty or null array. Here it yields three rows and loses parents 20 and 30 from the child relation. An outer explode retains those parents with a single null placeholder each, yielding five rows. That is useful for parent-preserving reporting, but COUNT(*) then measures child rows plus placeholders. COUNT(position) measures actual occurrences when the position is generated from the original array.

Array state must be recorded before flattening. After an outer explode, both an empty array and a missing array can appear as a null child. They have different meanings: the empty array says the collection is known and has no elements, whereas null says the collection is unknown. Similarly, an actual element may itself have an unknown quantity. Parent 40 has one observed item and zero known quantities; its total is unknown, not an observed zero. Parent 10 has two observed items whose quantities sum to five.

The examples use bounded collection only to compare tiny literal outputs. Parsing, projection and generation remain Spark expressions. The executable references use the same explicit schemas in Scala and Python, and compare against independent expected identities. Matching the two implementations would be insufficient if both forgot to count an outer placeholder separately.

The final comparison separates two legitimate array relationships. Exploding an array of two SKUs and an independent array of three channels produces six pairs. Zipping them produces three positional rows with one missing SKU. Neither result is universally correct. The relationship between the arrays determines the operator, and a faster implementation of the wrong relationship is still incorrect.

## Supplied local fixture

Each source row has an ID and a raw JSON string. Parent 10 has two items with the same SKU `a` and quantities 2 and 3, parent 20 has an empty array, parent 30 has an explicit `null` array, and parent 40 has one item with a NULL quantity. Source 5 is broken JSON, source 6 has no `parent_id` and source 7 has no payload.

```scala
import org.apache.spark.sql.Row
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val inputSchema = StructType(
  Seq(StructField("source_id", LongType, false), StructField("raw", StringType, true))
)
val raw = spark.createDataFrame(
  spark.sparkContext.parallelize(
    Seq(
      Row(1L, """{"parent_id":10,"items":[{"sku":"a","qty":2},{"sku":"a","qty":3}]}"""),
      Row(2L, """{"parent_id":20,"items":[]}"""),
      Row(3L, """{"parent_id":30,"items":null}"""),
      Row(4L, """{"parent_id":40,"items":[{"sku":"b","qty":null}]}"""),
      Row(5L, "{bad"),
      Row(6L, """{"items":[]}"""),
      Row(7L, null)
    ),
    2
  ),
  inputSchema
)
```

```python
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

input_schema = StructType(
    [StructField("source_id", LongType(), False), StructField("raw", StringType(), True)]
)
raw = spark.createDataFrame(
    [
        (1, '{"parent_id":10,"items":[{"sku":"a","qty":2},{"sku":"a","qty":3}]}'),
        (2, '{"parent_id":20,"items":[]}'),
        (3, '{"parent_id":30,"items":null}'),
        (4, '{"parent_id":40,"items":[{"sku":"b","qty":null}]}'),
        (5, "{bad"),
        (6, '{"items":[]}'),
        (7, None),
    ],
    schema=input_schema,
)
```

## Worked example / walkthrough

### Worked example 1

```scala
val sample = spark.sql("SELECT array(10,20) AS values")
assert(sample.select(posexplode(col("values"))).count() == 2L)
println("Two array occurrences become two child rows")
```

```python
sample = spark.sql("SELECT array(10,20) AS values")
assert sample.select(F.posexplode("values")).count() == 2
print("Two array occurrences become two child rows")
```

The generator returns a zero-based position and the element. Position belongs to an occurrence, so equal values at different positions remain distinct. A stable parent identifier must accompany this position when several parent arrays are flattened together.

### Worked example 2

```scala
val sample = spark.sql(
  "SELECT CAST(array() AS ARRAY<BIGINT>) AS empty_items, CAST(NULL AS ARRAY<BIGINT>) AS unknown_items"
)
assert(sample.select(explode(col("empty_items"))).count() == 0L)
assert(sample.select(explode_outer(col("unknown_items"))).count() == 1L)
println("An outer row can be a placeholder, not an item")
```

```python
sample = spark.sql(
    "SELECT CAST(array() AS ARRAY<BIGINT>) AS empty_items, CAST(NULL AS ARRAY<BIGINT>) AS unknown_items"
)
assert sample.select(F.explode("empty_items")).count() == 0
assert sample.select(F.explode_outer("unknown_items")).count() == 1
print("An outer row can be a placeholder, not an item")
```

The typed empty array and typed null array are intentionally different inputs. Their output counts demonstrate the generator contract without reading an external file or depending on inferred element types. Preserve that distinction before an outer transformation merges their visible child representation.

## Exercises

### Exercise 1: Parse once and retain rejection evidence

Parse raw with the explicit payload schema and PERMISSIVE mode, then add reason using precedence missing_payload, malformed_json, missing_parent, accepted. Preserve source_id and raw.

**Expected result/shape:** Sources 1-4 accepted; 5 malformed_json; 6 missing_parent; 7 missing_payload. No source disappears and accepted count is 4.

**Verify:** Assert all seven ordered source/reason rows and reconcile accepted 4 plus rejected 3 with input 7.

**Progressive hint:** Include _corrupt_record in the schema; a required field being NULL does not by itself prove malformed JSON.

### Exercise 2: Record collection state before changing grain

For accepted records return source_id, parent_id, items, array_state, with array_state unknown, empty or populated. Keep arrays typed and preserve the two repeated SKU occurrences.

**Expected result/shape:** Parent 10 populated,20 empty,30 unknown,40 populated. Parent 10 has size 2; parent 40 size 1.

**Verify:** Assert the four parent/state rows and item lengths independently of any later explode output.

**Progressive hint:** Check items IS NULL before checking size=0.

### Exercise 3: Flatten observed child occurrences

Use posexplode to return parent_id, position, sku, qty for actual items. Order by parent_id and position, and retain repeated SKU a.

**Expected result/shape:** `Rows(10, 0, a, 2)`, `(10, 1, a, 3)`, `(40, 0, b, NULL)`. Exactly 3 children; parents 20 and 30 produce none.

**Verify:** Assert the entire three-row occurrence list and unique (parent_id, position) count 3.

**Progressive hint:** A child identity includes its position rather than only the SKU value.

### Exercise 4: Preserve parents without inventing observed children

Use posexplode_outer, preserving parent_id and array_state along with position, sku, qty. Keep null placeholders for empty and unknown arrays.

**Expected result/shape:** Five rows: the three observed children plus `(20, empty, NULL, NULL, NULL)` and `(30, unknown, NULL, NULL, NULL)`.

**Verify:** Assert five rows, four distinct parents and exactly three nonnull generated positions.

**Progressive hint:** Retain array_state before using the outer generator; distinguish a missing position from a child with missing qty.

### Exercise 5: Reconcile child counts and nullable measures

Aggregate the outer relation to parent_id, array_state, child_count, known_qty_count, total_qty. Count positions for children and preserve SUM NULL when there are no known quantities.

**Expected result/shape:** Parent `10:(2, 2, 5)`; `20:(0, 0, NULL)`; `30:(0, 0, NULL)`; `40:(1, 0, NULL)`. Empty and unknown collection states remain visible.

**Verify:** Assert each parent count tuple and that summed child_count is 3 while known_qty_count is 2.

**Progressive hint:** COUNT(*) would count placeholders; COUNT(qty) answers a different completeness question from child count.

### Exercise 6: Choose Cartesian or positional array semantics

For one parent with SKUs [a, b] and channels [web, shop, api], return both independent exploded pairs and arrays_zip positional rows. Explain the relationship required for each interpretation.

**Expected result/shape:** Independent generators produce 6 pairs; zip produces (a, web), (b, shop), (NULL, api), three rows.

**Verify:** Assert the complete Cartesian pair set and all three ordered zipped rows including the padded NULL.

**Progressive hint:** Consecutive explodes multiply occurrence counts; arrays_zip aligns by position and pads the shorter side.

## Common pitfalls

Do not use inferred JSON schema as a substitute for an explicit producer contract. Do not classify every null field as malformed input. Do not drop source identity at parsing, collapse repeated child occurrences with DISTINCT, or count an outer placeholder as an observed child. Preserve array state before flattening. If a null element is allowed inside an otherwise populated array, its nonnull generated position still identifies a real occurrence even when every nested field is null. Larger arrays can produce large outputs despite a small parent count; inspect length distributions before applying the same operation at scale.

## Self-check

- Parent 10 has two items with the same SKU. Why must both rows survive, and which column from `posexplode` keeps them distinct?
- `explode_outer` returns a row for parent 30 with NULL item fields. How would a later count of items go wrong if it counted those rows?
- Parent 40's quantity is NULL. Explain why its summary is `(1, 0, NULL)` and not `(1, 1, 0)`.
- Exercise 6 compares two independent `explode` calls with `arrays_zip`. Why does one give 6 rows and the other 3, and which one matches "the item at position i belongs with the channel at position i"?

## Next step

Go on to [spark-018: Timestamp types, time zones and interval boundaries](spark-018.md). Arrays tested your row accounting; timestamps test your assumptions about what a value means, starting with a day that is 25 hours long.

## Primary sources and official APIs

- [Apache Spark 4.3.0 from_json](https://spark.apache.org/docs/4.3.0/api/python/reference/pyspark.sql/api/pyspark.sql.functions.from_json.html)

- [Apache Spark 4.3.0 explode_outer](https://spark.apache.org/docs/4.3.0/api/python/reference/pyspark.sql/api/pyspark.sql.functions.explode_outer.html)

- [Apache Spark built-in functions](https://spark.apache.org/docs/4.3.0/sql-ref-functions-builtin.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-017: Nested records, JSON and explode row accounting.
Read courses/scala-spark/guides/spark-017.md and courses/scala-spark/lessons/spark-017.py; the paired sources are courses/scala-spark/lessons/spark-017.scala and courses/scala-spark/lessons/spark-017.py.
Direct prerequisites: spark-016. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
