# csharp-034: explanation and comparison

Reference program: [csharp-034_solution.cs](csharp-034_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Count atomically:** Each increment is one supported atomic operation rather than a compound unsynchronized expression. The atomic count is exactly 400.

**Update one key safely:** The update delegate is a pure calculation, so repeated evaluation cannot duplicate an external effect. Twenty admitted updates produce 20.

## Task answers

### Task 1: Predict and explain

Compare count++ with Interlocked.Increment.

**Written answer.** `count++` is a read, an add and a write. Two tasks can both read 57 and both write 58, losing one increment, so four tasks of 100 can end below 400. `Interlocked.Increment(ref count)` performs the read, add and write as one indivisible operation, so the total is exactly 400.

**Why it is correct.** The processor's atomic increment never exposes an intermediate value, so no other task can read between the load and the store.

**Plausible wrong approach.** Marking a field `volatile` and keeping `count++` does not help. `volatile` makes each read and write visible, but the three steps can still interleave, so updates are still lost.

**How to verify.** Swap in `count++` and raise the loop to 100,000 per task; repeated runs usually end below 400,000 and the check throws. With `Interlocked.Increment` every run is exact. With only 100 iterations a lost update is rare, which is why the count is raised.

### Task 2: Guided modification

Add a second independently counted key.

**Written answer.** Add ten tasks calling `counts.AddOrUpdate("b", 1, (_, previous) => previous + 1)` to the same `Task.WhenAll`, then check `counts["a"] == 20 && counts["b"] == 10`.

**Why it is correct.** Each `AddOrUpdate` call is atomic for its key, and updates to `a` and `b` never affect each other, so the two counts are independent.

**Plausible wrong approach.** Writing `counts["b"] = counts.GetValueOrDefault("b") + 1;` uses two thread-safe calls, but the read and the write are separate. Two tasks can read 4 and both store 5, so `b` sometimes ends below 10.

**How to verify.** Run the combined example ten times in a loop and check both counts every time.

### Task 3: Independent construction

Build a concurrent frequency counter using pure update functions.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var counts = new ConcurrentDictionary<string, int>();
string[] words = { "a", "b", "a", "a" };
int Next(string key, int before) => before + 1;
Task Add(string w) => Task.Run(() => counts.AddOrUpdate(w, 1, Next));
await Task.WhenAll(words.Select(Add));
Check(counts["a"] == 3 && counts["b"] == 1, "concurrent frequencies");
```

**Observe:** a is counted 3 times and b once.

AddOrUpdate may retry the update function under contention, so the function is pure: it computes the new count from the old one without side effects.

**Plausible wrong approach.** Replacing `AddOrUpdate` with `counts.TryGetValue(w, out int c); counts[w] = c + 1;` keeps the dictionary itself consistent but loses updates between the read and the write, so `a` can end at 2.

**How to verify.** The block checks `a` is 3 and `b` is 1. Scale it to `Enumerable.Repeat("a", 10_000)` and check `counts["a"] == 10_000` on several runs; the read-then-write version usually falls short.

### Task 4: Diagnose a defect

Diagnose sending a message inside an AddOrUpdate delegate.

**Written answer.** A delegate such as `(k, old) => { mailer.Send($"{k} updated"); return old + 1; }` can run more than once for one logical update. `AddOrUpdate` reads the value, calls the delegate, then tries to store; if another task changed the value first, it calls the delegate again. Send after the call, using its return value.

**Why it is correct.** `ConcurrentDictionary` runs the delegate outside its internal lock and retries on contention, so only the returned value is guaranteed to correspond to one successful update.

**Plausible wrong approach.** Wrapping `mailer.Send` in a `lock` inside the delegate serializes the sends but does not stop the retry, so a retried update still sends a second message.

**How to verify.** Count delegate calls with `Interlocked.Increment` during 20 concurrent updates of one key. Under contention the call count can exceed 19 while `counts["a"]` is 20; messages sent after the call are exactly 20.

### Task 5: Boundary evidence

Test absent and already-present keys.

**Written answer.** Check `counts.AddOrUpdate("x", 1, (_, p) => p + 1) == 1` for an absent key, and a second call returns 2. For `GetOrAdd`, check the factory is not called when the key already exists.

**Why it is correct.** `AddOrUpdate` uses `addValue` when the key is absent and the update function only when it is present, so the two cases exercise different code.

**Plausible wrong approach.** Passing `0` as `addValue` passes every test that only uses already-present keys, but the first word is then counted as 0 and every frequency is one too low.

**How to verify.** Run the absent and present checks on a fresh dictionary, then change `addValue` to 0 and confirm the absent-key check throws.

### Task 6: Transfer and justify

Explain why atomically updating two separate balances does not preserve a transfer invariant.

**Written answer.** A transfer of 10 from A to B done as two atomic updates, `A - 10` and then `B + 10`, leaves a moment where the money is in neither account. A concurrent audit sums 90 instead of 100, and an exception between the calls loses the 10 permanently.

**Why it is correct.** Atomicity per key protects one location. The invariant `A + B == 100` spans two locations, so both updates need one lock or a transaction that the audit also respects.

**Plausible wrong approach.** Making the debit conditional with `TryUpdate("A", old - 10, old)` stops overdrafts but does not join the two steps. A reader between the debit and the credit still sees 90.

**How to verify.** Run 1,000 transfers in one task while another task sums both balances repeatedly. Without a shared lock some sums are 90; with one lock around both the transfer and the audit, every sum is 100.

## Mechanism and diagnostic reasoning

Interlocked provides atomic operations on supported locations, such as increment and compare-exchange. These operations are useful for simple shared state, but several individually atomic operations do not automatically form one atomic transaction. Match the mechanism to the complete invariant.

Concurrent collections make their documented operations thread-safe. Delegates passed to GetOrAdd or AddOrUpdate may execute more than once and outside internal locks. They should therefore avoid irreversible side effects. A dictionary value being safely published does not make a mutable object stored inside it automatically thread-safe.

`Interlocked.Increment(ref value)` atomically updates one location. ConcurrentDictionary manages concurrent lookup/update operations. A factory must tolerate repeated evaluation.

Concurrent containers protect their own structure, not arbitrary objects stored inside them. Do not infer once-only callback execution. Use a higher-level lock or transaction for multi-location invariants.

## Review before continuing

Run the reference and confirm it prints `csharp-034: passed`, then rerun the guide's counterexample.
