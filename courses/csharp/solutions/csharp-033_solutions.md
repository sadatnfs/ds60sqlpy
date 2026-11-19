# csharp-033: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-033_solution.cs](csharp-033_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Protect increments:** The lock protects the read-modify-write transition, so the expected count does not depend on scheduling. Four tasks produce exactly 400 increments.

**Protect a multi-field invariant:** A synchronized writer with an unsynchronized reader does not establish the same contract. The reader uses the same gate as mutation.

## Task answers

### Task 1: Predict and explain

Decompose an increment into its logical steps.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The lock protects the read-modify-write transition, so the expected count does not depend on scheduling. Four tasks produce exactly 400 increments.

### Task 2: Guided modification

Increase task count while keeping the exact expected total.

No separate reference answer has been written for this task. Start from Example B: A synchronized writer with an unsynchronized reader does not establish the same contract. The reader uses the same gate as mutation.

### Task 3: Independent construction

Implement a locked transfer preserving the sum of two balances.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var gate = new Lock();
int left = 100;
int right = 0;
void Transfer(int amount) {
  lock (gate) {
    left -= amount;
    right += amount;
  }
}
Task Move() => Task.Run(() => Transfer(5));
var moves = new List<Task>();
for (int i = 0; i < 10; i++) {
  moves.Add(Move());
}
await Task.WhenAll(moves);
Check(left + right == 100 && right == 50, "sum preserved");
```

**Observe:** After ten concurrent transfers of 5 the balances are 50 and 50, still summing to 100.

Both balances change inside one lock, so no other transfer can observe or interleave with a half-finished move.

### Task 4: Diagnose a defect

Describe a two-lock acquisition cycle and repair it with an ordering rule.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A passing unsynchronized stress run does not prove absence of races. Locking a different object in the reader does not protect the writer invariant. Never await inside a synchronous lock.

### Task 5: Boundary evidence

Test zero operations and concurrent readers.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Protect increments) and Example B (Protect a multi-field invariant).

### Task 6: Transfer and justify

Choose immutable snapshots or a lock for a shared report cache and justify the ownership model.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Atomicity**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Concurrency permits operations to overlap. A data race occurs when unsynchronized access to shared mutable state violates the required memory and ordering rules. Even an apparently simple increment includes read, calculation and write, so it is not automatically atomic. Correctness requires protecting the entire invariant, not just individual fields.

A lock establishes mutual exclusion and ordering for code using the same lock object. Keep the protected region small and avoid awaiting while holding a synchronous lock. Never choose a publicly accessible object or a mutable value as the lock identity. Deadlock is a separate risk when multiple locks are acquired in conflicting orders; a single documented ordering can prevent that class of cycle.

`lock (gate)` enters a protected region and exits even on exceptions. All accesses participating in the invariant must use the same gate. Since .NET 9 and C# 13, `System.Threading.Lock` is the dedicated lock type: `lock` on a `Lock` uses its scope API, and the compiler warns when a `Lock` is converted to `object`. Task.WhenAll observes the completion of the scheduled work.

A passing unsynchronized stress run does not prove absence of races. Locking a different object in the reader does not protect the writer invariant. Never await inside a synchronous lock.

## Review before continuing

Run the reference and confirm that it prints `csharp-033: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
