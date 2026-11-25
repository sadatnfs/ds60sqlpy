# swift-031: Actors and serialized state ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-030`

## Learning objectives

Protect mutable state with actors so access is serialized by construction. The central exercise is task 3: Implement a bounded actor-owned queue with explicit admission.

## Purpose and mental model

An actor isolates mutable state so asynchronous callers cannot directly access it without crossing the actor boundary. This prevents many data races by making ownership part of the type system. Actor methods can still contain logical races: when an operation suspends, another task may enter and change state before it resumes.

Keep a state transition synchronous inside the actor whenever possible. If an operation must await external work, revalidate assumptions after suspension or model a reservation explicitly. Actors provide isolation, not an automatic transaction across every await. Sendable describes which values can safely cross concurrency boundaries.

## Vocabulary and concepts

**Actor isolation:** Exclusive ownership of actor state under concurrency rules.

**Reentrancy:** Other work entering an actor while an operation is suspended.

**Sendable:** A contract for values safely crossing concurrency boundaries.

## How to run this lesson

Both actors are declared above `LessonMain` in both examples. Every access to actor state from outside needs `await`, including reading `counter.value`; leaving it out fails to compile. Task 4 introduces a suspension in the middle of a check and update, which compiles cleanly, so only a carefully ordered test reveals it.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`actor CounterActor` owns isolated state. Calls from outside use await even when the method body itself does not suspend. Read an actor result into a local value before passing it to precondition, whose autoclosure is synchronous.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Serialize increments

The actor owns mutation, while child tasks send requests rather than sharing a writable integer.

```swift
import Foundation

actor CounterActor {
  private(set) var value = 0
  func increment() { value += 1 }
}
actor InventoryActor {
  private(set) var stock: Int
  init(stock: Int) { self.stock = stock }
  func reserve(_ amount: Int) -> Bool {
    guard amount >= 0 && amount <= stock else { return false }
    stock -= amount
    return true
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let counter = CounterActor()
      await withTaskGroup(of: Void.self) { group in
        for _ in 0..<20 { group.addTask { await counter.increment() } }
      }
      let value = await counter.value
      precondition(value == 20)
    }
    print("swift-031: passed")
  }
}
```

**Observe:** All twenty increments are retained.

**Trace.** `counter` is an actor instance with `value` 0. The task group adds twenty children, and each calls `await counter.increment()`. The actor runs one isolated method at a time, so the twenty increments are serialized even though the children may run in parallel; no two read-modify-write steps interleave. When the group completes, the parent awaits a read of `value` and gets 20. With a plain class and no synchronization the count could come out lower.

### Example B: Keep a reservation atomic within the actor

The check and update contain no suspension, preserving the invariant as one actor operation.

```swift
import Foundation

actor CounterActor {
  private(set) var value = 0
  func increment() { value += 1 }
}
actor InventoryActor {
  private(set) var stock: Int
  init(stock: Int) { self.stock = stock }
  func reserve(_ amount: Int) -> Bool {
    guard amount >= 0 && amount <= stock else { return false }
    stock -= amount
    return true
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let inventory = InventoryActor(stock: 3)
      let first = await inventory.reserve(2)
      let second = await inventory.reserve(2)
      let remaining = await inventory.stock
      precondition(first && !second && remaining == 1)
    }
    print("swift-031: passed")
  }
}
```

**Observe:** The second reservation is rejected without making stock negative.

**Trace.** `inventory` starts with stock 3. The first `reserve(2)` runs entirely inside the actor: the guard sees 2 at most 3, subtraction leaves 1, and it returns true. The second `reserve(2)` sees 2 greater than 1 and returns false without changing anything. The read of `stock` gives 1. Because `reserve` contains no `await`, no other actor call can run between its check and its update.

## Exercises

1. **Predict and explain.** Identify every actor-isolated read and write.

2. **Guided modification.** Add a read-only snapshot method returning a value type.

3. **Independent construction.** Implement a bounded actor-owned queue with explicit admission.

4. **Diagnose a defect.** Diagnose checking stock, awaiting another operation and then subtracting without revalidation.

5. **Boundary evidence.** Test zero and excess reservations.

6. **Transfer and justify.** Design a reservation state machine for an operation requiring external I/O before commitment.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Actors do not make all multi-step workflows transactional. Await inside an invariant-sensitive operation is a reentrancy boundary. Do not use unchecked Sendable merely to silence a real ownership diagnostic.

Task 4's version checks stock, then awaits an external call, then subtracts. During that await, another call can reserve the same units, so both subtract and stock goes negative. The counterexample is two concurrent reservations of 2 from stock 3. Rechecking after the await, or keeping the check and update in one synchronous actor method, restores the invariant.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Serialize increments) before changing anything, and confirm its observation: All twenty increments are retained.
2. Compare Example B (Keep a reservation atomic within the actor) with Example A and name the first line whose behavior differs. Its observation is: The second reservation is rejected without making stock negative.
3. Before opening the explanation, check your task 3 attempt (Implement a bounded actor-owned queue with explicit admission) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why reading `counter.value` from `main` needs `await` even though it is only a read. Describe actor reentrancy and why it makes a suspension inside a method risky. For task 2, explain why returning a value-type snapshot is safer than exposing actor state to callers.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Actors, isolation and the rule that actor methods may interleave at suspension points are explained in the book's Concurrency chapter.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-031: Actors and serialized state ownership.
Read courses/swift/guides/swift-031.md and courses/swift/lessons/swift-031.swift. Prerequisites: swift-030.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-031_solution.swift and
courses/swift/solutions/swift-031_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
