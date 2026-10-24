# csharp-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-029_solution.cs](csharp-029_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Await values explicitly:** The task handle and the eventual integer are distinct values even when this fixture completes immediately. Await yields 7 and confirms successful completion.

**Compose and observe failure:** Awaiting establishes ownership of both success and failure instead of losing an unobserved background result. WhenAll retains input order and await exposes the task exception.

## Reason through the six tasks

1. **Predict and explain.** Distinguish the Task<int> handle from its awaited integer.

2. **Guided modification.** Combine three completed tasks and predict output ordering.

3. **Independent construction.** Write an async method returning a validated total.

4. **Diagnose a defect.** Diagnose forgetting to await an operation whose failure matters.

5. **Boundary evidence.** Test successful, failed and empty WhenAll inputs.

6. **Transfer and justify.** Explain when CPU work might need scheduling separately from an asynchronous I/O API.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A Task represents eventual completion, failure or cancellation. Async methods let control return to a caller while an awaited operation is incomplete. Async does not automatically mean a new thread, and awaiting a task does not block a thread in the same way as calling Wait or Result. For I/O, the goal is to avoid holding a thread idle while another system works.

Keep task ownership visible: the caller should await work whose result or failure matters. Fire-and-forget work can outlive its owner and lose exceptions. CPU-heavy work has different scheduling needs from asynchronous I/O. This chapter uses already completed and explicitly coordinated tasks so results do not depend on network access or arbitrary delays.

`async Task<int>` declares an asynchronous result. `await` obtains the completed result or rethrows the task failure. Task.WhenAll combines completion of several tasks; its result order follows the input task order, not completion order.

Async void is mainly for required event-handler signatures, not general composable methods. Blocking with Result can deadlock in synchronization contexts. Task.Run does not make a blocking external API inherently scalable.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
