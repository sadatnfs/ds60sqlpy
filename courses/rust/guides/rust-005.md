# rust-005: Expressions, branches and exhaustive matches

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-004`

## Learning objectives

Write a negative, zero and positive classifier. Then choose explicit enum matches or a wildcard for a finite application state model.

## Purpose and mental model

Rust treats many control-flow constructs as expressions producing values. An if expression must return compatible types from its branches. This encourages deriving one result instead of initializing a mutable variable and assigning it inconsistently on several paths.

Match handles patterns and requires coverage of possibilities. A broad wildcard can be useful for invalid numeric ranges but can hide newly added enum cases. Make boundaries explicit and test adjacent inputs. A correct normal example does not prove that an inclusive versus exclusive threshold is right.

## Vocabulary and concepts

**Expression:** Code that produces a value.

**Pattern:** A rule matching a value shape or category.

**Exhaustiveness:** Coverage of every possible input category.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`let label = if condition { "yes" } else { "no" };` uses a branch result. The final expression in a block has no semicolon when it supplies the value. `0..=59` is an inclusive pattern range.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Choose a value with if

Both branches return the same kind of value, so the result has one static type.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let count = 3;
        let label = if count > 0 { "present" } else { "empty" };
        assert_eq!(label, "present");
    }
    println!("rust-005: passed");
    Ok(())
}
```

**Observe:** The branch expression supplies one immutable label.

### Example B: Classify explicit boundaries

A tiny boundary fixture rejects an off-by-one policy error.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let classify = |score| match score {
            0..=59 => "retry",
            60..=100 => "pass",
            _ => "invalid",
        };
        assert_eq!(classify(59), "retry");
        assert_eq!(classify(60), "pass");
        assert_eq!(classify(101), "invalid");
    }
    println!("rust-005: passed");
    Ok(())
}
```

**Observe:** The transition at sixty and the invalid upper range are distinct.

## Exercises

1. **Predict and explain.** Identify the value produced by each branch.

2. **Guided modification.** Change the threshold and update neighboring tests.

3. **Independent construction.** Write a negative, zero and positive classifier.

4. **Diagnose a defect.** Diagnose a semicolon that changes a branch result into unit.

5. **Boundary evidence.** Test both valid endpoints and one value beyond each.

6. **Transfer and justify.** Choose explicit enum matches or a wildcard for a finite application state model.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A semicolon can change a block value. Match arm order matters when patterns overlap. A wildcard that hides an unhandled domain state weakens maintenance feedback.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Expression, Pattern, Exhaustiveness without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-005: Expressions, branches and exhaustive matches.
Read courses/rust/guides/rust-005.md and courses/rust/lessons/rust-005.rs. Prerequisites: rust-004.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-005_solution.rs and
courses/rust/solutions/rust-005_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
