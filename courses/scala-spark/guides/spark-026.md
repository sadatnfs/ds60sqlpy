# spark-026: Built-ins, UDFs and Python-JVM columnar boundaries

One label rule gets three implementations: plain code on the driver, Spark built-in functions and a Python UDF. Twelve labels include a NULL, an empty string, the text `NULL`, a German sharp s, a Turkish dotted capital I, an emoji and a decomposed accent, and the rule must leave everything except ASCII capitals and four ASCII whitespace characters alone.

## Level and prerequisites

Intermediate; approximately 105 minutes. Direct prerequisites: `spark-025`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-paired-lesson).

Learner pads: [Scala](../lessons/spark-026.scala) and [PySpark](../lessons/spark-026.py).

Open the [explained solutions](../solutions/spark-026_solutions.md) after an attempt.

The first worked example applies the ASCII-only `translate` to `CAFÉ` and prints `ASCII mapping preserves non-ASCII É` once `cafÉ` comes back. The second tests a NULL, an empty string and the text `null` for missingness, gets `(True, False, False)`, and prints `Missing, empty and literal null text are distinct`.

## Learning objectives

- Prefer engine expressions when possible and make Python/JVM conversion and NULL behavior measurable.
- Build the rule from `translate`, `regexp_replace` and `trim`, wrap the same rule as a Python UDF with a declared `StringType`, and find `BatchEvalPython` in the UDF plan but not in the built-in plan.
- Keep the 1 missing, 2 empty and 9 text labels in separate categories, and show that a plausible `strip().lower()` rule disagrees with the golden list on IDs 4, 5, 6 and 9, and on ID 8 as well in Python.

## Vocabulary and concepts

- **Engine expression:** A transformation represented in the Spark SQL expression tree, allowing the engine to analyze its types and many of its semantics.

- **Scalar UDF:** A user-defined function applied to values with a declared return type; its body may be opaque to query optimization.

- **Python evaluation boundary:** The transfer of values between JVM execution and a Python worker for a Python UDF.

- **NULL contract:** The explicit behavior for unknown input, kept separate from empty strings and a literal string spelling null.

- **ASCII-only case mapping:** A deliberately narrow A-Z to a-z translation that leaves other Unicode code points unchanged.

- **Golden fixture:** A reviewed list of exact expected outputs that checks every implementation independently of agreement among implementations.

This lesson compares implementations of one precisely defined label rule. Unknown input stays NULL. Runs of exactly four ASCII whitespace characters, space, tab, line feed and carriage return, collapse to one ordinary space. Leading and trailing ordinary spaces are removed. Only ASCII uppercaseA through Z map to lowercase. Other Unicode characters, including nonbreaking space,É,İ,ß, emoji and combining marks, remain otherwise unchanged.

The narrow rule is intentional. General lowercasing, case folding, Unicode normalization and whitespace trimming are different operations with language and Unicode-version details. A business product may need one of them, but it must name that requirement explicitly. Here an ASCII mapping makes the cross-language contract concrete enough to explain and test without claiming that a generic lower().strip() call means the same policy everywhere.

The twelve-row fixture covers NULL, empty text, space-only text, multiple interior spaces, tab/newline/carriage-return combinations, non-ASCII capitals, nonbreaking spaces, a Turkish dotted capital I, emoji, a decomposed accented character and the literal string NULL. The golden output preserves the distinction between missing, empty and the ordinary text null. It also preserves the decomposed accent rather than silently normalizing it to a different code-point sequence.

The built-in path composes translate, regexp_replace and trim. Its operations remain Spark expressions, so the engine can reason about their result types and integrate them into the query plan. A built-in is not automatically the right choice merely because it is built in: it still must express the exact rule. The explicit ASCII character class prevents Java and Python regular-expression whitespace defaults from quietly broadening the accepted normalization policy.

The Scala path wraps a pure String function in a Scala UDF. It executes inside the JVM and does not introduce a Python worker boundary. The Python path wraps an equivalent pure function in a scalar Python UDF with StringType and useArrow=False. That explicit flag keeps the default demonstration independent of pandas and PyArrow. Both language-specific UDFs and both built-in implementations compare with the same twelve golden values.

The physical plan shows where the Python evaluation is inserted. The Python reference expects BatchEvalPython for its deliberately non-Arrow scalar UDF and no such node for the built-in expression. The Scala reference expects a UDF expression but no Python evaluation node. This is boundary evidence, not a performance benchmark. Data transfer, batching, serialization, worker startup and opaque function logic can all affect cost, and a tiny local fixture cannot determine their production impact.

A UDF must be pure for this example: it does not write files, call a service, mutate shared counters or depend on invocation order. Spark can reevaluate expressions or retry tasks, so an application should not encode exactly-once external effects in a scalar UDF. Marking a function nondeterministic changes optimizer assumptions but does not turn it into a transactional side-effect mechanism. The result contract concerns returned values rather than the number of Python or JVM calls.

The final counterexample deliberately uses a broader lowercase-and-trim implementation. It changes non-ASCII capitals and fails to collapse interior whitespace correctly. Python's default strip also removes the nonbreaking spaces that this contract preserves, while the JVM trim behavior differs. The validators must reject the wrong implementation even if its output looks reasonable to a human. This teaches why a business rule needs examples at semantic boundaries rather than only a happy-path word.

