# csharp-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-030_solution.cs](csharp-030_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe a requested cancellation:** Calling Cancel changes request state; the explicit observation is what changes the operation control flow. The token check acknowledges cancellation.

**Cancel waiting while work remains live:** This deterministic distinction prevents treating an interrupted observer as proof that an operation never happened. The wait cancels, then the original task later completes with 9.

## Reason through the six tasks

1. **Predict and explain.** Identify the request, observation and completion events.

2. **Guided modification.** Pass a token through a helper and check it before a state change.

3. **Independent construction.** Write an operation that stops cooperatively and preserves already committed work.

4. **Diagnose a defect.** Diagnose automatically replaying a write after its waiter times out.

5. **Boundary evidence.** Test cancellation requested before start and after successful completion.

6. **Transfer and justify.** Design an operation receipt distinguishing cancelled waiting, confirmed cancellation and unknown outcome.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Cancellation is a request for cooperation. A CancellationTokenSource owns the request; its token lets operations observe it. An operation that never checks or passes the token can continue after cancellation is requested. A timeout on the caller waiting is also distinct from termination of the underlying work.

Correct ownership includes awaiting or otherwise accounting for admitted work after a timeout. Do not retry a state-changing operation merely because the result is unknown. The first operation may still complete. Use operation identity and recovery evidence for such systems. Here, a TaskCompletionSource establishes exact states without guessing how long a background task takes.

`ThrowIfCancellationRequested` reports acknowledged cancellation. `WaitAsync(token)` cancels the wait without necessarily canceling the source task. TaskCompletionSource with RunContinuationsAsynchronously avoids executing arbitrary continuations inline inside a signal setter.

A catch for OperationCanceledException should match the intended cancellation policy. Cancelling a waiter does not dispose all resources owned by the operation. Retain and observe tasks that may still complete.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
