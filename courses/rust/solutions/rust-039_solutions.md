# rust-039: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-039_solution.rs](rust-039_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Build an aligned batch:** Names and types are explicit rather than inferred from arbitrary array positions. Two aligned columns form a two-row, two-column batch.

**Reject incompatible lengths:** A batch cannot invent which row a shorter column should align with. Unequal column lengths are rejected.

## Task answers

### Task 1: Predict and explain

State the row grain and schema of the valid batch.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Names and types are explicit rather than inferred from arbitrary array positions. Two aligned columns form a two-row, two-column batch.

### Task 2: Guided modification

Add a nullable numeric field with matching length.

No separate reference answer has been written for this task. Start from Example B: A batch cannot invent which row a shorter column should align with. Unequal column lengths are rejected.

### Task 3: Independent construction

Construct a batch for a small validated inventory dataset.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{ArrayRef, Int32Array, StringArray};
    use arrow::datatypes::{DataType, Field, Schema};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let rows = [("pear", 2), ("apple", -1), ("fig", 4)];
    let valid: Vec<_> = rows.iter().filter(|(_, qty)| *qty >= 0).collect();
    let names: Vec<&str> = valid.iter().map(|(name, _)| *name).collect();
    let quantities: Vec<i32> = valid.iter().map(|(_, qty)| *qty).collect();
    let schema = Schema::new(vec![
        Field::new("name", DataType::Utf8, false),
        Field::new("quantity", DataType::Int32, false),
    ]);
    let columns: Vec<ArrayRef> = vec![
        Arc::new(StringArray::from(names)),
        Arc::new(Int32Array::from(quantities)),
    ];
    let batch = RecordBatch::try_new(Arc::new(schema), columns)?;
    assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));
    Ok(())
}
```

**Observe:** The negative apple row is rejected before construction, leaving a batch of 2 rows and 2 columns.

Validation runs on plain rows first, so the batch only ever holds valid data, and try_new still checks that the columns match the schema.

### Task 4: Diagnose a defect

Diagnose swapping arrays while retaining the old field order.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A nullable field permits nulls; it does not require them. Schema validation does not establish unique keys or domain ranges. Do not infer whole-dataset row count from one batch.

### Task 5: Boundary evidence

Test type mismatch, length mismatch and a zero-row batch.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Build an aligned batch) and Example B (Reject incompatible lengths).

### Task 6: Transfer and justify

Design a schema evolution policy that preserves names, units and saved data meaning.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Schema**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A Schema gives columns names, logical types, nullability and optional metadata. A RecordBatch pairs that schema with arrays representing one batch of rows. The arrays must match the schema types and have compatible lengths. This is a useful executable contract at a data boundary.

A batch is not the entire dataset and does not imply a global uniqueness or ordering guarantee. Several batches can share a schema while representing different chunks. Validate domain rules such as unique IDs separately. A schema mismatch should remain an error rather than being repaired by silently dropping or reordering columns.

Field::new records name, DataType and nullable policy. Schema::new groups fields. RecordBatch::try_new validates arrays against an Arc<Schema>. ArrayRef stores different concrete arrays behind one shared interface.

A nullable field permits nulls; it does not require them. Schema validation does not establish unique keys or domain ranges. Do not infer whole-dataset row count from one batch.

## Review before continuing

Run the reference and confirm that it prints `rust-039: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
