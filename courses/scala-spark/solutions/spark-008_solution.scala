import scala.util.control.NonFatal

object Main {

  def bagEqual(left: Seq[Long], right: Seq[Long]): Boolean = {
    def counts(values: Seq[Long]): Map[Long, Long] =
      values.groupMapReduce(value => value)(_ => 1L)(_ + _)
    counts(left) == counts(right)
  }

  def exactSum(values: Seq[Long]): Long = {
    values.foldLeft(0L)((sum, value) => Math.addExact(sum, value))
  }

  def promotedIncrement(value: Int): Long = {
    value.toLong + 1L
  }

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

  def validPartition(input: Seq[Long], accepted: Seq[Long], rejected: Seq[Long]): Boolean = {
    bagEqual(input, accepted ++ rejected) && accepted.forall(_ >= 0L) && rejected.forall(_ < 0L)
  }

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

  def expectIllegalArgument(body: => Any): Unit = {
    var caught = false
    try body
    catch { case _: IllegalArgumentException => caught = true }
    assert(caught, "Expected IllegalArgumentException")
  }
  def expectArithmetic(body: => Any): Unit = {
    var caught = false
    try body
    catch { case _: ArithmeticException => caught = true }
    assert(caught, "Expected ArithmeticException")
  }

  def main(args: Array[String]): Unit = {
    // Exercise 1: Compare multiplicity without requiring order
    assert(bagEqual(Seq(1L, 1L, 2L), Seq(2L, 1L, 1L)))
    assert(!bagEqual(Seq(1L, 1L, 2L), Seq(1L, 2L)))
    assert(!bagEqual(Seq(1L, 3L), Seq(2L, 2L)))
    assert(bagEqual(Seq.empty, Seq.empty))
    // Exercise 2: Detect a sum outside Long range
    assert(exactSum(Seq(100L, -25L, 0L, 100L)) == 175L && exactSum(Seq.empty) == 0L)
    expectArithmetic(exactSum(Seq(Long.MaxValue, 1L)))
    expectArithmetic(exactSum(Seq(Long.MinValue, -1L)))
    // Exercise 3: Promote before arithmetic
    assert(promotedIncrement(Int.MaxValue) == 2147483648L)
    assert(promotedIncrement(Int.MinValue) == -2147483647L && promotedIncrement(0) == 1L)
    // Exercise 4: Define an approximate comparison policy
    assert(closeEnough(1e8 + 1.0, 1e8, 0.0, 1e-7))
    assert(closeEnough(1e-9, 0.0, 1e-8, 0.0))
    assert(!closeEnough(1.0, 2.0, 0.0, 0.0) && !closeEnough(Double.NaN, 0.0, 1.0, 1.0))
    assert(!closeEnough(1.7e308, -1.7e308, 0.0, 1.9))
    assert(closeEnough(1.7e308, -1.7e308, 0.0, 2.0))
    expectIllegalArgument(closeEnough(1.0, 1.0, -1.0, 0.0))
    // Exercise 5: Check both conservation and classification
    assert(validPartition(Seq(1L, -1L, 0L, 1L), Seq(1L, 0L, 1L), Seq(-1L)))
    assert(!validPartition(Seq(1L, 1L), Seq(1L), Seq.empty))
    assert(!validPartition(Seq(1L, 3L), Seq(2L, 2L), Seq.empty))
    assert(!validPartition(Seq(0L), Seq.empty, Seq(0L)))
    // Exercise 6: Show that an oracle rejects real misconceptions
    assert(filterContract(values => values.filter(_ >= 0L)))
    assert(!filterContract(values => values.filter(_ > 0L)))
    assert(!filterContract(values => values.filter(_ >= 0L).distinct))
    assert(!filterContract(_ => throw new IllegalStateException("broken")))
    println("spark-008: six reference contracts passed")
    println(
      "Scala=" + scala.util.Properties.versionNumberString + "; Java=" + System.getProperty(
        "java.version"
      )
    )
  }
}

// Exercise 1: Compare multiplicity without requiring order. Inputs/task: Return whether two Long sequences contain the same values with the same occurrence counts, ignoring order. Do not convert to Set. Empty sequences are equal. Expected: (1,1,2) equals(2,1,1) as a bag but differs from(1,2). Equal count and sum alone are insufficient for(1,3) versus(2,2). Verify: Assert all three comparisons and the empty case against literal expected Booleans.
// Exercise 2: Detect a sum outside Long range. Inputs/task: Sum Long values with checked addition and an explicit empty identity. Report overflow through ArithmeticException instead of allowing wraparound. Negative values are permitted for this arithmetic contract. Expected: (100,-25,0,100) sums to 175;empty sums to 0;Long.MaxValue plus 1 and Long.MinValue minus 1 both fail. Verify: Assert both exact sums and catch each directional overflow with the supplied exception helper.
// Exercise 3: Promote before arithmetic. Inputs/task: Return the mathematical value of an Int plus one as a Long. Convert before adding and support the full Int range. Expected: Int.MaxValue becomes 2147483648 L, Int.MinValue becomes-2147483647L, and 0 becomes 1 L. Verify: Assert exact literals at both boundaries and zero; compare with the deliberately too-late conversion example.
// Exercise 4: Define an approximate comparison policy. Inputs/task: Compare finite Double values using absolute plus reference-relative tolerance. Require finite nonnegative tolerances with IllegalArgumentException on invalid policy. Return false for nonfinite actual or expected values. Expected: 1e8+1 versus 1 e8 passes with atol 0, rtol 1 e-7;1e-9 versus 0 passes with atol 1 e-8;NaN never passes;negative tolerance is rejected. Verify: Assert large-scale and near-zero cases separately, then a strict zero-tolerance failure and nonfinite rejection.
// Exercise 5: Check both conservation and classification. Inputs/task: Validate a nonnegative/negative partition by checking the full combined bag and each branch predicate. Do not accept equal counts or sums as sufficient evidence. Expected: Input(1,-1,0,1) with accepted(1,0,1), rejected(-1) passes. Dropping a duplicate, replacing(1,3) with (2,2), or placing zero in rejected fails. Verify: Assert the good split and all three distinct counterexamples.
// Exercise 6: Show that an oracle rejects real misconceptions. Inputs/task: Test a supplied nonnegative-filter candidate against four independent literal fixtures:empty,(0),(-1,0,2),(2,2,-1). Return false if it throws or violates a sequence result. Demonstrate rejection of zero-dropping and deduplicating candidates. Expected: The >=0 filter passes. The >0 filter and a nonnegative-then-distinct implementation fail. A candidate throwing an exception also fails. Verify: Assert one accepted candidate and three rejected candidates, so a success-only harness cannot pass unnoticed.
