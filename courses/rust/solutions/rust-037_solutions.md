# rust-037: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-037_solution.rs](rust-037_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Create a concrete integer column:** The trait supplies common array behavior while the concrete type supplies typed value access. The concrete column contains three non-null integers.

**Use a variable-width text column:** Offsets and UTF-8 data support variable-width values without pretending every row has a fixed-size string slot. Different text lengths share one logical column.

## Reason through the six tasks

1. **Predict and explain.** Identify logical length, type and null count.

2. **Guided modification.** Add a fourth value and inspect its typed access.

3. **Independent construction.** Construct paired integer and text columns with equal row counts.

4. **Diagnose a defect.** Diagnose treating Arrow as an automatically installed SQL engine.

5. **Boundary evidence.** Test an empty typed array and a non-ASCII string.

6. **Transfer and justify.** Compare row-object and columnar representations for a repeated analytical scan.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Apache Arrow defines a columnar in-memory representation for analytical data. A typed array stores values of one logical type along with validity information and, for variable-width types, offsets and data buffers. This differs from a collection of row objects with independent allocations for every field.

Columnar layout can make scans and vectorized operations efficient, but Arrow is not a database, query optimizer or automatic distributed engine. Its arrays provide a representation and compute building blocks. The prepared Arrow 60 crate is real library code linked into the worker. Begin with typed arrays and the Array trait before using type-erased columns in a RecordBatch.

Int32Array stores signed 32-bit integer values. Importing the Array trait exposes common methods such as len and null_count. StringArray stores variable-width UTF-8 values. ArrayRef later erases concrete type behind Arc<dyn Array>.

Value access at an invalid index still violates bounds. A library being linked does not mean every optional Arrow feature is enabled. Parquet and DataFusion are separate crates and workflows.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
