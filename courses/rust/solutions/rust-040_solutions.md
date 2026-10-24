# rust-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-040_solution.rs](rust-040_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Filter with an explicit mask:** The mask expresses one admission decision for every original position. Filtering retains two and six in input order.

**Reorder and repeat with take:** A selected row can appear more than once, so cardinality and aggregation assumptions need review. Take repeats and reorders values according to the index sequence.

## Reason through the six tasks

1. **Predict and explain.** Predict row count and order for both operations.

2. **Guided modification.** Change one mask value and independently derive the result.

3. **Independent construction.** Filter every column of a batch consistently under one row mask.

4. **Diagnose a defect.** Diagnose filtering one column while leaving others unfiltered.

5. **Boundary evidence.** Test empty selection, all-selected rows and checked invalid indices.

6. **Transfer and justify.** Choose filter or take for a sampling procedure and explain duplicate-row consequences.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Arrow compute kernels operate on arrays while respecting their logical representation. A Boolean mask selects rows; take selects positions by an index array. These are different operations with different output ordering. Filtering normally preserves the order of admitted rows, while take can repeat or reorder positions.

Type erasure means a kernel can return ArrayRef. Inspect or validate the logical type before downcasting to a concrete array. An unwrap can be justified only by a nearby known kernel/type contract in a controlled fixture. Production generic code should return a useful error for an unexpected type. Preserve null and index bounds policies explicitly.

compute::filter accepts an array and BooleanArray mask. compute::take selects by integer indices. as_any().downcast_ref recovers a known concrete array after the type contract has been established.

Downcast failure is possible in generic code. A mask and array must have compatible lengths. A kernel result does not establish a domain-level ordering guarantee unless the operation contract does.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
