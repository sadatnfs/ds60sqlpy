# swift-032: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-032_solution.swift](swift-032_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Replay without duplicate effect:** Identity lookup and state change occur under one actor-owned transition. A repeated operation returns its receipt without applying again.

**Reject conflicting identity reuse:** Reconciliation needs payload identity as well as an operation key. A changed payload is rejected and prior state remains intact.

## Task answers

### Task 1: Predict and explain

Trace effect and receipt for the first and repeated calls.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Identity lookup and state change occur under one actor-owned transition. A repeated operation returns its receipt without applying again.

### Task 2: Guided modification

Apply a second unique identity and predict the total.

No separate reference answer has been written for this task. Start from Example B: Reconciliation needs payload identity as well as an operation key. A changed payload is rejected and prior state remains intact.

### Task 3: Independent construction

Add a read-only receipt lookup that never re-executes work.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
actor ReceiptLedger {
  private var receipts: [String: Int] = [:]
  private(set) var executions = 0
  func apply(id: String, amount: Int) -> Int {
    if let receipt = receipts[id] { return receipt }
    executions += 1
    receipts[id] = amount
    return amount
  }
  func receipt(for id: String) -> Int? { receipts[id] }
}
let ledger = ReceiptLedger()
_ = await ledger.apply(id: "one", amount: 3)
let found = await ledger.receipt(for: "one")
let missing = await ledger.receipt(for: "two")
let executions = await ledger.executions
precondition(found == 3 && missing == nil && executions == 1)
```

**Observe:** The lookup finds receipt 3 for one, reports nil for two, and the work ran only once.

receipt(for:) only reads stored results, so asking about an operation can never execute it again.

### Task 4: Diagnose a defect

Diagnose applying the effect before checking the operation identity.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An in-memory actor ledger loses its state after restart. Overflow and retention policy remain explicit production requirements. Do not claim exactly-once delivery from a local dictionary.

### Task 5: Boundary evidence

Test negative payloads and concurrent identical requests.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Replay without duplicate effect) and Example B (Reject conflicting identity reuse).

### Task 6: Transfer and justify

Design a durable adapter and document what actor isolation alone cannot guarantee.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Idempotency**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The intermediate project gives one actor ownership of operation identities and accumulated totals. Validating a payload and recording its effect together prevents duplicate application within the actor lifetime. A repeated identity with a changed payload is a conflict, not a legitimate retry.

This is deliberately an in-memory example. Actor isolation proves a concurrency boundary, but it does not provide durable transactions across process restart. A production ledger needs storage that commits the effect and receipt atomically. The distinction between source logic, runtime checks and durable system behavior should remain explicit in the project README.

An actor dictionary records identity to payload/result. A synchronous actor method validates replay and applies new work without await between its check and update. Errors preserve conflicting requests as failures.

An in-memory actor ledger loses its state after restart. Overflow and retention policy remain explicit production requirements. Do not claim exactly-once delivery from a local dictionary.

## Review before continuing

Run the reference and confirm that it prints `swift-032: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
