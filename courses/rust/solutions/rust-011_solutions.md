# rust-011: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-011_solution.rs](rust-011_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Accept arrays and vectors uniformly:** The function requires read access, not a particular allocation strategy. One slice interface accepts several owning representations.

**Separate capacity from logical elements:** The optional lookup exposes absence instead of indexing uninitialized capacity. Reserved storage still contains zero logical elements until push.

## Task answers

### Task 1: Predict and explain

Identify owner, length and borrowed view in each call.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The function requires read access, not a particular allocation strategy. One slice interface accepts several owning representations.

### Task 2: Guided modification

Use a subslice and predict its total.

No separate reference answer has been written for this task. Start from Example B: The optional lookup exposes absence instead of indexing uninitialized capacity. Reserved storage still contains zero logical elements until push.

### Task 3: Independent construction

Implement a maximum function accepting a slice and returning Option.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn maximum(values: &[i32]) -> Option<i32> {
        values.iter().copied().max()
    }
    assert_eq!(maximum(&[3, 9, 4]), Some(9));
    assert_eq!(maximum(&[]), None);
    Ok(())
}
```

**Observe:** The maximum of 3, 9 and 4 is Some(9); an empty slice gives None.

Returning Option makes the empty case explicit instead of inventing a sentinel such as i32::MIN.

### Task 4: Diagnose a defect

Diagnose keeping an element reference live across a conflicting vector push.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Capacity is not a valid index limit. A slice does not extend its owner's lifetime. Avoid accepting &Vec when a slice expresses the actual requirement.

### Task 5: Boundary evidence

Test empty, singleton and out-of-range get cases.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Accept arrays and vectors uniformly) and Example B (Separate capacity from logical elements).

### Task 6: Transfer and justify

Choose an array, Vec or slice for stored state, function input and fixed-size coordinates.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Array**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An array has a compile-time length as part of its type. A Vec owns a growable allocation. A slice borrows a contiguous region and carries its length without owning that allocation. Accepting &[T] lets a function read arrays and vectors through one interface.

Vector growth can reallocate storage, which explains why a borrow into a vector cannot remain live while a conflicting push changes its allocation. Capacity reserves room but does not create initialized logical elements. Indexing panics outside the valid range; get returns Option when absence is a normal possibility.

`[i32; 3]` is an array of exactly three integers. `Vec<i32>` owns a variable-length sequence. `&[i32]` is a borrowed slice. len and capacity describe different properties.

Capacity is not a valid index limit. A slice does not extend its owner's lifetime. Avoid accepting &Vec when a slice expresses the actual requirement.

## Review before continuing

Run the reference and confirm that it prints `rust-011: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
