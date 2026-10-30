# spark-008: Explained reference solutions

Read the [guide](../guides/spark-008.md) and attempt the [learner source](../lessons/spark-008.scala) first. The [complete reference](spark-008_solution.scala) contains each implementation and its assertions. Values, identity, missingness and failure behavior are separate checks; compilation alone does not establish any of them.

## Exercises and reasoning

### Exercise 1: Compare multiplicity without requiring order

Return whether two Long sequences contain the same values with the same occurrence counts, ignoring order. Do not convert to Set. Empty sequences are equal.

**Expected:** (1,1,2) equals(2,1,1) as a bag but differs from(1,2). Equal count and sum alone are insufficient for(1,3) versus(2,2).

```scala
def bagEqual(left: Seq[Long], right: Seq[Long]): Boolean = {
  def counts(values: Seq[Long]): Map[Long, Long] =
    values.groupMapReduce(value => value)(_ => 1L)(_ + _)
  counts(left) == counts(right)
}
```

groupMapReduce groups by the value, contributes one count per occurrence and adds counts for equal values. Comparing the maps ignores presentation order while preserving multiplicity. The(1,3) versus(2,2) counterexample has equal length and sum but a different bag, showing why aggregate reconciliation alone cannot prove row-level equality.

```scala
assert(bagEqual(Seq(1L, 1L, 2L), Seq(2L, 1L, 1L)))
assert(!bagEqual(Seq(1L, 1L, 2L), Seq(1L, 2L)))
assert(!bagEqual(Seq(1L, 3L), Seq(2L, 2L)))
assert(bagEqual(Seq.empty, Seq.empty))
```

### Exercise 2: Detect a sum outside Long range

Sum Long values with checked addition and an explicit empty identity. Report overflow through ArithmeticException instead of allowing wraparound. Negative values are permitted for this arithmetic contract.

**Expected:** (100,-25,0,100) sums to 175; empty sums to 0; Long.MaxValue plus 1 and Long.MinValue minus 1 both fail.

```scala
def exactSum(values: Seq[Long]): Long = {
  values.foldLeft(0L)((sum, value) => Math.addExact(sum, value))
}
```

A sign-based overflow heuristic fails when negative values are legitimate or cancellation occurs. Math.addExact checks the actual representable range for each addition and throws on overflow. The empty identity is part of the contract rather than an exception case. This sequential checked sum may reject an intermediate overflow even if a differently ordered mathematical sum would fit; that order policy is deliberate and visible.

```scala
assert(exactSum(Seq(100L, -25L, 0L, 100L)) == 175L && exactSum(Seq.empty) == 0L)
expectArithmetic(exactSum(Seq(Long.MaxValue, 1L)))
expectArithmetic(exactSum(Seq(Long.MinValue, -1L)))
```

### Exercise 3: Promote before arithmetic

Return the mathematical value of an Int plus one as a Long. Convert before adding and support the full Int range.

**Expected:** Int.MaxValue becomes 2147483648 L, Int.MinValue becomes-2147483647L, and 0 becomes 1 L.

```scala
def promotedIncrement(value: Int): Long = {
  value.toLong + 1L
}
```

Every Int value is exactly representable as a Long, and adding one to the promoted range remains within Long bounds. The operation therefore has an exact result for the complete stated input domain. A conversion after value+1 would preserve an Int overflow. Testing both extremes verifies the type boundary rather than merely a common small-number case.

```scala
assert(promotedIncrement(Int.MaxValue) == 2147483648L)
assert(promotedIncrement(Int.MinValue) == -2147483647L && promotedIncrement(0) == 1L)
```

### Exercise 4: Define an approximate comparison policy

Compare finite Double values using absolute plus reference-relative tolerance. Require finite nonnegative tolerances with IllegalArgumentException on invalid policy. Return false for nonfinite actual or expected values.

**Expected:** 1e8+1 versus 1 e8 passes with atol 0, rtol 1 e-7;1e-9 versus 0 passes with atol 1 e-8; NaN never passes; negative tolerance is rejected.

```scala
def closeEnough(actual: Double, expected: Double, atol: Double, rtol: Double): Boolean = {
  require(
    java.lang.Double.isFinite(atol) && java.lang.Double
      .isFinite(rtol) && atol >= 0.0 && rtol >= 0.0,
    "invalid tolerance"
  )
  if (!java.lang.Double.isFinite(actual) || !java.lang.Double.isFinite(expected)) false
  else {
    val scale = math.max(math.abs(actual), math.abs(expected))
    if (scale == 0.0) true
    else
      math.abs(actual / scale - expected / scale) <= atol / scale + rtol * (math.abs(
        expected
      ) / scale)
  }
}
```

