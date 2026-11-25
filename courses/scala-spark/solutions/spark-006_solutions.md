# spark-006: Explained reference solutions

Attempt the [guide](../guides/spark-006.md) exercises first.

Reference: [complete Scala program](spark-006_solution.scala).

## Exercises and reasoning

### Shared domain definitions

```scala
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
```

### Exercise 1: Keep identity independent of value

Return the event's identity for every domain state. Test two paid events with equal cents but different IDs and verify constructor rejection of a blank ID.

**Expected:** `Paid(p1, 100)`, `Paid(p2, 100)`, `Voided(v1, duplicate)`, `Refunded(r1, 25)` retain IDs p1, p2, v1, r1. A blank-ID Paid cannot be constructed.

```scala
def eventId(event: Event): String = {
  event.id
}
```

The common trait field provides identity without inspecting a monetary field or converting a whole object to text. Equal payment values remain separate because their IDs differ. Constructor validation prevents a blank identity from entering this valid-object domain. External raw records need an explicit validation result rather than relying on this exception boundary as a data-quality ledger.

```scala
val events: Seq[Event] =
  Seq(Paid("p1", 100L), Paid("p2", 100L), Voided("v1", "duplicate"), Refunded("r1", 25L))
assert(events.map(eventId) == Seq("p1", "p2", "v1", "r1"))
expectIllegalArgument(Paid("", 100L))
```

### Exercise 2: Match every defined state

Return paid, voided or refunded through an exhaustive pattern match. Include Refunded explicitly; do not use a catch-all branch that labels every unfamiliar state paid.

**Expected:** The four-event fixture yields paid, paid, voided, refunded. Adding another sealed-domain case requires reviewing this match and its tests.

```scala
def kind(event: Event): String = {
  event match {
    case Paid(_, _)     => "paid"
    case Voided(_, _)   => "voided"
    case Refunded(_, _) => "refunded"
  }
}
```

The cases represent domain alternatives rather than arbitrary strings. An explicit branch for every state makes a future model extension visible to review and tests. A wildcard default can hide that extension by assigning a misleading existing category. The zero-payment assertion separates state classification from numerical truthiness: amount zero does not make a Paid event a void.

```scala
assert(events.map(kind) == Seq("paid", "paid", "voided", "refunded"))
assert(kind(Paid("zero", 0L)) == "paid")
```

### Exercise 3: Separate magnitude from signed contribution

Return positive cents for Paid, negative cents for Refunded, and zero for Voided. Stored payment/refund magnitudes must remain within constructor bounds. Test observed zero and a rejected negative magnitude.

**Expected:** The fixture contributes `100`, `100`, `0` and `-25`. `Refunded(r0, 0)` contributes 0 but remains refunded; Paid with -1 cents is rejected.

```scala
def signedCents(event: Event): Long = {
  event match {
    case Paid(_, amount)     => amount
    case Voided(_, _)        => 0L
    case Refunded(_, amount) => -amount
  }
}
```

The stored magnitude and the reporting sign are different concepts. Keeping refund cents nonnegative simplifies constructor validation while the match defines its negative contribution. The bounded domain makes negation safe from the Long.MinValue corner. A void still contributes an event count even though its signed amount is zero, so net value alone cannot describe the ledger.

```scala
assert(events.map(signedCents) == Seq(100L, 100L, 0L, -25L))
assert(signedCents(Refunded("r0", 0L)) == 0L && kind(Refunded("r0", 0L)) == "refunded")
expectIllegalArgument(Paid("bad", -1L))
```

### Exercise 4: Create a validated replacement value

Return a new Paid value with the same ID and a revised amount, leaving the original unchanged. Use copy and preserve constructor validation for an out-of-domain amount.

**Expected:** `Paid(p1, 100)` revised to 125 becomes `Paid(p1, 125)`, while the original remains 100. Amount 1000001 is rejected.

```scala
def revisePaid(event: Paid, newCents: Long): Paid = {
  event.copy(cents = newCents)
}
```

copy constructs a replacement record rather than mutating the existing object. Named fields make the revised attribute explicit, and the case-class constructor rechecks its invariants. Preserving identity does not mean both versions should be counted as separate events. A versioned ledger needs a version key or an explicit replacement policy, which the final uniqueness audit deliberately does not invent.

```scala
val original = Paid("p1", 100L)
val revised = revisePaid(original, 125L)
assert(original.cents == 100L && revised == Paid("p1", 125L) && revised.id == original.id)
expectIllegalArgument(revisePaid(original, 1000001L))
```

### Exercise 5: Reduce signed events without dropping zero states

Compute the checked Long sum of signedCents for every event. Empty input returns 0. Preserve all domain states in the source even when their numerical contribution is zero.

**Expected:** The four-event fixture nets 175 cents. `Paid(z, 0)` and Voided(v, reason) together net 0 while remaining two distinct events.

```scala
def netTotal(events: Seq[Event]): Long = {
  events.foldLeft(0L)((total, event) => Math.addExact(total, signedCents(event)))
}
```

Every event is processed through the signed domain rule before accumulation. This keeps the definition centralized and avoids a second ad hoc status filter that might omit refunds or void evidence. Checked addition makes arithmetic range failures visible. The zero-total example demonstrates why total equality alone is an incomplete reconciliation: two events and no events can both sum to zero.

```scala
assert(netTotal(events) == 175L && netTotal(Seq.empty) == 0L)
val zeroStates: Seq[Event] = Seq(Paid("z", 0L), Voided("v", "reason"))
assert(netTotal(zeroStates) == 0L && zeroStates.size == 2)
```

### Exercise 6: Reconcile identity, state and net value

Reject repeated event IDs, then return IDs in source order, net total, and counts for paid/voided/refunded including zero categories. Do not deduplicate equal monetary amounts.

**Expected:** The fixture returns IDs [p1, p2, v1, r1], net 175 and counts paid 2, voided 1, refunded 1. Repeated ID same is rejected even if both amounts agree.

```scala
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
```

Uniqueness is checked on the actual event identity rather than on amount or the whole projected row. The report keeps occurrence IDs, state counts and signed value as separate evidence. Initial category keys make an empty or single-state report structurally consistent. Rejecting duplicate identity avoids deciding whether repeated delivery is a correction or duplication without an explicit policy.

```scala
val report = audit(events)
assert(report._1 == Seq("p1", "p2", "v1", "r1") && report._2 == 175L)
assert(
  report._3 == Map("paid" -> 2L, "voided" -> 1L, "refunded" -> 1L) && report._3.values.sum == 4L
)
expectIllegalArgument(audit(Seq(Paid("same", 10L), Paid("same", 10L))))
```

## Evidence and scope

The reference asserts identity, state and value separately against the literal fixture. It checks the four IDs in source order, the kinds paid, paid, voided and refunded, the signed contributions 100, 100, 0 and -25, the net 175, and the per-kind counts. It verifies that `revisePaid` leaves the original `Paid(p1, 100)` unchanged, that a blank ID or a negative amount cannot be constructed, and that `audit` rejects two events sharing ID `same` even though their amounts agree.

After those checks the program prints `spark-006: six reference contracts passed` and the versions it ran with. The checks establish that this sealed domain keeps identity and value apart on these events; they cannot show that a future fourth case is handled, which is why the compiler's exhaustiveness warning matters more than any single test. When you later read the same events as Spark rows, the case class becomes a schema with a status column, and the exhaustive match becomes a `CASE WHEN` that you must keep complete by review and by tests.

