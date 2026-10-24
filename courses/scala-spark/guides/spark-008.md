# spark-008: Assertions, numeric boundaries, and independent oracles

Authored tutorial and practice content. The prepared Scala/JVM worker executes a bounded program; process success and understanding remain distinct. No source file installs a tool or downloads a dependency.

## Level and prerequisites

Beginner; approximately 105 minutes. Direct design prerequisites: `spark-007`. The lesson uses Scala 2.13 syntax and the prepared JDK 17 worker. The older design document proposed a different Spark/JDK tuple; use the current [execution baseline](../execution-baseline.md) for this authored material.

## How to run this lesson

Open `spark-008` in the classroom, select the Scala source, prepare the `scala-jvm` profile and run the saved pad. The worker stages the single source as `Main.scala` and invokes `object Main`. Read the terminal output and exact assertions. The [learner source](../lessons/spark-008.scala) runs two complete demonstrations; its six task functions remain explicit stubs until you implement them. Preserve your saved attempt. The [reference program](../solutions/spark-008_solution.scala) and [explained solutions](../solutions/spark-008_solutions.md) are separate and should be opened after an attempt or an explicit worked-comparison request. If the profile is unavailable, reading and saving remain available; opening this guide does not prepare a runtime.

## Learning objectives

- Test functions with exact integer money values and recognize overflow and order-sensitive comparisons.
- Explain the result of both worked examples before running them.
- Implement the six contracts, inspect normal and boundary evidence, and explain a counterexample in your own words.

## Vocabulary and concepts

- **Oracle:** An independently specified expected result used to challenge an implementation, rather than a second copy of the same algorithm.

- **Bag equality:** Equality of values and multiplicities while ignoring sequence order.

- **Checked arithmetic:** An operation that reports representational overflow instead of silently wrapping.

- **Absolute and relative tolerance:** Two explicit scales for comparing approximate values, with absolute tolerance governing behavior near zero.

An assertion is useful when it distinguishes the intended behavior from a plausible mistake. Checking only that a program exits or returns a nonempty result is weak evidence. Exact integer fixtures, empty inputs, zero values, repeated occurrences and malformed boundaries each expose different failure modes. The reference deliberately includes candidates that drop zero or deduplicate equal amounts so the oracle proves it can reject them.

Sequence equality compares order and values. Bag equality compares each value's occurrence count. Set equality discards multiplicity and is therefore insufficient for an event ledger. The sequences(1,1,2) and (2,1,1) are the same bag, while(1,2) is not. Decide which equality the output contract requires before choosing a comparison helper.

Numeric type conversion must happen before an overflowing operation. Int.MaxValue+1 wraps in Int arithmetic; converting that wrapped result to Long does not recover the intended 2147483648. Convert the operand to Long first, then add. For arbitrary Long sums, use Math.addExact when silent wraparound would invalidate the result. A wider type increases range but does not make it unlimited.

Approximate floating values require a different comparison contract. The rule abs(actual-expected)<=atol+rtol*abs(expected) combines a near-zero allowance with scale-relative error. It is not a substitute for exact money arithmetic. Reject nonfinite comparison inputs and invalid tolerances explicitly so NaN or infinity cannot make a failed calculation appear acceptable.

A partition audit should verify more than accepted_count+rejected_count=input_count. Two changed values can preserve both count and sum. Compare the full bag and the classification rule: accepted amounts must be nonnegative and rejected amounts negative. This catches hidden replacement and a zero assigned to the wrong branch.

Finally, a finite fixture suite is evidence rather than a proof for every possible input. An implementation can overfit known cases, and a model can satisfy arithmetic checks while representing the wrong business quantity. State the input domain, choose adversarial examples from the mechanism, and combine exact fixtures with general invariants. The lesson's candidate-checking function is a teaching harness, not the classroom's registered trusted verifier.

## Worked example / walkthrough

### Worked example 1

```scala
val values = Seq(1L,1L,2L)
assert(values.toSet == Seq(1L,2L).toSet)
assert(values.sorted != Seq(1L,2L).sorted)
assert(values.sorted == Seq(2L,1L,1L).sorted)
println("Set equality loses a repeated occurrence")
```

The first assertion intentionally shows a misleading equality: sets agree despite a lost occurrence. Sorting retains every occurrence and lets order-insensitive sequence comparison expose the loss. An oracle should name whether order, multiplicity or identity matters rather than choosing a convenient collection conversion.

### Worked example 2

```scala
val wrapped: Int = Int.MaxValue + 1
val promoted: Long = Int.MaxValue.toLong + 1L
val tooLate: Long = wrapped.toLong
assert(wrapped == Int.MinValue)
assert(promoted == 2147483648L && tooLate == -2147483648L)
println(s"promoted=$promoted tooLate=$tooLate")
```

The expression is evaluated using the operand types at the time of addition. A later conversion preserves the already-wrong wrapped value. The independent literal 2147483648 L shows the intended mathematical result and the Long suffix prevents the expected value from suffering the same type mistake.