Absolute tolerance permits a small difference near zero where relative tolerance alone provides no allowance. Relative tolerance scales with the expected value and is therefore reference-oriented rather than symmetric. Scaling by the larger absolute input avoids an overflowed difference being compared with an overflowed tolerance. Nonfinite inputs are rejected as comparison evidence. These tolerances belong to approximate scientific values; integer cents in the earlier tasks retain exact equality and should not be made to pass by increasing a floating tolerance.

```scala
assert(closeEnough(1e8 + 1.0, 1e8, 0.0, 1e-7))
assert(closeEnough(1e-9, 0.0, 1e-8, 0.0))
assert(!closeEnough(1.0, 2.0, 0.0, 0.0) && !closeEnough(Double.NaN, 0.0, 1.0, 1.0))
assert(!closeEnough(1.7e308, -1.7e308, 0.0, 1.9))
assert(closeEnough(1.7e308, -1.7e308, 0.0, 2.0))
expectIllegalArgument(closeEnough(1.0, 1.0, -1.0, 0.0))
```

### Exercise 5: Check both conservation and classification

Validate a nonnegative/negative partition by checking the full combined bag and each branch predicate. Do not accept equal counts or sums as sufficient evidence.

**Expected:** Input(1,-1,0,1) with accepted(1,0,1), rejected(-1) passes. Dropping a duplicate, replacing(1,3) with (2,2), or placing zero in rejected fails.

```scala
def validPartition(input: Seq[Long], accepted: Seq[Long], rejected: Seq[Long]): Boolean = {
  bagEqual(input, accepted ++ rejected) && accepted.forall(_ >= 0L) && rejected.forall(_ < 0L)
}
```

Bag equality proves that the two outputs jointly preserve every input occurrence, but it does not prove that occurrences went to the correct side. The branch predicates add that semantic check. Count and total comparisons are useful diagnostics but weaker than this full tiny-fixture oracle. The zero misclassification case specifically challenges a common > versus>= mistake.

```scala
assert(validPartition(Seq(1L, -1L, 0L, 1L), Seq(1L, 0L, 1L), Seq(-1L)))
assert(!validPartition(Seq(1L, 1L), Seq(1L), Seq.empty))
assert(!validPartition(Seq(1L, 3L), Seq(2L, 2L), Seq.empty))
assert(!validPartition(Seq(0L), Seq.empty, Seq(0L)))
```

### Exercise 6: Show that an oracle rejects real misconceptions

Test a supplied nonnegative-filter candidate against four independent literal fixtures: empty,(0),(-1,0,2),(2,2,-1). Return false if it throws or violates a sequence result. Demonstrate rejection of zero-dropping and deduplicating candidates.

**Expected:** The >=0 filter passes. The >0 filter and a nonnegative-then-distinct implementation fail. A candidate throwing an exception also fails.

```scala
def filterContract(candidate: Seq[Long] => Seq[Long]): Boolean = {
  val cases = Seq(
    (Seq.empty[Long], Seq.empty[Long]),
    (Seq(0L), Seq(0L)),
    (Seq(-1L, 0L, 2L), Seq(0L, 2L)),
    (Seq(2L, 2L, -1L), Seq(2L, 2L))
  )
  try cases.forall { case (input, expected) => candidate(input) == expected }
  catch { case NonFatal(_) => false }
}
```

Expected outputs are independent literals chosen to distinguish the important behaviors. A harness that checks only one positive input could accept both zero loss and duplicate loss. Catching ordinary nonfatal exceptions converts a broken candidate into a failed contract rather than a misleading partial test run. Passing four fixtures is useful evidence within this teaching scope, not proof that arbitrary code is correct for every possible input.

```scala
assert(filterContract(values => values.filter(_ >= 0L)))
assert(!filterContract(values => values.filter(_ > 0L)))
assert(!filterContract(values => values.filter(_ >= 0L).distinct))
assert(!filterContract(_ => throw new IllegalStateException("broken")))
```

## Evidence and scope

Run the complete reference using the same prepared profile as the learner source. Its assertions check normal values, malformed or boundary inputs and conservation where relevant. The final version line records the actual compiler/runtime family used. The reference is an executable explanation, not a hidden grading service or proof that a distributed Spark job would have the same performance characteristics.
