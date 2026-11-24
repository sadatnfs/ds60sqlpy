# rust-037: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-037_solution.rs](rust-037_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Create a concrete integer column:** The trait supplies common array behavior while the concrete type supplies typed value access. The concrete column contains three non-null integers.

**Use a variable-width text column:** Offsets and UTF-8 data support variable-width values without pretending every row has a fixed-size string slot. Different text lengths share one logical column.

## Task answers

### Task 1: Predict and explain

Identify logical length, type and null count.

**Written answer.** Example A's column has logical length 3 (`len()`), data type `Int32` (from `data_type()`, fixed by the concrete `Int32Array`), and null count 0. Example B's `labels` also has length 3 and null count 0, but its type is `Utf8`, which is variable width: `len()` counts rows, not bytes, so the row `"é"` counts as one entry while it stores two UTF-8 bytes.

**Why it is correct.** Length, type and null count are the metadata every `Array` exposes through the trait, before any typed value access, so they are the first checks when a column is handed over.

**Plausible wrong approach.** Reading `null_count() == 0` as proof that all values are meaningful mixes validity with domain rules: a non-null 0 or an empty string is still present.

**How to verify.** Assert `values.data_type() == &arrow::datatypes::DataType::Int32` and `labels.data_type() == &arrow::datatypes::DataType::Utf8` next to the existing length assertions.

### Task 2: Guided modification

Add a fourth value and inspect its typed access.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Int32Array};
    let values = Int32Array::from(vec![2, 4, 6, 8]);
    assert_eq!(values.len(), 4);
    let fourth: i32 = values.value(3);
    assert_eq!(fourth, 8);
    assert!(values.is_valid(3));
    assert_eq!(values.values().iter().sum::<i32>(), 20);
    Ok(())
}
```

**Observe:** The column has four rows; index 3 returns the plain i32 8, which is valid, and the four values sum to 20.

`Int32Array::value` returns an `i32` directly because the concrete type is known, with no casting or `Option`. It does not check validity, which is why the `is_valid` assertion comes next; for a column with nulls, `iter()` returns `Option<i32>` instead.

**Plausible wrong approach.** Calling `values.value(4)` to reach the fourth value uses a one-based index and panics, because index 4 is past the end of a four-row array.

**How to verify.** Run the block. Then change `value(3)` to `value(4)` and read the out-of-bounds panic.

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

**Written answer.** The defect is writing something like `use arrow::sql::query;` or expecting `SELECT name FROM batch` to run after linking Arrow. rustc rejects the import with E0432, unresolved import, because the arrow crate has no SQL module. Arrow supplies arrays, schemas, record batches and compute kernels; a SQL planner and executor such as DataFusion is a separate crate that would need its own deliberate dependency setup.

**Why it is correct.** Arrow standardizes the in-memory columnar format. Query parsing, planning and optimization sit in a layer above it, so selection is written with kernels such as `filter` and `take`.

**Plausible wrong approach.** Assuming the classroom omitted a feature flag and that enabling `sql` would fix it sends the learner looking for an option that does not exist.

**How to verify.** Compile `use arrow::sql::query;` in the pad and read E0432. Then express the same selection with `arrow::compute::filter` as in chapter 40.

### Task 5: Boundary evidence

Test an empty typed array and a non-ASCII string.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Int32Array, StringArray};
    let empty = Int32Array::from(Vec::<i32>::new());
    assert_eq!((empty.len(), empty.null_count()), (0, 0));
    assert!(empty.is_empty());
    assert_eq!(empty.iter().count(), 0);
    let labels = StringArray::from(vec!["é", "日本", "a"]);
    assert_eq!(labels.len(), 3);
    assert_eq!(labels.value(0), "é");
    assert_eq!(
        (labels.value(0).len(), labels.value(0).chars().count()),
        (2, 1)
    );
    assert_eq!(
        (labels.value_length(1), labels.value(1).chars().count()),
        (6, 2)
    );
    Ok(())
}
```

**Observe:** The empty column has length 0, no nulls and nothing to iterate. The text column keeps é and 日本 intact; é is 2 bytes and 1 character, 日本 is 6 bytes and 2 characters.

An empty array is a valid column with zero rows, not an error. For text, `value` returns a `&str` slice of UTF-8 bytes chosen by the offsets, so `value_length` and `str::len` count bytes while `chars().count()` counts characters.

**Plausible wrong approach.** Using `value_length` as a character count reports 6 for 日本, which breaks a length limit stated in characters.

**How to verify.** Run the block. Add `empty.value(0);` and the access panics, because an empty array has no index 0.

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
