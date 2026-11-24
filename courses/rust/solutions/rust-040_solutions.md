# rust-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-040_solution.rs](rust-040_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Filter with an explicit mask:** The mask expresses one admission decision for every original position. Filtering retains two and six in input order.

**Reorder and repeat with take:** A selected row can appear more than once, so cardinality and aggregation assumptions need review. Take repeats and reorders values according to the index sequence.

## Task answers

### Task 1: Predict and explain

Predict row count and order for both operations.

**Written answer.** `filter` returns one output row for each true mask position, in input order, so Example A produces 2 rows, 2 then 6. `take` returns one output row for each index, in index order, so Example B produces 3 rows, 6, 2, 6. Filter can only keep or drop rows; take can reorder and repeat them.

**Why it is correct.** The output row count is the number of trues for `filter` and the number of indices for `take`. That rule predicts both results before running anything.

**Plausible wrong approach.** Expecting `take` to deduplicate indices or to keep input order predicts [2, 6] for Example B and misses the repeated row that can double-count an aggregate.

**How to verify.** Assert `result.len()` in each example: 2 for filter, 3 for take.

### Task 2: Guided modification

Change one mask value and independently derive the result.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, BooleanArray, Int32Array};
    let values = Int32Array::from(vec![2, 4, 6]);
    let mask = BooleanArray::from(vec![true, true, false]);
    let expected: Vec<i32> = values
        .values()
        .iter()
        .zip([true, true, false])
        .filter(|(_, keep)| *keep)
        .map(|(value, _)| *value)
        .collect();
    let result = arrow::compute::filter(&values, &mask)?;
    let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
    assert_eq!(typed.values().to_vec(), expected);
    assert_eq!(expected, vec![2, 4]);
    Ok(())
}
```

**Observe:** With the last position switched to false, the kernel keeps 2 and 4, matching the result derived with a plain iterator.

The independent derivation zips the values with the same decisions and keeps the true positions, so it shares no code with the kernel. The `unwrap` on the downcast is justified here because `filter` on an `Int32Array` returns an array of the same type.

**Plausible wrong approach.** Changing only the expected vector and not the mask makes the test check your edit, not the kernel.

**How to verify.** Run the block. Set the mask to all false and both the kernel and the derivation produce an empty result.

### Task 3: Independent construction

Filter every column of a batch consistently under one row mask.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{ArrayRef, AsArray, BooleanArray, Int32Array, StringArray};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let names: ArrayRef = Arc::new(StringArray::from(vec!["pear", "fig", "kiwi"]));
    let qty: ArrayRef = Arc::new(Int32Array::from(vec![2, 0, 5]));
    let batch = RecordBatch::try_from_iter(vec![("name", names), ("qty", qty)])?;
    let mask = BooleanArray::from(vec![true, false, true]);
    let kept = arrow::compute::filter_record_batch(&batch, &mask)?;
    assert_eq!(kept.num_rows(), 2);
    let kept_names = kept.column(0).as_string::<i32>();
    assert_eq!(kept_names.value(1), "kiwi");
    Ok(())
}
```

**Observe:** Filtering keeps rows 0 and 2 in every column: pear and kiwi with their quantities.

filter_record_batch applies one mask to all columns at once, so names and quantities can never fall out of alignment.

### Task 4: Diagnose a defect

Diagnose filtering one column while leaving others unfiltered.

**Written answer.** The defect is `let names = filter(&names, &mask)?;` followed by building a batch from the filtered names and the original, unfiltered `quantities`. If the lengths differ, `RecordBatch::try_new` fails with an error that all columns in a record batch must have the same length. If a later step pads or trims to make them equal, every row pairs a name with another row's quantity. Filter the whole batch with `arrow::compute::filter_record_batch(&batch, &mask)`, as in task 3.

**Why it is correct.** A row is the set of values at one position across all columns. Selection is a row decision, so it must apply the same mask to every column at once.

**Plausible wrong approach.** Filtering each column separately with the same mask works, but it is easy to miss a column when the schema grows; the batch-level kernel cannot miss one.

**How to verify.** Build a batch from one filtered and one unfiltered column and read the length error; then use `filter_record_batch` and assert that every column has `num_rows()` values.

### Task 5: Boundary evidence

Test empty selection, all-selected rows and checked invalid indices.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, BooleanArray, Int32Array, UInt32Array};
    use arrow::compute::TakeOptions;
    let values = Int32Array::from(vec![2, 4, 6]);
    let none = arrow::compute::filter(&values, &BooleanArray::from(vec![false; 3]))?;
    assert_eq!((none.len(), none.data_type()), (0, values.data_type()));
    let all = arrow::compute::filter(&values, &BooleanArray::from(vec![true; 3]))?;
    assert_eq!(all.as_any().downcast_ref::<Int32Array>().unwrap(), &values);
    let checked = TakeOptions { check_bounds: true };
    let bad = UInt32Array::from(vec![0, 5]);
    assert!(arrow::compute::take(&values, &bad, Some(checked.clone())).is_err());
    let fine = UInt32Array::from(vec![1]);
    let taken = arrow::compute::take(&values, &fine, Some(checked))?;
    assert_eq!(
        taken
            .as_any()
            .downcast_ref::<Int32Array>()
            .unwrap()
            .value(0),
        4
    );
    Ok(())
}
```

**Observe:** An all-false mask gives an empty Int32 column, an all-true mask returns a copy equal to the input, and a checked take with index 5 returns an error while index 1 returns 4.

Empty selection is a valid result with the same type, not a failure. With `check_bounds: true`, `take` validates every index and reports an out-of-range one as an error that the caller can handle, instead of relying on the input being correct.

**Plausible wrong approach.** Calling `take` with `None` options on indices from an untrusted source assumes they were already validated, so an out-of-range index is no longer reported as a handled error.

**How to verify.** Run the block. Print the error from the bad take with `{:?}`; it names index 5 and the three available entries.

### Task 6: Transfer and justify

Choose filter or take for a sampling procedure and explain duplicate-row consequences.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Kernel**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Arrow compute kernels operate on arrays while respecting their logical representation. A Boolean mask selects rows; take selects positions by an index array. These are different operations with different output ordering. Filtering normally preserves the order of admitted rows, while take can repeat or reorder positions.

Type erasure means a kernel can return ArrayRef. Inspect or validate the logical type before downcasting to a concrete array. An unwrap can be justified only by a nearby known kernel/type contract in a controlled fixture. Production generic code should return a useful error for an unexpected type. Preserve null and index bounds policies explicitly.

compute::filter accepts an array and BooleanArray mask. compute::take selects by integer indices. as_any().downcast_ref recovers a known concrete array after the type contract has been established.

Downcast failure is possible in generic code. A mask and array must have compatible lengths. A kernel result does not establish a domain-level ordering guarantee unless the operation contract does.

## Review before continuing

Run the reference and confirm that it prints `rust-040: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
