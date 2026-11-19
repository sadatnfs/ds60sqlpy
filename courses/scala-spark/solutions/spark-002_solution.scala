object Main {
  def main(args: Array[String]): Unit = {
    val first: Long = 125L
    val second: Long = 200L
    val third: Long = 75L
    val total: Long = first + second + third
    val budget: Long = 450L
    val remaining: Long = budget - total
    val message: String = if (remaining >= 0L) "within budget" else "over budget"
    assert(total == 400L)
    assert(remaining == 50L)
    assert(message == "within budget")
    val revisedBudget: Long = 350L
    assert(revisedBudget - total == -50L)
    assert(2147483647L + 1L == 2147483648L)
    println(s"total=$total remaining=$remaining message=$message")
    println(s"revisedRemaining=${revisedBudget - total}")
  }
}

// Exercise 1: Compute the basket. Inputs: 125L, 200L, 75L. Expected: total is 400L. Verify: assert total==400L and print the named value.
// Exercise 2: Preserve the type boundary. Inputs: 2147483647L+1L and an intentionally reviewed Int-only variant. Expected: Long result 2147483648L; reject relying on the overflowing Int value as money. Verify: run the Long assertion; explain why the narrower arithmetic is a different contract.
// Exercise 3: Calculate remaining budget. Inputs: budget 450L, total 400L. Expected: remaining 50L. Verify: assert the difference, not merely the total.
// Exercise 4: Return a branch value. Inputs: remaining 50L, threshold 0L. Expected: String message is within budget. Verify: assert the exact String and its nonnegative condition.
// Exercise 5: Diagnose reassignment. Inputs: one immutable binding and a proposed reassignment. Expected: compile-time rejection; repaired code uses a new name revisedBudget with 350L. Verify: retain the compiler error category and show the new-name repair; do not include broken code in the final reference.
// Exercise 6: Transfer the budget. Inputs: same 400L basket, new 350L budget. Expected: remaining-50L and over budget label. Verify: assert both changed outputs while the original total stays 400L.
