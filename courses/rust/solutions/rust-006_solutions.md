# rust-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-006_solution.rs](rust-006_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Maintain a sum invariant:** The loop changes only its accumulator, not the source ownership. The borrowed traversal totals twelve and retains the vector.

**Find the first position:** Position stops at the first matching element rather than returning the last repeated match. The first match is position one and absence stays explicit.

## Task answers

### Task 1: Predict and explain

Write the accumulator before and after every iteration.

**Written answer.** In Example A, `total` is 0 before the loop. Iteration 1 reads 2 and leaves 2; iteration 2 reads 4 and leaves 6; iteration 3 reads 6 and leaves 12. After the loop, `total` is 12 and `values` still has length 3.

**Why it is correct.** `for value in &values` yields a shared reference to each element in order, and `total += value` adds through it. The loop borrows rather than consumes the vector, so the length check after it still compiles.

**Plausible wrong approach.** Listing the values 2, 4, 6 as the accumulator's states confuses the element with the running total. Writing `for value in values` would also change the answer to the later check: it moves the vector, and `values.len()` becomes E0382.

**How to verify.** Add `let mut states = vec![total];` before the loop and `states.push(total);` inside it, then assert `states == vec![0, 2, 6, 12]`.

### Task 2: Guided modification

Skip negative values while preserving a clear invariant.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let values = [4, -2, 5, -7, 1];
    let mut total = 0;
    let mut skipped = 0;
    for value in values {
        if value < 0 {
            skipped += 1;
            continue;
        }
        total += value;
    }
    assert_eq!(total, 10);
    assert_eq!(skipped, 2);
    assert_eq!(
        total,
        values.iter().filter(|value| **value >= 0).sum::<i32>()
    );
    Ok(())
}
```

**Observe:** The non-negative values 4, 5 and 1 sum to 10, two negatives are skipped, and the loop agrees with an independent filter-and-sum.

The invariant is that after each iteration `total` equals the sum of the non-negative values seen so far and `skipped` counts the rest. `continue` leaves the accumulator untouched for -2 and -7, and counting them keeps the skip visible.

**Plausible wrong approach.** Clamping with `total += value.max(0)` gets the same 10 but loses the count of discarded readings, so a batch that was mostly negative looks as healthy as a clean one.

**How to verify.** Run the block. Remove `continue` and the total becomes 1, so the first assertion fails with `left: 1` and `right: 10`.

### Task 3: Independent construction

Implement a first-match search with Option output.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn first_index(values: &[i32], target: i32) -> Option<usize> {
        for (index, value) in values.iter().enumerate() {
            if *value == target {
                return Some(index);
            }
        }
        None
    }
    assert_eq!(first_index(&[5, 7, 7], 7), Some(1));
    assert_eq!(first_index(&[5, 7], 9), None);
    assert_eq!(first_index(&[], 1), None);
    Ok(())
}
```

**Observe:** The first 7 is at index 1; a missing target and an empty slice give None.

Option keeps not-found separate from every valid index, and the loop stops at the first match.

### Task 4: Diagnose a defect

Diagnose an inclusive loop bound used as an array index.

**Written answer.** The defect is `for index in 0..=values.len() { total += values[index]; }`. With three values the last index is 3, and the run panics with `index out of bounds: the len is 3 but the index is 3`. Use the exclusive range `0..values.len()`, or better, iterate the values directly with `for value in &values`.

**Why it is correct.** Valid indices of a length-3 vector are 0, 1 and 2. `..=` includes its end, so it produces one index past the last element; direct iteration never produces an index at all.

**Plausible wrong approach.** Subtracting one, `0..=values.len() - 1`, works for three values but underflows `usize` for an empty vector and panics with `attempt to subtract with overflow` before the loop starts.

**How to verify.** Run the faulty loop on `[2, 4, 6]` and read the panic naming index 3. After the fix, `total` is 12, and running the same loop on an empty vector leaves it 0.

### Task 5: Boundary evidence

Test empty, singleton and repeated-match sequences.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let empty: [i32; 0] = [];
    assert_eq!(empty.iter().position(|value| *value == 8), None);
    assert_eq!(empty.iter().sum::<i32>(), 0);
    assert_eq!([8].iter().position(|value| *value == 8), Some(0));
    assert_eq!([3].iter().position(|value| *value == 8), None);
    let repeated = [8, 8, 8];
    assert_eq!(repeated.iter().position(|value| *value == 8), Some(0));
    assert_eq!(repeated.iter().rposition(|value| *value == 8), Some(2));
    assert_eq!(repeated.iter().filter(|value| **value == 8).count(), 3);
    Ok(())
}
```

**Observe:** An empty slice has no match and sums to 0; a singleton 8 is found at 0 and a singleton 3 is not; in [8, 8, 8] the first match is 0, the last is 2 and there are 3 matches.

Each sequence shape exercises a different stop: no iterations, a match on the only element, and early stopping at the first of several matches. `rposition` and the count show that the search really did stop early rather than missing the later copies.

**Plausible wrong approach.** Returning the last matching index by keeping a `found = Some(index)` variable without stopping passes the empty and singleton cases but returns Some(2) for the repeated case.

**How to verify.** Run the block; every check is silent and `rust-006: passed` prints. Swap `position` for `rposition` in the first repeated check and it fails with `left: Some(2)`.

### Task 6: Transfer and justify

Design a bounded retry loop and state both its progress measure and its effect policy.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Invariant**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A loop repeats a state transition. An invariant explains what remains true, and a termination argument explains why repetition stops. For a sum, the accumulator equals the values already processed. For a search, the inspected prefix contains no earlier match before the chosen result.

For-in consumes an iterable, so ownership of the sequence or its borrowed view matters. Iterating an array of small Copy values can look similar to borrowing a vector, but the types determine what remains available. Use iterator adapters when they expose intent, and use an explicit loop when intermediate state or early exits need explanation.

`for value in &values` borrows elements. `enumerate` supplies traversal positions. `break` exits a loop, and loop itself can return a value through break value. An exclusive range uses `0..n`.

An iterator can consume values or borrow them depending on its construction. A position is not automatically a valid index in a different collection. Avoid unbounded loops without a deliberate stop and cancellation policy.

## Review before continuing

Run the reference and confirm that it prints `rust-006: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
