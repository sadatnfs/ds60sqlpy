object Main {
  def main(args: Array[String]): Unit = {
    val first: Long = 125L
    val second: Long = 200L
    val third: Long = 75L
    val total: Long = first + second + third
    println(s"total=$total")
    // Add your named values, expression and exact checks below.
  }
}

// Exercise 1: Compute the basket. Inputs: 125L,200L,75L. Expected: total is400L. Verify: assert total==400L and print the named value.
// Exercise 2: Preserve the type boundary. Inputs: 2147483647L+1L and an intentionally reviewed Int-only variant. Expected: Long result2147483648L; reject relying on the overflowing Int value as money. Verify: run the Long assertion; explain why the narrower arithmetic is a different contract.
// Exercise 3: Calculate remaining budget. Inputs: budget450L,total400L. Expected: remaining50L. Verify: assert the difference, not merely the total.
// Exercise 4: Return a branch value. Inputs: remaining50L, threshold0L. Expected: String message is within budget. Verify: assert the exact String and its nonnegative condition.
// Exercise 5: Diagnose reassignment. Inputs: one immutable binding and a proposed reassignment. Expected: compile-time rejection; repaired code uses a new name revisedBudget with350L. Verify: retain the compiler error category and show the new-name repair; do not include broken code in the final reference.
// Exercise 6: Transfer the budget. Inputs: same400L basket,new350L budget. Expected: remaining-50L and over budget label. Verify: assert both changed outputs while the original total stays400L.