Arrow and pandas UDFs are an optional extension, not imported or executed by the default sources. Spark 4.3.0 documents pandas 2.0.0 and PyArrow 11.0.0 as minimum supported versions for this SQL integration. A dedicated profile must still record exact compatible package pins, then rerun the golden fixture and inspect the resulting plan; minimum versions alone do not qualify an environment. Arrow changes the transfer representation and batching boundary; it does not eliminate data conversion or guarantee speed. No optional dependency is assumed installed, and no lesson code downloads one.

## Supplied local fixture

The session runs `local[2]` under the Python profile. The twelve labels are a NULL, an empty string, a single space, `  ALPHA  Beta ` with doubled spaces, a tab, `A`, newline, `B`, carriage return and space sequence, `CAFÉ`, `Straße`, an `A` between nonbreaking spaces, `İI`, `🙂 OK`, an `e` followed by a combining acute accent, and the four letters `NULL`. Every expected output is written out literally, so no implementation grades another.

```scala
import org.apache.spark.sql.Row
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val schema = StructType(
  Seq(StructField("id", LongType, false), StructField("label", StringType, true))
)
val raw = spark.createDataFrame(
  spark.sparkContext.parallelize(
    Seq(
      Row(1L, null),
      Row(2L, ""),
      Row(3L, "   "),
      Row(4L, "  ALPHA  Beta "),
      Row(5L, "\tA\nB\r "),
      Row(6L, "CAFÉ"),
      Row(7L, "Straße"),
      Row(8L, "\u00a0A\u00a0"),
      Row(9L, "İI"),
      Row(10L, "🙂 OK"),
      Row(11L, "e\u0301"),
      Row(12L, "NULL")
    ),
    2
  ),
  schema
)
val expected = Seq(
  (1L, None),
  (2L, Some("")),
  (3L, Some("")),
  (4L, Some("alpha beta")),
  (5L, Some("a b")),
  (6L, Some("cafÉ")),
  (7L, Some("straße")),
  (8L, Some("\u00a0a\u00a0")),
  (9L, Some("İi")),
  (10L, Some("🙂 ok")),
  (11L, Some("e\u0301")),
  (12L, Some("null"))
)
```

```python
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType
import re

schema = StructType(
    [StructField("id", LongType(), False), StructField("label", StringType(), True)]
)
raw = spark.createDataFrame(
    [
        (1, None),
        (2, ""),
        (3, "   "),
        (4, "  ALPHA  Beta "),
        (5, "\tA\nB\r "),
        (6, "CAFÉ"),
        (7, "Straße"),
        (8, "\u00a0A\u00a0"),
        (9, "İI"),
        (10, "🙂 OK"),
        (11, "e\u0301"),
        (12, "NULL"),
    ],
    schema=schema,
)
expected = [
    (1, None),
    (2, ""),
    (3, ""),
    (4, "alpha beta"),
    (5, "a b"),
    (6, "cafÉ"),
    (7, "straße"),
    (8, "\u00a0a\u00a0"),
    (9, "İi"),
    (10, "🙂 ok"),
    (11, "e\u0301"),
    (12, "null"),
]
```

## Worked example / walkthrough

### Worked example 1

```scala
val row = spark
  .sql(
    "SELECT translate('CAFÉ','ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz') AS ascii_only"
  )
  .first()
assert(row.getString(0) == "cafÉ")
println("ASCII mapping preserves non-ASCII É")
```

```python
row = spark.sql(
    "SELECT translate('CAFÉ','ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz') AS ascii_only"
).first()
assert row[0] == "cafÉ"
print("ASCII mapping preserves non-ASCII É")
```

The result demonstrates the declared narrow case policy. Calling a general Unicode lowercase function would produce a different output for the accented capital and therefore implement a different rule, even if both could be sensible in another product.

### Worked example 2

```scala
val row = spark
  .sql(
    "SELECT CAST(NULL AS STRING) IS NULL AS missing, '' IS NULL AS empty_missing, 'null' IS NULL AS text_missing"
  )
  .first()
assert(row.getBoolean(0) && !row.getBoolean(1) && !row.getBoolean(2))
println("Missing, empty and literal null text are distinct")
```

```python
row = spark.sql(
    "SELECT CAST(NULL AS STRING) IS NULL AS missing, '' IS NULL AS empty_missing, 'null' IS NULL AS text_missing"
).first()
assert tuple(row) == (True, False, False)
print("Missing, empty and literal null text are distinct")
```

NULL is absence of a known value, not a special spelling stored in every string column. The fixture keeps missing, empty and text categories separate so a normalizer cannot silently replace one with another and still pass.

## Exercises

### Exercise 1: Implement the pure scalar rule precisely

Return NULL/None unchanged; collapse only space, tab, newline and carriage return runs, trim ordinary spaces, and translate ASCII A-Z to a-z. Preserve other Unicode code points.

**Expected result/shape:** All 12 golden outputs, including cafÉ, İi, nonbreaking-space-wrapped a and unchanged decomposed e-plus-accent.

