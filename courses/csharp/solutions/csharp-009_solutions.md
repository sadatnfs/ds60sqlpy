# csharp-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-009_solution.cs](csharp-009_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Separate count from reserved storage:** Capacity is an implementation resource, not a promise that ten logical entries exist. Reserving ten slots leaves Count at zero; two appends produce Count two.

**Remove under one mutation policy:** A bulk operation owns traversal and mutation, avoiding an invalidated external enumerator. Two entries are removed while the earlier integer snapshot keeps four values.

## Task answers

### Task 1: Predict and explain

Predict Count and Capacity before and after appends.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Capacity is an implementation resource, not a promise that ten logical entries exist. Reserving ten slots leaves Count at zero; two appends produce Count two.

### Task 2: Guided modification

Replace one existing entry and explain why Count stays constant.

No separate reference answer has been written for this task. Start from Example B: A bulk operation owns traversal and mutation, avoiding an invalidated external enumerator. Two entries are removed while the earlier integer snapshot keeps four values.

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

### Task 4: Diagnose a defect

Diagnose removing an entry inside foreach.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Capacity is not an index boundary. A snapshot of objects still shares those objects. Repeated front insertion can turn an apparently simple loop into quadratic work.

### Task 5: Boundary evidence

Test no removals, all removals and an empty list.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Separate count from reserved storage) and Example B (Remove under one mutation policy).

### Task 6: Transfer and justify

Choose mutation or a new sequence for an undoable editor operation and explain who observes the change.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Count**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A List stores a resizable indexed sequence. Count is the number of elements logically present; capacity is storage reserved to reduce reallocations. Increasing capacity does not create valid elements. Append is often efficient, but inserting at the front shifts existing entries. The interface makes these operations equally easy to write while their costs differ.

Enumeration assumes a stable collection structure. Removing items during foreach invalidates that assumption. Choose a bulk removal operation, construct a new result, or use a deliberate index strategy. The right choice depends on whether other parts of the program should observe mutation of the original list.

`new List<int> { ... }` uses a collection initializer. `Add` changes Count; an indexer replaces an existing element. `RemoveAll(predicate)` expresses structural removal as one owned operation. `ToArray` creates a snapshot of the element references or values.

Capacity is not an index boundary. A snapshot of objects still shares those objects. Repeated front insertion can turn an apparently simple loop into quadratic work.

## Review before continuing

Run the reference and confirm that it prints `csharp-009: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
