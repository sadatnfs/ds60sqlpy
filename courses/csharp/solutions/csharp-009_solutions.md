# csharp-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-009_solution.cs](csharp-009_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Separate count from reserved storage:** Capacity is an implementation resource, not a promise that ten logical entries exist. Reserving ten slots leaves Count at zero; two appends produce Count two.

**Remove under one mutation policy:** A bulk operation owns traversal and mutation, avoiding an invalidated external enumerator. Two entries are removed while the earlier integer snapshot keeps four values.

## Reason through the six tasks

1. **Predict and explain.** Predict Count and Capacity before and after appends.

2. **Guided modification.** Replace one existing entry and explain why Count stays constant.

3. **Independent construction.** Produce a filtered list while preserving the original.

4. **Diagnose a defect.** Diagnose removing an entry inside foreach.

5. **Boundary evidence.** Test no removals, all removals and an empty list.

6. **Transfer and justify.** Choose mutation or a new sequence for an undoable editor operation and explain who observes the change.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A List stores a resizable indexed sequence. Count is the number of elements logically present; capacity is storage reserved to reduce reallocations. Increasing capacity does not create valid elements. Append is often efficient, but inserting at the front shifts existing entries. The interface makes these operations equally easy to write while their costs differ.

Enumeration assumes a stable collection structure. Removing items during foreach invalidates that assumption. Choose a bulk removal operation, construct a new result, or use a deliberate index strategy. The right choice depends on whether other parts of the program should observe mutation of the original list.

`new List<int> { ... }` uses a collection initializer. `Add` changes Count; an indexer replaces an existing element. `RemoveAll(predicate)` expresses structural removal as one owned operation. `ToArray` creates a snapshot of the element references or values.

Capacity is not an index boundary. A snapshot of objects still shares those objects. Repeated front insertion can turn an apparently simple loop into quadratic work.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
