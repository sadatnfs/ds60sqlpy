# csharp-010: explanation and comparison

Reference program: [csharp-010_solution.cs](csharp-010_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Preserve absence information:** The comparer belongs to the collection contract. A missing value cannot be inferred from the integer alone. OAK finds a present zero; Pine is absent.

**Deduplicate by an explicit policy:** Deduplication is meaningful only after defining equality. Case-insensitive comparison is appropriate for this fixture, not for every identifier. RED is a duplicate under the selected comparer.

## Task answers

### Task 1: Predict and explain

Predict the difference between absent Pine and present-zero Oak.

**Written answer.** `TryGetValue("OAK", out int zero)` returns true with 0, because the `OrdinalIgnoreCase` comparer matches the stored `Oak`. `TryGetValue("Pine", out _)` returns false and its out value is also 0. Only the Boolean result separates them.

**Why it is correct.** `TryGetValue` reports presence through its return value and sets the out parameter to `default` when the key is absent, so the integer by itself cannot carry absence.

**Plausible wrong approach.** Comparing `counts.GetValueOrDefault("Pine")` with 0 treats a missing tree as a counted tree with zero sightings. Indexing `counts["Pine"]` instead throws `KeyNotFoundException`.

**How to verify.** Add `Check(counts.ContainsKey("OAK") && !counts.ContainsKey("Pine"), "presence")` and `Check(counts.GetValueOrDefault("Pine") == counts["Oak"], "same zero")`; both pass, showing the value alone hides the difference.

### Task 2: Guided modification

Switch to an ordinal case-sensitive comparer and explain the changed lookup.

**Written answer.** Construct the dictionary with `StringComparer.Ordinal`. The lookup for `OAK` now returns false, so look up `Oak` for the present zero and add `Check(!counts.TryGetValue("OAK", out _), "case matters")`.

**Why it is correct.** The comparer supplies both hashing and equality for keys. Ordinal comparison matches exact UTF-16 code units, so `OAK` and `Oak` are different keys under it.

**Plausible wrong approach.** Normalizing only the lookup with `"oak".ToUpper()` still searches for `OAK` while the stored key is `Oak`. The entry looks lost, although the dictionary is behaving exactly as the ordinal comparer specifies.

**How to verify.** Run with both checks: the present zero is found under `Oak`, `OAK` is absent, and `counts.Count` is still 1.

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

**Plausible wrong approach.** `counts[tag]++` without a prior entry throws `KeyNotFoundException` on the first `red`, because the indexer getter runs before the increment. Calling `counts.Add(tag, 1)` for every tag throws `ArgumentException` on the second `red`.

**How to verify.** The block checks red 2, blue 1 and two entries. Append `"Red"` to `tags`: under `StringComparer.Ordinal` the count becomes 3 entries, which confirms the stated identity policy.

### Task 4: Diagnose a defect

Diagnose indexing a missing key without an absence policy.

**Written answer.** `int n = counts["Pine"];` throws `KeyNotFoundException` because the indexer getter requires the key to exist. Choose a policy: `TryGetValue` when absence is expected, `GetValueOrDefault` only when a missing tag truly means a count of 0, or let the exception stand when absence means corrupted input.

**Why it is correct.** Each policy states what absence means instead of relying on whatever the indexer happens to do. `TryGetValue` costs one lookup and keeps presence and value separate.

**Plausible wrong approach.** Wrapping the indexer in `try { n = counts[key]; } catch { n = 0; }` makes absence look like a zero count, and the bare `catch` also swallows unrelated failures such as the `ArgumentNullException` a null key raises.

**How to verify.** Catch `KeyNotFoundException` from the unguarded indexer and `Check` it occurred, then check that the `TryGetValue` version returns false for `Pine` with no exception.

### Task 5: Boundary evidence

Test empty tags, repeated tags and keys differing only by case.

**Written answer.** Feed the frequency loop three fixtures: an empty array gives `counts.Count == 0`; `{ "red", "red", "red" }` gives `red` 3 with one entry; `{ "red", "Red" }` gives two entries under `Ordinal` and one entry with count 2 under `OrdinalIgnoreCase`.

**Why it is correct.** The loop creates an entry only on a key's first sighting, and the comparer alone decides whether `red` and `Red` are that same key.

**Plausible wrong approach.** Expecting the case variants to merge regardless of comparer makes `counts["red"] == 2` fail under `Ordinal`. Under `OrdinalIgnoreCase`, expecting the stored key to read `Red` is also wrong: the dictionary keeps the first spelling, `red`.

**How to verify.** Check each count and `counts.Keys.Single() == "red"` for the case-insensitive fixture; all checks pass silently.

### Task 6: Transfer and justify

Design stable identity for records and explain which fields may change without invalidating lookup.

**Written answer.** Give each customer an immutable surrogate key, such as a `Guid Id` assigned at creation, and store records in `Dictionary<Guid, Customer>`. Fields such as `Email` and `DisplayName` may change without touching the key.

**Why it is correct.** A hash table places an entry by the key's hash at insertion. If the key never changes, the bucket stays correct for the record's lifetime. The limitation is that the id must exist before insertion and must never be reused.

**Plausible wrong approach.** Putting the records themselves in a `HashSet<Customer>`, where `record Customer(Guid Id, string Email)` compares every property, breaks on an email change: `customer with { Email = "new@x.test" }` is a different value and `set.Contains(updated)` is false.

**How to verify.** Insert a customer, update its email with `with`, and check `byId.ContainsKey(updated.Id)` is true while `set.Contains(updated)` is false.

## Mechanism and diagnostic reasoning

A dictionary maps unique keys to values. A set represents membership without duplicates. Their behavior depends on equality and hashing: values considered equal must have compatible hash codes. Choosing a string comparer is therefore a data-model decision, not just a search convenience. Machine identifiers may be case-sensitive or case-insensitive depending on the contract.

A missing key is different from a present key holding a default value. Use TryGetValue when absence is expected. Sorting output separately from lookup makes demonstrations deterministic without claiming that dictionary iteration order is the business ordering. If order matters, encode that requirement explicitly.

`Dictionary<string,int>(StringComparer.OrdinalIgnoreCase)` defines key identity. `TryGetValue(key, out value)` separates absence from a stored zero. `HashSet<T>.Add` returns whether membership changed.

Changing a key field after insertion can break hash-based lookup for mutable custom keys. Distinct text spellings are not always distinct identities. Do not rely on incidental traversal order for reports.

## Review before continuing

Run the reference and confirm it prints `csharp-010: passed`, then rerun the guide's counterexample.
