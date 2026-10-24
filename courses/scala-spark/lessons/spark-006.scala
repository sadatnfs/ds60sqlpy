object Main {
  sealed trait Event { def id: String }
  final case class Paid(id: String, cents: Long) extends Event {
    require(id != null && id.trim.nonEmpty, "event ID is required")
    require(cents >= 0L && cents <= 1000000L, "paid amount outside domain")
  }
  final case class Voided(id: String, reason: String) extends Event {
    require(id != null && id.trim.nonEmpty, "event ID is required")
    require(reason != null && reason.trim.nonEmpty, "void reason is required")
  }
  final case class Refunded(id: String, cents: Long) extends Event {
    require(id != null && id.trim.nonEmpty, "event ID is required")
    require(cents >= 0L && cents <= 1000000L, "refund amount outside domain")
  }

  def eventId(event: Event): String =
    throw new UnsupportedOperationException("Complete eventId")

  def kind(event: Event): String =
    throw new UnsupportedOperationException("Complete kind")

  def signedCents(event: Event): Long =
    throw new UnsupportedOperationException("Complete signedCents")

  def revisePaid(event: Paid, newCents: Long): Paid =
    throw new UnsupportedOperationException("Complete revisePaid")

  def netTotal(events: Seq[Event]): Long =
    throw new UnsupportedOperationException("Complete netTotal")

  def audit(events: Seq[Event]): (Seq[String], Long, Map[String, Long]) =
    throw new UnsupportedOperationException("Complete audit")

  def main(args: Array[String]): Unit = {
    locally {
      val first = Paid("p1", 100L)
      val second = Paid("p2", 100L)
      assert(first != second)
      assert(first.cents == second.cents)
      val revised = first.copy(cents = 125L)
      assert(first.cents == 100L && revised.cents == 125L)
      println(s"original=$first revised=$revised")
    }
    locally {
      def describe(event: Event): String = event match {
        case Paid(id, amount)     => s"paid:$id:$amount"
        case Voided(id, reason)   => s"voided:$id:$reason"
        case Refunded(id, amount) => s"refunded:$id:$amount"
      }
      assert(describe(Refunded("r1", 25L)) == "refunded:r1:25")
      assert(describe(Voided("v1", "duplicate")) == "voided:v1:duplicate")
      println(describe(Paid("p1", 0L)))
    }
    println("spark-006: worked examples passed; six task implementations remain")
  }
}

// Exercise 1: Keep identity independent of value. Inputs/task: Return the event's identity for every domain state. Test two paid events with equal cents but different IDs and verify constructor rejection of a blank ID. Expected: Paid(p1,100), Paid(p2,100), Voided(v1, duplicate), Refunded(r1,25) retain IDs p1, p2, v1, r1. A blank-ID Paid cannot be constructed. Verify: Assert the four IDs in input order and catch IllegalArgumentException for Paid("",100L).
// Exercise 2: Match every defined state. Inputs/task: Return paid, voided or refunded through an exhaustive pattern match. Include Refunded explicitly; do not use a catch-all branch that labels every unfamiliar state paid. Expected: The four-event fixture yields paid, paid, voided, refunded. Adding another sealed-domain case requires reviewing this match and its tests. Verify: Assert all four classifications. Temporarily inspect an omitted-refund match as a compiler-warning counterexample, then restore the complete implementation.
// Exercise 3: Separate magnitude from signed contribution. Inputs/task: Return positive cents for Paid, negative cents for Refunded, and zero for Voided. Stored payment/refund magnitudes must remain within constructor bounds. Test observed zero and a rejected negative magnitude. Expected: The fixture contributes 100,100,0,-25. Refunded(r0,0) contributes 0 but remains refunded; Paid with-1 cents is rejected. Verify: Assert exact signed contributions, zero-refund behavior and the constructor failure for a negative paid amount.
// Exercise 4: Create a validated replacement value. Inputs/task: Return a new Paid value with the same ID and a revised amount, leaving the original unchanged. Use copy and preserve constructor validation for an out-of-domain amount. Expected: Paid(p1,100) revised to 125 becomes Paid(p1,125), while the original remains 100. Amount 1000001 is rejected. Verify: Assert old/new amounts and equal IDs, then catch the out-of-domain constructor failure.
// Exercise 5: Reduce signed events without dropping zero states. Inputs/task: Compute the checked Long sum of signedCents for every event. Empty input returns 0. Preserve all domain states in the source even when their numerical contribution is zero. Expected: The four-event fixture nets 175 cents. Paid(z,0) and Voided(v, reason) together net 0 while remaining two distinct events. Verify: Assert 175, empty 0, and a two-event zero-total fixture without filtering either event.
// Exercise 6: Reconcile identity, state and net value. Inputs/task: Reject repeated event IDs, then return IDs in source order, net total, and counts for paid/voided/refunded including zero categories. Do not deduplicate equal monetary amounts. Expected: The fixture returns IDs[p1, p2, v1, r1], net 175 and counts paid 2, voided 1, refunded 1. Repeated ID same is rejected even if both amounts agree. Verify: Assert the full result and count sum 4, then demonstrate that two equal-ID Paid records fail instead of being silently collapsed.
