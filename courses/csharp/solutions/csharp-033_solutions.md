# csharp-033: explanation and comparison

Reference program: [csharp-033_solution.cs](csharp-033_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Protect increments:** The lock protects the read-modify-write transition, so the expected count does not depend on scheduling. Four tasks produce exactly 400 increments.

**Protect a multi-field invariant:** A synchronized writer with an unsynchronized reader does not establish the same contract. The reader uses the same gate as mutation.

## Task answers

### Task 1: Predict and explain

Decompose an increment into its logical steps.

**Written answer.** `value++` inside `LockedCounter.Add` is three logical steps: read the current `value` into a register, add 1 to that copy, and write the copy back to the field. Without the lock, two tasks can both read 41, both compute 42 and both write 42, so one increment disappears even though neither task failed. The `lock (gate)` statement makes the read, add and write one indivisible step with respect to every other code path that takes the same gate, which is why Example A always ends at 400.

**Why it is correct.** The lost update is not visible in any single line of code; it only appears when you split the line into the steps the processor actually performs. Naming the steps shows exactly which window the lock closes.

**Plausible wrong approach.** Assuming `++` is atomic because it is one operator, or protecting only the write, leaves the read and the write separable and still loses updates under contention.

**How to verify.** Temporarily replace `lock (gate) value++;` with `value++;`, run Example A several times with more iterations, and observe totals below the expected count.

### Task 2: Guided modification

Increase task count while keeping the exact expected total.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var counter = new LockedCounter();
const int tasks = 8;
const int perTask = 250;
void AddMany() {
  for (int i = 0; i < perTask; i++)
    counter.Add();
}
var work = new List<Task>();
for (int t = 0; t < tasks; t++)
  work.Add(Task.Run(AddMany));
await Task.WhenAll(work);
Check(counter.Value == tasks * perTask, "exact total 2000");
```

**Observe:** Eight tasks of 250 increments each end at exactly 2000.

The expected total is the product of task count and increments per task, so it is computed from the same constants the loop uses instead of being typed separately. Doubling the tasks and changing the per-task count does not change the reasoning: every `Add` passes through the same gate, so no increment is lost no matter how the tasks interleave, and `Task.WhenAll` guarantees all of them finished before `Value` is read.

**Plausible wrong approach.** Reading `Value` before awaiting `Task.WhenAll`, or hardcoding 800 after changing the constants, produces a check that fails or passes for the wrong reason.

**How to verify.** Change `tasks` to 16 and `perTask` to 1000 and confirm the check still passes with 16000 without editing the expected value.

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

**Written answer.** Two locks form a cycle when task 1 takes `accountA` and then waits for `accountB`, while task 2 takes `accountB` and then waits for `accountA`. Each holds the lock the other needs, so both wait forever and nothing throws. The repair is a global acquisition order: every code path that needs both locks takes them in the same order, for example the account with the smaller identifier first, regardless of the direction of the transfer. With one order, a task can only ever wait for a lock ranked above one it holds, so no cycle can form.

**Why it is correct.** Deadlock needs a cycle in the wait-for graph. An ordering rule removes cycles by construction, which is stronger than hoping the timing never lines up.

**Plausible wrong approach.** Adding a timeout or a retry hides the symptom and can livelock; taking the locks in the order of the transfer arguments keeps the cycle, because transfer(A, B) and transfer(B, A) still disagree.

**How to verify.** Write a transfer that orders the two locks by identifier, run many A to B and B to A transfers concurrently, and confirm they all finish and the sum of balances is unchanged.

### Task 5: Boundary evidence

Test zero operations and concurrent readers.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var idle = new LockedCounter();
Check(idle.Value == 0, "zero operations read 0");
var live = new LockedCounter();
void Write() {
  for (int i = 0; i < 1000; i++)
    live.Add();
}
int Sample() => live.Value;
var writer = Task.Run(Write);
var samples = new List<Task<int>>();
for (int r = 0; r < 4; r++)
  samples.Add(Task.Run(Sample));
int[] during = await Task.WhenAll(samples);
await writer;
Check(during.All(v => v >= 0 && v <= 1000), "each read is a whole count");
Check(live.Value == 1000, "final total exact");
```

**Observe:** A fresh counter reads 0, every concurrent read lies between 0 and 1000, and the final value is exactly 1000.

With zero operations nothing has written the field, so the reader sees the default 0 and taking the lock is harmless. During writes, each reader takes the same gate as `Add`, so it observes the counter between two whole increments, never in the middle of one. The exact value a reader sees depends on timing, which is why the check states a range instead of a number; only the final value after `await writer` is exact.

**Plausible wrong approach.** Asserting that the concurrent readers see a specific value such as 500 makes the test depend on scheduling and fail at random.

**How to verify.** Add a fifth reader after `await writer` and confirm it always sees 1000, while the readers started during the writes may differ between runs.

### Task 6: Transfer and justify

Choose immutable snapshots or a lock for a shared report cache and justify the ownership model.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

Concurrency permits operations to overlap. A data race occurs when unsynchronized access to shared mutable state violates the required memory and ordering rules. Even an apparently simple increment includes read, calculation and write, so it is not automatically atomic. Correctness requires protecting the entire invariant, not just individual fields.

A lock establishes mutual exclusion and ordering for code using the same lock object. Keep the protected region small and avoid awaiting while holding a synchronous lock. Never choose a publicly accessible object or a mutable value as the lock identity. Deadlock is a separate risk when multiple locks are acquired in conflicting orders; a single documented ordering can prevent that class of cycle.

`lock (gate)` enters a protected region and exits even on exceptions. All accesses participating in the invariant must use the same gate. Since .NET 9 and C# 13, `System.Threading.Lock` is the dedicated lock type: `lock` on a `Lock` uses its scope API, and the compiler warns when a `Lock` is converted to `object`. Task.WhenAll observes the completion of the scheduled work.

A passing unsynchronized stress run does not prove absence of races. Locking a different object in the reader does not protect the writer invariant. Never await inside a synchronous lock.

## Review before continuing

Run the reference and confirm it prints `csharp-033: passed`, then rerun the guide's counterexample.
