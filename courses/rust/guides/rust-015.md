# rust-015: Result, error propagation and recoverable failure

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-014`

## Learning objectives

Write a function using ? to compose two fallible steps. Then choose a public error enum and explain which internal details should remain private.

## Purpose and mental model

Result distinguishes Ok(value) from Err(error). It is appropriate when failure has a reason that a caller should inspect or propagate. Parsing text naturally returns a Result because malformed input is different from an ordinary missing lookup. A robust boundary should preserve the distinction between syntax failure and domain rejection.

The question-mark operator returns early with an error while continuing with the successful value. It is a control-flow shortcut with a clear type contract, not an instruction to ignore failure. The main wrapper used in this course can propagate errors to an unsuccessful process outcome. Production APIs should choose error types that expose useful categories without leaking sensitive raw input.

## Vocabulary and concepts

**Result:** A success-or-error value with typed payloads.

**Propagation:** Returning a failure to a caller rather than hiding it.

**Error category:** A meaningful classification for recovery or reporting.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Result<T,E>` carries a success type and an error type. `?` unwraps success or converts and returns an error. map_err translates an error deliberately. match handles both paths explicitly.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Calling .ok discards the error reason. A catch-all fallback can turn data loss into success. Panic is generally the wrong interface for expected invalid external input.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Result, Propagation, Error category without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
