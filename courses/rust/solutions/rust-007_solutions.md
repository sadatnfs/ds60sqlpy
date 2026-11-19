# rust-007: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-007_solution.rs](rust-007_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return a derived integer:** The Copy semantics of this small value permit reuse without transferring an owned allocation. The integer remains available after the call.

**Accept different text owners:** The function needs only a read-only text view, so taking String would impose unnecessary ownership transfer. One borrowed interface accepts owned text and a literal.

## Task answers

### Task 1: Predict and explain

Identify which arguments are copied and which are borrowed.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The Copy semantics of this small value permit reuse without transferring an owned allocation. The integer remains available after the call.

### Task 2: Guided modification

Add a function computing a labeled length from &str.

No separate reference answer has been written for this task. Start from Example B: The function needs only a read-only text view, so taking String would impose unnecessary ownership transfer. One borrowed interface accepts owned text and a literal.

### Task 3: Independent construction

Write a pure rectangle-area function with a documented valid range.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// Area of a rectangle; both sides must be at most 65_535.
    fn area(width: u32, height: u32) -> u32 {
        assert!(width <= 65_535 && height <= 65_535);
        width * height
    }
    assert_eq!(area(3, 4), 12);
    assert_eq!(area(0, 9), 0);
    assert_eq!(area(65_535, 65_535), 4_294_836_225);
    Ok(())
}
```

**Observe:** 3 by 4 gives 12, a zero side gives 0, and the documented maximum still fits in u32.

The documented range is exactly the one whose product fits in u32, and the function checks it, so callers cannot reach an overflow.

### Task 4: Diagnose a defect

Diagnose an accidental semicolon on the final return expression.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A reference is not permission to retain data beyond its lifetime. Pure-looking names can hide side effects. Do not clone an entire buffer when a borrow expresses the actual requirement.

### Task 5: Boundary evidence

Test empty text and zero dimensions.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Return a derived integer) and Example B (Accept different text owners).

### Task 6: Transfer and justify

Choose owned or borrowed inputs for an API that stores data after the call.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Parameter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A function should expose accepted inputs, result meaning, mutation and failure. A compact signature cannot tell the whole story, so write the domain contract beside it. Begin with pure computations that return a value; their behavior is easy to test because they do not depend on hidden state.

Rust makes ownership transfer part of an argument type. Passing an integer copies it, while passing an owned String normally moves it. Borrowing can let a function inspect text while leaving ownership with the caller. Choose the signature from the needed capability rather than adding clones until the compiler is quiet.

`fn double(value: i32) -> i32` declares input and output types. A final expression returns its value without a semicolon. `&str` accepts borrowed text, including literals and owned String views.

A reference is not permission to retain data beyond its lifetime. Pure-looking names can hide side effects. Do not clone an entire buffer when a borrow expresses the actual requirement.

## Review before continuing

Run the reference and confirm that it prints `rust-007: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
