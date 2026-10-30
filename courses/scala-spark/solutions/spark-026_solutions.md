# spark-026: Explained paired reference solutions

Read the [guide](../guides/spark-026.md) and attempt one language first. The [Scala reference](spark-026_solution.scala) and [PySpark reference](spark-026_solution.py) are complete single-file programs with explicit local sessions and finally-based stop. Each compares with literal expectations; matching two implementations alone would not rule out a shared mistake.

## Exercises and reasoning

### Exercise 1: Implement the pure scalar rule precisely

ReturnNULL/None unchanged; collapse only space, tab, newline and carriage return runs, trim ordinary spaces, and translateASCII A-Z to a-z. Preserve otherUnicode code points.

**Expected:** All 12 golden outputs, includingcafÉ,İi, nonbreaking-space-wrapped a and unchanged decomposed e-plus-accent.

```scala
def normalizeLabel(value: String): String = {
  if (value == null) null
  else
    value
      .replaceAll("[ \t\r\n]+", " ")
      .replaceAll("^ +| +$", "")
      .map(ch => if (ch >= 'A' && ch <= 'Z') (ch + 32).toChar else ch)
}
```

```python
def normalize_label(value):
    if value is None:
        return None
    collapsed = re.sub(r"[ \t\r\n]+", " ", value).strip(" ")
    return collapsed.translate(
        str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
    )
```

The function is a pure value transformation with an explicit missingness rule. The character class and mapping delimit its semantics instead of inheriting different broad language defaults. Preserving all other code points is part of the contract; this implementation deliberately does not perform Unicode case folding, NFC normalization or transliteration.

**Verification evidence:** Apply the scalar function to every raw fixture value and compare with all golden pairs.

### Exercise 2: Express the same rule with native Spark functions

Produce id, normalized using translate, regexp_replace and trim on the label column. PreserveNULL propagation and the exact golden values.

**Expected:** The twelve ordered output pairs equal the golden fixture and normalized has string type.

```scala
def builtinLabels(raw: DataFrame): DataFrame = {
  raw.select(
    col("id"),
    trim(
      regexp_replace(
        translate(col("label"), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"),
        "[ \t\r\n]+",
        " "
      )
    ).as("normalized")
  )
}
```

```python
def builtin_labels(raw):
    return raw.select(
        "id",
        F.trim(
            F.regexp_replace(
                F.translate("label", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"),
                r"[ \t\r\n]+",
                " ",
            )
        ).alias("normalized"),
    )
```

The expression tree makes the rule visible as a composition of supported string operations. NULL propagates through these functions in the intended way. The full golden list confirms that their exact behavior matches the business rule, including boundaries where a seemingly simpler Unicode lowercase or whitespace shorthand would differ.

**Verification evidence:** Assert the full pair list and StringType; do not accept agreement with only one UDF implementation.

### Exercise 3: Wrap the scalar rule with a declared UDF return type

Create a Scala String UDF or a Python StringType scalar UDF with useArrow=False, then return id, normalized. Keep the function pure and validate all outputs.

**Expected:** Every pair matches the same twelve golden values. Python uses the non-Arrow scalar path; Scala stays in the JVM.

```scala
def udfLabels(raw: DataFrame): DataFrame = {
  val normalize = udf((value: String) => normalizeLabel(value))
  raw.select(col("id"), normalize(col("label")).as("normalized"))
}
```

```python
def udf_labels(raw):
    normalize = F.udf(normalize_label, StringType(), useArrow=False)
    return raw.select("id", normalize("label").alias("normalized"))
```

The UDF declaration describes how Spark should represent the returned value but does not verify semantic correctness. Golden checks remain necessary. Python explicitly opts out of Arrow so optional packages cannot silently change the execution mode. The scalar body receives values, not DataFrames, and must not start a session or perform external effects.

**Verification evidence:** Assert all golden pairs and string result type for the enabled language-specific UDF.

### Exercise 4: Locate the execution boundary in physical evidence

Return the physical plan strings for the built-in and language-specific UDF relations. Identify Python evaluation only where it is actually present.

**Expected:** Python UDF plan contains BatchEvalPython; built-in contains no Python evaluator. Scala UDF expression is present without BatchEvalPython or ArrowEvalPython.

```scala
def planEvidence(frame: DataFrame): String = {
  frame.queryExecution.executedPlan.toString
}
```

```python
def plan_evidence(frame):
    return frame._jdf.queryExecution().executedPlan().toString()
```

The plan records an actual execution boundary instead of treating every UDF as the same mechanism. The Python worker node explains why JVM/Python value transfer matters, while the Scala expression stays inside the JVM. This observation does not measure serialization volume, CPU cost or throughput. Those require representative execution metrics and controlled comparisons.

**Verification evidence:** Assert the language-appropriate markers and print both plans; do not infer a speed ratio from them.

### Exercise 5: Preserve missing, empty and ordinary-text populations

Classify normalized values as missing, empty or text and count each category. Separately select the identity whose normalized text equals the literal null.

**Expected:** Missing 1, empty 2, text 9. Literal null text belongs only to ID 12; unknown value belongs only to ID 1.

```scala
def labelCategories(frame: DataFrame): Seq[(String, Long)] = {
  frame
    .withColumn(
      "category",
      when(col("normalized").isNull, "missing")
        .when(col("normalized") === "", "empty")
        .otherwise("text")
    )
    .groupBy("category")
    .count()
    .collect()
    .toSeq
    .map(r => (r.getString(0), r.getLong(1)))
    .sortBy(_._1)
}
```

```python
def label_categories(frame):
    return sorted(
        tuple(r)
        for r in frame.withColumn(
            "category",
            F.when(F.col("normalized").isNull(), "missing")
            .when(F.col("normalized") == "", "empty")
            .otherwise("text"),
        )
        .groupBy("category")
        .count()
        .collect()
    )
```

The population checks catch a normalizer that turns unknown input into empty text or interprets a literal spelling as a missing-value marker. Both are common but consequential policy changes. Keeping these categories separate supports honest completeness reporting and prevents string-cleaning convenience from silently changing downstream denominators.

**Verification evidence:** Assert all category counts and both exact identity selections for built-in and UDF results.

### Exercise 6: Reject a plausible but semantically broader implementation

Validate a result against the full golden sequence. Deliberately apply general lowercasing and default trimming without interior-whitespace collapse, and require rejection.

**Expected:** The wrong implementation disagrees at least on IDs 4,5,6,9. Python additionally removes the preserved nonbreaking spaces atID 8.

```scala
def validateGolden(
    actual: Seq[(Long, Option[String])],
    expected: Seq[(Long, Option[String])]
): Unit = {
  require(actual == expected, "Golden label contract mismatch")
}
```

```python
def validate_golden(actual, expected):
    if actual != expected:
        raise ValueError("Golden label contract mismatch")
```

The negative control proves that the fixture distinguishes the declared policy from a tempting shortcut. Unicode lowercasing and default trimming are not inherently wrong; they are wrong for this specificASCII-only contract. Named counterexamples explain the failure and make it harder to weaken a test merely because an output looks polished to a reader.

**Verification evidence:** Assert named mismatch identities and that the golden validator raises rather than accepting a visually plausible normalization.

## Execution and interpretation

Run the complete reference in its prepared fixed worker. The small fixture is constructed inside the program,so opening a lesson does not fetch data. A final success line is printed only after the reference assertions complete. Plan observations,partition evidence and resource measurements apply to the actual local configuration; they do not establish cluster-scale performance. Session cleanup is explicit,and any additional owned file/query lifecycle is described in the lesson.
