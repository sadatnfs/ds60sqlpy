

object Main {


  def accepted(values: Seq[Long]): Seq[Long] = {
    values.filter(_ >= 0L)
  }

  def partitionAmounts(values: Seq[Long]): (Seq[Long], Seq[Long]) = {
    values.partition(_ >= 0L)
  }

  def fivePercent(values: Seq[Long]): Seq[Long] = {
    require(values.forall(_ >= 0L), "fees require nonnegative amounts")
    values.map(_ / 20L)
  }

  def summary(values: Seq[Long]): (Long, Long) = {
    values.foldLeft((0L, 0L)) { case ((count, total), amount) =>
      (count + 1L, Math.addExact(total, amount))
    }
  }

  def frequencies(values: Seq[Long]): Map[Long, Long] = {
    values.foldLeft(Map.empty[Long, Long]) { (counts, amount) =>
      counts.updated(amount, counts.getOrElse(amount, 0L) + 1L)
    }
  }

  def groupedSummary(records: Seq[(String, Long)]): Map[String, (Long, Long)] = {
    require(records.forall { case (group, _) => group != null && group.trim.nonEmpty }, "group labels must be known")
    records.filter(_._2 >= 0L).groupBy(_._1).map { case (group, rows) =>
      group -> summary(rows.map(_._2))
    }
  }

  def expectIllegalArgument(body: => Any): Unit = {
    var caught = false
    try body catch { case _: IllegalArgumentException => caught = true }
    assert(caught, "Expected IllegalArgumentException")
  }
  def expectArithmetic(body: => Any): Unit = {
    var caught = false
    try body catch { case _: ArithmeticException => caught = true }
    assert(caught, "Expected ArithmeticException")
  }

  def main(args: Array[String]): Unit = {
    // Exercise 1: Retain observed zero and repeated values
    val raw = Seq(100L, -5L, 0L, 100L, 25L)
    assert(accepted(raw) == Seq(100L, 0L, 100L, 25L))
    assert(raw == Seq(100L, -5L, 0L, 100L, 25L))
    assert(accepted(Seq.empty[Long]).isEmpty)
    // Exercise 2: Keep a rejected ledger
    val split = partitionAmounts(raw)
    assert(split._1 == Seq(100L, 0L, 100L, 25L) && split._2 == Seq(-5L))
    assert(split._1.size + split._2.size == raw.size)
    assert(partitionAmounts(Seq(-2L, -1L)) == (Seq.empty[Long], Seq(-2L, -1L)))
    // Exercise 3: Map a bounded numeric policy
    assert(fivePercent(accepted(raw)) == Seq(5L, 0L, 5L, 1L))
    assert(fivePercent(Seq(Long.MaxValue)) == Seq(Long.MaxValue / 20L))
    expectIllegalArgument(fivePercent(Seq(-1L)))
    // Exercise 4: Fold count and total together
    assert(summary(accepted(raw)) == (4L, 225L))
    assert(summary(Seq.empty[Long]) == (0L, 0L))
    expectArithmetic(summary(Seq(Long.MaxValue, 1L)))
    // Exercise 5: Represent multiplicity in a Map
    val frequency = frequencies(accepted(raw))
    assert(frequency == Map(100L -> 2L, 0L -> 1L, 25L -> 1L))
    assert(frequency.values.sum == 4L && frequencies(Seq.empty[Long]).isEmpty)
    // Exercise 6: Transfer the bag contract to grouped reporting
    val grouped = groupedSummary(Seq(("A",100L),("A",100L),("B",0L),("B",25L),("C",-5L)))
    assert(grouped == Map("A" -> (2L,200L), "B" -> (2L,25L)))
    assert(grouped.values.map(_._1).sum == 4L && grouped.values.map(_._2).sum == 225L)
    expectIllegalArgument(groupedSummary(Seq(("",-5L))))
    println("spark-004: six reference contracts passed")
    println("Scala=" + scala.util.Properties.versionNumberString + "; Java=" + System.getProperty("java.version"))
  }
}

// Exercise 1: Retain observed zero and repeated values. Inputs/task: Implement a nonnegative filter for Seq(100L,-5L,0L,100L,25L). Preserve input order and duplicate values. An empty input should remain empty. Expected: The result is Seq(100L,0L,100L,25L), with four occurrences. Both 100-cent entries and the zero remain. Verify: Assert the exact sequence and confirm the original five-element sequence is unchanged; also assert accepted(Seq.empty) is empty.
// Exercise 2: Keep a rejected ledger. Inputs/task: Split every input amount into accepted nonnegative and rejected negative sequences, preserving order within each output. Return both sequences instead of dropping rejected data. Expected: The five-value fixture yields accepted four values and rejected Seq(-5L). Accepted size plus rejected size equals five, including an all-negative or empty fixture. Verify: Assert both exact outputs, their combined count and an all-negative case with empty accepted output.
// Exercise 3: Map a bounded numeric policy. Inputs/task: For nonnegative Long amounts, return integer-cent five-percent fees rounded down. Reject a negative amount with IllegalArgumentException. Avoid multiplying by five before division, which could overflow on a very large Long. Expected: Seq(100L,0L,100L,25L) maps to Seq(5L,0L,5L,1L). Long.MaxValue maps safely to Long.MaxValue/20L. Verify: Assert the exact four fees, the maximum-Long case and rejection of Seq(-1L).
// Exercise 4: Fold count and total together. Inputs/task: Return occurrence count and checked Long total for a supplied sequence. Use an explicit tuple accumulator and Math.addExact for the total. Empty input returns (0L,0L); an overflowing total raises ArithmeticException. Expected: The accepted fixture returns (4L,225L), while Seq(Long.MaxValue,1L) is rejected by checked addition. Verify: Assert the two-component result, the empty identity and the overflow exception independently.
// Exercise 5: Represent multiplicity in a Map. Inputs/task: Return a map from amount to occurrence count without discarding repeated values. Compare maps by keys and counts rather than assuming iteration order. Empty input returns an empty map. Expected: The accepted fixture yields Map(100L->2L,0L->1L,25L->1L); the sum of counts is four. Verify: Assert exact map equality and reconcile all map counts to the accepted sequence size.
// Exercise 6: Transfer the bag contract to grouped reporting. Inputs/task: Given group/amount pairs, reject blank group labels, retain nonnegative amount occurrences and return per-group(count, total) using checked summary. Groups with only rejected amounts are absent from the accepted report and remain explainable through the rejection policy. Expected: A100, A100, B0, B25, C-5 yields A:(2,200), B:(2,25). Report counts sum to four and totals to 225; a blank label is rejected even on a negative row. Verify: Assert the complete map, both global reconciliations and the blank-label failure before filtering can hide it.
