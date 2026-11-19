# csharp-019: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-019_solution.cs](csharp-019_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**A closure observes its captured variable:** The closure refers to the variable, not a permanently copied value from creation time. Changing factor changes later calls through the closure.

**Manage an event subscription:** Keeping the handler reference makes unsubscription precise and prevents a lingering callback. Only the first emission reaches the removed handler.

## Task answers

### Task 1: Predict and explain

Predict both scale results before running.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The closure refers to the variable, not a permanently copied value from creation time. Changing factor changes later calls through the closure.

### Task 2: Guided modification

Capture a separate local snapshot and compare its behavior after factor changes.

No separate reference answer has been written for this task. Start from Example B: Keeping the handler reference makes unsubscription precise and prevents a lingering callback. Only the first emission reaches the removed handler.

### Task 3: Independent construction

Write a transformation method accepting Func<int,int>.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int[] Transform(int[] values, Func<int, int> change) {
  var result = new int[values.Length];
  for (int i = 0; i < values.Length; i++) {
    result[i] = change(values[i]);
  }
  return result;
}
int[] input = { 1, 2, 3 };
int[] scaled = Transform(input, value => value * 10);
Check(scaled.SequenceEqual(new[] { 10, 20, 30 }), "delegate applied");
Check(input[0] == 1, "input unchanged");
```

**Observe:** Applying value * 10 gives 10, 20 and 30 and leaves the input unchanged.

The caller supplies the behavior as a Func<int, int>, while the method owns iteration and the new result array.

### Task 4: Diagnose a defect

Diagnose unsubscribing with a newly created lambda instead of the subscribed delegate.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Closure capture can retain large objects or unexpected mutable state. Event handlers should avoid hiding failures. A new lambda with similar source is not necessarily the same delegate needed for unsubscription.

### Task 5: Boundary evidence

Test no subscribers and two subscribers.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (A closure observes its captured variable) and Example B (Manage an event subscription).

### Task 6: Transfer and justify

Design ownership for subscriptions in a screen or service that can be disposed.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Delegate**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A delegate is a typed reference to callable behavior. Passing behavior lets a reusable algorithm vary one decision, such as filtering or transformation, while keeping traversal unchanged. A closure also carries access to variables from its surrounding scope. It captures the variable relationship, which can make later mutations visible when the function eventually executes.

Events build a publish-and-subscribe boundary. The publisher controls when to raise an event; subscribers supply reactions. Subscriptions also create reference relationships and lifetime obligations. A long-lived publisher can retain subscribers unless they unsubscribe. Start with short, deterministic delegate examples before adding event-driven application lifetime.

`Func<int,int>` represents a callable taking int and returning int. `x => x * factor` is a lambda. An event uses `+=` to subscribe and `-=` to remove the same handler instance.

Closure capture can retain large objects or unexpected mutable state. Event handlers should avoid hiding failures. A new lambda with similar source is not necessarily the same delegate needed for unsubscription.

## Review before continuing

Run the reference and confirm that it prints `csharp-019: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
