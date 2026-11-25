# rust-039: Schemas, fields and RecordBatch invariants

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-038`

## Learning objectives

Build RecordBatches whose schema and column lengths are checked at construction. The central exercise is task 3: Construct a batch for a small validated inventory dataset.

## Purpose and mental model

A Schema gives columns names, logical types, nullability and optional metadata. A RecordBatch pairs that schema with arrays representing one batch of rows. The arrays must match the schema types and have compatible lengths. This is a useful executable contract at a data boundary.

A batch is not the entire dataset and does not imply a global uniqueness or ordering guarantee. Several batches can share a schema while representing different chunks. Validate domain rules such as unique IDs separately. A schema mismatch should remain an error rather than being repaired by silently dropping or reordering columns.

## Vocabulary and concepts

**Schema:** A contract for column names, types and nullability.

**RecordBatch:** Equal-length columns representing one batch of rows.

**ArrayRef:** Shared ownership of a type-erased Arrow array.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array`, `arrow::datatypes`, `arrow::record_batch` and `std::sync`. A passing run prints `rust-039: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Field::new records name, DataType and nullable policy. Schema::new groups fields. RecordBatch::try_new validates arrays against an Arc<Schema>. ArrayRef stores different concrete arrays behind one shared interface.

**Reading Example A (Build an aligned batch, code below).** `Field::new("name", DataType::Utf8, false)` declares one column: its name, its Arrow type and whether it may contain nulls. `Schema::new` collects the fields in order, and `Arc::new` wraps the schema so many batches can share it cheaply. The `columns` vector holds `ArrayRef` values, which are `Arc<dyn Array>`: each concrete array sits behind a shared trait object, so arrays of different types fit in one vector. `RecordBatch::try_new` validates the pairing of schema and columns and returns a `Result`, and `?` propagates a mismatch as an error. The last line reads the first column back: `as_any().downcast_ref::<StringArray>()` recovers the concrete type from the trait object and would return `None` if the type were wrong.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Build an aligned batch

Names and types are explicit rather than inferred from arbitrary array positions.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use arrow::array::{ArrayRef, Int32Array, StringArray};
        use arrow::datatypes::{DataType, Field, Schema};
        use arrow::record_batch::RecordBatch;
        let schema = Arc::new(Schema::new(vec![Field::new("name", DataType::Utf8, false), Field::new("quantity", DataType::Int32, false)]));
        let columns: Vec<ArrayRef> = vec![Arc::new(StringArray::from(vec!["pear", "apple"])), Arc::new(Int32Array::from(vec![2, 3]))];
        let batch = RecordBatch::try_new(schema, columns)?;
        assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));
        assert_eq!(batch.column(0).as_any().downcast_ref::<arrow::array::StringArray>().unwrap().value(0), "pear");
    }
    println!("rust-039: passed");
    Ok(())
}
```

**Observe:** Two aligned columns form a two-row, two-column batch.

### Example B: Reject incompatible lengths

A batch cannot invent which row a shorter column should align with.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use arrow::array::{ArrayRef, Int32Array};
        use arrow::datatypes::{DataType, Field, Schema};
        use arrow::record_batch::RecordBatch;
        let schema = Arc::new(Schema::new(vec![Field::new("a", DataType::Int32, false), Field::new("b", DataType::Int32, false)]));
        let columns: Vec<ArrayRef> = vec![Arc::new(Int32Array::from(vec![1, 2])), Arc::new(Int32Array::from(vec![3]))];
        assert!(RecordBatch::try_new(schema, columns).is_err());
    }
    println!("rust-039: passed");
    Ok(())
}
```

**Observe:** Unequal column lengths are rejected.

## Exercises

1. **Predict and explain.** State the row grain and schema of the valid batch.

2. **Guided modification.** Add a nullable numeric field with matching length.

3. **Independent construction.** Construct a batch for a small validated inventory dataset.

4. **Diagnose a defect.** Diagnose swapping arrays while retaining the old field order.

5. **Boundary evidence.** Test type mismatch, length mismatch and a zero-row batch.

6. **Transfer and justify.** Design a schema evolution policy that preserves names, units and saved data meaning.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A nullable field permits nulls; it does not require them. Schema validation does not establish unique keys or domain ranges. Do not infer whole-dataset row count from one batch.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Build an aligned batch) before changing anything, and confirm its observation: Two aligned columns form a two-row, two-column batch.
2. Compare Example B (Reject incompatible lengths) with Example A and name the first line whose behavior differs. Its observation is: Unequal column lengths are rejected.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A nullable field permits nulls; it does not require them.

Tempting approaches to rule out before you compare:

- **Task 1.** Calling this batch the inventory reads more into it than it says: it is one two-row chunk, and nothing in it proves that names are unique or that there are no other batches.
- **Task 2.** Declaring `price` as non-nullable while the array contains a null fails `try_new` with an error that the column is declared non-nullable but contains a null.
- **Task 5.** Treating the zero-row batch as an error, or skipping its schema, loses the column definitions a later empty result still needs.

## Self-check and next step

What `num_rows()` and `num_columns()` does Example A's batch report, and where does "pear" appear? What error does `RecordBatch::try_new` return in Example B, and why is rejecting it better than padding the shorter column with nulls? Why does a field's `nullable` flag belong in the schema rather than in a comment?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `RecordBatch` documentation](https://docs.rs/arrow/60.0.0/arrow/record_batch/struct.RecordBatch.html) for the checks `try_new` performs.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-039: Schemas, fields and RecordBatch invariants.
Read courses/rust/guides/rust-039.md and courses/rust/lessons/rust-039.rs. Prerequisites: rust-038.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-039_solution.rs and
courses/rust/solutions/rust-039_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
