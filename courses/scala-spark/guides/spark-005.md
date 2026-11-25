# spark-005: Option, missing values, and total functions

An amount can be present, absent or present but unreadable, and those are three different facts. This lesson parses optional amount text into `Option[Long]`, keeps a ledger with a separate count for each state, and refuses to turn a missing or rejected value into a zero that would quietly lower a total.

## Level and prerequisites

Beginner; approximately 75 minutes. Direct prerequisites: `spark-004`. Pinned versions: [execution baseline](../execution-baseline.md).

## How to run this lesson

Shared run steps and profile rules: [study guide](../STUDY-GUIDE.md#run-a-language-lesson).

Learner pad: [spark-005.scala](../lessons/spark-005.scala).

Open the [explained solutions](../solutions/spark-005_solutions.md) after an attempt.

The first worked example prints `present=Some(0) absent=None`: a real zero is still a present value, and mapping `_ + 5L` over it gives `Some(5)` while the same map over `None` stays `None`. The second prints that `Option(null)` and `Some(null)` are distinct constructions, because `Option(null)` is `None` but `Some(null)` is defined and only `flatMap(Option(_))` exposes the hidden null. Exercises 1 and 2 depend on that difference.

## Learning objectives

- Represent absence explicitly and distinguish None, zero, empty text and JVM null.
- Classify `Some("0")`, `Some("25")`, `None`, `Some("bad")` and `Some(null)` as observed, observed, missing, rejected and rejected, and say why a supplied `null` is rejected rather than missing.
- Reconcile every input token into exactly one of the three ledger keys, so the counts always sum to the input size and an empty input still reports all three keys at zero.

## Vocabulary and concepts

- **Option:** A container representing either one present value with Some or absence with None.

- **Total function:** A function that returns a defined result for every input in its stated domain, rather than relying on an unchecked missing value.

- **flatMap:** A composition operation that avoids adding an extra container layer when the transformation itself returns an Option.

- **Missing versus rejected:** Missing means no token was supplied; rejected means a supplied token violated the parsing contract.

Option makes absence visible in a type. Some(0L) is a present observed zero, while None contains no amount. Those states should not be collapsed merely because zero is a convenient fallback. A reporting boundary may display a placeholder for absence, but the underlying record should retain whether a value was observed.

The Option type does not remove JVM null automatically. Option(null) becomes None, but Some(null) is a present container holding a null reference. This lesson treats a supplied null token as rejected rather than the same state as an absent token. It also rejects blank strings, signs, decimals and values outside the declared amount domain. That deliberate grammar prevents a permissive conversion from silently accepting representations the data contract did not authorize.

Scala 2.13 String.toLongOption returns Some for a representable whole-number token and None when conversion fails. Here it is combined with an ASCII-digit grammar and a nonnegative upper bound of 1000000 cents. Trimming is an explicit normalization rule, so Some(" 25 ") is accepted. Overflowing decimal text is rejected rather than wrapped or converted through floating point.

map transforms a present value while preserving None. flatMap composes a parser returning Option without producing Option[Option[Long]]. getOrElse can supply a display default, but using it too early with 0 L would lose missingness. Unchecked .get is avoided because it turns a missing-data branch into a runtime exception instead of a defined result.

A parser returning only Option cannot by itself distinguish no supplied token from an invalid supplied token. The ledger therefore consults both the original Option[String] and the parse result. This is a bridge toward the later Either lesson, which will carry a reason directly in the return type. For now, the classification string makes observed, missing and rejected counts explicit and reconciles them to input count.

The five token fixture contains observed zero, observed 25, absence, invalid text and a supplied null. Keep the first two numerical values, count one missing and two rejected, and retain their positions for review. A successful sum of 25 is insufficient evidence by itself because replacing every invalid or missing token with zero would produce the same sum while destroying the data-quality distinctions.

## Worked example / walkthrough

### Worked example 1

```scala
val present = Some(0L)
val absent = Option.empty[Long]
assert(present.contains(0L) && absent.isEmpty)
assert(present.map(_ + 5L).contains(5L))
assert(absent.map(_ + 5L).isEmpty)
println(s"present=$present absent=$absent")
```

map applies its function only to a present value. The observed zero transforms to five while absence remains absence. contains checks a value without calling unchecked get. The two states have different meanings even when a later display chooses a numeric fallback.

### Worked example 2

```scala
val safe = Option(null: String)
val suppliedNull = Some(null: String)
assert(safe.isEmpty)
assert(suppliedNull.isDefined)
assert(suppliedNull.flatMap(text => Option(text)).isEmpty)
println("Option(null) and Some(null) are distinct constructions")
```

The outer Some records that a token container was supplied, even though its reference is null. Wrapping the inner reference with Option prevents a method call on null. The exercise ledger uses that distinction to classify supplied malformed content separately from an absent field.

## Exercises

### Exercise 1: Parse a strict optional amount

Accept trimmed ASCII digits representing 0 through 1000000 cents. Return None for absent, blank, signed, decimal, overflowing or supplied-null tokens. Do not convert invalid input to zero or call unchecked Option.get.

**Expected result/shape:** Some("0") gives Some(0L), Some(" 25 ") gives Some(25L), None and Some("bad") give None. Some(null), Some("-1"), Some("1.0") and values above the bound are rejected.

**Verify:** Assert accepted zero and 25 independently, then test each invalid token and absence without an exception.

**Progressive hint:** Compose Option around the inner reference, trim, filter the grammar, then flatMap toLongOption and apply the bound.

### Exercise 2: Separate absence from invalid supplied content

Return observed for a valid supplied amount, missing for None, and rejected for any invalid Some token including Some(null). Keep the original input state available when classifying.

**Expected result/shape:** Some("0"), Some("25"), None, Some("bad"), Some(null) map to observed, observed, missing, rejected, rejected.

**Verify:** Assert the five classifications in order and show that parseAmount alone returns None for both missing and rejected cases.

**Progressive hint:** Pattern-match the original Option first; only supplied tokens need the parse-result decision.

### Exercise 3: Collect only observed numerical values

Return valid parsed amounts in original order using flatMap. Preserve zero and duplicate amounts; do not substitute defaults for missing or rejected tokens.

**Expected result/shape:** The five-token fixture yields `Seq(0L, 25L)`. Adding another Some("25") yields two 25-cent occurrences.

**Verify:** Assert exact observed sequences and an all-missing/rejected fixture returning empty.

**Progressive hint:** A sequence flatMap can concatenate zero-or-one results from each Option parser.

### Exercise 4: Reconcile all input states

Return counts for all three keys observed, missing, rejected, including zero counts. Classify every original token and require the counts to sum to input size.

**Expected result/shape:** The five-token fixture yields observed 2, missing 1, rejected 2. Empty input retains all three keys with count 0.

**Verify:** Assert the full map, its summed count, and the explicit empty-ledger keys.

**Progressive hint:** Start the fold with all three categories initialized to zero.

### Exercise 5: Keep presentation distinct from measurement

Return a valid amount as decimal text, or the literal missing/rejected classification for unavailable values. Do not display every unavailable value as 0.

**Expected result/shape:** Some("0") displays"0", None displays"missing", and Some("bad") displays"rejected". Whitespace around a valid 25 is normalized to"25".

**Verify:** Assert all four display strings and verify that missing is not numerically indistinguishable from observed zero.

**Progressive hint:** Use Option.fold with a fallback classification and a present-value formatting function.

### Exercise 6: Compose a downstream calculation without losing absence

Return the five-percent integer-cent fee for a valid parsed amount and None otherwise. Compose the calculation through Option rather than using getOrElse(0L) before the fee calculation.

**Expected result/shape:** Some("100") gives Some(5L), Some("0") gives Some(0L), and None or Some("bad") remain None.

**Verify:** Assert presence and exact fee for valid zero and 100, then absence for both invalid and missing inputs.

**Progressive hint:** The parser already returns Option[Long], so map is enough for a calculation that returns Long.

## Common pitfalls

If observed zero disappears, inspect a value-based filter rather than blaming Option. If None causes an exception, look for unchecked get or a method call on Some(null). If missing and invalid tokens have identical ledger labels, retain the original input state or move to Either with reasons. If total 25 passes while counts fail, do not repair the ledger by inventing zeros. If a signed or decimal token is accepted unexpectedly, compare the lexical grammar with the conversion method's broader behavior.

## Self-check

- What does `parseAmount` return for `Some(" 25 ")`, `Some("-1")`, `Some("1.0")` and `Some("1000001")`, and which of those are bound violations rather than format violations?
- Explain why `classify(Some(null))` must be "rejected" and not "missing". What would a ledger total of observed 2, missing 2, rejected 1 hide?
- `observed` returns `Seq(0L, 25L)` for the five-token fixture. Why is `flatMap` the right operation here, and why must the zero stay in the result?
- `displayAmount` prints "0", "missing" or "rejected". Why is this a presentation function only, and what goes wrong if a report sums the displayed text instead of the parsed values?
- `feeOption(Some("100"))` is `Some(5L)`. Trace `feeOption(Some("bad"))` and show where the absence carries through without a `.get`.

## Next step

Go on to [spark-006: Case classes, pattern matching, and domain states](spark-006.md). Here the value was the only question; next, each record carries an identity and one of several states (paid, voided, refunded), and a sealed type lets the compiler point out every place a new state must be handled.

## Primary sources and official APIs

- [Scala 2 Option and functional error handling](https://docs.scala-lang.org/overviews/scala-book/functional-error-handling.html).

- [Scala 2.13 Option API](https://www.scala-lang.org/api/2.13.16/scala/Option.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-005: Option, missing values, and total functions.
Read courses/scala-spark/guides/spark-005.md and courses/scala-spark/lessons/spark-005.scala. Direct prerequisites: spark-004.
Explain the Scala 2.13 syntax and data contract, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact assertion evidence and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt. Use only the prepared scala-jvm profile and preserve my saved work; do not install or download dependencies.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why an incorrect implementation fails.
```
