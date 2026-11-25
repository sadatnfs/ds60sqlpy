# csharp-019: explanation and comparison

Reference program: [csharp-019_solution.cs](csharp-019_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**A closure observes its captured variable:** The closure refers to the variable, not a permanently copied value from creation time. Changing factor changes later calls through the closure.

**Manage an event subscription:** Keeping the handler reference makes unsubscription precise and prevents a lingering callback. Only the first emission reaches the removed handler.

## Task answers

### Task 1: Predict and explain

Predict both scale results before running.

**Written answer.** The first call `scale(3)` returns 6 because `factor` is 2. After `factor = 4`, the same delegate returns 12. The lambda captured the variable `factor`, not its value at the time the lambda was created.

**Why it is correct.** The compiler moves a captured local into a hidden object shared by the method and the lambda. Assigning `factor = 4` writes to that shared storage, and the next call reads it.

**Plausible wrong approach.** Predicting 6 for both calls treats capture as a copy taken at creation time. That is how a parameter or a separate local snapshot behaves, not a captured variable.

**How to verify.** Example A checks both values. Insert `factor = 10;` before the second check and confirm `scale(3)` would now be 30, which shows the delegate reads the variable at each call.

### Task 2: Guided modification

Capture a separate local snapshot and compare its behavior after factor changes.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
int factor = 2;
int snapshot = factor;
Func<int, int> live = value => value * factor;
Func<int, int> frozen = value => value * snapshot;
factor = 4;
Check(live(3) == 12, "live capture sees the new factor");
Check(frozen(3) == 6, "snapshot keeps the old factor");
```

**Observe:** After factor changes to 4, live(3) is 12 while frozen(3) is still 6.

`snapshot` is a separate local that received the value 2 once. The `frozen` lambda captures `snapshot`, and nothing assigns to it later, so its result stays 6. The `live` lambda captures `factor`, which changed, so its result follows to 12.

**Plausible wrong approach.** Writing `Func<int, int> frozen = value => value * factor;` and expecting it to remember 2 because it was created earlier gives 12 instead. The creation time of a lambda does not freeze the variables it reads.

**How to verify.** Assign `snapshot = 5;` after creating `frozen` and confirm `frozen(3)` becomes 15. The snapshot is only safe while nothing writes to it.

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

**Written answer.** `source.Raised += (_, _) => calls++;` followed by `source.Raised -= (_, _) => calls++;` does not unsubscribe. The second lambda creates a new delegate instance that is not equal to the subscribed one, so the removal finds no match and silently does nothing. After two `Emit` calls `calls` is 2. Keep the delegate in a variable, as Example B does with `handler`, and remove that same variable.

**Why it is correct.** Event removal compares delegates by target and method. Each lambda expression that captures `calls` produces its own delegate, so two textually identical lambdas do not compare equal, and `-=` removes nothing.

**Plausible wrong approach.** Assuming the removal worked because no exception was raised misreads the API: removing a delegate that is not subscribed is allowed and has no effect. The leftover handler keeps the subscriber and everything it captured alive.

**How to verify.** Run the faulty version: emit, remove with a new lambda, emit again, and check `calls == 2`. With the stored `handler`, the same sequence gives `calls == 1`, as Example B shows.

### Task 5: Boundary evidence

Test no subscribers and two subscribers.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var source = new Signal();
int first = 0;
int second = 0;
source.Emit();
Check(first == 0 && second == 0, "no subscribers, no calls");
source.Raised += (_, _) => first++;
source.Raised += (_, _) => second++;
source.Emit();
Check(first == 1 && second == 1, "both subscribers called once");
```

**Observe:** Emitting with no subscribers does nothing and does not throw; with two subscribers each counter becomes 1.

With no subscribers `Raised` is null, and `Raised?.Invoke(...)` skips the call instead of throwing `NullReferenceException`. Each `+=` adds a delegate to the invocation list, so one `Emit` calls both handlers once, in subscription order.

**Plausible wrong approach.** Writing `Raised.Invoke(this, EventArgs.Empty)` without `?.` passes the two-subscriber test but throws on the first `Emit` with no subscribers. Testing only the two-subscriber case would never reveal it.

**How to verify.** Subscribe the same delegate twice and confirm one `Emit` increments it twice. Then remove it once and confirm the next `Emit` increments it once.

### Task 6: Transfer and justify

Design ownership for subscriptions in a screen or service that can be disposed.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A delegate is a typed reference to callable behavior. Passing behavior lets a reusable algorithm vary one decision, such as filtering or transformation, while keeping traversal unchanged. A closure also carries access to variables from its surrounding scope. It captures the variable relationship, which can make later mutations visible when the function eventually executes.

Events build a publish-and-subscribe boundary. The publisher controls when to raise an event; subscribers supply reactions. Subscriptions also create reference relationships and lifetime obligations. A long-lived publisher can retain subscribers unless they unsubscribe. Start with short, deterministic delegate examples before adding event-driven application lifetime.

`Func<int,int>` represents a callable taking int and returning int. `x => x * factor` is a lambda. An event uses `+=` to subscribe and `-=` to remove the same handler instance.

Closure capture can retain large objects or unexpected mutable state. Event handlers should avoid hiding failures. A new lambda with similar source is not necessarily the same delegate needed for unsubscription.

## Review before continuing

Run the reference and confirm it prints `csharp-019: passed`, then rerun the guide's counterexample.