## Exercises

### Exercise 1: Compare multiplicity without requiring order

Return whether two Long sequences contain the same values with the same occurrence counts, ignoring order. Do not convert to Set. Empty sequences are equal.

**Expected result/shape:** (1,1,2) equals(2,1,1) as a bag but differs from(1,2). Equal count and sum alone are insufficient for(1,3) versus(2,2).

**Verify:** Assert all three comparisons and the empty case against literal expected Booleans.

**Progressive hint:** Build a value-to-count Map for each sequence using groupMapReduce or a fold.

### Exercise 2: Detect a sum outside Long range

Sum Long values with checked addition and an explicit empty identity. Report overflow through ArithmeticException instead of allowing wraparound. Negative values are permitted for this arithmetic contract.

**Expected result/shape:** (100,-25,0,100) sums to 175; empty sums to 0; Long.MaxValue plus 1 and Long.MinValue minus 1 both fail.

**Verify:** Assert both exact sums and catch each directional overflow with the supplied exception helper.

**Progressive hint:** Use Math.addExact in a fold, not ordinary addition followed by a sign check.

### Exercise 3: Promote before arithmetic

Return the mathematical value of an Int plus one as a Long. Convert before adding and support the full Int range.

**Expected result/shape:** Int.MaxValue becomes 2147483648 L, Int.MinValue becomes-2147483647L, and 0 becomes 1 L.

**Verify:** Assert exact literals at both boundaries and zero; compare with the deliberately too-late conversion example.

**Progressive hint:** The receiver of toLong must be the input, not the result of an Int addition.

### Exercise 4: Define an approximate comparison policy

Compare finite Double values using absolute plus reference-relative tolerance. Require finite nonnegative tolerances with IllegalArgumentException on invalid policy. Return false for nonfinite actual or expected values.

**Expected result/shape:** 1e8+1 versus 1 e8 passes with atol 0, rtol 1 e-7;1e-9 versus 0 passes with atol 1 e-8; NaN never passes; negative tolerance is rejected.

**Verify:** Assert large-scale and near-zero cases separately, then a strict zero-tolerance failure and nonfinite rejection.

**Progressive hint:** Validate the policy before computing the reference-scaled tolerance.

### Exercise 5: Check both conservation and classification

Validate a nonnegative/negative partition by checking the full combined bag and each branch predicate. Do not accept equal counts or sums as sufficient evidence.

**Expected result/shape:** Input(1,-1,0,1) with accepted(1,0,1), rejected(-1) passes. Dropping a duplicate, replacing(1,3) with (2,2), or placing zero in rejected fails.

**Verify:** Assert the good split and all three distinct counterexamples.

**Progressive hint:** Combine bagEqual with forall checks on both branches.

### Exercise 6: Show that an oracle rejects real misconceptions

Test a supplied nonnegative-filter candidate against four independent literal fixtures: empty,(0),(-1,0,2),(2,2,-1). Return false if it throws or violates a sequence result. Demonstrate rejection of zero-dropping and deduplicating candidates.

**Expected result/shape:** The >=0 filter passes. The >0 filter and a nonnegative-then-distinct implementation fail. A candidate throwing an exception also fails.

**Verify:** Assert one accepted candidate and three rejected candidates, so a success-only harness cannot pass unnoticed.

**Progressive hint:** Keep expected sequences as literals instead of computing them with the same filter being tested.

## Common pitfalls

If a test passes despite a dropped duplicate, inspect whether the oracle compared Sets or only a total. If a boundary result is negative after increasing an Int, move the conversion before the operation. If a floating comparison passes NaN or a huge tolerance hides a logic error, review the policy rather than weakening assertions. If an invalid candidate passes every test, add a mechanism-specific counterexample and keep expected values independent of the candidate implementation. Finite fixture success is not automatic learner mastery or a universal correctness proof.

## Self-check

Without opening the reference, trace the listed boundary case through `bagEqual`. Then explain why `filterContract` needs its declared invariant or input restriction. Name the exact assertion that would reject one tempting wrong implementation. Retain the observed values and explain how they support the lesson outcome: Test functions with exact integer money values and recognize overflow and order-sensitive comparisons.

## Next step

Continue to the next lesson only after you can explain the boundary behavior. The [course route](../README.md) shows authored material and runtime evidence separately.

## Primary sources and official APIs

- [Scala 2.13 collections operations](https://docs.scala-lang.org/overviews/collections-2.13/operations.html).

- [Java17 Math.addExact](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Math.html#addExact(long,long)).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-008: Assertions, numeric boundaries, and independent oracles.
Read courses/scala-spark/guides/spark-008.md and courses/scala-spark/lessons/spark-008.scala. Direct prerequisites: spark-007.
Explain the Scala 2.13 syntax and data contract, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact assertion evidence and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt. Use only the prepared scala-jvm profile and preserve my saved work; do not install or download dependencies.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why an incorrect implementation fails.
```
