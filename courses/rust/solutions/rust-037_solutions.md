# rust-037: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-037_solution.rs](rust-037_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Create a concrete integer column:** The trait supplies common array behavior while the concrete type supplies typed value access. The concrete column contains three non-null integers.

**Use a variable-width text column:** Offsets and UTF-8 data support variable-width values without pretending every row has a fixed-size string slot. Different text lengths share one logical column.

## Task answers

### Task 1: Predict and explain

Identify logical length, type and null count.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The trait supplies common array behavior while the concrete type supplies typed value access. The concrete column contains three non-null integers.

### Task 2: Guided modification

Add a fourth value and inspect its typed access.

No separate reference answer has been written for this task. Start from Example B: Offsets and UTF-8 data support variable-width values without pretending every row has a fixed-size string slot. Different text lengths share one logical column.

### Task 3: Independent construction

Construct paired integer and text columns with equal row counts.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Int32Array, StringArray};
    let names = StringArray::from(vec!["pear", "apple", "fig"]);
    let quantities = Int32Array::from(vec![2, 5, 1]);
    assert_eq!(names.len(), quantities.len());
    assert_eq!(names.value(1), "apple");
    assert_eq!(quantities.value(1), 5);
    Ok(())
}
```

**Observe:** Both columns have 3 rows, and row 1 pairs apple with 5.

Paired columns describe the same rows only when their lengths match, so the length check comes before reading any position.

### Task 4: Diagnose a defect

Diagnose treating Arrow as an automatically installed SQL engine.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Value access at an invalid index still violates bounds. A library being linked does not mean every optional Arrow feature is enabled. Parquet and DataFusion are separate crates and workflows.

### Task 5: Boundary evidence

Test an empty typed array and a non-ASCII string.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Create a concrete integer column) and Example B (Use a variable-width text column).

### Task 6: Transfer and justify

Compare row-object and columnar representations for a repeated analytical scan.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Columnar layout**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Apache Arrow defines a columnar in-memory representation for analytical data. A typed array stores values of one logical type along with validity information and, for variable-width types, offsets and data buffers. This differs from a collection of row objects with independent allocations for every field.

Columnar layout can make scans and vectorized operations efficient, but Arrow is not a database, query optimizer or automatic distributed engine. Its arrays provide a representation and compute building blocks. The prepared Arrow 60 crate is real library code linked into the worker. Begin with typed arrays and the Array trait before using type-erased columns in a RecordBatch.

Int32Array stores signed 32-bit integer values. Importing the Array trait exposes common methods such as len and null_count. StringArray stores variable-width UTF-8 values. ArrayRef later erases concrete type behind Arc<dyn Array>.

Value access at an invalid index still violates bounds. A library being linked does not mean every optional Arrow feature is enabled. Parquet and DataFusion are separate crates and workflows.

## Review before continuing

Run the reference and confirm that it prints `rust-037: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
