# rust-011: explanation and comparison

Executable reference: [rust-011_solution.rs](rust-011_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Accept arrays and vectors uniformly:** The function requires read access, not a particular allocation strategy. One slice interface accepts several owning representations.

**Separate capacity from logical elements:** The optional lookup exposes absence instead of indexing uninitialized capacity. Reserved storage still contains zero logical elements until push.

## Task answers

### Task 1: Predict and explain

Identify owner, length and borrowed view in each call.

**Written answer.** `total(&[2, 3, 4])` borrows a temporary array of length 3; `total(&vec![1, 2])` borrows a temporary `Vec<i32>` of length 2; `total(&[])` borrows an empty array. Each reaches `total` as a `&[i32]`. In Example B, `values` owns the `Vec`, its length goes from 0 to 1, and `get` lends an `Option<&i32>`.

**Why it is correct.** `&[i32; 3]` unsizes to `&[i32]` and `&Vec<i32>` deref-coerces to it, so one parameter type covers both owners. A slice reference is a pointer plus a length, and each temporary lives until the end of its statement.

**Plausible wrong approach.** Treating `with_capacity(10)` as length 10 predicts that `values[5]` is valid. It panics with `index out of bounds: the len is 1 but the index is 5`, because capacity is reserved space, not elements.

**How to verify.** Add `assert_eq!(values.len(), 1);`, `assert_eq!(values.get(5), None);` and `assert_eq!(std::mem::size_of::<&[i32]>(), 2 * std::mem::size_of::<usize>());`, which shows a slice reference is a pointer and a length.

### Task 2: Guided modification

Use a subslice and predict its total.

**Written answer.** With `let data = [2, 3, 4, 5];`, `total(&data[1..3])` covers indices 1 and 2, so it is 3 + 4 = 7. The subslice borrows part of `data` without copying.

**Why it is correct.** `1..3` is half-open: it includes the start and excludes the end. The slice therefore has length 2 and starts at the element 3.

**Plausible wrong approach.** Reading `1..3` as inclusive predicts 12, which is what `1..=3` gives. Extending the range to `&data[2..5]` panics, because the end 5 is past the length 4.

**How to verify.** Assert `total(&data[1..3]) == 7` and `total(&data[1..=3]) == 12`, and probe the overrun safely with `assert_eq!(data.get(2..5), None);`.

### Task 3: Independent construction

Implement a maximum function accepting a slice and returning Option.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Plausible wrong approach.** Dropping `.copied()` returns `values.iter().max()`, an `Option<&i32>`, and the signature promising `Option<i32>` is rejected with E0308. Keeping a plain `i32` return with `unwrap_or(i32::MIN)` compiles but makes an empty slice look like a real minimum value.

**How to verify.** Add `assert_eq!(maximum(&[-5, -2]), Some(-2));`, `assert_eq!(maximum(&vec![4, 4]), Some(4));` and `assert_eq!(maximum(&[i32::MIN]), Some(i32::MIN));`. The last check would be indistinguishable from empty input under the sentinel version.

### Task 4: Diagnose a defect

Diagnose keeping an element reference live across a conflicting vector push.

**Written answer.** The defect is `let mut values = vec![1, 2]; let first = &values[0]; values.push(3); assert_eq!(*first, 1);`. rustc rejects it with E0502: `values` cannot be borrowed as mutable for `push` while `first` still holds a shared borrow that is used afterwards. Copy the element instead, `let first = values[0];`, since `i32` is `Copy`.

**Why it is correct.** `push` may reallocate the buffer, and with a length and capacity of 2 it must grow, moving the elements. A reference held across that push would point at freed memory, so the borrow checker forbids it.

**Plausible wrong approach.** Calling `values.reserve(10)` before taking the reference, so the push cannot reallocate, does not help. The rule is about overlapping borrows, not capacity, so E0502 is still reported.

**How to verify.** Compile the defect and read E0502 with its immutable and mutable borrow labels. With the copied value, `assert_eq!(first, 1);` and `assert_eq!(values, [1, 2, 3]);` both pass.

### Task 5: Boundary evidence

Test empty, singleton and out-of-range get cases.

**Written answer.** For empty input, `let empty: Vec<i32> = Vec::new();` with `empty.get(0) == None` and `total(&empty) == 0`. For one element, `let one = vec![7];` with `one.get(0) == Some(&7)`, `one.get(1) == None` and `maximum(&one) == Some(7)`.

**Why it is correct.** Valid indices run from 0 to one less than `len()`, so `get` at the length returns `None`. The sum of no elements is 0, and the maximum of one element is that element.

**Plausible wrong approach.** Probing with `one[1]` instead of `get` panics with `index out of bounds: the len is 1 but the index is 1`, which aborts the test rather than recording the out-of-range case.

**How to verify.** Run the five checks and add `assert_eq!(Vec::<i32>::with_capacity(10).get(3), None);`: reserved capacity still has no elements. `rust-011: passed` follows.

### Task 6: Transfer and justify

Choose an array, Vec or slice for stored state, function input and fixed-size coordinates.

**Written answer.** Store a growing list, such as cart items, in a `Vec<T>`; accept read-only input as `&[T]`; and model fixed-size coordinates as an array such as `[i32; 2]`, whose length is part of its type and which needs no heap allocation.

**Why it is correct.** `Vec` owns and can grow, a slice parameter accepts arrays, vectors and subslices alike, and an array makes a three-number point a type error. A limitation is that an array's length must be known at compile time.

**Plausible wrong approach.** Declaring `fn total(values: &Vec<i32>)` rejects `total(&[2, 3, 4])` with E0308 and cannot take `&data[1..3]`. Storing a point as `Vec<i32>` lets a three-element point appear at run time.

**How to verify.** Call `total(&cart)`, `total(&point)` and `total(&cart[..1])`; all compile against `&[i32]`. Then write `let point: [i32; 2] = [1, 2, 3];` and the compiler reports a mismatched array length.

## Mechanism and diagnostic reasoning

An array has a compile-time length as part of its type. A Vec owns a growable allocation. A slice borrows a contiguous region and carries its length without owning that allocation. Accepting &[T] lets a function read arrays and vectors through one interface.

Vector growth can reallocate storage, which explains why a borrow into a vector cannot remain live while a conflicting push changes its allocation. Capacity reserves room but does not create initialized logical elements. Indexing panics outside the valid range; get returns Option when absence is a normal possibility.

`[i32; 3]` is an array of exactly three integers. `Vec<i32>` owns a variable-length sequence. `&[i32]` is a borrowed slice. len and capacity describe different properties.

Capacity is not a valid index limit. A slice does not extend its owner's lifetime. Avoid accepting &Vec when a slice expresses the actual requirement.

## Review before continuing

Rebuild Example B (Separate capacity from logical elements) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
