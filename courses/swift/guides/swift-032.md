# swift-032: Composition project: an actor-owned import ledger

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-031`

## Learning objectives

Build an actor-owned import ledger with idempotent operations and conflict detection. The central exercise is task 3: Add a read-only receipt lookup that never re-executes work.

## Purpose and mental model

The intermediate project gives one actor ownership of operation identities and accumulated totals. Validating a payload and recording its effect together prevents duplicate application within the actor lifetime. A repeated identity with a changed payload is a conflict, not a legitimate retry.

This is deliberately an in-memory example. Actor isolation proves a concurrency boundary, but it does not provide durable transactions across process restart. A production ledger needs storage that commits the effect and receipt atomically. The distinction between source logic, runtime checks and durable system behavior should remain explicit in the project README.

## Vocabulary and concepts

**Idempotency:** Repeated request identity does not duplicate the intended effect.

**Receipt:** A retained description of an operation outcome.

**Conflict:** A reused identity with incompatible meaning.

## How to run this lesson

Both examples use `ImportLedger` and `LedgerError`, declared above `LessonMain`. Calls into the ledger are `try await`, because its method throws and lives on an actor. For task 5, launch two identical requests in a task group and check that the total grows once.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

An actor dictionary records identity to payload/result. A synchronous actor method validates replay and applies new work without await between its check and update. Errors preserve conflicting requests as failures.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Replay without duplicate effect

Identity lookup and state change occur under one actor-owned transition.

```swift
import Foundation

enum LedgerError: Error {
  case invalid
  case conflict
}
actor ImportLedger {
  private var records: [String: (Int, Int)] = [:]
  private(set) var total = 0
  func apply(id: String, amount: Int) throws -> Int {
    guard !id.isEmpty, amount >= 0 else { throw LedgerError.invalid }
    if let old = records[id] {
      guard old.0 == amount else { throw LedgerError.conflict }
      return old.1
    }
    total += amount
    records[id] = (amount, total)
    return total
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let ledger = ImportLedger()
      let first = try await ledger.apply(id: "one", amount: 3)
      let repeated = try await ledger.apply(id: "one", amount: 3)
      let total = await ledger.total
      precondition(first == 3 && repeated == 3 && total == 3)
    }
    print("swift-032: passed")
  }
}
```

**Observe:** A repeated operation returns its receipt without applying again.

**Trace.** `ledger` starts with no records and a total of 0. The first `apply(id: "one", amount: 3)` passes validation, finds no record, adds 3 to the total, stores the pair of amount 3 and receipt 3 under one and returns 3. The repeated call finds that record, confirms the stored amount equals 3 and returns the saved receipt 3 without touching the total. The final read shows a total of 3, so the replay had no second effect.

### Example B: Reject conflicting identity reuse

Reconciliation needs payload identity as well as an operation key.

```swift
import Foundation

enum LedgerError: Error {
  case invalid
  case conflict
}
actor ImportLedger {
  private var records: [String: (Int, Int)] = [:]
  private(set) var total = 0
  func apply(id: String, amount: Int) throws -> Int {
    guard !id.isEmpty, amount >= 0 else { throw LedgerError.invalid }
    if let old = records[id] {
      guard old.0 == amount else { throw LedgerError.conflict }
      return old.1
    }
    total += amount
    records[id] = (amount, total)
    return total
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let ledger = ImportLedger()
      _ = try await ledger.apply(id: "one", amount: 3)
      var conflict = false
      do { _ = try await ledger.apply(id: "one", amount: 4) } catch LedgerError.conflict {
        conflict = true
      }
      let total = await ledger.total
      precondition(conflict && total == 3)
    }
    print("swift-032: passed")
  }
}
```

**Observe:** A changed payload is rejected and prior state remains intact.

**Trace.** After the first call stores one with amount 3, a second call reuses the identity with amount 4. The lookup finds the record, but the stored amount 3 differs, so the method throws `LedgerError.conflict` before any update. The catch sets `conflict`, and the total is still 3. A key alone is not enough: the stored payload lets the ledger tell an honest replay from a different operation that reused the key.

## Exercises

1. **Predict and explain.** Trace effect and receipt for the first and repeated calls.

2. **Guided modification.** Apply a second unique identity and predict the total.

3. **Independent construction.** Add a read-only receipt lookup that never re-executes work.

4. **Diagnose a defect.** Diagnose applying the effect before checking the operation identity.

5. **Boundary evidence.** Test negative payloads and concurrent identical requests.

6. **Transfer and justify.** Design a durable adapter and document what actor isolation alone cannot guarantee.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An in-memory actor ledger loses its state after restart. Overflow and retention policy remain explicit production requirements. Do not claim exactly-once delivery from a local dictionary.

Task 4's defect adds the amount to the total first and checks the identity afterward. A replayed request then increases the total to 6 even though it returns the old receipt. The counterexample is Example A's own repeated call with a check on the total. For task 5, a negative amount must throw `invalid` before any record is stored, so a later valid call with that id still succeeds.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Replay without duplicate effect) before changing anything, and confirm its observation: A repeated operation returns its receipt without applying again.
2. Compare Example B (Reject conflicting identity reuse) with Example A and name the first line whose behavior differs. Its observation is: A changed payload is rejected and prior state remains intact.
3. Before opening the explanation, check your task 3 attempt (Add a read-only receipt lookup that never re-executes work) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain what idempotent means for this ledger and why the receipt must be stored with the record. Say why the actor makes concurrent identical requests safe in memory but not across a process restart. List what a durable adapter must store so a replay after a crash still returns the original receipt.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Actor isolation is covered in the book's Concurrency chapter, and errors from throwing actor methods follow the ordinary Error Handling chapter.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-032: Composition project: an actor-owned import ledger.
Read courses/swift/guides/swift-032.md and courses/swift/lessons/swift-032.swift. Prerequisites: swift-031.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-032_solution.swift and
courses/swift/solutions/swift-032_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
