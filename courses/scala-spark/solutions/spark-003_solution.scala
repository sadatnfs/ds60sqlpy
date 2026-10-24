object Main {
  // Lesson domain: -1000000L <= amount <= 1000000L.
  def addCents(left: Long, right: Long): Long = left + right
  def feeCents(amount: Long, isMember: Boolean): Long = {
    require(amount >= -1000000L && amount <= 1000000L, "outside lesson domain")
    if (amount <= 0L) 0L
    else if (!isMember) 20L
    else if (amount < 500L) 0L
    else amount * 5L / 100L
  }
  def main(args: Array[String]): Unit = {
    assert(addCents(100L, 25L) == 125L)
    assert(feeCents(0L, true) == 0L && feeCents(0L, false) == 0L)
    assert(feeCents(100L, true) == 0L && feeCents(100L, false) == 20L)
    assert(feeCents(500L, true) == 25L && feeCents(500L, false) == 20L)
    assert(feeCents(499L, true) == 0L)
    assert(feeCents(501L, true) == 25L)
    assert(feeCents(-1L, false) == 0L)
    assert(feeCents(isMember = true, amount = 1000L) == 50L)
    assert(feeCents(1000L, true) == feeCents(1000L, true))
    println("fee checks passed: boundaries, branches, exact cents")
  }
}

// Exercise 1: Separate definition and call. Inputs: addCents(100L,25L),addCents(0L,25L). Expected: 125L and25L. Verify: assert both returned values; distinguish parameter names from arguments.
// Exercise 2: Implement branch order. Inputs: 0L with both membership values;100L with both values. Expected: fees0/0 for zero and0/20 for100. Verify: assert all four cases and inspect guard order.
// Exercise 3: Test the membership threshold. Inputs: member499L,500L,501L. Expected: fees0L,25L,25L. Verify: assert the exact three outputs and explain integer division.
// Exercise 4: Use named arguments. Inputs: feeCents(isMember=true,amount=1000L). Expected: 50L, equal to the positional call. Verify: assert both calls give50L; do not change the definition.
// Exercise 5: Reject hidden state. Inputs: two consecutive feeCents(1000L,true) calls and negative amount-1L. Expected: both calls50L; negative amount yields0L even for a nonmember. Verify: repeat exact calls and explain why a call counter must not alter the returned fee.
// Exercise 6: Transfer and explain the domain. Inputs: 2000L,true/false and2000000L. Expected: 100L/20L; the out-of-domain input is rejected by the reference precondition. Verify: assert the two valid results and identify the violated bound for the third.
