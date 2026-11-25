# spark-007: Either and validation without hidden data loss

Six pipe-separated records arrive; three are valid and three are broken in different ways. This lesson validates ID, status and amount with `Either`, composes them in a `for` comprehension with a declared error order, and keeps every rejected line with its position and reason so nothing disappears between input and report.

## Level and prerequisites

Beginner; approximately 75 minutes. Direct prerequisites: `spark-006`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-language-lesson).

Learner pad: [spark-007.scala](../lessons/spark-007.scala).

Open the [explained solutions](../solutions/spark-007_solutions.md) after an attempt.

The first worked example prints `Right(5)`, the result of `Right(25L).map(_ / 5L)`; mapping over a `Left` would have passed the error through untouched. The second prints `Right(25)` from a `for` comprehension that adds an amount and a fee. Its companion assertion shows that once the first step is `Left("invalid_amount")`, the comprehension stops there and returns that `Left`, which is the behavior Exercise 4 relies on.

## Learning objectives

- Return accepted data or an explicit validation reason without throwing away invalid rows.
- Predict the first error reported for a record with several defects, using the declared order ID, then status, then amount, and explain why a short-circuiting `for` comprehension gives that order.
- Produce a rejection ledger for the six-line fixture (positions 3, 4 and 5 with `missing_id`, `invalid_amount` and `unknown_status`) whose accepted and rejected counts add up to six.

## Vocabulary and concepts

- **Either:** A value containing either a Left error or a Right accepted result, with right-biased map/flatMap composition in Scala 2.13.

- **For comprehension:** Syntax that composes map/flatMap-style operations while naming intermediate successful values.

- **Validation precedence:** The defined order in which malformed fields are checked, determining which reason is reported when several fail.

- **Rejection ledger:** An explicit collection retaining source position, raw input and a reason for every rejected record.

Parsing and validation are expected parts of data processing. A malformed user record should not disappear because a flatMap happened to return None, and it should not necessarily crash an entire batch through an exception. Either [String, Record] represents the two intended outcomes directly: Left(reason) for rejection or Right(record) for accepted data.

The miniature input format is exactly three pipe-separated fields: id, status, amount. It is not a complete CSV parser and does not support quoted delimiters or embedded pipes. split("\\|",-1) preserves an empty trailing field, which is important for distinguishing missing amount text from a shorter line. A field-count check happens before indexing the array.

The ID must be trimmed nonempty text, status must be paid or void, and amount must be trimmed ASCII digits representing 0 through 1000000 cents. The amount is validated even for a void record, so a business filter cannot hide malformed source data. These are teaching-domain policies; real source contracts may need more statuses, negative adjustments or different representations.

A for comprehension over Either short-circuits on the first Left and passes Right values forward. The order here is ID, status, amount. That order is part of the reported reason policy when multiple fields fail. If the business needs every error per row, a fail-fast Either chain is insufficient and an accumulating validation structure is required. The lesson makes this limitation explicit instead of claiming that one error reason is a complete diagnosis.

Accepted records preserve identity, status and exact cents. Rejected records preserve the zero-based input position, raw text and reason, so no input occurrence vanishes. The fixture has six records: three accepted and one rejection each for missing_id, invalid_amount and unknown_status. Accepted count plus rejected count must equal six before any paid total is trusted.

A later report selects paid records from the accepted domain. The accepted void remains in the ledger even though it does not contribute to paid revenue. This separates source validity from business eligibility. Replacing invalid amounts with zero, filtering voids before validation or counting only accepted rows would each hide a different failure.

The reference uses pure functions and immutable sequences. There is no file read, network request or external side effect. The same contract can later be applied in Spark, but distributed retries require their own delivery and side-effect design; an Either parser alone does not provide exactly-once processing.

## Worked example / walkthrough

### Worked example 1

```scala
val value: Either[String, Long] = Right(25L)
val invalid: Either[String, Long] = Left("invalid_amount")
assert(value.map(_ + 5L) == Right(30L))
assert(invalid.map(_ + 5L) == Left("invalid_amount"))
println(value.map(_ / 5L))
```

map transforms only the accepted Right branch. The rejection reason remains intact and the numeric function is never applied to it. This differs from throwing an exception or replacing the amount with zero, each of which changes how a batch can account for invalid data.

### Worked example 2

```scala
val combined = for {
  amount <- (Right(20L): Either[String, Long])
  fee <- (Right(5L): Either[String, Long])
} yield amount + fee
assert(combined == Right(25L))
val blocked = for {
  amount <- (Left("invalid_amount"): Either[String, Long])
  fee <- (Right(5L): Either[String, Long])
} yield amount + fee
assert(blocked == Left("invalid_amount"))
println(combined)
```

Each generator binds a value only from a successful Right. The yield expression builds the final accepted value. A Left stops the composition and preserves its reason. The explicit Either types make the example's left and right type parameters visible to a beginner and to the compiler.

## Exercises

### Exercise 1: Validate source identity explicitly

Trim an ID token and return Right for nonempty text. Return Left(missing_id) for null, empty or whitespace-only tokens. Do not invent an identifier.

