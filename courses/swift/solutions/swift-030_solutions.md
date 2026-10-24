# swift-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-030_solution.swift](swift-030_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Cancel before observing a check:** The loop observes cancellation state rather than guessing a scheduling delay. The task acknowledges cancellation and its completion is awaited.

**Cancellation need not prevent a result:** A cancellation request alone is not proof that an operation failed to execute. This task still returns 9 because its body does not check cancellation.

## Reason through the six tasks

1. **Predict and explain.** Separate cancellation request from acknowledged completion.

2. **Guided modification.** Add a cancellation check before a simulated state-changing step.

3. **Independent construction.** Write a bounded processing loop with cleanup on cancellation.

4. **Diagnose a defect.** Diagnose retrying an unknown write merely because its waiter was cancelled.

5. **Boundary evidence.** Test cancellation before work and after an already completed result.

6. **Transfer and justify.** Design a receipt distinguishing success, confirmed cancellation and unknown outcome.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Task cancellation records a request that cooperative code can observe. It does not forcibly stop every instruction. A cancelled task can still return a value if it never checks cancellation. Distinguish a caller no longer wanting a result from the operation having stopped before effects occurred.

Use cancellation checks before admitting expensive work and at meaningful loop boundaries. Cleanup remains necessary on cancellation paths. Do not replay a state-changing request simply because an observer was cancelled; the first operation may have completed. The fixture observes cancellation deterministically without relying on a race between sleep durations.

Task.isCancelled inspects state and Task.checkCancellation throws CancellationError. A task handle can be cancelled and then awaited to observe its actual completion. Cancellation handlers require careful sendable state ownership.

Polling cancellation in a tight CPU loop without yielding can waste resources. A cancellation handler must not race unsafely with the operation. Preserve result identity when deciding whether replay is safe.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
