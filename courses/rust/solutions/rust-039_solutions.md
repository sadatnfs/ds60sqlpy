# rust-039: explanation and comparison

Executable reference: [rust-039_solution.rs](rust-039_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Build an aligned batch:** Names and types are explicit rather than inferred from arbitrary array positions. Two aligned columns form a two-row, two-column batch.

**Reject incompatible lengths:** A batch cannot invent which row a shorter column should align with. Unequal column lengths are rejected.

## Task answers

### Task 1: Predict and explain

State the row grain and schema of the valid batch.

**Written answer.** The row grain of Example A's batch is one product line: each row pairs a `name` with its `quantity`, and there are two rows, pear with 2 and apple with 3. The schema has two fields in order, `name` of type `Utf8` and `quantity` of type `Int32`, both non-nullable. Column 0 is therefore always the names, which is what the downcast to `StringArray` relies on.

**Why it is correct.** The schema is the contract that gives each position a name, a type and a nullability rule. Without it the two arrays are just a list of columns with no meaning attached.

**Plausible wrong approach.** Calling this batch the inventory reads more into it than it says: it is one two-row chunk, and nothing in it proves that names are unique or that there are no other batches.

**How to verify.** Print `batch.schema()` and check the field names, types and `nullable: false` against your description.

### Task 2: Guided modification

Add a nullable numeric field with matching length.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, ArrayRef, Float64Array, Int32Array, StringArray};
    use arrow::datatypes::{DataType, Field, Schema};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let schema = Arc::new(Schema::new(vec![
        Field::new("name", DataType::Utf8, false),
        Field::new("quantity", DataType::Int32, false),
        Field::new("price", DataType::Float64, true),
    ]));
    let columns: Vec<ArrayRef> = vec![
        Arc::new(StringArray::from(vec!["pear", "apple"])),
        Arc::new(Int32Array::from(vec![2, 3])),
        Arc::new(Float64Array::from(vec![Some(1.25), None])),
    ];
    let batch = RecordBatch::try_new(schema, columns)?;
    assert_eq!((batch.num_rows(), batch.num_columns()), (2, 3));
    assert!(batch.schema().field(2).is_nullable());
    assert_eq!(batch.column(2).null_count(), 1);
    Ok(())
}
```

**Observe:** The batch has two rows and three columns, the price field is nullable, and its column holds one null.

The new array has the same two rows, so `try_new` accepts it, and the nullable field allows apple's unknown price to be stored as a null instead of a made-up 0.0.

**Plausible wrong approach.** Declaring `price` as non-nullable while the array contains a null fails `try_new` with an error that the column is declared non-nullable but contains a null.

**How to verify.** Run the block. Change the price field's flag to `false` and `try_new` returns that error.

### Task 3: Independent construction

Construct a batch for a small validated inventory dataset.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is reordering the `columns` vector, for example to quantity first and name second, while the schema still lists `name` then `quantity`. When the types differ, `try_new` returns an error that column types must match the schema, expected Utf8 but found Int32 at column index 0. When the types match, such as two `Int32` fields `quantity` and `price`, the swap is accepted and every row carries quantities under the price label. Build each column next to its field, or use `RecordBatch::try_from_iter` with explicit name and array pairs.

**Why it is correct.** A batch binds columns to fields by position only. Arrow can catch a type mismatch, but it cannot know that two same-typed arrays have been swapped.

**Plausible wrong approach.** Relying on `try_new` returning `Ok` as proof that the columns are in the right order misses exactly the same-type swap.

**How to verify.** Swap two `Int32` columns under fields `quantity` and `price`, build the batch, and read the column called `price`: it holds the quantities.

### Task 5: Boundary evidence

Test type mismatch, length mismatch and a zero-row batch.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{ArrayRef, Int32Array, StringArray};
    use arrow::datatypes::{DataType, Field, Schema};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let schema = Arc::new(Schema::new(vec![
        Field::new("name", DataType::Utf8, false),
        Field::new("quantity", DataType::Int32, false),
    ]));
    let wrong_type: Vec<ArrayRef> = vec![
        Arc::new(StringArray::from(vec!["pear"])),
        Arc::new(StringArray::from(vec!["2"])),
    ];
    assert!(RecordBatch::try_new(schema.clone(), wrong_type).is_err());
    let wrong_length: Vec<ArrayRef> = vec![
        Arc::new(StringArray::from(vec!["pear", "fig"])),
        Arc::new(Int32Array::from(vec![2])),
    ];
    assert!(RecordBatch::try_new(schema.clone(), wrong_length).is_err());
    let no_rows: Vec<ArrayRef> = vec![
        Arc::new(StringArray::from(Vec::<&str>::new())),
        Arc::new(Int32Array::from(Vec::<i32>::new())),
    ];
    let empty = RecordBatch::try_new(schema.clone(), no_rows)?;
    assert_eq!((empty.num_rows(), empty.num_columns()), (0, 2));
    assert_eq!(empty.schema(), schema);
    Ok(())
}
```

**Observe:** A text array under the Int32 field and a one-row column beside a two-row column are both rejected; the zero-row batch is accepted and keeps both columns and the full schema.

Type and length checks are the structural invariants `try_new` enforces, so both broken inputs return errors instead of a coerced or truncated batch. Zero rows breaks neither invariant, and the schema still describes what a nonempty batch would contain.

**Plausible wrong approach.** Treating the zero-row batch as an error, or skipping its schema, loses the column definitions a later empty result still needs.

**How to verify.** Run the block. Print the two errors with `{:?}` to see the type and length messages separately.

### Task 6: Transfer and justify

Design a schema evolution policy that preserves names, units and saved data meaning.

**Judging criteria.** A strong policy allows only additive changes by default: a new nullable field may be appended, while renaming a field, changing its type or changing its unit requires a new field name and a migration. Units live in field metadata, such as `unit=ms`, and the schema carries a version. Readers of old data supply nulls for new fields and never reinterpret saved values. Test it by reading a batch written under the old schema with the new code. State one limitation: Arrow does not enforce metadata, so the reader needs its own check.

## Mechanism and diagnostic reasoning

A Schema gives columns names, logical types, nullability and optional metadata. A RecordBatch pairs that schema with arrays representing one batch of rows. The arrays must match the schema types and have compatible lengths. This is a useful executable contract at a data boundary.

A batch is not the entire dataset and does not imply a global uniqueness or ordering guarantee. Several batches can share a schema while representing different chunks. Validate domain rules such as unique IDs separately. A schema mismatch should remain an error rather than being repaired by silently dropping or reordering columns.

Field::new records name, DataType and nullable policy. Schema::new groups fields. RecordBatch::try_new validates arrays against an Arc<Schema>. ArrayRef stores different concrete arrays behind one shared interface.

A nullable field permits nulls; it does not require them. Schema validation does not establish unique keys or domain ranges. Do not infer whole-dataset row count from one batch.

## Review before continuing

Rebuild Example B (Reject incompatible lengths) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
