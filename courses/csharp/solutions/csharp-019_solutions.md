# csharp-019: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-019_solution.cs](csharp-019_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**A closure observes its captured variable:** The closure refers to the variable, not a permanently copied value from creation time. Changing factor changes later calls through the closure.

**Manage an event subscription:** Keeping the handler reference makes unsubscription precise and prevents a lingering callback. Only the first emission reaches the removed handler.

## Reason through the six tasks

1. **Predict and explain.** Predict both scale results before running.

2. **Guided modification.** Capture a separate local snapshot and compare its behavior after factor changes.

3. **Independent construction.** Write a transformation method accepting Func<int,int>.

4. **Diagnose a defect.** Diagnose unsubscribing with a newly created lambda instead of the subscribed delegate.

5. **Boundary evidence.** Test no subscribers and two subscribers.

6. **Transfer and justify.** Design ownership for subscriptions in a screen or service that can be disposed.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A delegate is a typed reference to callable behavior. Passing behavior lets a reusable algorithm vary one decision, such as filtering or transformation, while keeping traversal unchanged. A closure also carries access to variables from its surrounding scope. It captures the variable relationship, which can make later mutations visible when the function eventually executes.

Events build a publish-and-subscribe boundary. The publisher controls when to raise an event; subscribers supply reactions. Subscriptions also create reference relationships and lifetime obligations. A long-lived publisher can retain subscribers unless they unsubscribe. Start with short, deterministic delegate examples before adding event-driven application lifetime.

`Func<int,int>` represents a callable taking int and returning int. `x => x * factor` is a lambda. An event uses `+=` to subscribe and `-=` to remove the same handler instance.

Closure capture can retain large objects or unexpected mutable state. Event handlers should avoid hiding failures. A new lambda with similar source is not necessarily the same delegate needed for unsubscription.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
