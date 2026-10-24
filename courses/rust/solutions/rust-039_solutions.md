# rust-039: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-039_solution.rs](rust-039_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Build an aligned batch:** Names and types are explicit rather than inferred from arbitrary array positions. Two aligned columns form a two-row, two-column batch.

**Reject incompatible lengths:** A batch cannot invent which row a shorter column should align with. Unequal column lengths are rejected.

## Reason through the six tasks

1. **Predict and explain.** State the row grain and schema of the valid batch.

2. **Guided modification.** Add a nullable numeric field with matching length.

3. **Independent construction.** Construct a batch for a small validated inventory dataset.

4. **Diagnose a defect.** Diagnose swapping arrays while retaining the old field order.

5. **Boundary evidence.** Test type mismatch, length mismatch and a zero-row batch.

6. **Transfer and justify.** Design a schema evolution policy that preserves names, units and saved data meaning.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A Schema gives columns names, logical types, nullability and optional metadata. A RecordBatch pairs that schema with arrays representing one batch of rows. The arrays must match the schema types and have compatible lengths. This is a useful executable contract at a data boundary.

A batch is not the entire dataset and does not imply a global uniqueness or ordering guarantee. Several batches can share a schema while representing different chunks. Validate domain rules such as unique IDs separately. A schema mismatch should remain an error rather than being repaired by silently dropping or reordering columns.

Field::new records name, DataType and nullable policy. Schema::new groups fields. RecordBatch::try_new validates arrays against an Arc<Schema>. ArrayRef stores different concrete arrays behind one shared interface.

A nullable field permits nulls; it does not require them. Schema validation does not establish unique keys or domain ranges. Do not infer whole-dataset row count from one batch.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
