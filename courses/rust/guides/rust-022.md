# rust-022: Custom errors and preserving causes

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-021`

## Learning objectives

Define a custom error for an importer with syntax and storage boundaries. Then choose which layer translates an internal error into a public response and what context it may expose.

## Purpose and mental model

A public error type should expose categories a caller can act on. A string alone may be readable but makes structured recovery brittle. An enum can distinguish malformed input, missing resources and storage failure. Implementing Display supplies a human description while Error can preserve an underlying cause.

Translate errors at a meaningful boundary and avoid logging or wrapping the same failure at every layer. The question-mark operator can use From conversions to preserve composition. Never expose credentials or full private payloads merely to make an error verbose. Keep a small safe context such as a field name or operation stage.

## Vocabulary and concepts

**Error enum:** A closed set of meaningful failure categories.

**Display:** A trait producing a human-readable representation.

**Cause chain:** The relationship between a domain failure and an underlying error.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Implement std::fmt::Display and std::error::Error for a domain error. map_err can translate a lower-level category. A match over the enum preserves structured decisions without parsing an error string.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Preserve a domain category

A caller can decide from the type rather than inspect a fragile message substring.

```rust
#[derive(Debug)] enum InputError { Malformed, Negative }
impl std::fmt::Display for InputError { fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { write!(f, "{}", match self { Self::Malformed => "quantity is not an integer", Self::Negative => "quantity must be nonnegative" }) } }
impl std::error::Error for InputError {}
fn validated(text: &str) -> Result<i32, InputError> { let value = text.parse().map_err(|_| InputError::Malformed)?; if value < 0 { Err(InputError::Negative) } else { Ok(value) } }

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
#[derive(Debug)] enum InputError { Malformed, Negative }
impl std::fmt::Display for InputError { fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { write!(f, "{}", match self { Self::Malformed => "quantity is not an integer", Self::Negative => "quantity must be nonnegative" }) } }
impl std::error::Error for InputError {}
fn validated(text: &str) -> Result<i32, InputError> { let value = text.parse().map_err(|_| InputError::Malformed)?; if value < 0 { Err(InputError::Negative) } else { Ok(value) } }

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

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A generic string loses structured recovery information. Unwrap belongs only where a nearby fixture invariant establishes success. Do not map cancellation or unknown outcomes into an ordinary empty result.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Error enum, Display, Cause chain without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