**Verify:** Apply the scalar function to every raw fixture value and compare with all golden pairs.

**Progressive hint:** Use an explicit whitespace class and ASCII mapping rather than broad lower/strip defaults.

### Exercise 2: Express the same rule with native Spark functions

Produce id, normalized using translate, regexp_replace and trim on the label column. Preserve NULL propagation and the exact golden values.

**Expected result/shape:** The twelve ordered output pairs equal the golden fixture and normalized has string type.

**Verify:** Assert the full pair list and StringType; do not accept agreement with only one UDF implementation.

**Progressive hint:** Collapse the explicit whitespace class before trimming the resulting ordinary boundary spaces.

### Exercise 3: Wrap the scalar rule with a declared UDF return type

Create a Scala String UDF or a Python StringType scalar UDF with useArrow=False, then return id, normalized. Keep the function pure and validate all outputs.

**Expected result/shape:** Every pair matches the same twelve golden values. Python uses the non-Arrow scalar path; Scala stays in the JVM.

**Verify:** Assert all golden pairs and string result type for the enabled language-specific UDF.

**Progressive hint:** Handle NULL inside the scalar function and declare the result type; do not call Spark APIs inside the UDF.

### Exercise 4: Locate the execution boundary in physical evidence

Return the physical plan strings for the built-in and language-specific UDF relations. Identify Python evaluation only where it is actually present.

**Expected result/shape:** Python UDF plan contains BatchEvalPython; built-in contains no Python evaluator. Scala UDF expression is present without BatchEvalPython or ArrowEvalPython.

**Verify:** Assert the language-appropriate markers and print both plans; do not infer a speed ratio from them.

**Progressive hint:** A Scala UDF is still opaque user logic but does not cross into a Python worker.

### Exercise 5: Preserve missing, empty and ordinary-text populations

Classify normalized values as missing, empty or text and count each category. Separately select the identity whose normalized text equals the literal null.

**Expected result/shape:** Missing 1, empty 2, text 9. Literal null text belongs only to ID 12; unknown value belongs only to ID 1.

**Verify:** Assert all category counts and both exact identity selections for built-in and UDF results.

**Progressive hint:** Check IS NULL before equality to the empty string; ordinary text null is not missingness.

### Exercise 6: Reject a plausible but semantically broader implementation

Validate a result against the full golden sequence. Deliberately apply general lowercasing and default trimming without interior-whitespace collapse, and require rejection.

**Expected result/shape:** The wrong implementation disagrees at least on IDs 4, 5, 6 and 9. Python additionally removes the preserved nonbreaking spaces at ID 8.

**Verify:** Assert named mismatch identities and that the golden validator raises rather than accepting a visually plausible normalization.

**Progressive hint:** A cross-language result can look reasonable while implementing a different Unicode or whitespace policy.

## Common pitfalls

Do not claim that all whitespace classes or lowercasing functions have identical Unicode behavior. Do not confuse NULL, empty and literal null text. Do not put side effects in a UDF or assume task retries imply exactly-once invocation. A declared return type does not validate the business rule. Arrow/pandas is optional until an exact provisioned profile exists and passes the same golden fixture; it changes the boundary but does not eliminate serialization or guarantee a faster implementation.

## Self-check

- ID 4 is `  ALPHA  Beta `. Walk it through the rule step by step and explain why the result is `alpha beta` with one interior space.
- Why does `CAFÉ` become `cafÉ` rather than `café`, and which business requirement would have to be written down before the second answer became correct?
- The UDF plan contains `BatchEvalPython` and the built-in plan does not. What does that operator tell you about where each label is processed, and what can the optimizer no longer see?
- Python's `strip()` removes the nonbreaking spaces around ID 8 but Java's `trim` does not. Why does that make ID 8 a Python-only mismatch for the wrong rule?

## Next step

Go on to [spark-027: Persistence lifecycle and cross-language golden tests](spark-027.md). You now compare implementations against a literal golden list; the next lesson makes that comparison duplicate-aware and schema-aware, and adds a cache that must always be released.

## Primary sources and official APIs

- [Spark 4.3.0 regexp_replace](https://spark.apache.org/docs/4.3.0/api/python/reference/pyspark.sql/api/pyspark.sql.functions.regexp_replace.html)

- [Spark 4.3.0 Arrow and pandas guide](https://spark.apache.org/docs/4.3.0/api/python/tutorial/sql/arrow_pandas.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-026: Built-ins, UDFs and Python-JVM columnar boundaries.
Read courses/scala-spark/guides/spark-026.md and courses/scala-spark/lessons/spark-026.py; the paired sources are courses/scala-spark/lessons/spark-026.scala and courses/scala-spark/lessons/spark-026.py.
Direct prerequisites: spark-025. Explain the schema, row grain and new Scala/Python/Spark syntax, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact result and boundary evidence, and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use only the prepared local[2] worker profile and owned job scratch. Do not download dependencies, start a remote service, reset existing checkpoints or alter unrelated learner work.
Done when all six contracts have inspected evidence and I can explain the stated assumptions and a meaningful failure case.
```
