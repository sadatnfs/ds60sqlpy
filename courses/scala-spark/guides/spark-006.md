# spark-006: Case classes, pattern matching, and domain states

Authored tutorial and practice content. The prepared Scala/JVM worker executes a bounded program; process success and understanding remain distinct. No source file installs a tool or downloads a dependency.

## Level and prerequisites

Beginner; approximately 105 minutes. Direct design prerequisites: `spark-005`. The lesson uses Scala 2.13 syntax and the prepared JDK 17 worker. The older design document proposed a different Spark/JDK tuple; use the current [execution baseline](../execution-baseline.md) for this authored material.

## How to run this lesson

Open `spark-006` in the classroom, select the Scala source, prepare the `scala-jvm` profile and run the saved pad. The worker stages the single source as `Main.scala` and invokes `object Main`. Read the terminal output and exact assertions. The [learner source](../lessons/spark-006.scala) runs two complete demonstrations; its six task functions remain explicit stubs until you implement them. Preserve your saved attempt. The [reference program](../solutions/spark-006_solution.scala) and [explained solutions](../solutions/spark-006_solutions.md) are separate and should be opened after an attempt or an explicit worked-comparison request. If the profile is unavailable, reading and saving remain available; opening this guide does not prepare a runtime.

## Learning objectives

- Model a small event domain with case classes and exhaustive pattern matching.
- Explain the result of both worked examples before running them.
- Implement the six contracts, inspect normal and boundary evidence, and explain a counterexample in your own words.

## Vocabulary and concepts

- **Case class:** A compact immutable record definition that supplies named fields, structural equality, pattern extraction and a copy method.

- **Sealed trait:** A closed family whose direct implementations are declared in the same source file, allowing the compiler to reason about match coverage.

- **Pattern matching:** Selecting behavior by the shape of a value and binding fields from the matched case.

- **Domain invariant:** A rule valid objects must satisfy, such as a known event identity or a nonnegative bounded amount.

A domain model makes valid states explicit. A Paid event carries cents, a Voided event carries a reason, and a Refunded event carries refund cents. A single record with status text and several nullable fields would allow combinations such as a paid event with no amount or an unknown status spelling. Separate case classes make those differences visible in types and pattern matches.

`sealed trait Event { def id: String }` says every event exposes an identity. `final case class Paid(id: String, cents: Long) extends Event` defines one allowed shape with immutable fields. Case-class equality compares every field, not only the monetary amount. Paid("p1",100L) and Paid("p2",100L) are distinct events despite equal values. Data-grain reasoning must therefore preserve the ID rather than deduplicate a projection of cents.

A match expression returns a value. `event match { case Paid(_, amount) => amount ... }` extracts the amount from the Paid shape. The underscore deliberately ignores a field; it is not a missing value. A sealed family lets the compiler warn when a defined shape is omitted, but a warning does not automatically prevent execution in every compiler configuration. The final references cover every case explicitly and assertions include every state.

The lesson's monetary domain is 0 through 1000000 cents per amount. require checks constructor invariants and raises IllegalArgumentException if they fail. This is a deliberate object-creation boundary, not a replacement for a rejected-record ledger at an ingestion boundary. The next lesson will return validation reasons with Either instead of throwing for expected malformed input.

Refunds contribute negative signed amounts even though their stored cents are nonnegative magnitudes. A void contributes zero to net value but remains an event with its own identity and reason. Equal numerical contribution therefore does not imply equal semantic state. An observed zero payment, a zero refund and a void can all contribute zero while requiring different reporting counts.

copy creates a new case-class value rather than changing the original. Revising a payment amount preserves its ID and validates the new amount through the constructor. If both old and revised versions are placed in a ledger claiming unique event identity, the audit rejects that duplicate ID; a real versioned-event model would need an explicit version key or replacement policy.

The final audit returns exact event IDs, net cents and state counts. Each part catches a different error: identity checks detect duplicate delivery, count checks preserve zero/void records, and signed totals distinguish refunds from payments. This is a bounded event model, not a complete payment accounting system or an implicit authorization to move money.

## Worked example / walkthrough

### Worked example 1

```scala
val first = Paid("p1", 100L)
val second = Paid("p2", 100L)
assert(first != second)
assert(first.cents == second.cents)
val revised = first.copy(cents = 125L)
assert(first.cents == 100L && revised.cents == 125L)
println(s"original=$first revised=$revised")
```

Structural equality includes identity, so equal cents do not collapse two events. copy returns a new record and leaves the original unchanged. The named argument identifies which field changes and the constructor's amount invariant still applies to the copy.

### Worked example 2

```scala
def describe(event: Event): String = event match {
  case Paid(id, amount)     => s"paid:$id:$amount"
  case Voided(id, reason)   => s"voided:$id:$reason"
  case Refunded(id, amount) => s"refunded:$id:$amount"
}
assert(describe(Refunded("r1", 25L)) == "refunded:r1:25")
assert(describe(Voided("v1", "duplicate")) == "voided:v1:duplicate")
println(describe(Paid("p1", 0L)))
```

