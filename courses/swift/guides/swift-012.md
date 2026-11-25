# swift-012: Structures and controlled value mutation

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-011`

## Learning objectives

Encapsulate state in structs with private(set) and mutating methods that keep invariants. The central exercise is task 3: Build a bounded counter with private mutation.

## Purpose and mental model

A struct models a value with named properties and operations. Assignment follows value semantics, making independent state snapshots straightforward when its stored members also have appropriate semantics. A mutating method explicitly changes self or its stored properties. Methods without mutating cannot silently alter a value-type instance.

Constructors should establish valid state, and operations should preserve it. Do not expose unrestricted writable fields if they allow callers to bypass the rule. A small value type can be a strong domain boundary, but wrapping a primitive without adding meaning or validation is only extra syntax.

## Vocabulary and concepts

**Struct:** A nominal value type.

**Mutating method:** An operation explicitly allowed to modify a value.

**Encapsulation:** Controlling changes through a meaningful interface.

## How to run this lesson

`Inventory` is declared in the helper section above `LessonMain`, and both examples share it. Because `stock` is `private(set)`, assigning to it from `LessonMain` fails to compile with a message that the setter is inaccessible; record that diagnostic as evidence that the setter is restricted, not missing.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`struct Inventory` defines a value type. `private(set)` exposes reading but restricts assignment. A `mutating func` may update stored state. An initializer can reject invalid input with a throwing or failable contract in later chapters.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Keep copied value state independent

The struct contains value state and its mutation is explicit.

```swift
import Foundation

struct Inventory {
  private(set) var stock: Int
  mutating func reserve(_ amount: Int) -> Bool {
    guard amount >= 0, amount <= stock else { return false }
    stock -= amount
    return true
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var first = Inventory(stock: 5)
      var second = first
      precondition(second.reserve(2))
      precondition(first.stock == 5 && second.stock == 3)
      precondition(first.reserve(0))
    }
    print("swift-012: passed")
  }
}
```

**Observe:** Reserving from the copied inventory does not change the original.

**Trace.** `first` is an `Inventory` with stock 5. `var second = first` copies the whole value, so `second` has its own stock of 5. `second.reserve(2)` passes both guard conditions, subtracts 2 and returns true; `second.stock` is now 3. `first.stock` is still 5, because no reference connects the two values. The last call, `first.reserve(0)`, shows that reserving nothing is allowed: it returns true and leaves the stock at 5.

### Example B: Reject without partial mutation

Checking every rejection condition before subtraction preserves failure atomicity.

```swift
import Foundation

struct Inventory {
  private(set) var stock: Int
  mutating func reserve(_ amount: Int) -> Bool {
    guard amount >= 0, amount <= stock else { return false }
    stock -= amount
    return true
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var inventory = Inventory(stock: 3)
      precondition(!inventory.reserve(4))
      precondition(!inventory.reserve(-1))
      precondition(inventory.stock == 3)
    }
    print("swift-012: passed")
  }
}
```

**Observe:** Rejected requests retain the previous valid stock.

**Trace.** `inventory` starts with stock 3. `reserve(4)` fails `amount <= stock`, so the guard returns false before the subtraction runs. `reserve(-1)` fails `amount >= 0` and also returns false. The final check confirms the stock is still 3. Because every rejection path leaves before `stock -= amount`, a rejected call cannot leave the value half-updated, which is the failure-atomicity property this lesson is about.

## Exercises

1. **Predict and explain.** Trace both inventory copies through reservation.

2. **Guided modification.** Add a validated restock operation.

3. **Independent construction.** Build a bounded counter with private mutation.

4. **Diagnose a defect.** Diagnose subtracting stock before checking the requested amount.

5. **Boundary evidence.** Test zero, exact-stock and excess reservations.

6. **Transfer and justify.** Choose a value model for an editable form and explain how cancel can restore an earlier snapshot.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A struct can contain shared class references. Private setters are useful only when methods enforce invariants. The public memberwise initializer in a small fixture is not a substitute for validating external state.

Task 4's defect subtracts first and repairs afterward, for example subtracting and then adding the amount back when the stock goes negative. It appears to work until something between the two steps returns early. The counterexample inputs are an exact-stock request, which must succeed and leave 0, and the stock plus one, which must fail and leave the stock unchanged.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Keep copied value state independent) before changing anything, and confirm its observation: Reserving from the copied inventory does not change the original.
2. Compare Example B (Reject without partial mutation) with Example A and name the first line whose behavior differs. Its observation is: Rejected requests retain the previous valid stock.
3. Before opening the explanation, check your task 3 attempt (Build a bounded counter with private mutation) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why `reserve` must be `mutating` and what the compiler says if you call it on a `let` inventory. Describe a struct containing a class reference and what copying it shares. Explain how a value-type form model lets a cancel button restore the snapshot taken when editing began.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Swift book's Structures and Classes chapter explains value types, Methods covers mutating methods, and Access Control explains private setters.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-012: Structures and controlled value mutation.
Read courses/swift/guides/swift-012.md and courses/swift/lessons/swift-012.swift. Prerequisites: swift-011.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-012_solution.swift and
courses/swift/solutions/swift-012_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
