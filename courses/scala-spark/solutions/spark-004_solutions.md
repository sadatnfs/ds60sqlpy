# spark-004: Explained reference solutions

Read the [guide](../guides/spark-004.md) and attempt the [learner source](../lessons/spark-004.scala) first. The [complete reference](spark-004_solution.scala) contains each implementation and its assertions. Values, identity, missingness and failure behavior are separate checks; compilation alone does not establish any of them.

## Exercises and reasoning

### Exercise 1: Retain observed zero and repeated values

Implement a nonnegative filter for Seq(100L,-5L,0L,100L,25L). Preserve input order and duplicate values. An empty input should remain empty.

**Expected:** The result is Seq(100L,0L,100L,25L), with four occurrences. Both 100-cent entries and the zero remain.

```scala
def accepted(values: Seq[Long]): Seq[Long] = {
  values.filter(_ >= 0L)
}
```

The >= comparison retains zero, which is an observed amount rather than missing data. filter preserves the original order and multiplicity of retained values. A Set would lose one 100-cent occurrence, while a > comparison would lose zero. Checking the exact sequence distinguishes these plausible but incorrect implementations from a correct result with the same positive-value sum.

```scala
val raw = Seq(100L, -5L, 0L, 100L, 25L)
assert(accepted(raw) == Seq(100L, 0L, 100L, 25L))
assert(raw == Seq(100L, -5L, 0L, 100L, 25L))
assert(accepted(Seq.empty[Long]).isEmpty)
```

### Exercise 2: Keep a rejected ledger

Split every input amount into accepted nonnegative and rejected negative sequences, preserving order within each output. Return both sequences instead of dropping rejected data.

**Expected:** The five-value fixture yields accepted four values and rejected Seq(-5L). Accepted size plus rejected size equals five, including an all-negative or empty fixture.

```scala
def partitionAmounts(values: Seq[Long]): (Seq[Long], Seq[Long]) = {
  values.partition(_ >= 0L)
}
```

partition records both sides of the predicate, making rejected data countable and inspectable. Tuple fields _1 and _2 refer to the accepted and rejected outputs in the declared order. Count conservation verifies that no input occurrence disappeared, but exact-value checks are still needed because counts alone could conceal a misclassified zero or negative amount.

```scala
val split = partitionAmounts(raw)
assert(split._1 == Seq(100L, 0L, 100L, 25L) && split._2 == Seq(-5L))
assert(split._1.size + split._2.size == raw.size)
assert(partitionAmounts(Seq(-2L, -1L)) == (Seq.empty[Long], Seq(-2L, -1L)))
```

### Exercise 3: Map a bounded numeric policy

For nonnegative Long amounts, return integer-cent five-percent fees rounded down. Reject a negative amount with IllegalArgumentException. Avoid multiplying by five before division, which could overflow on a very large Long.

**Expected:** Seq(100L,0L,100L,25L) maps to Seq(5L,0L,5L,1L). Long.MaxValue maps safely to Long.MaxValue/20L.

```scala
def fivePercent(values: Seq[Long]): Seq[Long] = {
  require(values.forall(_ >= 0L), "fees require nonnegative amounts")
  values.map(_ / 20L)
}
```

The algebraic simplification removes an unnecessary overflow-prone intermediate while preserving the stated rounding policy for nonnegative integers. map retains one fee per accepted occurrence, including zero and repeated amounts. The precondition rejects negative amounts because division rounding for negative values would need a separately defined financial rule rather than silently inheriting JVM integer behavior.

```scala
assert(fivePercent(accepted(raw)) == Seq(5L, 0L, 5L, 1L))
assert(fivePercent(Seq(Long.MaxValue)) == Seq(Long.MaxValue / 20L))
expectIllegalArgument(fivePercent(Seq(-1L)))
```

### Exercise 4: Fold count and total together

