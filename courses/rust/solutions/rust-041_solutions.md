# rust-041: explanation and comparison

Executable reference: [rust-041_solution.rs](rust-041_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Distinguish nonempty, empty and null lists:** The first row even contains a null child, demonstrating independent validity levels. The three rows are a two-child list, an empty list and a null list.

**Slice without confusing logical positions:** A view's logical indices are interpreted relative to the sliced array rather than the original source positions. The sliced array exposes middle at its logical index zero.

## Task answers

### Task 1: Predict and explain

Classify parent-null, empty and child-null states.

**Written answer.** Example A has all three states. Row 2 is a parent null: `append(false)` marks the whole list missing, so `is_null(2)` is true. Row 1 is an empty list: it is valid, with `value_length(1) == 0`. Row 0 is a valid list of length 2 whose second child is null: the list is present, and the child array has its own validity bit unset for that element.

**Why it is correct.** A list column has two validity layers, one for each list row and one in the child array for each element. Each state answers a different question: is the list known, does it have elements, and is a given element known.

**Plausible wrong approach.** Reading `value_length(2) == 0` as an empty list misses that row 2 is null; the length of a null row carries no meaning.

**How to verify.** Assert `lists.values().null_count() == 1` and `lists.null_count() == 1`: one child null and one parent null, counted separately.

### Task 2: Guided modification

Add another valid list with two non-null children.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, AsArray, Int32Builder, ListBuilder};
    use arrow::datatypes::Int32Type;
    let mut builder = ListBuilder::new(Int32Builder::new());
    builder.values().append_value(2);
    builder.values().append_null();
    builder.append(true);
    builder.append(true);
    builder.append(false);
    builder.values().append_value(7);
    builder.values().append_value(9);
    builder.append(true);
    let lists = builder.finish();
    assert_eq!(lists.len(), 4);
    assert!(lists.is_valid(3));
    assert_eq!(lists.value_length(3), 2);
    let added = lists.value(3);
    let children = added.as_primitive::<Int32Type>();
    assert_eq!(children.null_count(), 0);
    assert_eq!(children.values().to_vec(), vec![7, 9]);
    Ok(())
}
```

**Observe:** The column now has four rows; row 3 is valid, holds two children, and those children are 7 and 9 with no nulls.

Child values go into the shared child builder first, and `append(true)` closes them into the next list row. `value(3)` returns that row's children as their own array, so the new row is checked independently of the null child in row 0.

**Plausible wrong approach.** Calling `append(true)` before appending 7 and 9 closes an empty row 3 and gives the next row the two children, so `value_length(3)` is 0.

**How to verify.** Run the block. Move `builder.append(true);` above the two `append_value` calls and the row-3 assertions fail.

### Task 3: Independent construction

Build a nested column from a small ragged dataset.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is a missing-data check written as `lists.value_length(i) == 0`, or as a count of rows with no elements reported as missing. In Example A it flags both row 1, which is a known, empty list, and row 2, which is null. Check `lists.is_null(i)` for missing rows and `value_length(i) == 0` only on valid rows.

**Why it is correct.** Empty and missing mean different things: a customer with no orders is not a customer whose orders are unknown. Arrow keeps them apart through the validity bitmap, and the code has to read it.

**Plausible wrong approach.** Replacing nulls with empty lists before the count makes the two cases agree by erasing the information that distinguished them.

**How to verify.** Count `(0..lists.len()).filter(|&i| lists.is_null(i))` and compare it with the zero-length count on Example A: 1 null against 2 rows of length zero.

### Task 5: Boundary evidence

Test zero-length slices and nonzero source offsets.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, StringArray};
    let values = StringArray::from(vec![Some("first"), None, Some("middle"), Some("last")]);
    let nothing = values.slice(2, 0);
    assert_eq!((nothing.len(), nothing.null_count()), (0, 0));
    let tail = values.slice(1, 3);
    let typed = tail.as_any().downcast_ref::<StringArray>().unwrap();
    assert_eq!(typed.len(), 3);
    assert!(typed.is_null(0));
    assert_eq!(typed.value(1), "middle");
    assert_eq!(
        typed.iter().collect::<Vec<_>>(),
        vec![None, Some("middle"), Some("last")]
    );
    let end = values.slice(values.len(), 0);
    assert!(end.is_empty());
    Ok(())
}
```

**Observe:** A zero-length slice is empty with no nulls. The slice starting at source offset 1 reads the null at its index 0 and middle at its index 1, and a zero-length slice at the very end is also valid.

Slicing changes where index 0 starts for both values and validity, so the null that was at source position 1 is at slice position 0. A zero-length slice is legal anywhere up to `len()` and contains nothing.

**Plausible wrong approach.** Indexing the slice with source positions, `typed.value(2)` for middle, reads last instead.

**How to verify.** Run the block. Then try `values.slice(3, 2)`, which runs past the end, and it panics because a slice must stay within the array.

### Task 6: Transfer and justify

Explain when retaining a tiny shared slice may retain excessive memory and when copying is justified.

**Judging criteria.** A strong answer explains that `slice` on a `StringArray` or `ListArray` shares the parent's buffers, so keeping one short slice of a large array keeps every byte of the parent allocated. Zero-copy is right when the slice is short-lived or covers most of the parent. Copying into a new array, for example through `take` or a builder, is justified when a small slice outlives a large parent, such as a cache entry kept after its batch is done. State one limitation: copying costs time in proportion to the slice and loses sharing with other views.

## Mechanism and diagnostic reasoning

Variable-width arrays use offsets to locate each logical value in a shared data region. Nested list arrays add another layer: a parent position can be null, an empty list, or a nonempty list whose children may themselves be null. These states carry different meanings and must not be flattened indiscriminately.

Arrow slices often share underlying buffers instead of copying all data. This makes views cheap, but a small retained slice can keep a large allocation alive. Logical offsets and validity still matter. Zero-copy is a specific ownership and representation property, not a blanket claim that an entire analytical pipeline performs no allocations.

ListBuilder<Int32Builder> appends child values, then append(true) closes a valid parent list. append(false) adds a null parent. Array::slice creates a logical view over a selected region.

Nested nullability has several layers. Zero-copy views can extend buffer lifetime. Do not manually manipulate offset buffers without validating every format invariant.

## Review before continuing

Rebuild Example B (Slice without confusing logical positions) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
