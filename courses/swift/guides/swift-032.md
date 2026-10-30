# swift-032: Composition project: an actor-owned import ledger

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-031`

## Learning objectives

Add a read-only receipt lookup that never re-executes work. Then design a durable adapter and document what actor isolation alone cannot guarantee.

## Purpose and mental model

The intermediate project gives one actor ownership of operation identities and accumulated totals. Validating a payload and recording its effect together prevents duplicate application within the actor lifetime. A repeated identity with a changed payload is a conflict, not a legitimate retry.

This is deliberately an in-memory example. Actor isolation proves a concurrency boundary, but it does not provide durable transactions across process restart. A production ledger needs storage that commits the effect and receipt atomically. The distinction between source logic, runtime checks and durable system behavior should remain explicit in the project README.

## Vocabulary and concepts

**Idempotency:** Repeated request identity does not duplicate the intended effect.

**Receipt:** A retained description of an operation outcome.

**Conflict:** A reused identity with incompatible meaning.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

An actor dictionary records identity to payload/result. A synchronous actor method validates replay and applies new work without await between its check and update. Errors preserve conflicting requests as failures.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Trace effect and receipt for the first and repeated calls.

2. **Guided modification.** Apply a second unique identity and predict the total.

3. **Independent construction.** Add a read-only receipt lookup that never re-executes work.

4. **Diagnose a defect.** Diagnose applying the effect before checking the operation identity.

5. **Boundary evidence.** Test negative payloads and concurrent identical requests.

6. **Transfer and justify.** Design a durable adapter and document what actor isolation alone cannot guarantee.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An in-memory actor ledger loses its state after restart. Overflow and retention policy remain explicit production requirements. Do not claim exactly-once delivery from a local dictionary.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Idempotency, Receipt, Conflict without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
