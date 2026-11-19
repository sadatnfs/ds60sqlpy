# rust-015: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-015_solution.rs](rust-015_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Parse and validate separately:** Parsing establishes a representation; the second check enforces the domain. Malformed text and negative quantity preserve different reasons.

**Collect only explicitly accepted values:** Converting to Option is deliberate here because the separate count retains rejection evidence; a real importer may need the full reasons. Two accepted values and one rejection are accounted for.

## Task answers

### Task 1: Predict and explain

Trace the success, parse-error and domain-error paths.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Parsing establishes a representation; the second check enforces the domain. Malformed text and negative quantity preserve different reasons.

### Task 2: Guided modification

Add an application maximum quantity with a separate error category.

No separate reference answer has been written for this task. Start from Example B: Converting to Option is deliberate here because the separate count retains rejection evidence; a real importer may need the full reasons. Two accepted values and one rejection are accounted for.

### Task 3: Independent construction

Write a function using ? to compose two fallible steps.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file. It uses `parse_quantity` from the lesson's helpers, defined in the reference program.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn doubled_quantity(text: &str) -> Result<i32, &'static str> {
        let value = parse_quantity(text)?;
        value.checked_mul(2).ok_or("quantity too large")
    }
    assert_eq!(doubled_quantity("4"), Ok(8));
    assert_eq!(doubled_quantity("bad"), Err("not an integer"));
    assert_eq!(doubled_quantity("-3"), Err("negative quantity"));
    Ok(())
}
```

**Observe:** 4 doubles to Ok(8); bad text and -3 return their original errors.

The ? operator returns the parse error unchanged, so each failure keeps the message of the step that produced it.

### Task 4: Diagnose a defect

Diagnose replacing every Err with zero.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Calling .ok discards the error reason. A catch-all fallback can turn data loss into success. Panic is generally the wrong interface for expected invalid external input.

### Task 5: Boundary evidence

Test empty, zero, negative and overflowing textual input.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Parse and validate separately) and Example B (Collect only explicitly accepted values).

### Task 6: Transfer and justify

Choose a public error enum and explain which internal details should remain private.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Result**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Result distinguishes Ok(value) from Err(error). It is appropriate when failure has a reason that a caller should inspect or propagate. Parsing text naturally returns a Result because malformed input is different from an ordinary missing lookup. A robust boundary should preserve the distinction between syntax failure and domain rejection.

The question-mark operator returns early with an error while continuing with the successful value. It is a control-flow shortcut with a clear type contract, not an instruction to ignore failure. The main wrapper used in this course can propagate errors to an unsuccessful process outcome. Production APIs should choose error types that expose useful categories without leaking sensitive raw input.

`Result<T,E>` carries a success type and an error type. `?` unwraps success or converts and returns an error. map_err translates an error deliberately. match handles both paths explicitly.

Calling .ok discards the error reason. A catch-all fallback can turn data loss into success. Panic is generally the wrong interface for expected invalid external input.

## Review before continuing

Run the reference and confirm that it prints `rust-015: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
