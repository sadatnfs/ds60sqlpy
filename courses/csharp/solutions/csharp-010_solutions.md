# csharp-010: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-010_solution.cs](csharp-010_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve absence information:** The comparer belongs to the collection contract. A missing value cannot be inferred from the integer alone. OAK finds a present zero; Pine is absent.

**Deduplicate by an explicit policy:** Deduplication is meaningful only after defining equality. Case-insensitive comparison is appropriate for this fixture, not for every identifier. RED is a duplicate under the selected comparer.

## Reason through the six tasks

1. **Predict and explain.** Predict the difference between absent Pine and present-zero Oak.

2. **Guided modification.** Switch to an ordinal case-sensitive comparer and explain the changed lookup.

3. **Independent construction.** Build a frequency dictionary from a list of tags.

4. **Diagnose a defect.** Diagnose indexing a missing key without an absence policy.

5. **Boundary evidence.** Test empty tags, repeated tags and keys differing only by case.

6. **Transfer and justify.** Design stable identity for records and explain which fields may change without invalidating lookup.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A dictionary maps unique keys to values. A set represents membership without duplicates. Their behavior depends on equality and hashing: values considered equal must have compatible hash codes. Choosing a string comparer is therefore a data-model decision, not just a search convenience. Machine identifiers may be case-sensitive or case-insensitive depending on the contract.

A missing key is different from a present key holding a default value. Use TryGetValue when absence is expected. Sorting output separately from lookup makes demonstrations deterministic without claiming that dictionary iteration order is the business ordering. If order matters, encode that requirement explicitly.

`Dictionary<string,int>(StringComparer.OrdinalIgnoreCase)` defines key identity. `TryGetValue(key, out value)` separates absence from a stored zero. `HashSet<T>.Add` returns whether membership changed.

Changing a key field after insertion can break hash-based lookup for mutable custom keys. Distinct text spellings are not always distinct identities. Do not rely on incidental traversal order for reports.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
