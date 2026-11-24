# csharp-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-036_solution.cs](csharp-036_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use only admitted buffer contents:** The pool guarantees minimum capacity, not exact size or zeroed contents. Only three initialized elements contribute to the total.

**Release retained references deliberately:** The test checks controllable ownership, avoiding a flaky assumption about when garbage collection occurs. Clearing removes the application references without promising collection timing.

## Task answers

### Task 1: Predict and explain

Separate logical length from rented array length.

**Written answer.** `Rent(3)` promises an array of at least 3 elements. The shared pool rounds requests up to bucket sizes, so `rented.Length` is typically 16. The logical length is 3: the number of slots this code wrote and is allowed to read, which is why the sum uses `AsSpan(0, 3)`.

**Why it is correct.** Only the logical range holds values this code wrote. Slots 3 and beyond may be zero or may hold whatever a previous renter left there.

**Plausible wrong approach.** Summing `rented.Sum()` or looping to `rented.Length` reads the extra capacity. It happens to give 9 when those slots are zero, which hides the bug until a previous renter leaves data behind.

**How to verify.** Inside the `try`, write 100 into `rented[rented.Length - 1]`. The logical sum stays 9 while `rented.Sum()` becomes 109.

### Task 2: Guided modification

Use a different requested length while initializing exactly that region.

**Written answer.** Keep one variable, `int count = 5;`, use it for `Rent(count)`, for the loop that writes `i + 1` into slots 0 to 4, and for `AsSpan(0, count)`. The sum is 15.

**Why it is correct.** Driving the request, the initialization and the read from one value keeps the logical region identical in all three places.

**Plausible wrong approach.** Changing only `Rent(3)` to `Rent(5)` while the read still says `AsSpan(0, 3)` sums 1 + 2 + 3 = 6 and silently ignores two initialized slots.

**How to verify.** Check the sum is 15, then set `count = 17`: the array is typically 32 long, yet the sum is 153, the total of 1 to 17.

### Task 3: Independent construction

Write a pooled-buffer helper with finally-based return.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int SumPooled(int count) {
  int[] buffer = ArrayPool<int>.Shared.Rent(count);
  try {
    for (int i = 0; i < count; i++) {
      buffer[i] = i + 1;
    }
    return buffer.AsSpan(0, count).ToArray().Sum();
  } finally {
    ArrayPool<int>.Shared.Return(buffer, clearArray: true);
  }
}
Check(SumPooled(4) == 10, "logical range only");
```

**Observe:** Summing the first four slots gives 10.

The rented array may be longer than requested, so the code uses only the first count slots, and finally returns the buffer on every path.

**Plausible wrong approach.** Returning the buffer first and summing afterward, `Return(buffer, clearArray: true); return buffer.AsSpan(0, count).ToArray().Sum();`, reads an array the pool already owns. The clear has zeroed it, so `SumPooled(4)` returns 0 instead of 10.

**How to verify.** The block checks `SumPooled(4) == 10`. Add `SumPooled(1) == 1` and `SumPooled(100) == 5050`; the second needs a larger bucket and still uses only the first 100 slots.

### Task 4: Diagnose a defect

Diagnose reading uninitialized pooled capacity or returning the same buffer twice.

**Written answer.** Two defects. Reading past the logical length: rent 4, fill with 7, return without clearing, rent 4 again on the same thread, and `buffer[0]` is likely 7 rather than 0. Returning twice: `Return(buffer); Return(buffer);` can let two later `Rent` calls hand out the same array.

**Why it is correct.** The pool does not track who owns an array and does not reject a second return. Each caller must initialize what it reads and return each rental exactly once.

**Plausible wrong approach.** Wrapping the second `Return` in a `try` and expecting an exception to flag the mistake does not work, because the pool accepts the duplicate silently. The damage appears later, in unrelated code that shares the array.

**How to verify.** After a double return, `var x = Rent(4); var y = Rent(4);` and print `ReferenceEquals(x, y)`; it is likely true, which never happens with buffers returned once. Rent with a fresh `ArrayPool<int>.Create()` to see initial zeros for comparison.

### Task 5: Boundary evidence

Test cleanup when the computation throws.

**Written answer.** Wrap a pool created with `ArrayPool<int>.Create()` in a small `CountingPool : ArrayPool<int>` that counts `Rent` and `Return` calls and forwards them. Make the computation throw at element 2, catch the exception, and check one rent and one return.

**Why it is correct.** A counting pool gives deterministic evidence. Checking whether the shared pool later hands back the same array depends on per-thread caching and can vary between runs.

**Plausible wrong approach.** Placing `Return` after the computation instead of in `finally` skips it when the throw happens. Nothing crashes, because the pool simply allocates new arrays later, so the leak is invisible without counting.

**How to verify.** Check `rents == 1 && returns == 1` after the exception. Move `Return` out of `finally` and the same check throws because `returns` is 0.

### Task 6: Transfer and justify

Decide whether pooling is justified using allocation measurements and a stated lifetime contract.

**Written answer.** Pool a 128 KB parse buffer that a service allocates on every request, because arrays over 85,000 bytes go on the large object heap and are collected only in generation 2. State the contract: the buffer is rented and returned within one synchronous call and is never stored or captured by asynchronous work.

**Why it is correct.** Pooling pays off when measured allocation and generation 2 collections drop while results stay identical. The contract keeps the ownership risk small enough to review.

**Plausible wrong approach.** Pooling a 32-byte array used once per request adds `Rent` and `Return` calls and an ownership rule for almost no saving, because small short-lived arrays are cheap generation 0 allocations.

**How to verify.** Run a fixed workload of 10,000 parses with `new byte[131072]` and again with the pool. Compare `GC.GetAllocatedBytesForCurrentThread()` and `GC.CollectionCount(2)`, and check both versions produce identical parse results.

## Mechanism and diagnostic reasoning

The garbage collector reclaims unreachable managed objects. Reachability is not the same as usefulness: a global list or event subscription can keep an otherwise unwanted object alive. Resource cleanup still belongs to IDisposable rather than collection timing. Measure retained references before assuming the collector is malfunctioning.

ArrayPool reuses buffers to reduce allocation pressure. A rented array may be larger than requested and may contain prior data. Use only the logical length, initialize what will be read, and return exactly the borrowed array once. Clearing sensitive contents is a deliberate policy. Pooling adds ownership complexity, so it should solve a measured allocation problem.

`ArrayPool<T>.Shared.Rent(n)` grants temporary use of at least n elements. `Return` ends ownership. A try/finally protects return on failure; never expose a view after return.

Never assert that a weak reference must disappear immediately after a collection request. Returning a buffer while asynchronous work still uses it causes data corruption. Pooling is not inherently a performance win.

## Review before continuing

Run the reference and confirm that it prints `csharp-036: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
