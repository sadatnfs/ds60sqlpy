# rust-034: explanation and comparison

Executable reference: [rust-034_solution.rs](rust-034_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Reconstruct a bounded borrowed view:** The safety proof is tied to the pointer origin and exact length, not merely to the pointer being non-null. The reconstructed view matches the live initialized array.

**Prefer the safe operation when available:** Unsafe should be justified by a real boundary, not used because pointer syntax appears advanced. A normal slice provides the same read contract without a manual safety burden.

## Task answers

### Task 1: Predict and explain

State every precondition needed by from_raw_parts.

**Written answer.** `std::slice::from_raw_parts(pointer, len)` requires that `pointer` is non-null and aligned for `i32`; that it is valid for reading `len * size_of::<i32>()` bytes inside one allocation; that those `len` values are initialized; that nothing mutates them while the returned slice is in use; that the total size is at most `isize::MAX`; and that the chosen lifetime does not outlive the owner. In Example A all of them follow from `values.as_ptr()` on a live array, `values.len()` as the exact length, and no writes before the assertion.

**Why it is correct.** An `unsafe` block moves these checks from the compiler to the author. Writing each one down and tying it to a fact in the code is what turns `unsafe` from a hope into an argument.

**Plausible wrong approach.** Treating a null check as sufficient misses alignment, length, initialization, aliasing and lifetime. A non-null pointer into freed memory satisfies it and is still undefined behavior.

**How to verify.** Compare your list with the Safety section of the `std::slice::from_raw_parts` documentation and check that each item is answered by a phrase in Example A's SAFETY comment.

### Task 2: Guided modification

Reduce the borrowed length while retaining valid initialized storage.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let values = [2_i32, 3, 4, 5];
    let pointer = values.as_ptr();
    let length = 2;
    assert!(length <= values.len());
    // SAFETY: pointer comes from this live initialized array, and length 2 stays within its 4 elements.
    let view = unsafe { std::slice::from_raw_parts(pointer, length) };
    assert_eq!(view, &[2, 3]);
    assert_eq!(view, &values[..length]);
    Ok(())
}
```

**Observe:** The two-element view reads 2 and 3, the same as the safe slice `&values[..2]`.

Shortening the length keeps every precondition: the first two elements are inside the same live, initialized array. The `assert!` documents the bound the SAFETY comment relies on, and the comparison with the safe slice is the oracle.

**Plausible wrong approach.** Increasing the length beyond `values.len()` to read neighboring memory is undefined behavior even if a run happens to print plausible numbers.

**How to verify.** Run the block. Then change `length` to 5 and the `assert!` fails before the unsafe call can run.

### Task 3: Independent construction

Write a safe wrapper specification before considering an unsafe implementation.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// Returns the first two values, or None when fewer than two exist.
    /// Never reads past the end of the slice and never panics.
    fn first_two(values: &[i32]) -> Option<(i32, i32)> {
        match values {
            [first, second, ..] => Some((*first, *second)),
            _ => None,
        }
    }
    assert_eq!(first_two(&[4, 5, 6]), Some((4, 5)));
    assert_eq!(first_two(&[4]), None);
    Ok(())
}
```

**Observe:** first_two returns Some((4, 5)) for three values and None for one.

The specification fixes the input, the output and the no-panic guarantee before any implementation. A safe slice pattern already meets it; an unsafe body such as get_unchecked would be considered only if measurement showed a need, with a SAFETY comment proving each index is below the checked length.

### Task 4: Diagnose a defect

Diagnose returning a pointer after its owner is dropped.

**Written answer.** The defect is `fn data() -> *const i32 { let values = vec![1, 2, 3]; values.as_ptr() }`. It compiles, because raw pointers carry no lifetime, but the `Vec` frees its buffer when the function returns, so any later `from_raw_parts` on that pointer reads freed memory. Return the `Vec` itself, or borrow from storage the caller owns.

