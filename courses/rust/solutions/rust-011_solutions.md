# rust-011: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-011_solution.rs](rust-011_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Accept arrays and vectors uniformly:** The function requires read access, not a particular allocation strategy. One slice interface accepts several owning representations.

**Separate capacity from logical elements:** The optional lookup exposes absence instead of indexing uninitialized capacity. Reserved storage still contains zero logical elements until push.

## Reason through the six tasks

1. **Predict and explain.** Identify owner, length and borrowed view in each call.

2. **Guided modification.** Use a subslice and predict its total.

3. **Independent construction.** Implement a maximum function accepting a slice and returning Option.

4. **Diagnose a defect.** Diagnose keeping an element reference live across a conflicting vector push.

5. **Boundary evidence.** Test empty, singleton and out-of-range get cases.

6. **Transfer and justify.** Choose an array, Vec or slice for stored state, function input and fixed-size coordinates.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An array has a compile-time length as part of its type. A Vec owns a growable allocation. A slice borrows a contiguous region and carries its length without owning that allocation. Accepting &[T] lets a function read arrays and vectors through one interface.

Vector growth can reallocate storage, which explains why a borrow into a vector cannot remain live while a conflicting push changes its allocation. Capacity reserves room but does not create initialized logical elements. Indexing panics outside the valid range; get returns Option when absence is a normal possibility.

`[i32; 3]` is an array of exactly three integers. `Vec<i32>` owns a variable-length sequence. `&[i32]` is a borrowed slice. len and capacity describe different properties.

Capacity is not a valid index limit. A slice does not extend its owner's lifetime. Avoid accepting &Vec when a slice expresses the actual requirement.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
