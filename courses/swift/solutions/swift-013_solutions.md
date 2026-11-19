# swift-013: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-013_solution.swift](swift-013_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe shared identity:** The copied reference still identifies one object, even though both bindings are constant. Both names observe the same increment.

**Equal state need not mean identity:** Object identity answers a different question from comparing a property value. Two fresh counters have equal state but distinct identities.

## Task answers

### Task 1: Predict and explain

Draw references before and after assignment.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The copied reference still identifies one object, even though both bindings are constant. Both names observe the same increment.

### Task 2: Guided modification

Create a separate object and mutate only one.

No separate reference answer has been written for this task. Start from Example B: Object identity answers a different question from comparing a property value. Two fresh counters have equal state but distinct identities.

### Task 3: Independent construction

Choose class or struct for a shared connection coordinator and a coordinate value.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
final class Coordinator {
  var openConnections = 0
}
struct Coordinate {
  var x: Int
  var y: Int
}
let shared = Coordinator()
let alias = shared
alias.openConnections += 1
let point = Coordinate(x: 1, y: 2)
var moved = point
moved.x = 5
precondition(shared.openConnections == 1 && shared === alias)
precondition(point.x == 1 && moved.x == 5)
```

**Observe:** Both coordinator references see 1 open connection, while moving the copied coordinate leaves the original at x = 1.

A coordinator is shared state with one identity, so it is a class; a coordinate is a small value, so a struct copy is the right behavior.

### Task 4: Diagnose a defect

Diagnose expecting class assignment to create an independent snapshot.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Let does not make a referenced object deeply immutable. Reference semantics do not imply thread safety. Inheritance is not a general-purpose code reuse requirement.

### Task 5: Boundary evidence

Test equal property values on distinct objects.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Observe shared identity) and Example B (Equal state need not mean identity).

### Task 6: Transfer and justify

Explain whether a shared class needs synchronization before use from concurrent tasks.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Reference identity**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A class models reference identity. Assigning a class instance copies a reference, so both names can observe the same mutation. This is useful for shared coordinators and resources whose identity matters, but it makes ownership and lifetime more demanding. A let binding prevents replacing the reference while still permitting mutations allowed by the object.

Inheritance lets a subclass reuse or refine behavior, but a subclass must preserve the expectations of callers using the base type. Prefer composition when the relationship is collaboration rather than a true substitutable specialization. Mark a class final when subclassing is not part of its intended contract.

`final class Counter` declares a reference type without subclasses. `===` compares object identity, while `==` requires an Equatable meaning. `let reference` can still call a mutating object method.

Let does not make a referenced object deeply immutable. Reference semantics do not imply thread safety. Inheritance is not a general-purpose code reuse requirement.

## Review before continuing

Run the reference and confirm that it prints `swift-013: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
