# swift-012: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-012_solution.swift](swift-012_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep copied value state independent:** The struct contains value state and its mutation is explicit. Reserving from the copied inventory does not change the original.

**Reject without partial mutation:** Checking every rejection condition before subtraction preserves failure atomicity. Rejected requests retain the previous valid stock.

## Task answers

### Task 1: Predict and explain

Trace both inventory copies through reservation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The struct contains value state and its mutation is explicit. Reserving from the copied inventory does not change the original.

### Task 2: Guided modification

Add a validated restock operation.

No separate reference answer has been written for this task. Start from Example B: Checking every rejection condition before subtraction preserves failure atomicity. Rejected requests retain the previous valid stock.

### Task 3: Independent construction

Build a bounded counter with private mutation.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct BoundedCounter {
  private(set) var value = 0
  let limit: Int
  mutating func increment() -> Bool {
    guard value < limit else { return false }
    value += 1
    return true
  }
}
var counter = BoundedCounter(limit: 2)
precondition(counter.increment() && counter.increment())
precondition(!counter.increment() && counter.value == 2)
```

**Observe:** Two increments succeed, the third is refused, and the value stays at 2.

private(set) lets callers read value but change it only through increment, which enforces the limit.

### Task 4: Diagnose a defect

Diagnose subtracting stock before checking the requested amount.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A struct can contain shared class references. Private setters are useful only when methods enforce invariants. The public memberwise initializer in a small fixture is not a substitute for validating external state.

### Task 5: Boundary evidence

Test zero, exact-stock and excess reservations.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Keep copied value state independent) and Example B (Reject without partial mutation).

### Task 6: Transfer and justify

Choose a value model for an editable form and explain how cancel can restore an earlier snapshot.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Struct**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A struct models a value with named properties and operations. Assignment follows value semantics, making independent state snapshots straightforward when its stored members also have appropriate semantics. A mutating method explicitly changes self or its stored properties. Methods without mutating cannot silently alter a value-type instance.

Constructors should establish valid state, and operations should preserve it. Do not expose unrestricted writable fields if they allow callers to bypass the rule. A small value type can be a strong domain boundary, but wrapping a primitive without adding meaning or validation is only extra syntax.

`struct Inventory` defines a value type. `private(set)` exposes reading but restricts assignment. A `mutating func` may update stored state. An initializer can reject invalid input with a throwing or failable contract in later chapters.

A struct can contain shared class references. Private setters are useful only when methods enforce invariants. The public memberwise initializer in a small fixture is not a substitute for validating external state.

## Review before continuing

Run the reference and confirm that it prints `swift-012: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
