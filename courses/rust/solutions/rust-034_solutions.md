# rust-034: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-034_solution.rs](rust-034_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reconstruct a bounded borrowed view:** The safety proof is tied to the pointer origin and exact length, not merely to the pointer being non-null. The reconstructed view matches the live initialized array.

**Prefer the safe operation when available:** Unsafe should be justified by a real boundary, not used because pointer syntax appears advanced. A normal slice provides the same read contract without a manual safety burden.

## Task answers

### Task 1: Predict and explain

State every precondition needed by from_raw_parts.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The safety proof is tied to the pointer origin and exact length, not merely to the pointer being non-null. The reconstructed view matches the live initialized array.

### Task 2: Guided modification

Reduce the borrowed length while retaining valid initialized storage.

No separate reference answer has been written for this task. Start from Example B: Unsafe should be justified by a real boundary, not used because pointer syntax appears advanced. A normal slice provides the same read contract without a manual safety burden.

### Task 3: Independent construction

Write a safe wrapper specification before considering an unsafe implementation.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Never test undefined behavior by hoping it crashes predictably. A null check is insufficient to prove pointer validity. Panics crossing an incompatible FFI boundary need a deliberate policy.

### Task 5: Boundary evidence

Review zero-length and alignment rules without executing undefined behavior.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Reconstruct a bounded borrowed view) and Example B (Prefer the safe operation when available).

### Task 6: Transfer and justify

Design an FFI ownership document stating allocation, release, encoding and error conventions.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Unsafe operation**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Unsafe permits a small set of operations whose correctness the compiler cannot fully establish. It does not disable every safety rule or turn wrong memory access into valid behavior. Each unsafe block needs an argument covering pointer validity, alignment, initialized length, aliasing and lifetime. Keep the block small and wrap it in a safe interface that enforces those conditions.

Foreign-function interfaces add an ABI contract: layout, calling convention, string encoding, ownership and failure signaling must agree across languages. A successful link does not prove those agreements. The ordinary fixture uses a pointer obtained from a live array and immediately reconstructs a read-only slice under a documented invariant, without calling undeclared native libraries.

`as_ptr` borrows an address from live storage. `slice::from_raw_parts` is unsafe because the caller supplies validity and length. A SAFETY comment explains why this exact operation satisfies its preconditions.

Never test undefined behavior by hoping it crashes predictably. A null check is insufficient to prove pointer validity. Panics crossing an incompatible FFI boundary need a deliberate policy.

## Review before continuing

Run the reference and confirm that it prints `rust-034: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
