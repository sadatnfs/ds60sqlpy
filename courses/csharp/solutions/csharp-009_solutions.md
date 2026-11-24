# csharp-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-009_solution.cs](csharp-009_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Separate count from reserved storage:** Capacity is an implementation resource, not a promise that ten logical entries exist. Reserving ten slots leaves Count at zero; two appends produce Count two.

**Remove under one mutation policy:** A bulk operation owns traversal and mutation, avoiding an invalidated external enumerator. Two entries are removed while the earlier integer snapshot keeps four values.

## Task answers

### Task 1: Predict and explain

Predict Count and Capacity before and after appends.

**Written answer.** `new List<int>(10)` starts with `Count == 0` and `Capacity >= 10`. After `Add(3)` and `Add(5)`, `Count` is 2 and `Capacity` is unchanged, because two entries fit in the reserved buffer.

**Why it is correct.** `Count` is the number of logical entries; `Capacity` is the size of the internal array. The buffer grows only when an `Add` would exceed it, and the exact growth rule is an implementation detail.

**Plausible wrong approach.** Treating capacity as valid positions and reading `values[5]` fails: the indexer checks against `Count`, so it throws `ArgumentOutOfRangeException` even though the buffer has room.

**How to verify.** After the appends add `Check(values.Capacity >= 10, "buffer kept")`, and wrap `_ = values[5];` in a `try` block that must catch `ArgumentOutOfRangeException`.

### Task 2: Guided modification

Replace one existing entry and explain why Count stays constant.

**Written answer.** After the two appends, write `values[1] = 8;`. The list becomes `{ 3, 8 }` and `Count` remains 2.

**Why it is correct.** The indexer setter overwrites a slot that already exists in the range 0 to `Count - 1`; it never adds a slot, so the count cannot change.

**Plausible wrong approach.** `values.Insert(1, 8)` looks like a replacement but shifts 5 to the right, giving `{ 3, 8, 5 }` with `Count` 3. Using `values[2] = 8` to append throws `ArgumentOutOfRangeException` because index 2 equals `Count`.

**How to verify.** Check `values.Count == 2 && values.SequenceEqual(new[] { 3, 8 })`; it passes silently.

### Task 3: Independent construction

Produce a filtered list while preserving the original.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var original = new List<int> { -1, 2, -3, 4 };
List<int> positives = original.Where(value => value > 0).ToList();
Check(positives.SequenceEqual(new[] { 2, 4 }), "filtered copy");
Check(original.Count == 4 && original[0] == -1, "original unchanged");
```

**Observe:** The new list holds 2 and 4 while the original still has four items.

Where reads the source and ToList builds a separate list, so no element of the original is removed.

**Plausible wrong approach.** Dropping `.ToList()` keeps `positives` as a deferred `Where` query over `original`. Nothing is copied: if `original.Add(6)` runs later, the next enumeration of `positives` yields 2, 4 and 6. Calling `original.RemoveAll(value => value <= 0)` instead mutates the source, and the `original unchanged` check throws.

**How to verify.** After building `positives`, add `original.Add(6)` and check `positives.Count == 2`. The materialized list passes; the deferred query version would report 3.

### Task 4: Diagnose a defect

Diagnose removing an entry inside foreach.

**Written answer.** `foreach (int v in values) if (v < 0) values.Remove(v);` removes -1 and then the next `MoveNext` throws `InvalidOperationException` with "Collection was modified". Repair it with `values.RemoveAll(v => v < 0)`, or iterate a snapshot `values.ToArray()` while removing from `values`.

**Why it is correct.** `List<T>` keeps a version number that every structural change increments, and its enumerator compares versions on each step. `RemoveAll` owns traversal and removal together, so no outside enumerator is invalidated.

**Plausible wrong approach.** A forward `for` loop with `RemoveAt(i)` avoids the exception but skips the element after each removal. It happens to work on `{ -1, 2, -3, 4 }` because the negatives are not adjacent, yet on `{ -1, -2, 3 }` it leaves `{ -2, 3 }`.

**How to verify.** Catch `InvalidOperationException` around the original loop and `Check` it was raised. Then check that the repaired code turns `{ -1, -2, 3 }` into `{ 3 }`; that adjacent-negatives fixture exposes the forward-index bug.

### Task 5: Boundary evidence

Test no removals, all removals and an empty list.

**Written answer.** Run `RemoveAll(v => v < 0)` on three fixtures: `{ 1, 2 }` returns 0 and leaves both, `{ -1, -2 }` returns 2 and leaves `Count` 0, and an empty list returns 0 and stays empty.

**Why it is correct.** `RemoveAll` returns how many entries it removed and handles any size, including zero, so asserting both the return value and the remaining sequence pins the behavior at each extreme.

**Plausible wrong approach.** Looping `values.Remove(values.Find(v => v < 0))` breaks on the no-removal case: `Find` returns `default(int)`, which is 0, when nothing matches. On `{ 0, 1 }` that removes a legitimate 0.

**How to verify.** Check the returned counts 0, 2 and 0 and compare each list with `SequenceEqual`. Add `{ 0, 1 }` as a fourth fixture and confirm it is unchanged.

### Task 6: Transfer and justify

Choose mutation or a new sequence for an undoable editor operation and explain who observes the change.

**Written answer.** Treat each edit as producing a new list and push the previous list onto a `Stack<List<string>>`: `history.Push(current); current = new List<string>(current) { "b" };`. Undo is `current = history.Pop();`.

**Why it is correct.** Views holding the old reference keep the version they rendered, and undo restores state by reassignment instead of reversing each mutation. The cost is copying every line on each edit, and if lines were mutable objects the copy would still share them.

**Plausible wrong approach.** Mutating `current` in place and pushing the same reference onto the stack stores an alias, not a history. Undo then pops a list that already contains the edit, so nothing is undone.

**How to verify.** Start from `{ "a" }`, apply the edit, check `current` is `{ "a", "b" }`, undo, and check it is `{ "a" }` again. The aliasing version fails the second check.

## Mechanism and diagnostic reasoning

A List stores a resizable indexed sequence. Count is the number of elements logically present; capacity is storage reserved to reduce reallocations. Increasing capacity does not create valid elements. Append is often efficient, but inserting at the front shifts existing entries. The interface makes these operations equally easy to write while their costs differ.

Enumeration assumes a stable collection structure. Removing items during foreach invalidates that assumption. Choose a bulk removal operation, construct a new result, or use a deliberate index strategy. The right choice depends on whether other parts of the program should observe mutation of the original list.

`new List<int> { ... }` uses a collection initializer. `Add` changes Count; an indexer replaces an existing element. `RemoveAll(predicate)` expresses structural removal as one owned operation. `ToArray` creates a snapshot of the element references or values.

Capacity is not an index boundary. A snapshot of objects still shares those objects. Repeated front insertion can turn an apparently simple loop into quadratic work.

## Review before continuing

Run the reference and confirm that it prints `csharp-009: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
