# rust-040: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-040_solution.rs](rust-040_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Filter with an explicit mask:** The mask expresses one admission decision for every original position. Filtering retains two and six in input order.

**Reorder and repeat with take:** A selected row can appear more than once, so cardinality and aggregation assumptions need review. Take repeats and reorders values according to the index sequence.

## Task answers

### Task 1: Predict and explain

Predict row count and order for both operations.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The mask expresses one admission decision for every original position. Filtering retains two and six in input order.

### Task 2: Guided modification

Change one mask value and independently derive the result.

No separate reference answer has been written for this task. Start from Example B: A selected row can appear more than once, so cardinality and aggregation assumptions need review. Take repeats and reorders values according to the index sequence.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Downcast failure is possible in generic code. A mask and array must have compatible lengths. A kernel result does not establish a domain-level ordering guarantee unless the operation contract does.

### Task 5: Boundary evidence

Test empty selection, all-selected rows and checked invalid indices.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Filter with an explicit mask) and Example B (Reorder and repeat with take).

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
