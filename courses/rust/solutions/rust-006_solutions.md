# rust-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-006_solution.rs](rust-006_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Maintain a sum invariant:** The loop changes only its accumulator, not the source ownership. The borrowed traversal totals twelve and retains the vector.

**Find the first position:** Position stops at the first matching element rather than returning the last repeated match. The first match is position one and absence stays explicit.

## Task answers

### Task 1: Predict and explain

Write the accumulator before and after every iteration.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The loop changes only its accumulator, not the source ownership. The borrowed traversal totals twelve and retains the vector.

### Task 2: Guided modification

Skip negative values while preserving a clear invariant.

No separate reference answer has been written for this task. Start from Example B: Position stops at the first matching element rather than returning the last repeated match. The first match is position one and absence stays explicit.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An iterator can consume values or borrow them depending on its construction. A position is not automatically a valid index in a different collection. Avoid unbounded loops without a deliberate stop and cancellation policy.

### Task 5: Boundary evidence

Test empty, singleton and repeated-match sequences.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Maintain a sum invariant) and Example B (Find the first position).

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