**Why it is correct.** Raw pointers opt out of borrow checking, so the compiler cannot connect the pointer to its owner. The safe version, `-> &[i32]` returning `&values[..]`, is rejected with E0515, which is exactly the error the raw pointer hid.

**Plausible wrong approach.** Checking `!pointer.is_null()` before using it does not help: a pointer to freed memory is usually still non-null.

**How to verify.** Change the return type to `&'static [i32]` with body `&values[..]` and read E0515, cannot return value referencing local variable `values`.

### Task 5: Boundary evidence

Review zero-length and alignment rules without executing undefined behavior.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let empty: [u64; 0] = [];
    let pointer = empty.as_ptr();
    assert!(!pointer.is_null() && pointer.is_aligned());
    // SAFETY: a zero-length slice needs only a non-null, aligned pointer, which as_ptr provides.
    let view = unsafe { std::slice::from_raw_parts(pointer, 0) };
    assert!(view.is_empty());
    let dangling = std::ptr::NonNull::<u64>::dangling();
    // SAFETY: NonNull::dangling is non-null and aligned, which is all a zero-length slice requires.
    let also_empty = unsafe { std::slice::from_raw_parts(dangling.as_ptr(), 0) };
    assert_eq!(also_empty.len(), 0);
    let bytes = [0_u8; 16];
    let start = bytes.as_ptr().cast::<u64>();
    let next = bytes.as_ptr().wrapping_add(1).cast::<u64>();
    assert!(!(start.is_aligned() && next.is_aligned()));
    Ok(())
}
```

**Observe:** Both zero-length slices are empty and valid, and of two byte addresses one apart, at most one is aligned for u64.

A zero-length slice reads no memory, but its pointer must still be non-null and aligned, which is why `NonNull::dangling` exists. Alignment is checked with `is_aligned` on the address alone, without reading through it: a `u64` needs an address that is a multiple of its alignment, and two adjacent byte addresses cannot both be multiples of 8.

**Plausible wrong approach.** Passing `std::ptr::null()` as the pointer of an empty slice, on the reasoning that nothing is read, is undefined behavior, and dereferencing a misaligned `*const u64` to see what happens is undefined behavior too.

**How to verify.** Run the block. For unaligned data, use `std::ptr::read_unaligned` or `u64::from_ne_bytes` on a copied `[u8; 8]` instead of a cast pointer.

### Task 6: Transfer and justify

Design an FFI ownership document stating allocation, release, encoding and error conventions.

**Judging criteria.** A strong document answers four questions for every pointer that crosses the boundary: which side allocates it; which side frees it and with which function, never mixing Rust's allocator with C `free`; how text is encoded, for example NUL-terminated UTF-8 through `CString` and `CStr` with invalid bytes rejected; and how errors are reported, as a return code plus an out-parameter rather than a panic unwinding into C. It also states whether a pointer may outlive the call. State one limitation: the compiler checks none of it, so each rule needs a test or review step.

## Mechanism and diagnostic reasoning

Unsafe permits a small set of operations whose correctness the compiler cannot fully establish. It does not disable every safety rule or turn wrong memory access into valid behavior. Each unsafe block needs an argument covering pointer validity, alignment, initialized length, aliasing and lifetime. Keep the block small and wrap it in a safe interface that enforces those conditions.

Foreign-function interfaces add an ABI contract: layout, calling convention, string encoding, ownership and failure signaling must agree across languages. A successful link does not prove those agreements. The ordinary fixture uses a pointer obtained from a live array and immediately reconstructs a read-only slice under a documented invariant, without calling undeclared native libraries.

`as_ptr` borrows an address from live storage. `slice::from_raw_parts` is unsafe because the caller supplies validity and length. A SAFETY comment explains why this exact operation satisfies its preconditions.

Never test undefined behavior by hoping it crashes predictably. A null check is insufficient to prove pointer validity. Panics crossing an incompatible FFI boundary need a deliberate policy.

## Review before continuing

Rebuild Example B (Prefer the safe operation when available) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
