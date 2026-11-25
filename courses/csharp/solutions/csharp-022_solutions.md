# csharp-022: explanation and comparison

Reference program: [csharp-022_solution.cs](csharp-022_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Consume only a prefix:** The producer does not need to allocate all four outputs before serving the first one. The consumer receives 5 and 6 and can stop before the full range.

**Validate before returning the sequence:** The outer method validates first; the local iterator performs only the admitted traversal. Negative count is rejected immediately, without enumeration.

## Task answers

### Task 1: Predict and explain

Trace how many values Take(2) requests.

**Written answer.** `RangeFrom(5, 4).Take(2)` pulls two values. The iterator yields 5, then 6, and `Take` stops asking after the second, so 7 and 8 are never computed. `RangeFrom(5, 0).Any()` calls `MoveNext` once and gets false.

**Why it is correct.** Each `MoveNext` call resumes the iterator until the next `yield return`. `Take(2)` stops calling `MoveNext` after two items, and `SequenceEqual` then disposes the enumerator.

**Plausible wrong approach.** Assuming the loop computes all four values up front and `Take` trims the result describes an array-returning method. With `yield return`, the remaining iterations never run at all.

**How to verify.** Add a counter inside the loop, for example a static `produced` incremented before each `yield return`. After `RangeFrom(5, 4).Take(2).ToArray()` it is 2, not 4.

### Task 2: Guided modification

Generate every second integer with a bounded count.

**Written answer.** Add `static IEnumerable<int> EverySecond(int start, int count) { if (count < 0) throw new ArgumentOutOfRangeException(nameof(count)); return Iterate(); IEnumerable<int> Iterate() { for (int i = 0; i < count; i++) yield return checked(start + 2 * i); } }` and check `EverySecond(0, 3)` is `{ 0, 2, 4 }`.

**Why it is correct.** Following the `RangeFrom` pattern, validation happens before the iterator is returned, and the loop is bounded by `count`, so the sequence is finite and each step adds 2.

**Plausible wrong approach.** Writing `while (true) yield return start += 2;` with no count gives an infinite sequence. `EverySecond(0).ToArray()` then never returns, and `start += 2` also skips the starting value.

**How to verify.** Check `EverySecond(0, 3).SequenceEqual(new[] { 0, 2, 4 })`, `EverySecond(7, 2).SequenceEqual(new[] { 7, 9 })` and `!EverySecond(7, 0).Any()`, and confirm `EverySecond(0, -1)` throws at the call.

### Task 3: Independent construction

Implement a lazy sequence of cumulative totals.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
IEnumerable<int> Cumulative(IEnumerable<int> values) {
  int total = 0;
  foreach (int value in values) {
    total = checked(total + value);
    yield return total;
  }
}
int[] totals = Cumulative(new[] { 1, 2, 3 }).ToArray();
Check(totals.SequenceEqual(new[] { 1, 3, 6 }), "running totals");
Check(!Cumulative(Array.Empty<int>()).Any(), "empty input");
```

**Observe:** 1, 2, 3 produces 1, 3, 6; an empty input produces nothing.

yield return makes the sequence lazy: each total is computed only when the consumer asks for the next element.

**Plausible wrong approach.** Materializing inside the method with `var list = new List<int>(); ... return list;` gives the same totals but computes all of them before returning, so `Cumulative(hugeSource).First()` would read the entire input first.

**How to verify.** The block checks `1, 3, 6` and empty input. Also check `Cumulative(new[] { int.MaxValue, 1 }).First() == int.MaxValue` succeeds while `.ToArray()` throws `OverflowException` at the second element, showing the overflow is raised lazily.

### Task 4: Diagnose a defect

Diagnose validation inside an iterator body that callers expect to run immediately.

**Written answer.** If `count < 0` is checked inside a method that itself contains `yield return`, `var seq = Broken(0, -1);` returns without error. The `ArgumentOutOfRangeException` appears only at the first `MoveNext`, perhaps far from the faulty call. Split the method as `RangeFrom` does.

**Why it is correct.** The compiler turns a method containing `yield` into a state machine, and none of its body, including the guard, runs until enumeration begins. A non-iterator outer method runs immediately.

**Plausible wrong approach.** Adding `.ToList()` at the call site, as in `Broken(0, -1).ToList()`, surfaces the exception immediately, but only for callers that remember it. A caller that stores the sequence for later still gets the late failure, and the eager copy gives up laziness.

**How to verify.** With the broken version, the Example B `try` block catches nothing and `rejected` stays false, so the check throws. With the split version the same block sets `rejected` to true.

### Task 5: Boundary evidence

Test count zero, one and negative.

**Written answer.** Check `!RangeFrom(3, 0).Any()`, `RangeFrom(3, 1).SequenceEqual(new[] { 3 })` and that `RangeFrom(3, -1)` throws `ArgumentOutOfRangeException` when called, before any enumeration.

**Why it is correct.** A count of 0 never enters the loop, a count of 1 yields exactly `start`, and the outer guard rejects a negative count. Those three inputs cover the loop bound and the guard.

**Plausible wrong approach.** Writing the bound as `i <= count` yields one extra value: `RangeFrom(3, 0)` produces 3 instead of nothing and `RangeFrom(3, 1)` produces 3 and 4, so both count checks throw.

**How to verify.** Run the three checks. Then change `<` to `<=` temporarily and confirm the empty-range check throws.

### Task 6: Transfer and justify

Choose a sequence API for a large file and document repeated-enumeration and resource-lifetime behavior.

**Written answer.** Expose `IEnumerable<string> ReadRecords(string path)` built with `File.ReadLines`, and document that each enumeration reopens and rereads the file, that the file is closed when a `foreach` finishes or breaks, and that callers wanting a snapshot must call `ToList`.

**Why it is correct.** `File.ReadLines` opens the file when called and closes it when the enumerator is disposed, which `foreach` does even after `break`. A second enumeration opens the file again. Memory stays at one line at a time.

**Plausible wrong approach.** Returning the enumerator directly and having callers call `MoveNext` by hand risks skipping `Dispose`, which keeps the file handle open until finalization, so a later write to the file fails with `IOException`.

**How to verify.** Enumerate `ReadRecords(path).Take(1)` in a `foreach`, then open the same file for writing with `FileShare.None`; it succeeds because the reader was disposed.

## Mechanism and diagnostic reasoning

An iterator describes a sequence whose values are produced as the consumer asks for them. It can avoid materializing a large collection and can stop work when the consumer stops early. `yield return` pauses the iterator with its local state retained; the next request resumes it. This is different from returning a fully constructed list.

Lazy code shifts both work and some errors into enumeration. If argument validation must happen at the call site, place it outside the iterator body and return a nested iterator. Resource-owning iterators must also release resources when enumeration is abandoned. Consumers using foreach receive disposal behavior; custom enumerator handling must preserve it.

`IEnumerable<int>` exposes an iterable sequence. `yield return value` supplies one element and suspends. A nested local iterator separates immediate argument validation from delayed generation.

A sequence is not necessarily repeatable or cheap to enumerate. Do not assume calling an iterator method executes its body. Overflow remains possible even in a lazy generator.

## Review before continuing

Run the reference and confirm it prints `csharp-022: passed`, then rerun the guide's counterexample.
