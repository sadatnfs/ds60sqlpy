# csharp-047: explanation and comparison

Reference program: [csharp-047_solution.cs](csharp-047_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Replay a recorded result without applying again:** Operation identity separates a replay from a genuinely new command. The repeated identity returns its prior result without increasing the total.

**Distinguish a new operation:** Idempotency keys need a payload consistency rule or they can hide conflicting requests. A new identity applies separately, while a changed payload under an old key is rejected.

## Task answers

### Task 1: Predict and explain

Trace the effect and receipt for the repeated operation.

**Written answer.** In Example A the first `Apply("op-1", 3)` finds no record, adds 3 to `Total` and stores `(3, 3)` under `op-1`; the effect is the change to `Total` and the receipt is the returned 3. The repeated call finds `op-1`, sees the same amount, and returns the stored result 3 without touching `Total`. So there is one effect and two identical receipts, and `Total` stays 3.

**Why it is correct.** Separating the effect from the receipt is what makes a retry safe: the caller can ask again and get the original answer without causing the effect twice.

**Plausible wrong approach.** Recomputing the receipt from the current `Total` instead of storing it would make an old operation's reply change after later operations run.

**How to verify.** Apply `op-2` with 3 between the two `op-1` calls and confirm the replayed `op-1` receipt is still 3 while `Total` is 6.

### Task 2: Guided modification

Add a third unique operation and predict the total.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var ledger = new Ledger();
ledger.Apply("op-1", 3);
ledger.Apply("op-2", 3);
int third = ledger.Apply("op-3", 5);
Check(third == 11 && ledger.Total == 11, "predicted total 11");
Check(ledger.Apply("op-3", 5) == 11 && ledger.Total == 11, "op-3 replay");
```

**Observe:** The third unique operation brings the total to 11, as predicted, and repeating it returns 11 again without changing the total.

Each new identity applies once, so the prediction is 3 plus 3 plus 5, which is 11. The receipt for `op-3` is the total right after its effect, 11, and a retry of `op-3` replays that stored receipt instead of adding 5 again.

**Plausible wrong approach.** Predicting 16 after the retry counts the replay as a second effect.

**How to verify.** Apply `op-4` with 0 and predict whether the total changes and what its receipt is before running.

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

**Written answer.** The client sends `Apply("op-1", 3)`, the server applies it, and the reply is lost, so the client sees a timeout. The outcome is unknown, not failed. If the client retries with a fresh identity, `op-1b`, the ledger has no record of it and applies 3 again, so `Total` becomes 6 for one intended payment. The retry must reuse the original identity so the server can recognize it and replay the receipt; generate the identity once per intended operation, before the first attempt, and persist it with the request.

**Why it is correct.** Idempotency depends on the server seeing the same key for the same intent. A new key tells the server it is a new operation.

**Plausible wrong approach.** Not retrying at all loses operations whose request never arrived, and retrying with a new key duplicates operations whose request did arrive. Only a stable key covers both cases.

**How to verify.** Simulate the lost reply by ignoring the first return value, retry once with the same identity and once with a fresh one, and compare totals of 3 and 6.

### Task 5: Boundary evidence

Test repeated identity with identical and conflicting payloads.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var ledger = new Ledger();
int first = ledger.Apply("op-9", 4);
int same = ledger.Apply("op-9", 4);
Check(first == 4 && same == 4 && ledger.Total == 4, "identical replays");
bool conflict = false;
try {
  ledger.Apply("op-9", 5);
} catch (InvalidOperationException) {
  conflict = true;
}
Check(conflict && ledger.Total == 4, "conflict rejected, no effect");
Check(ledger.Apply("op-9", 4) == 4, "original receipt still valid");
```

**Observe:** The identical repeat replays receipt 4; the conflicting payload throws `InvalidOperationException`, leaves the total at 4, and the original request still replays.

The ledger stores the payload with the receipt, so it can tell a retry from a different command reusing a key. An identical payload is a retry and gets the stored answer. A different amount under the same key is a client error: applying it would change the meaning of a recorded operation and replaying the old receipt would hide the mistake, so it is rejected before any effect. The rejection does not damage the record, so the genuine retry still works.

**Plausible wrong approach.** Replaying the old receipt for the conflicting payload would let the client believe 5 was applied when 4 was.

**How to verify.** Apply `op-10` with 5 after the conflict and confirm the total becomes 9, which shows the rejection did not block new identities.

### Task 6: Transfer and justify

Design durable atomic storage for an effect and its receipt and state remaining failure modes.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A failed observation is not always a failed operation. A server may commit a write before the client loses its response. Retrying that write can duplicate an effect unless the protocol includes an idempotency key or another reconciliation mechanism. Exactly-once effects require careful scope and durable coordination; a retry loop alone cannot create that guarantee.

Bound retry attempts and use a failure policy that distinguishes transient, permanent and unknown outcomes. Backoff helps avoid overload but does not fix an invalid request. This offline state machine demonstrates once-per-key application under a single-threaded in-memory contract. Production durability and concurrency require additional storage and transaction evidence.

A dictionary of operation identities records prior results. Check identity before applying a side effect, and store the result with the effect under a single atomic boundary in a real durable implementation.

This in-memory ledger does not survive restart and is not concurrent. A production idempotency record needs retention and conflict policy. Do not describe retries as exactly-once delivery.

## Review before continuing

Run the reference and confirm it prints `csharp-047: passed`, then rerun the guide's counterexample.
