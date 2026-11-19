# csharp-047: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-047_solution.cs](csharp-047_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Replay a recorded result without applying again:** Operation identity separates a replay from a genuinely new command. The repeated identity returns its prior result without increasing the total.

**Distinguish a new operation:** Idempotency keys need a payload consistency rule or they can hide conflicting requests. A new identity applies separately, while a changed payload under an old key is rejected.

## Task answers

### Task 1: Predict and explain

Trace the effect and receipt for the repeated operation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Operation identity separates a replay from a genuinely new command. The repeated identity returns its prior result without increasing the total.

### Task 2: Guided modification

Add a third unique operation and predict the total.

No separate reference answer has been written for this task. Start from Example B: Idempotency keys need a payload consistency rule or they can hide conflicting requests. A new identity applies separately, while a changed payload under an old key is rejected.

### Task 3: Independent construction

Implement a result lookup that does not execute the command again.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var receipts = new Dictionary<string, int>(StringComparer.Ordinal);
int executions = 0;
int Execute(string id, int amount) {
  if (receipts.TryGetValue(id, out int receipt)) {
    return receipt;
  }
  executions++;
  receipts[id] = amount * 10;
  return receipts[id];
}
int first = Execute("op-1", 3);
int retry = Execute("op-1", 3);
Check(first == 30 && retry == 30, "same receipt");
Check(executions == 1, "command ran once");
```

**Observe:** Both calls return receipt 30, and the command ran only once.

The lookup answers a repeated request from the stored receipt, so a retry after an unknown outcome cannot apply the command a second time.

### Task 4: Diagnose a defect

Diagnose retrying a write after an observer timeout with a fresh identity.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: This in-memory ledger does not survive restart and is not concurrent. A production idempotency record needs retention and conflict policy. Do not describe retries as exactly-once delivery.

### Task 5: Boundary evidence

Test repeated identity with identical and conflicting payloads.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Replay a recorded result without applying again) and Example B (Distinguish a new operation).

### Task 6: Transfer and justify

Design durable atomic storage for an effect and its receipt and state remaining failure modes.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Idempotency key**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A failed observation is not always a failed operation. A server may commit a write before the client loses its response. Retrying that write can duplicate an effect unless the protocol includes an idempotency key or another reconciliation mechanism. Exactly-once effects require careful scope and durable coordination; a retry loop alone cannot create that guarantee.

Bound retry attempts and use a failure policy that distinguishes transient, permanent and unknown outcomes. Backoff helps avoid overload but does not fix an invalid request. This offline state machine demonstrates once-per-key application under a single-threaded in-memory contract. Production durability and concurrency require additional storage and transaction evidence.

A dictionary of operation identities records prior results. Check identity before applying a side effect, and store the result with the effect under a single atomic boundary in a real durable implementation.

This in-memory ledger does not survive restart and is not concurrent. A production idempotency record needs retention and conflict policy. Do not describe retries as exactly-once delivery.

## Review before continuing

Run the reference and confirm that it prints `csharp-047: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
