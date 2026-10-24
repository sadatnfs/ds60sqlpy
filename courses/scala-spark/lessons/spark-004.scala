object Main {

  def accepted(values: Seq[Long]): Seq[Long] =
    throw new UnsupportedOperationException("Complete accepted")

  def partitionAmounts(values: Seq[Long]): (Seq[Long], Seq[Long]) =
    throw new UnsupportedOperationException("Complete partitionAmounts")

  def fivePercent(values: Seq[Long]): Seq[Long] =
    throw new UnsupportedOperationException("Complete fivePercent")

  def summary(values: Seq[Long]): (Long, Long) =
    throw new UnsupportedOperationException("Complete summary")

  def frequencies(values: Seq[Long]): Map[Long, Long] =
    throw new UnsupportedOperationException("Complete frequencies")

  def groupedSummary(records: Seq[(String, Long)]): Map[String, (Long, Long)] =
    throw new UnsupportedOperationException("Complete groupedSummary")

  def main(args: Array[String]): Unit = {
    locally {
      val original = Seq(1L, 2L, 3L)
      val doubled = original.map(value => value * 2L)
      assert(doubled == Seq(2L, 4L, 6L))
      assert(original == Seq(1L, 2L, 3L))
      println(doubled.mkString(","))
    }
    locally {
      val amounts = Seq(12L, 3L)
      val total = amounts.foldLeft(0L)((sum, amount) => Math.addExact(sum, amount))
      val emptyTotal = Seq.empty[Long].foldLeft(0L)(_ + _)
      assert(total == 15L && emptyTotal == 0L)
      println(s"total=$total empty=$emptyTotal")
    }
    println("spark-004: worked examples passed; six task implementations remain")
  }
}

// Exercise 1: Retain observed zero and repeated values. Inputs/task: Implement a nonnegative filter for Seq(100L,-5L,0L,100L,25L). Preserve input order and duplicate values. An empty input should remain empty. Expected: The result is Seq(100L,0L,100L,25L), with four occurrences. Both 100-cent entries and the zero remain. Verify: Assert the exact sequence and confirm the original five-element sequence is unchanged; also assert accepted(Seq.empty) is empty.
// Exercise 2: Keep a rejected ledger. Inputs/task: Split every input amount into accepted nonnegative and rejected negative sequences, preserving order within each output. Return both sequences instead of dropping rejected data. Expected: The five-value fixture yields accepted four values and rejected Seq(-5L). Accepted size plus rejected size equals five, including an all-negative or empty fixture. Verify: Assert both exact outputs, their combined count and an all-negative case with empty accepted output.
// Exercise 3: Map a bounded numeric policy. Inputs/task: For nonnegative Long amounts, return integer-cent five-percent fees rounded down. Reject a negative amount with IllegalArgumentException. Avoid multiplying by five before division, which could overflow on a very large Long. Expected: Seq(100L,0L,100L,25L) maps to Seq(5L,0L,5L,1L). Long.MaxValue maps safely to Long.MaxValue/20L. Verify: Assert the exact four fees, the maximum-Long case and rejection of Seq(-1L).
// Exercise 4: Fold count and total together. Inputs/task: Return occurrence count and checked Long total for a supplied sequence. Use an explicit tuple accumulator and Math.addExact for the total. Empty input returns (0L,0L); an overflowing total raises ArithmeticException. Expected: The accepted fixture returns (4L,225L), while Seq(Long.MaxValue,1L) is rejected by checked addition. Verify: Assert the two-component result, the empty identity and the overflow exception independently.
// Exercise 5: Represent multiplicity in a Map. Inputs/task: Return a map from amount to occurrence count without discarding repeated values. Compare maps by keys and counts rather than assuming iteration order. Empty input returns an empty map. Expected: The accepted fixture yields Map(100L->2L,0L->1L,25L->1L); the sum of counts is four. Verify: Assert exact map equality and reconcile all map counts to the accepted sequence size.
// Exercise 6: Transfer the bag contract to grouped reporting. Inputs/task: Given group/amount pairs, reject blank group labels, retain nonnegative amount occurrences and return per-group(count, total) using checked summary. Groups with only rejected amounts are absent from the accepted report and remain explainable through the rejection policy. Expected: A100, A100, B0, B25, C-5 yields A:(2,200), B:(2,25). Report counts sum to four and totals to 225; a blank label is rejected even on a negative row. Verify: Assert the complete map, both global reconciliations and the blank-label failure before filtering can hide it.
