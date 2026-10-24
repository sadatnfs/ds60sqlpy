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

  def eventId(event: Event): String = {
    event.id
  }

  def kind(event: Event): String = {
    event match {
      case Paid(_, _)     => "paid"
      case Voided(_, _)   => "voided"
      case Refunded(_, _) => "refunded"
    }
  }

  def signedCents(event: Event): Long = {
    event match {
      case Paid(_, amount)     => amount
      case Voided(_, _)        => 0L
      case Refunded(_, amount) => -amount
    }
  }

  def revisePaid(event: Paid, newCents: Long): Paid = {
    event.copy(cents = newCents)
  }

  def netTotal(events: Seq[Event]): Long = {
    events.foldLeft(0L)((total, event) => Math.addExact(total, signedCents(event)))
  }

  def audit(events: Seq[Event]): (Seq[String], Long, Map[String, Long]) = {
    val identities = events.map(eventId)
    require(identities.distinct.size == identities.size, "event IDs must be unique")
    val counts = events.foldLeft(Map("paid" -> 0L, "voided" -> 0L, "refunded" -> 0L)) {
      (current, event) =>
        val state = kind(event)
        current.updated(state, current(state) + 1L)
    }
    (identities, netTotal(events), counts)
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
    // Exercise 1: Keep identity independent of value
    val events: Seq[Event] =
      Seq(Paid("p1", 100L), Paid("p2", 100L), Voided("v1", "duplicate"), Refunded("r1", 25L))
    assert(events.map(eventId) == Seq("p1", "p2", "v1", "r1"))
    expectIllegalArgument(Paid("", 100L))
    // Exercise 2: Match every defined state
    assert(events.map(kind) == Seq("paid", "paid", "voided", "refunded"))
    assert(kind(Paid("zero", 0L)) == "paid")
    // Exercise 3: Separate magnitude from signed contribution
    assert(events.map(signedCents) == Seq(100L, 100L, 0L, -25L))
    assert(signedCents(Refunded("r0", 0L)) == 0L && kind(Refunded("r0", 0L)) == "refunded")
    expectIllegalArgument(Paid("bad", -1L))
    // Exercise 4: Create a validated replacement value
    val original = Paid("p1", 100L)
    val revised = revisePaid(original, 125L)
    assert(original.cents == 100L && revised == Paid("p1", 125L) && revised.id == original.id)
    expectIllegalArgument(revisePaid(original, 1000001L))
    // Exercise 5: Reduce signed events without dropping zero states
    assert(netTotal(events) == 175L && netTotal(Seq.empty) == 0L)
    val zeroStates: Seq[Event] = Seq(Paid("z", 0L), Voided("v", "reason"))
    assert(netTotal(zeroStates) == 0L && zeroStates.size == 2)
    // Exercise 6: Reconcile identity, state and net value
    val report = audit(events)
    assert(report._1 == Seq("p1", "p2", "v1", "r1") && report._2 == 175L)
    assert(
      report._3 == Map("paid" -> 2L, "voided" -> 1L, "refunded" -> 1L) && report._3.values.sum == 4L
    )
    expectIllegalArgument(audit(Seq(Paid("same", 10L), Paid("same", 10L))))
    println("spark-006: six reference contracts passed")
    println(
      "Scala=" + scala.util.Properties.versionNumberString + "; Java=" + System.getProperty(
        "java.version"
      )
    )
  }
}

// Exercise 1: Keep identity independent of value. Inputs/task: Return the event's identity for every domain state. Test two paid events with equal cents but different IDs and verify constructor rejection of a blank ID. Expected: Paid(p1,100), Paid(p2,100), Voided(v1, duplicate), Refunded(r1,25) retain IDs p1, p2, v1, r1. A blank-ID Paid cannot be constructed. Verify: Assert the four IDs in input order and catch IllegalArgumentException for Paid("",100L).
// Exercise 2: Match every defined state. Inputs/task: Return paid, voided or refunded through an exhaustive pattern match. Include Refunded explicitly; do not use a catch-all branch that labels every unfamiliar state paid. Expected: The four-event fixture yields paid, paid, voided, refunded. Adding another sealed-domain case requires reviewing this match and its tests. Verify: Assert all four classifications. Temporarily inspect an omitted-refund match as a compiler-warning counterexample, then restore the complete implementation.
// Exercise 3: Separate magnitude from signed contribution. Inputs/task: Return positive cents for Paid, negative cents for Refunded, and zero for Voided. Stored payment/refund magnitudes must remain within constructor bounds. Test observed zero and a rejected negative magnitude. Expected: The fixture contributes 100,100,0,-25. Refunded(r0,0) contributes 0 but remains refunded; Paid with-1 cents is rejected. Verify: Assert exact signed contributions, zero-refund behavior and the constructor failure for a negative paid amount.
// Exercise 4: Create a validated replacement value. Inputs/task: Return a new Paid value with the same ID and a revised amount, leaving the original unchanged. Use copy and preserve constructor validation for an out-of-domain amount. Expected: Paid(p1,100) revised to 125 becomes Paid(p1,125), while the original remains 100. Amount 1000001 is rejected. Verify: Assert old/new amounts and equal IDs, then catch the out-of-domain constructor failure.
// Exercise 5: Reduce signed events without dropping zero states. Inputs/task: Compute the checked Long sum of signedCents for every event. Empty input returns 0. Preserve all domain states in the source even when their numerical contribution is zero. Expected: The four-event fixture nets 175 cents. Paid(z,0) and Voided(v, reason) together net 0 while remaining two distinct events. Verify: Assert 175, empty 0, and a two-event zero-total fixture without filtering either event.
// Exercise 6: Reconcile identity, state and net value. Inputs/task: Reject repeated event IDs, then return IDs in source order, net total, and counts for paid/voided/refunded including zero categories. Do not deduplicate equal monetary amounts. Expected: The fixture returns IDs[p1, p2, v1, r1], net 175 and counts paid 2, voided 1, refunded 1. Repeated ID same is rejected even if both amounts agree. Verify: Assert the full result and count sum 4, then demonstrate that two equal-ID Paid records fail instead of being silently collapsed.
