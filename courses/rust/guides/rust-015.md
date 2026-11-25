# rust-015: Result, error propagation and recoverable failure

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-014`

## Learning objectives

Propagate recoverable errors with Result and ? while keeping each failure meaningful. The central exercise is task 3: Write a function using ? to compose two fallible steps.

## Purpose and mental model

Result distinguishes Ok(value) from Err(error). It is appropriate when failure has a reason that a caller should inspect or propagate. Parsing text naturally returns a Result because malformed input is different from an ordinary missing lookup. A robust boundary should preserve the distinction between syntax failure and domain rejection.

The question-mark operator returns early with an error while continuing with the successful value. It is a control-flow shortcut with a clear type contract, not an instruction to ignore failure. The main wrapper used in this course can propagate errors to an unsuccessful process outcome. Production APIs should choose error types that expose useful categories without leaking sensitive raw input.

## Vocabulary and concepts

**Result:** A success-or-error value with typed payloads.

**Propagation:** Returning a failure to a caller rather than hiding it.

**Error category:** A meaningful classification for recovery or reporting.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-015: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`Result<T,E>` carries a success type and an error type. `?` unwraps success or converts and returns an error. map_err translates an error deliberately. match handles both paths explicitly.

**Reading Example A (Parse and validate separately, code below).** `parse_quantity` returns `Result<i32, &'static str>`: `Ok` carries a valid quantity and `Err` carries a fixed message. `text.parse()` gets its target type from the annotation `let value: i32` and returns `Result<i32, ParseIntError>`. `map_err(|_| "not an integer")` replaces the library error with this function's message, and the closure's `_` discards the original error value. The `?` operator then either unwraps an `Ok` into `value` or returns the `Err` from the function immediately. A separate `if` enforces the domain rule after parsing succeeds, with its own `return Err(...)`. The final `Ok(value)` has no semicolon, so it is the function's result.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Parse and validate separately

Parsing establishes a representation; the second check enforces the domain.

```rust
fn parse_quantity(text: &str) -> Result<i32, &'static str> {
    let value: i32 = text.parse().map_err(|_| "not an integer")?;
    if value < 0 {
        return Err("negative quantity");
    }
    Ok(value)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(parse_quantity("3"), Ok(3));
        assert_eq!(parse_quantity("bad"), Err("not an integer"));
        assert_eq!(parse_quantity("-1"), Err("negative quantity"));
    }
    println!("rust-015: passed");
    Ok(())
}
```

**Observe:** Malformed text and negative quantity preserve different reasons.

### Example B: Collect only explicitly accepted values

Converting to Option is deliberate here because the separate count retains rejection evidence; a real importer may need the full reasons.

```rust
fn parse_quantity(text: &str) -> Result<i32, &'static str> {
    let value: i32 = text.parse().map_err(|_| "not an integer")?;
    if value < 0 {
        return Err("negative quantity");
    }
    Ok(value)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let inputs = ["2", "bad", "3"];
        let accepted: Vec<_> = inputs
            .iter()
            .filter_map(|text| parse_quantity(text).ok())
            .collect();
        assert_eq!(accepted, vec![2, 3]);
        assert_eq!(inputs.len() - accepted.len(), 1);
    }
    println!("rust-015: passed");
    Ok(())
}
```

**Observe:** Two accepted values and one rejection are accounted for.

## Exercises

1. **Predict and explain.** Trace the success, parse-error and domain-error paths.

2. **Guided modification.** Add an application maximum quantity with a separate error category.

3. **Independent construction.** Write a function using ? to compose two fallible steps.

4. **Diagnose a defect.** Diagnose replacing every Err with zero.

5. **Boundary evidence.** Test empty, zero, negative and overflowing textual input.

6. **Transfer and justify.** Choose a public error enum and explain which internal details should remain private.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Calling .ok discards the error reason. A catch-all fallback can turn data loss into success. Panic is generally the wrong interface for expected invalid external input.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Parse and validate separately) before changing anything, and confirm its observation: Malformed text and negative quantity preserve different reasons.
2. Compare Example B (Collect only explicitly accepted values) with Example A and name the first line whose behavior differs. Its observation is: Two accepted values and one rejection are accounted for.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Calling .ok discards the error reason.

Tempting approaches to rule out before you compare:

- **Task 1.** Reading `"-1"` as a parse failure confuses representation with domain. `-1` is a perfectly valid `i32`; it is the application rule that refuses it.
- **Task 2.** Folding the limit into the parse step with `text.parse::<i32>().ok().filter(|v| *v <= MAX_QUANTITY)` returns `None` for 1001, for `bad` and for `-1` alike, so the caller can no longer tell a typo from an oversized order.
- **Task 5.** Assuming `"2147483648"` would wrap to a negative number and be rejected as negative ignores that `parse` checks the range and never wraps.

## Self-check and next step

Trace `"3"`, `"bad"` and `"-1"` through `parse_quantity`: which step rejects each, and which message does each `Err` carry? Why does replacing every `Err` with 0 corrupt a total rather than just hide a message? What does `.ok()` inside `filter_map` discard, and how does Example B still account for the rejected value?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 9.2 Recoverable Errors with Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) for what the `?` operator expands to.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-015: Result, error propagation and recoverable failure.
Read courses/rust/guides/rust-015.md and courses/rust/lessons/rust-015.rs. Prerequisites: rust-014.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-015_solution.rs and
courses/rust/solutions/rust-015_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
