# rust-007: Functions, return values and contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-006`

## Learning objectives

Write a pure rectangle-area function with a documented valid range. Then choose owned or borrowed inputs for an API that stores data after the call.

## Purpose and mental model

A function should expose accepted inputs, result meaning, mutation and failure. A compact signature cannot tell the whole story, so write the domain contract beside it. Begin with pure computations that return a value; their behavior is easy to test because they do not depend on hidden state.

Rust makes ownership transfer part of an argument type. Passing an integer copies it, while passing an owned String normally moves it. Borrowing can let a function inspect text while leaving ownership with the caller. Choose the signature from the needed capability rather than adding clones until the compiler is quiet.

## Vocabulary and concepts

**Parameter:** A typed input in a function declaration.

**Return type:** The type of a function result.

**Borrowed interface:** An interface accepting temporary access rather than ownership.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`fn double(value: i32) -> i32` declares input and output types. A final expression returns its value without a semicolon. `&str` accepts borrowed text, including literals and owned String views.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Return a derived integer

The Copy semantics of this small value permit reuse without transferring an owned allocation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn double(value: i32) -> i32 {
            value * 2
        }
        let original = 7;
        assert_eq!(double(original), 14);
        assert_eq!(original, 7);
    }
    println!("rust-007: passed");
    Ok(())
}
```

**Observe:** The integer remains available after the call.

### Example B: Accept different text owners

The function needs only a read-only text view, so taking String would impose unnecessary ownership transfer.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn starts_with_p(text: &str) -> bool {
            text.starts_with('p')
        }
        let owned = String::from("pear");
        assert!(starts_with_p(&owned));
        assert!(!starts_with_p("apple"));
        assert_eq!(owned, "pear");
    }
    println!("rust-007: passed");
    Ok(())
}
```

**Observe:** One borrowed interface accepts owned text and a literal.

## Exercises

1. **Predict and explain.** Identify which arguments are copied and which are borrowed.

2. **Guided modification.** Add a function computing a labeled length from &str.

3. **Independent construction.** Write a pure rectangle-area function with a documented valid range.

4. **Diagnose a defect.** Diagnose an accidental semicolon on the final return expression.

5. **Boundary evidence.** Test empty text and zero dimensions.

6. **Transfer and justify.** Choose owned or borrowed inputs for an API that stores data after the call.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A reference is not permission to retain data beyond its lifetime. Pure-looking names can hide side effects. Do not clone an entire buffer when a borrow expresses the actual requirement.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Parameter, Return type, Borrowed interface without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-007: Functions, return values and contracts.
Read courses/rust/guides/rust-007.md and courses/rust/lessons/rust-007.rs. Prerequisites: rust-006.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-007_solution.rs and
courses/rust/solutions/rust-007_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