Every case returns a String, so the match is itself a String-valued expression. Each pattern binds only fields available in that state. The refund and void assertions ensure that completeness is tested rather than inferred from a successful paid example.

## Exercises

### Exercise 1: Keep identity independent of value

Return the event's identity for every domain state. Test two paid events with equal cents but different IDs and verify constructor rejection of a blank ID.

**Expected result/shape:** Paid(p1,100), Paid(p2,100), Voided(v1, duplicate), Refunded(r1,25) retain IDs p1, p2, v1, r1. A blank-ID Paid cannot be constructed.

**Verify:** Assert the four IDs in input order and catch IllegalArgumentException for Paid("",100L).

**Progressive hint:** The trait already declares the shared id contract.

### Exercise 2: Match every defined state

Return paid, voided or refunded through an exhaustive pattern match. Include Refunded explicitly; do not use a catch-all branch that labels every unfamiliar state paid.

**Expected result/shape:** The four-event fixture yields paid, paid, voided, refunded. Adding another sealed-domain case requires reviewing this match and its tests.

**Verify:** Assert all four classifications. Temporarily inspect an omitted-refund match as a compiler-warning counterexample, then restore the complete implementation.

**Progressive hint:** Use one case branch per case class and ignore unused fields with underscores.

### Exercise 3: Separate magnitude from signed contribution

Return positive cents for Paid, negative cents for Refunded, and zero for Voided. Stored payment/refund magnitudes must remain within constructor bounds. Test observed zero and a rejected negative magnitude.

**Expected result/shape:** The fixture contributes 100,100,0,-25. Refunded(r0,0) contributes 0 but remains refunded; Paid with-1 cents is rejected.

**Verify:** Assert exact signed contributions, zero-refund behavior and the constructor failure for a negative paid amount.

**Progressive hint:** Negate only the refund magnitude; do not infer the state from whether a value is zero.

### Exercise 4: Create a validated replacement value

Return a new Paid value with the same ID and a revised amount, leaving the original unchanged. Use copy and preserve constructor validation for an out-of-domain amount.

**Expected result/shape:** Paid(p1,100) revised to 125 becomes Paid(p1,125), while the original remains 100. Amount 1000001 is rejected.

**Verify:** Assert old/new amounts and equal IDs, then catch the out-of-domain constructor failure.

**Progressive hint:** The case-class copy method accepts named field replacements.

### Exercise 5: Reduce signed events without dropping zero states

Compute the checked Long sum of signedCents for every event. Empty input returns 0. Preserve all domain states in the source even when their numerical contribution is zero.

**Expected result/shape:** The four-event fixture nets 175 cents. Paid(z,0) and Voided(v, reason) together net 0 while remaining two distinct events.

**Verify:** Assert 175, empty 0, and a two-event zero-total fixture without filtering either event.

**Progressive hint:** Map the domain rule into a fold with Math.addExact and an explicit 0 L identity.

### Exercise 6: Reconcile identity, state and net value

Reject repeated event IDs, then return IDs in source order, net total, and counts for paid/voided/refunded including zero categories. Do not deduplicate equal monetary amounts.

**Expected result/shape:** The fixture returns IDs[p1, p2, v1, r1], net 175 and counts paid 2, voided 1, refunded 1. Repeated ID same is rejected even if both amounts agree.

**Verify:** Assert the full result and count sum 4, then demonstrate that two equal-ID Paid records fail instead of being silently collapsed.

**Progressive hint:** Validate IDs before computing the report; initialize all state categories and fold through kind.

## Common pitfalls

If two equal payments collapse, inspect whether a projection or Set discarded their IDs. If a match throws MatchError after a domain extension, review every sealed-state branch and add a corresponding assertion. If copy appears to change the original, check whether a mutable field was introduced rather than assuming case-class structure deep-copies objects. If a zero total hides missing events, reconcile identities and state counts as well. Expected malformed raw data belongs in a validation ledger, the next lesson's subject, not in an unhandled constructor exception.

## Self-check

Explain one input-to-output trace without reading your code. Identify which function preserves repeated values, which condition distinguishes an invalid or missing input, and which assertion would fail for the tempting incorrect implementation. A printed success line alone is not the evidence; retain the exact values and the reasoning that connect them to the contract.

## Next step

Continue to the next lesson only after you can explain the boundary behavior. The [course route](../README.md) shows authored material and runtime evidence separately.

## Primary sources and official APIs

- [Scala 2 case classes](https://docs.scala-lang.org/tour/case-classes.html).

- [Scala 2 pattern matching](https://docs.scala-lang.org/tour/pattern-matching.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through spark-006: Case classes, pattern matching, and domain states.
Read courses/scala-spark/guides/spark-006.md and courses/scala-spark/lessons/spark-006.scala. Direct prerequisites: spark-005.
Explain the Scala 2.13 syntax and data contract, ask me to predict a concrete result, then inspect my attempt. Give one hint at a time, review exact assertion evidence and ask retrieval questions in my own words. Do not read solutions/ until I ask or have made an honest attempt. Use only the prepared scala-jvm profile and preserve my saved work; do not install or download dependencies.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why an incorrect implementation fails.
```
