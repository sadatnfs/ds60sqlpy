# swift-032: explanation and comparison

Reference program: [swift-032_solution.swift](swift-032_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Replay without duplicate effect:** Identity lookup and state change occur under one actor-owned transition. A repeated operation returns its receipt without applying again.

**Reject conflicting identity reuse:** Reconciliation needs payload identity as well as an operation key. A changed payload is rejected and prior state remains intact.

## Task answers

### Task 1: Predict and explain

Trace effect and receipt for the first and repeated calls.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let ledger = ImportLedger()
let firstReceipt = try await ledger.apply(id: "a", amount: 5)
let afterFirst = await ledger.total
let repeatReceipt = try await ledger.apply(id: "a", amount: 5)
let afterRepeat = await ledger.total
precondition(firstReceipt == 5 && afterFirst == 5)
precondition(repeatReceipt == 5 && afterRepeat == 5)
```

**Observe:** The first call adds 5 and returns receipt 5; the repeat returns receipt 5 and the total stays 5.

The first call finds no record, adds to the total and stores the pair; the repeat finds the matching record and returns its stored receipt without touching the total.

### Task 2: Guided modification

Apply a second unique identity and predict the total.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let ledger = ImportLedger()
_ = try await ledger.apply(id: "one", amount: 3)
let receipt = try await ledger.apply(id: "two", amount: 4)
let total = await ledger.total
precondition(receipt == 7 && total == 7)
```

**Observe:** Applying two with 4 after one with 3 returns receipt 7 and a total of 7.

A new identity has no record, so its effect is applied and its receipt is the running total after the addition.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
actor CarelessLedger {
  private var receipts: [String: Int] = [:]
  private(set) var total = 0
  func apply(id: String, amount: Int) -> Int {
    total += amount
    if let receipt = receipts[id] { return receipt }
    receipts[id] = total
    return total
  }
}
let careless = CarelessLedger()
_ = await careless.apply(id: "one", amount: 3)
_ = await careless.apply(id: "one", amount: 3)
let carelessTotal = await careless.total
let ledger = ImportLedger()
_ = try await ledger.apply(id: "one", amount: 3)
_ = try await ledger.apply(id: "one", amount: 3)
let safeTotal = await ledger.total
precondition(carelessTotal == 6 && safeTotal == 3)
```

**Observe:** Applying first and checking later doubles the replayed effect to 6; ImportLedger stays at 3.

The careless ledger returns the old receipt, so the caller believes nothing happened while the total was already changed. The identity lookup must come before any effect.

### Task 5: Boundary evidence

Test negative payloads and concurrent identical requests.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let ledger = ImportLedger()
var invalid = false
do { _ = try await ledger.apply(id: "neg", amount: -1) } catch LedgerError.invalid {
  invalid = true
}
precondition(invalid)
let receipts = try await withThrowingTaskGroup(of: Int.self, returning: [Int].self) { group in
  for _ in 0..<5 { group.addTask { try await ledger.apply(id: "same", amount: 2) } }
  var collected: [Int] = []
  for try await receipt in group { collected.append(receipt) }
  return collected
}
let total = await ledger.total
precondition(receipts == [2, 2, 2, 2, 2] && total == 2)
```

**Observe:** A negative amount throws invalid, and five concurrent identical requests all receive receipt 2 while the total stays 2.

The actor runs each apply to completion without suspension, so only the first request applies the effect and the other four find its record.

### Task 6: Transfer and justify

Design a durable adapter and document what actor isolation alone cannot guarantee.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** `ImportLedger` is an actor that stores, per operation id, the amount and the running total that was its receipt. A first call applies the amount; a repeated call with the same id and amount returns the stored receipt; the same id with a different amount throws `conflict`. The task 3 answer adds a lookup that never re-executes work.

**Why it is correct.** In Example A, `apply(id: "one", amount: 3)` raises the total from 0 to 3 and records `(3, 3)`. The repeat finds the record, the amounts match, and it returns 3 without adding again, so the total stays 3. In Example B the second call carries 4, the stored amount is 3, so it throws and the total is untouched. In task 3 the lookup finds receipt 3 for one and nil for two.

**A plausible wrong approach.** Adding `total += amount` before looking up the id is the task 4 defect: a replay would raise the total to 6 before the duplicate is detected, and the `total == 3` check fails. Keying only on id without storing the amount would accept the conflicting payload 4 as a harmless replay.

**How to verify.** For task 2, apply `two` with 5 and predict a total of 8. For task 5, apply a negative amount and confirm `LedgerError.invalid`; then launch the same `apply` from two child tasks and confirm the total rises only once.

## Mechanism and diagnostic reasoning

The intermediate project gives one actor ownership of operation identities and accumulated totals. Validating a payload and recording its effect together prevents duplicate application within the actor lifetime. A repeated identity with a changed payload is a conflict, not a legitimate retry.

This is deliberately an in-memory example. Actor isolation proves a concurrency boundary, but it does not provide durable transactions across process restart. A production ledger needs storage that commits the effect and receipt atomically. The distinction between source logic, runtime checks and durable system behavior should remain explicit in the project README.

An actor dictionary records identity to payload/result. A synchronous actor method validates replay and applies new work without await between its check and update. Errors preserve conflicting requests as failures.

An in-memory actor ledger loses its state after restart. Overflow and retention policy remain explicit production requirements. Do not claim exactly-once delivery from a local dictionary.

## Review before continuing

Run the reference and confirm it prints `swift-032: passed`, then rerun the guide's counterexample.
