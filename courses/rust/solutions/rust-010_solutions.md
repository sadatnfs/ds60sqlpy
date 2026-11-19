# rust-010: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-010_solution.rs](rust-010_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Mutate through one explicit borrower:** The function receives mutation capability for the duration of the call. The caller retains ownership and observes the deliberate mutation.

**Mutate two proven-disjoint regions:** The standard library API establishes disjointness instead of relying on two potentially overlapping index borrows. The two slices mutate separate halves safely.

## Task answers

### Task 1: Predict and explain

Trace who may access text during the mutable call.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The function receives mutation capability for the duration of the call. The caller retains ownership and observes the deliberate mutation.

### Task 2: Guided modification

Add a second mutation after the first borrow ends.

No separate reference answer has been written for this task. Start from Example B: The standard library API establishes disjointness instead of relying on two potentially overlapping index borrows. The two slices mutate separate halves safely.

### Task 3: Independent construction

Write a function swapping the ends of a mutable slice safely.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn swap_ends(values: &mut [i32]) {
        if let Some(last) = values.len().checked_sub(1) {
            values.swap(0, last);
        }
    }
    let mut values = [1, 2, 3];
    swap_ends(&mut values);
    assert_eq!(values, [3, 2, 1]);
    let mut empty: [i32; 0] = [];
    swap_ends(&mut empty);
    assert!(empty.is_empty());
    Ok(())
}
```

**Observe:** [1, 2, 3] becomes [3, 2, 1], and an empty slice is left alone.

checked_sub avoids underflow for an empty slice, and swap performs both writes through the one exclusive borrow.

### Task 4: Diagnose a defect

Create conflicting mutable borrows and explain the compiler diagnostic.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An exclusive borrow is not a thread lock. More mut annotations do not solve aliasing conflicts. Prefer safe disjointness APIs to manually asserting pointer safety.

### Task 5: Boundary evidence

Test an empty slice and a split at either endpoint.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Mutate through one explicit borrower) and Example B (Mutate two proven-disjoint regions).

### Task 6: Transfer and justify

Design an API that exposes only the smallest mutable region needed by a transformation.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Exclusive borrow**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An exclusive reference grants mutation while preventing conflicting access to the same storage. The common rule is either shared readers or one exclusive borrower at a time. This is a capability rule about access, not a claim that the operating system has locked memory.

Small scopes make mutation ownership easier to see. After an exclusive borrow's last use, the owner can be used again. APIs such as split_at_mut safely produce disjoint mutable regions because they establish that the regions do not overlap. Do not reach for unsafe code merely because the compiler cannot infer a relationship you have not expressed.

`&mut value` creates exclusive access and the original binding must permit mutation. A function taking &mut T may update the borrowed value but does not own its eventual destruction. split_at_mut proves disjoint slices.

An exclusive borrow is not a thread lock. More mut annotations do not solve aliasing conflicts. Prefer safe disjointness APIs to manually asserting pointer safety.

## Review before continuing

Run the reference and confirm that it prints `rust-010: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
