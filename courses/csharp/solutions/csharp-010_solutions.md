# csharp-010: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-010_solution.cs](csharp-010_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve absence information:** The comparer belongs to the collection contract. A missing value cannot be inferred from the integer alone. OAK finds a present zero; Pine is absent.

**Deduplicate by an explicit policy:** Deduplication is meaningful only after defining equality. Case-insensitive comparison is appropriate for this fixture, not for every identifier. RED is a duplicate under the selected comparer.

## Task answers

### Task 1: Predict and explain

Predict the difference between absent Pine and present-zero Oak.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The comparer belongs to the collection contract. A missing value cannot be inferred from the integer alone. OAK finds a present zero; Pine is absent.

### Task 2: Guided modification

Switch to an ordinal case-sensitive comparer and explain the changed lookup.

No separate reference answer has been written for this task. Start from Example B: Deduplication is meaningful only after defining equality. Case-insensitive comparison is appropriate for this fixture, not for every identifier. RED is a duplicate under the selected comparer.

### Task 3: Independent construction

Build a frequency dictionary from a list of tags.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string[] tags = { "red", "blue", "red" };
var counts = new Dictionary<string, int>(StringComparer.Ordinal);
foreach (string tag in tags) {
  counts.TryGetValue(tag, out int before);
  counts[tag] = before + 1;
}
Check(counts["red"] == 2 && counts["blue"] == 1, "frequencies");
Check(counts.Count == 2, "one entry per distinct tag");
```

**Observe:** red counts 2 and blue counts 1.

TryGetValue reads an absent tag as 0 before the increment, and the explicit ordinal comparer documents the identity policy.

### Task 4: Diagnose a defect

Diagnose indexing a missing key without an absence policy.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Changing a key field after insertion can break hash-based lookup for mutable custom keys. Distinct text spellings are not always distinct identities. Do not rely on incidental traversal order for reports.

### Task 5: Boundary evidence

Test empty tags, repeated tags and keys differing only by case.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Preserve absence information) and Example B (Deduplicate by an explicit policy).

### Task 6: Transfer and justify

Design stable identity for records and explain which fields may change without invalidating lookup.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Key**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A dictionary maps unique keys to values. A set represents membership without duplicates. Their behavior depends on equality and hashing: values considered equal must have compatible hash codes. Choosing a string comparer is therefore a data-model decision, not just a search convenience. Machine identifiers may be case-sensitive or case-insensitive depending on the contract.

A missing key is different from a present key holding a default value. Use TryGetValue when absence is expected. Sorting output separately from lookup makes demonstrations deterministic without claiming that dictionary iteration order is the business ordering. If order matters, encode that requirement explicitly.

`Dictionary<string,int>(StringComparer.OrdinalIgnoreCase)` defines key identity. `TryGetValue(key, out value)` separates absence from a stored zero. `HashSet<T>.Add` returns whether membership changed.

Changing a key field after insertion can break hash-based lookup for mutable custom keys. Distinct text spellings are not always distinct identities. Do not rely on incidental traversal order for reports.

## Review before continuing

Run the reference and confirm that it prints `csharp-010: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
