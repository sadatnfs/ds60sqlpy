# csharp-047: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-047_solution.cs](csharp-047_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Replay a recorded result without applying again:** Operation identity separates a replay from a genuinely new command. The repeated identity returns its prior result without increasing the total.

**Distinguish a new operation:** Idempotency keys need a payload consistency rule or they can hide conflicting requests. A new identity applies separately, while a changed payload under an old key is rejected.

## Reason through the six tasks

1. **Predict and explain.** Trace the effect and receipt for the repeated operation.

2. **Guided modification.** Add a third unique operation and predict the total.

3. **Independent construction.** Implement a result lookup that does not execute the command again.

4. **Diagnose a defect.** Diagnose retrying a write after an observer timeout with a fresh identity.

5. **Boundary evidence.** Test repeated identity with identical and conflicting payloads.

6. **Transfer and justify.** Design durable atomic storage for an effect and its receipt and state remaining failure modes.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A failed observation is not always a failed operation. A server may commit a write before the client loses its response. Retrying that write can duplicate an effect unless the protocol includes an idempotency key or another reconciliation mechanism. Exactly-once effects require careful scope and durable coordination; a retry loop alone cannot create that guarantee.

Bound retry attempts and use a failure policy that distinguishes transient, permanent and unknown outcomes. Backoff helps avoid overload but does not fix an invalid request. This offline state machine demonstrates once-per-key application under a single-threaded in-memory contract. Production durability and concurrency require additional storage and transaction evidence.

A dictionary of operation identities records prior results. Check identity before applying a side effect, and store the result with the effect under a single atomic boundary in a real durable implementation.

This in-memory ledger does not survive restart and is not concurrent. A production idempotency record needs retention and conflict policy. Do not describe retries as exactly-once delivery.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