Return occurrence count and checked Long total for a supplied sequence. Use an explicit tuple accumulator and Math.addExact for the total. Empty input returns (0L,0L); an overflowing total raises ArithmeticException.

**Expected:** The accepted fixture returns (4L,225L), while Seq(Long.MaxValue,1L) is rejected by checked addition.

```scala
def summary(values: Seq[Long]): (Long, Long) = {
  values.foldLeft((0L, 0L)) { case ((count, total), amount) =>
    (count + 1L, Math.addExact(total, amount))
  }
}
```

The count records occurrences, not distinct values. The initial tuple defines both results for empty input and makes their Long types explicit. Math.addExact makes range failure observable; ordinary Long addition would wrap. A count of four and total 225 together distinguish the intended bag from a deduplicated or zero-dropping transformation that might preserve only one of those metrics.

```scala
assert(summary(accepted(raw)) == (4L, 225L))
assert(summary(Seq.empty[Long]) == (0L, 0L))
expectArithmetic(summary(Seq(Long.MaxValue, 1L)))
```

### Exercise 5: Represent multiplicity in a Map

Return a map from amount to occurrence count without discarding repeated values. Compare maps by keys and counts rather than assuming iteration order. Empty input returns an empty map.

**Expected:** The accepted fixture yields Map(100L->2L,0L->1L,25L->1L); the sum of counts is four.

```scala
def frequencies(values: Seq[Long]): Map[Long, Long] = {
  values.foldLeft(Map.empty[Long, Long]) { (counts, amount) =>
    counts.updated(amount, counts.getOrElse(amount, 0L) + 1L)
  }
}
```

updated returns a new immutable map value while retaining previously recorded keys. getOrElse supplies the zero-count identity only for a new key. The map now preserves multiplicity explicitly, unlike a Set. Map equality is independent of presentation order, so a separate sort should be used if a stable printed sequence is required.

```scala
val frequency = frequencies(accepted(raw))
assert(frequency == Map(100L -> 2L, 0L -> 1L, 25L -> 1L))
assert(frequency.values.sum == 4L && frequencies(Seq.empty[Long]).isEmpty)
```

### Exercise 6: Transfer the bag contract to grouped reporting

Given group/amount pairs, reject blank group labels, retain nonnegative amount occurrences and return per-group(count, total) using checked summary. Groups with only rejected amounts are absent from the accepted report and remain explainable through the rejection policy.

**Expected:** A100, A100, B0, B25, C-5 yields A:(2,200), B:(2,25). Report counts sum to four and totals to 225; a blank label is rejected even on a negative row.

```scala
def groupedSummary(records: Seq[(String, Long)]): Map[String, (Long, Long)] = {
  require(records.forall { case (group, _) => group != null && group.trim.nonEmpty }, "group labels must be known")
  records.filter(_._2 >= 0L).groupBy(_._1).map { case (group, rows) =>
    group -> summary(rows.map(_._2))
  }
}
```

Identity validation precedes amount filtering so an invalid group label cannot disappear inside the rejected-amount branch. groupBy retains all accepted occurrences for a group, and the already tested summary contract supplies count and checked total. The two global sums reconcile grouped output with accepted input. Absence of C means no accepted C rows, not a measured zero C total.

```scala
val grouped = groupedSummary(Seq(("A",100L),("A",100L),("B",0L),("B",25L),("C",-5L)))
assert(grouped == Map("A" -> (2L,200L), "B" -> (2L,25L)))
assert(grouped.values.map(_._1).sum == 4L && grouped.values.map(_._2).sum == 225L)
expectIllegalArgument(groupedSummary(Seq(("",-5L))))
```

## Evidence and scope

Run the complete reference using the same prepared profile as the learner source. Its assertions check normal values, malformed or boundary inputs and conservation where relevant. The final version line records the actual compiler/runtime family used. The reference is an executable explanation, not a hidden grading service or proof that a distributed Spark job would have the same performance characteristics.
