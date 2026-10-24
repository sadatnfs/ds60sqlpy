# swift-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-009_solution.swift](swift-009_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Mutate an independent array value:** The language contract concerns observable behavior even if storage was initially shared. Appending to the copy leaves the original unchanged.

**Do not confuse capacity and count:** Capacity is a performance hint, not an index range. Reserving twenty slots creates no logical elements.

## Reason through the six tasks

1. **Predict and explain.** Predict original and changed arrays after append.

2. **Guided modification.** Replace an element in the copy and retain the original.

3. **Independent construction.** Build a filtered array without changing the source.

4. **Diagnose a defect.** Diagnose indexing a reserved but still empty array.

5. **Boundary evidence.** Test an empty slice and a slice whose startIndex is not zero.

6. **Transfer and justify.** Explain what changes when array elements are mutable class instances.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Swift arrays are value types. Assigning an array produces a value that behaves independently when later mutated. The implementation can share backing storage until a write requires separation, a strategy called copy-on-write. The semantic promise is independent values, not a guarantee that every assignment immediately copies all bytes.

An array of class references still contains references as its element values. Copying the array separates its sequence structure but does not clone every referenced object. Keep that distinction in mind when building snapshots or undo history. Capacity is storage preparation and does not change the count of present elements.

`[Int]` is an array type. append grows logical count; an index replaces an existing element. reserveCapacity prepares storage. ArraySlice may preserve original indices, so use its indices rather than assuming zero.

Array value semantics do not recursively clone objects. Never assume ArraySlice starts at index zero. Repeated insertions at the front can create quadratic work.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
