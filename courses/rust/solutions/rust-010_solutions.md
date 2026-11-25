# rust-010: explanation and comparison

Executable reference: [rust-010_solution.rs](rust-010_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Mutate through one explicit borrower:** The function receives mutation capability for the duration of the call. The caller retains ownership and observes the deliberate mutation.

**Mutate two proven-disjoint regions:** The standard library API establishes disjointness instead of relying on two potentially overlapping index borrows. The two slices mutate separate halves safely.

## Task answers

### Task 1: Predict and explain

Trace who may access text during the mutable call.

**Written answer.** While `append_mark(&mut text)` runs, the function's parameter `text` is the only path to the String; `main` cannot read or write its own `text` until the call returns. Afterwards the borrow has ended, `main` regains full access and observes `ready!`.

**Why it is correct.** A `&mut` reference is exclusive for as long as it is live. The borrow lasts only for the call, so the later `assert_eq!` is a new shared borrow that starts after the exclusive one ended.

**Plausible wrong approach.** Thinking the function receives a copy predicts that `main` still sees `ready`; the passing assertion shows the change happened in place through the borrow.

**How to verify.** Keep the reference alive with `let borrow = &mut text; assert_eq!(text, "ready"); borrow.push('!');` and the compiler rejects the read with E0502.

### Task 2: Guided modification

Add a second mutation after the first borrow ends.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut values = [1, 2, 3, 4];
    let (left, right) = values.split_at_mut(2);
    left[0] = 9;
    right[0] = 8;
    values[3] = 7;
    assert_eq!(values, [9, 2, 8, 7]);
    Ok(())
}
```

**Observe:** After the two halves are last used, writing 7 directly into values[3] compiles and the array becomes [9, 2, 8, 7].

Non-lexical lifetimes end the borrows held by `left` and `right` after their last use, `right[0] = 8`. The direct write to `values` comes after that point, so it is the only borrow alive when it happens.

**Plausible wrong approach.** Placing `values[3] = 7;` between `left[0] = 9;` and `right[0] = 8;` is rejected with E0506, cannot assign to `values[_]` because it is borrowed, because `right` is still used afterwards and so its borrow of `values` is still live.

**How to verify.** Run the block. Move the direct write up one line and read the E0506 diagnostic naming the earlier `split_at_mut` borrow.

### Task 3: Independent construction

Write a function swapping the ends of a mutable slice safely.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is `let first = &mut values; let second = &mut values; first[0] = 1; second[1] = 2;`. rustc reports E0499, cannot borrow `values` as mutable more than once at a time, marking the first borrow, the second borrow and the later use of `first` that keeps it alive. Use `split_at_mut` for disjoint halves, or finish with `first` before creating `second`.

**Why it is correct.** Two live exclusive references could write the same element, so the rule forbids them regardless of which indices are touched. The compiler does not reason about indices 0 and 1 being different; `split_at_mut` provides that proof through its API.

**Plausible wrong approach.** Adding more `mut`, as in `let mut first = &mut values;`, changes nothing: the conflict is between two borrows of `values`, not about whether the reference bindings are reassignable.

**How to verify.** Compile the defect and read E0499. Rewrite with `let (first, second) = values.split_at_mut(1); first[0] = 1; second[0] = 2;` and assert the result.

### Task 5: Boundary evidence

Test an empty slice and a split at either endpoint.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut values = [1, 2, 3];
    let (left, right) = values.split_at_mut(0);
    assert!(left.is_empty());
    right[0] = 7;
    let (left, right) = values.split_at_mut(3);
    assert!(right.is_empty());
    left[2] = 9;
    assert_eq!(values, [7, 2, 9]);
    assert!(values.split_at_mut_checked(4).is_none());
    let mut empty: [i32; 0] = [];
    let (left, right) = empty.split_at_mut(0);
    assert!(left.is_empty() && right.is_empty());
    Ok(())
}
```

**Observe:** Splitting at 0 gives an empty left half and splitting at 3 an empty right half; writes through the other half turn [1, 2, 3] into [7, 2, 9], 4 is refused, and an empty slice splits into two empty halves.

Both endpoints are valid split points, so each produces one empty half and one half covering the whole slice. `split_at_mut_checked` turns the one-past-the-end index into `None` instead of the panic `split_at_mut(4)` would raise.

**Plausible wrong approach.** Assuming a split at 0 is invalid and guarding with `if mid > 0` skips the legitimate whole-slice case; using `split_at_mut(4)` to probe the far edge panics instead of observing it.

**How to verify.** Run the block. Replace the checked call with `values.split_at_mut(4)` and the program panics with a `mid > len` message.

### Task 6: Transfer and justify

Design an API that exposes only the smallest mutable region needed by a transformation.

**Judging criteria.** A strong design passes only the slice the transformation touches, for example `&mut values[start..end]`, rather than `&mut Vec<T>`, so the callee cannot push, truncate or reach other elements. When two regions must change together, `split_at_mut` or `chunks_mut` proves they are disjoint. State one limitation: a slice cannot change the length of its owner, so growth stays with the caller.

## Mechanism and diagnostic reasoning

An exclusive reference grants mutation while preventing conflicting access to the same storage. The common rule is either shared readers or one exclusive borrower at a time. This is a capability rule about access, not a claim that the operating system has locked memory.

Small scopes make mutation ownership easier to see. After an exclusive borrow's last use, the owner can be used again. APIs such as split_at_mut safely produce disjoint mutable regions because they establish that the regions do not overlap. Do not reach for unsafe code merely because the compiler cannot infer a relationship you have not expressed.

`&mut value` creates exclusive access and the original binding must permit mutation. A function taking &mut T may update the borrowed value but does not own its eventual destruction. split_at_mut proves disjoint slices.

An exclusive borrow is not a thread lock. More mut annotations do not solve aliasing conflicts. Prefer safe disjointness APIs to manually asserting pointer safety.

## Review before continuing

Rebuild Example B (Mutate two proven-disjoint regions) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
