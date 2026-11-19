# rust-041: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-041_solution.rs](rust-041_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Distinguish nonempty, empty and null lists:** The first row even contains a null child, demonstrating independent validity levels. The three rows are a two-child list, an empty list and a null list.

**Slice without confusing logical positions:** A view's logical indices are interpreted relative to the sliced array rather than the original source positions. The sliced array exposes middle at its logical index zero.

## Task answers

### Task 1: Predict and explain

Classify parent-null, empty and child-null states.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The first row even contains a null child, demonstrating independent validity levels. The three rows are a two-child list, an empty list and a null list.

### Task 2: Guided modification

Add another valid list with two non-null children.

No separate reference answer has been written for this task. Start from Example B: A view's logical indices are interpreted relative to the sliced array rather than the original source positions. The sliced array exposes middle at its logical index zero.

### Task 3: Independent construction

Build a nested column from a small ragged dataset.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Int32Builder, ListBuilder};
    let rows = [vec![1, 2], vec![], vec![3]];
    let mut builder = ListBuilder::new(Int32Builder::new());
    for row in &rows {
        for value in row {
            builder.values().append_value(*value);
        }
        builder.append(true);
    }
    let lists = builder.finish();
    assert_eq!(lists.len(), 3);
    let lengths: Vec<i32> = (0..3).map(|i| lists.value_length(i)).collect();
    assert_eq!(lengths, [2, 0, 1]);
    Ok(())
}
```

**Observe:** The nested column holds 3 lists with lengths 2, 0 and 1.

Child values are appended to one shared buffer and each append(true) closes a row, so the empty middle list is a valid row rather than a null.

### Task 4: Diagnose a defect

Diagnose treating an empty list as equivalent to a missing list.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Nested nullability has several layers. Zero-copy views can extend buffer lifetime. Do not manually manipulate offset buffers without validating every format invariant.

### Task 5: Boundary evidence

Test zero-length slices and nonzero source offsets.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Distinguish nonempty, empty and null lists) and Example B (Slice without confusing logical positions).

### Task 6: Transfer and justify

Explain when retaining a tiny shared slice may retain excessive memory and when copying is justified.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Offset buffer**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Variable-width arrays use offsets to locate each logical value in a shared data region. Nested list arrays add another layer: a parent position can be null, an empty list, or a nonempty list whose children may themselves be null. These states carry different meanings and must not be flattened indiscriminately.

Arrow slices often share underlying buffers instead of copying all data. This makes views cheap, but a small retained slice can keep a large allocation alive. Logical offsets and validity still matter. Zero-copy is a specific ownership and representation property, not a blanket claim that an entire analytical pipeline performs no allocations.

ListBuilder<Int32Builder> appends child values, then append(true) closes a valid parent list. append(false) adds a null parent. Array::slice creates a logical view over a selected region.

Nested nullability has several layers. Zero-copy views can extend buffer lifetime. Do not manually manipulate offset buffers without validating every format invariant.

## Review before continuing

Run the reference and confirm that it prints `rust-041: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
