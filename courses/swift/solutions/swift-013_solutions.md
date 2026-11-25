# swift-013: explanation and comparison

Reference program: [swift-013_solution.swift](swift-013_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Observe shared identity:** The copied reference still identifies one object, even though both bindings are constant. Both names observe the same increment.

**Equal state need not mean identity:** Object identity answers a different question from comparing a property value. Two fresh counters have equal state but distinct identities.

## Task answers

### Task 1: Predict and explain

Draw references before and after assignment.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let first = Counter()
let second = first
precondition(first === second)
second.increment()
precondition(first.value == 1)
precondition(ObjectIdentifier(first) == ObjectIdentifier(second))
```

**Observe:** Before and after the increment, first and second refer to one object, so first reads 1.

Assigning a class instance copies the reference, not the object; the drawing has two names pointing at one Counter box, and ObjectIdentifier confirms the single identity.

### Task 2: Guided modification

Create a separate object and mutate only one.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let first = Counter()
let second = Counter()
second.increment()
precondition(first.value == 0 && second.value == 1)
precondition(first !== second)
```

**Observe:** Incrementing the separately created second leaves first at 0 and second at 1.

Each Counter() call allocates its own object, so mutation through one reference cannot be seen through the other.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let live = Counter()
let alias = live
let snapshot = live.value
live.increment()
precondition(alias.value == 1)
precondition(snapshot == 0)
```

**Observe:** The alias sees 1 after the increment, while the Int snapshot taken earlier stays 0.

let alias = live copies only the reference, so it is not a snapshot; copying the Int value out is what preserves the earlier state.

### Task 5: Boundary evidence

Test equal property values on distinct objects.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let first = Counter()
let second = Counter()
first.increment()
second.increment()
precondition(first.value == second.value && first !== second)
first.increment()
precondition(first.value == 2 && second.value == 1)
```

**Observe:** Both objects read 1 yet are distinct; a further increment on first gives 2 and 1.

Equal property values say nothing about identity; === compares identity, and the later divergence shows the objects were never shared.

### Task 6: Transfer and justify

Explain whether a shared class needs synchronization before use from concurrent tasks.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A assigns one `Counter` instance to two constants, increments through the second, and reads through the first. Example B creates two separate counters and compares both their values and their identities. The task 3 answer contrasts a shared connection coordinator class with a copied coordinate struct.

**Why it is correct.** `let second = first` copies the reference, not the object, so one increment is visible through both names and `first === second` holds. `let` only freezes the binding; the object's `value` can still change through its method. Two fresh counters both have value 0, so `==` on values holds while `!==` shows two objects. In task 3 both coordinator references see 1 open connection, while moving the copied coordinate leaves the original at x = 1.

**A plausible wrong approach.** Expecting `let second = first` to snapshot a class, as it would for a struct, leads to the prediction that `first.value` stays 0; the check `first.value == 1` refutes it. Comparing two objects with `==` on a property to decide whether they are the same object conflates equal state with identity.

**How to verify.** Draw two boxes for Example A and one shared object; then repeat for Example B with two objects. Change `Counter` to a struct in a scratch pad and confirm the code no longer compiles, because `increment` would need to be `mutating` and `let` bindings cannot call it.

## Mechanism and diagnostic reasoning

A class models reference identity. Assigning a class instance copies a reference, so both names can observe the same mutation. This is useful for shared coordinators and resources whose identity matters, but it makes ownership and lifetime more demanding. A let binding prevents replacing the reference while still permitting mutations allowed by the object.

Inheritance lets a subclass reuse or refine behavior, but a subclass must preserve the expectations of callers using the base type. Prefer composition when the relationship is collaboration rather than a true substitutable specialization. Mark a class final when subclassing is not part of its intended contract.

`final class Counter` declares a reference type without subclasses. `===` compares object identity, while `==` requires an Equatable meaning. `let reference` can still call a mutating object method.

Let does not make a referenced object deeply immutable. Reference semantics do not imply thread safety. Inheritance is not a general-purpose code reuse requirement.

## Review before continuing

Run the reference and confirm it prints `swift-013: passed`, then rerun the guide's counterexample.