**Expected result/shape:** `" a1 "` gives `Right("a1")`; `null`, `""` and `"  "` each give `Left("missing_id")`.

**Verify:** Assert one normalized identity and all three missing representations without throwing.

**Progressive hint:** Option(raw) protects the JVM null boundary before trimming.

### Exercise 2: Reject unsupported domain states

Accept only trimmed lowercase paid or void. Return Left(unknown_status) for all other supplied values, including uppercase PAID and null. Do not silently case-fold unless the source contract explicitly permits it.

**Expected result/shape:** " paid " and"void" return Right("paid") and Right("void");"mystery","PAID" and null are rejected.

**Verify:** Assert both valid states and three unsupported forms; confirm that whitespace normalization is separate from case normalization.

**Progressive hint:** Filter the normalized token against a small declared Set of statuses.

### Exercise 3: Preserve exact bounded cents

Accept trimmed ASCII digits representing 0 through 1000000 as a Long. Return Left(invalid_amount) for null, blank, signed, decimal, overflowing or out-of-domain text.

**Expected result/shape:** "0" and"100" become Right(0L), Right(100L);"bad","-1","1.5","1000001" and a huge integer token are rejected.

**Verify:** Assert zero separately from rejection, and test both lexical failure and numeric range failure.

**Progressive hint:** Apply grammar and range checks around toLongOption, then convert the Option to Either.

### Exercise 4: Compose fields with declared error precedence

Require exactly three pipe-separated fields and compose ID, status, amount validation in that order using a for comprehension. Return Left(malformed_record) for null or wrong field count. Preserve empty trailing fields for validation.

**Expected result/shape:** `a1|paid|100` becomes `Right(Record(a1, paid, 100))`; `a2|paid|` becomes `invalid_amount`; an empty-ID malformed-status record reports missing_id first; two fields report malformed_record.

**Verify:** Assert a valid record, trailing-empty rejection, first-error precedence and field-count failure.

**Progressive hint:** Use split("\\|",-1) before the for comprehension so a trailing empty amount is not lost.

### Exercise 5: Retain a complete rejection ledger

Parse every input line and return accepted records plus rejected (position, raw, reason) tuples. Position is the zero-based occurrence index; preserve encounter order in both outputs and never discard a Left.

**Expected result/shape:** The six-line fixture has three accepted records and rejections at positions 3,4,5 with missing_id, invalid_amount, unknown_status. Accepted plus rejected equals six.

**Verify:** Assert accepted IDs `[a1, a2, a3]`, the exact rejected positions/reasons and count conservation.

**Progressive hint:** Use zipWithIndex and pattern-match each Either inside a fold.

### Exercise 6: Separate valid records from eligible revenue

From already accepted records, return paid-event count and checked paid cents total. Retain an observed zero paid event in the count and exclude valid void records only at this business-report stage.

**Expected result/shape:** The three accepted records yield paid count 2, total 100. A void record with malformed amount must have been rejected by parseRecord before this function can run.

**Verify:** Assert the paid metrics and show that `a4|void|bad` produces `Left(invalid_amount)`, not a silently skipped valid void.

**Progressive hint:** Filter accepted status paid, then fold both occurrence count and amount total.

## Common pitfalls

If rejected rows vanish, look for converting Either to Option and flatMapping only Right values without a separate ledger. If a trailing empty amount is misclassified as the wrong field count, inspect the split limit. If different errors appear after refactoring, review validation precedence. If void rows bypass amount validation, move source validation before business filtering. If a report total matches but accepted plus rejected count does not, trace every source position rather than inventing replacement zeros.

## Self-check

- What do `parseId(" a1 ")`, `parseId(null)` and `parseId("  ")` return, and why is trimming done before the emptiness test?
- `parseStatus` accepts "paid" and "void" but rejects "PAID". Give one reason a strict, case-sensitive status rule is safer than lowercasing input you have not seen.
- Trace `parseRecord("|bogus|100")`. Which error appears, and which field's defect is never reported because the comprehension stopped earlier?
- For the six-line fixture, list the rejected positions, raw lines and reasons. Why does the ledger store the original raw text rather than only the reason?
- `paidTotal` returns count 2 and total 100 for the accepted records. Why is a void record with a malformed amount never seen by this function?

## Next step

Go on to [spark-008: Assertions, numeric boundaries, and independent oracles](spark-008.md). You have been reading assertions written for you; next you write the checking helpers yourself (bag equality, checked sums, overflow-safe promotion and tolerance rules) and test whether they reject real wrong answers.

## Primary sources and official APIs

- [Scala 2.13 Either API](https://www.scala-lang.org/api/2.13.16/scala/util/Either.html).

- [Scala 2 for comprehensions](https://docs.scala-lang.org/tour/for-comprehensions.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-007: Either and validation without hidden data loss.
Read courses/scala-spark/guides/spark-007.md and courses/scala-spark/lessons/spark-007.scala. Direct prerequisites: spark-006.
Explain the Scala 2.13 syntax and data contract, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact assertion evidence and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt. Use only the prepared scala-jvm profile and preserve my saved work; do not install or download dependencies.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why an incorrect implementation fails.
```
