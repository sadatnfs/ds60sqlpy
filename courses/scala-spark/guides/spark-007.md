# spark-007: Either and validation without hidden data loss

Authored tutorial and practice content. The prepared Scala/JVM worker executes a bounded program; process success and understanding remain distinct. No source file installs a tool or downloads a dependency.

## Level and prerequisites

Beginner; approximately 105 minutes. Direct design prerequisites: `spark-006`. The lesson uses Scala 2.13 syntax and the prepared JDK 17 worker. The older design document proposed a different Spark/JDK tuple; use the current [execution baseline](../execution-baseline.md) for this authored material.

## How to run this lesson

Open `spark-007` in the classroom, select the Scala source, prepare the `scala-jvm` profile and run the saved pad. The worker stages the single source as `Main.scala` and invokes `object Main`. Read the terminal output and exact assertions. The [learner source](../lessons/spark-007.scala) runs two complete demonstrations; its six task functions remain explicit stubs until you implement them. Preserve your saved attempt. The [reference program](../solutions/spark-007_solution.scala) and [explained solutions](../solutions/spark-007_solutions.md) are separate and should be opened after an attempt or an explicit worked-comparison request. If the profile is unavailable, reading and saving remain available; opening this guide does not prepare a runtime.

## Learning objectives

- Return accepted data or an explicit validation reason without throwing away invalid rows.
- Explain the result of both worked examples before running them.
- Implement the six contracts, inspect normal and boundary evidence, and explain a counterexample in your own words.

## Vocabulary and concepts

- **Either:** A value containing either a Left error or a Right accepted result, with right-biased map/flatMap composition in Scala 2.13.

- **For comprehension:** Syntax that composes map/flatMap-style operations while naming intermediate successful values.

- **Validation precedence:** The defined order in which malformed fields are checked, determining which reason is reported when several fail.

- **Rejection ledger:** An explicit collection retaining source position, raw input and a reason for every rejected record.

Parsing and validation are expected parts of data processing. A malformed user record should not disappear because a flatMap happened to return None, and it should not necessarily crash an entire batch through an exception. Either[String, Record] represents the two intended outcomes directly: Left(reason) for rejection or Right(record) for accepted data.

The miniature input format is exactly three pipe-separated fields: id, status, amount. It is not a complete CSV parser and does not support quoted delimiters or embedded pipes. split("\\|",-1) preserves an empty trailing field, which is important for distinguishing missing amount text from a shorter line. A field-count check happens before indexing the array.

The ID must be trimmed nonempty text, status must be paid or void, and amount must be trimmed ASCII digits representing 0 through 1000000 cents. The amount is validated even for a void record, so a business filter cannot hide malformed source data. These are teaching-domain policies; real source contracts may need more statuses, negative adjustments or different representations.

A for comprehension over Either short-circuits on the first Left and passes Right values forward. The order here is ID, status, amount. That order is part of the reported reason policy when multiple fields fail. If the business needs every error per row, a fail-fast Either chain is insufficient and an accumulating validation structure is required. The lesson makes this limitation explicit instead of claiming that one error reason is a complete diagnosis.

Accepted records preserve identity, status and exact cents. Rejected records preserve the zero-based input position, raw text and reason, so no input occurrence vanishes. The fixture has six records: three accepted and one rejection each for missing_id, invalid_amount and unknown_status. Accepted count plus rejected count must equal six before any paid total is trusted.

A later report selects paid records from the accepted domain. The accepted void remains in the ledger even though it does not contribute to paid revenue. This separates source validity from business eligibility. Replacing invalid amounts with zero, filtering voids before validation or counting only accepted rows would each hide a different failure.

The reference uses pure functions and immutable sequences. There is no file read, network request or external side effect. The same contract can later be applied in Spark, but distributed retries require their own delivery and side-effect design; an Either parser alone does not provide exactly-once processing.

## Worked example / walkthrough

### Worked example 1

```scala
val value: Either[String,Long] = Right(25L)
val invalid: Either[String,Long] = Left("invalid_amount")
assert(value.map(_ + 5L) == Right(30L))
assert(invalid.map(_ + 5L) == Left("invalid_amount"))
println(value.map(_ / 5L))
```

map transforms only the accepted Right branch. The rejection reason remains intact and the numeric function is never applied to it. This differs from throwing an exception or replacing the amount with zero, each of which changes how a batch can account for invalid data.

### Worked example 2

```scala
val combined = for {
  amount <- (Right(20L): Either[String,Long])
  fee <- (Right(5L): Either[String,Long])
} yield amount + fee
assert(combined == Right(25L))
val blocked = for {
  amount <- (Left("invalid_amount"): Either[String,Long])
  fee <- (Right(5L): Either[String,Long])
} yield amount + fee
assert(blocked == Left("invalid_amount"))
println(combined)
```

Each generator binds a value only from a successful Right. The yield expression builds the final accepted value. A Left stops the composition and preserves its reason. The explicit Either types make the example's left and right type parameters visible to a beginner and to the compiler.

## Exercises

### Exercise 1: Validate source identity explicitly

Trim an ID token and return Right for nonempty text. Return Left(missing_id) for null, empty or whitespace-only tokens. Do not invent an identifier.

**Expected result/shape:** " a1 " gives Right("a1"); null,"" and"  " each give Left("missing_id").

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

**Expected result/shape:** a1|paid|100 becomes Right(Record(a1, paid,100)); a2|paid| becomes invalid_amount; an empty-ID malformed-status record reports missing_id first; two fields report malformed_record.

**Verify:** Assert a valid record, trailing-empty rejection, first-error precedence and field-count failure.

**Progressive hint:** Use split("\\|",-1) before the for comprehension so a trailing empty amount is not lost.

### Exercise 5: Retain a complete rejection ledger

Parse every input line and return accepted records plus rejected(position, raw, reason) tuples. Position is the zero-based occurrence index; preserve encounter order in both outputs and never discard a Left.

**Expected result/shape:** The six-line fixture has three accepted records and rejections at positions 3,4,5 with missing_id, invalid_amount, unknown_status. Accepted plus rejected equals six.

**Verify:** Assert accepted IDs[a1, a2, a3], the exact rejected positions/reasons and count conservation.

**Progressive hint:** Use zipWithIndex and pattern-match each Either inside a fold.

### Exercise 6: Separate valid records from eligible revenue

From already accepted records, return paid-event count and checked paid cents total. Retain an observed zero paid event in the count and exclude valid void records only at this business-report stage.

**Expected result/shape:** The three accepted records yield paid count 2, total 100. A void record with malformed amount must have been rejected by parseRecord before this function can run.

**Verify:** Assert the paid metrics and show that a4|void|bad produces Left(invalid_amount), not a silently skipped valid void.

**Progressive hint:** Filter accepted status paid, then fold both occurrence count and amount total.

## Common pitfalls

If rejected rows vanish, look for converting Either to Option and flatMapping only Right values without a separate ledger. If a trailing empty amount is misclassified as the wrong field count, inspect the split limit. If different errors appear after refactoring, review validation precedence. If void rows bypass amount validation, move source validation before business filtering. If a report total matches but accepted plus rejected count does not, trace every source position rather than inventing replacement zeros.

## Self-check

Explain one input-to-output trace without reading your code. Identify which function preserves repeated values, which condition distinguishes an invalid or missing input, and which assertion would fail for the tempting incorrect implementation. A printed success line alone is not the evidence; retain the exact values and the reasoning that connect them to the contract.

## Next step

Continue to the next lesson only after you can explain the boundary behavior. The [course route](../README.md) shows authored material and runtime evidence separately.

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
