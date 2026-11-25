# rust-022: Custom errors and preserving causes

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-021`

## Learning objectives

Define custom error types that keep their causes reachable through source. The central exercise is task 3: Define a custom error for an importer with syntax and storage boundaries.

## Purpose and mental model

A public error type should expose categories a caller can act on. A string alone may be readable but makes structured recovery brittle. An enum can distinguish malformed input, missing resources and storage failure. Implementing Display supplies a human description while Error can preserve an underlying cause.

Translate errors at a meaningful boundary and avoid logging or wrapping the same failure at every layer. The question-mark operator can use From conversions to preserve composition. Never expose credentials or full private payloads merely to make an error verbose. Keep a small safe context such as a field name or operation stage.

## Vocabulary and concepts

**Error enum:** A closed set of meaningful failure categories.

**Display:** A trait producing a human-readable representation.

**Cause chain:** The relationship between a domain failure and an underlying error.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::error` and `std::fmt`. A passing run prints `rust-022: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Implement std::fmt::Display and std::error::Error for a domain error. map_err can translate a lower-level category. A match over the enum preserves structured decisions without parsing an error string.

**Reading Example A (Preserve a domain category, code below).** `#[derive(Debug)]` asks the compiler to generate a `Debug` implementation, which `std::error::Error` requires alongside `Display`. The hand-written `Display` impl uses `match self` to choose the message for each variant, and `write!(f, ...)` sends it to the formatter. `impl std::error::Error for InputError {}` is empty because every method of the trait has a default. In `validated`, `text.parse()` infers `i32` from how `value` is compared and returned, and `map_err(|_| InputError::Malformed)` converts the library error into a domain variant before `?` propagates it. `matches!` checks a value against a pattern and returns the `bool` that `assert!` requires.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Preserve a domain category

A caller can decide from the type rather than inspect a fragile message substring.

```rust
#[derive(Debug)]
enum InputError {
    Malformed,
    Negative,
}
impl std::fmt::Display for InputError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", match self { Self::Malformed => "quantity is not an integer", Self::Negative => "quantity must be nonnegative" })
    }
}
impl std::error::Error for InputError {}
fn validated(text: &str) -> Result<i32, InputError> {
    let value = text.parse().map_err(|_| InputError::Malformed)?;
    if value < 0 {
        Err(InputError::Negative)
    } else {
        Ok(value)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert!(matches!(validated("-1"), Err(InputError::Negative)));
        assert!(matches!(validated("bad"), Err(InputError::Malformed)));
    }
    println!("rust-022: passed");
    Ok(())
}
```

**Observe:** Negative and malformed inputs remain separate variants.

### Example B: Render a safe message

Useful diagnostics can describe the contract while avoiding unnecessary payload disclosure.

```rust
#[derive(Debug)]
enum InputError {
    Malformed,
    Negative,
}
impl std::fmt::Display for InputError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", match self { Self::Malformed => "quantity is not an integer", Self::Negative => "quantity must be nonnegative" })
    }
}
impl std::error::Error for InputError {}
fn validated(text: &str) -> Result<i32, InputError> {
    let value = text.parse().map_err(|_| InputError::Malformed)?;
    if value < 0 {
        Err(InputError::Negative)
    } else {
        Ok(value)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let error = InputError::Negative;
        assert_eq!(error.to_string(), "quantity must be nonnegative");
        assert_eq!(validated("3").unwrap(), 3);
    }
    println!("rust-022: passed");
    Ok(())
}
```

**Observe:** The message explains the rule without repeating raw input.

## Exercises

1. **Predict and explain.** Match each failure to its domain variant.

2. **Guided modification.** Add a maximum-quantity category.

3. **Independent construction.** Define a custom error for an importer with syntax and storage boundaries.

4. **Diagnose a defect.** Diagnose branching on a translated message string.

5. **Boundary evidence.** Test zero, malformed and out-of-range text.

6. **Transfer and justify.** Choose which layer translates an internal error into a public response and what context it may expose.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A generic string loses structured recovery information. Unwrap belongs only where a nearby fixture invariant establishes success. Do not map cancellation or unknown outcomes into an ordinary empty result.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Preserve a domain category) before changing anything, and confirm its observation: Negative and malformed inputs remain separate variants.
2. Compare Example B (Render a safe message) with Example A and name the first line whose behavior differs. Its observation is: The message explains the rule without repeating raw input.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A generic string loses structured recovery information.

Tempting approaches to rule out before you compare:

- **Task 1.** Mapping `"-1"` to `Malformed` because it contains a sign confuses text shape with the domain rule, since `i32` parses negative numbers normally.
- **Task 2.** Returning `Err(InputError::Negative)` for oversized values because it is the nearest existing variant compiles and shows a false message saying the quantity must be nonnegative.
- **Task 5.** Expecting `"-2147483649"` to be `Negative` assumes the sign is checked before the range. Parsing runs first and fails, so the domain check never sees it.

## Self-check and next step

Why does `validated` map a parse failure to `InputError::Malformed` instead of returning the `ParseIntError`, and what does the caller gain and lose? Why does the `Display` text "quantity must be nonnegative" state the rule without echoing the input? Why do Example A's `matches!` checks on variants survive a rewording of the message when a comparison of `to_string()` output would not?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::error::Error` documentation](https://doc.rust-lang.org/std/error/trait.Error.html) for the `Display` and `Debug` requirements and the optional `source` chain.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-022: Custom errors and preserving causes.
Read courses/rust/guides/rust-022.md and courses/rust/lessons/rust-022.rs. Prerequisites: rust-021.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-022_solution.rs and
courses/rust/solutions/rust-022_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
