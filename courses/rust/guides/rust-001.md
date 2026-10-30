# rust-001: Source, compilation and the first Rust program

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: None. Begin with the source file and visible result.

## Learning objectives

Compute the capacity of three shelves with eight books each. Then model a three-level capacity calculation and explain every intermediate value.

## Purpose and mental model

Rust checks source before producing a native executable. A compiler diagnostic means the program has not reached its entrypoint. A panic during execution means an operation violated a checked assumption. Successful output means only the path that actually ran completed. Keep these forms of evidence separate when learning to diagnose a program.

The classroom supplies a pinned compiler and Arrow library inside Linux Docker. The browser sends a single source file, not a Cargo project or arbitrary shell command. Start by tracing a tiny calculation and independently checking its result. This builds the habit of distinguishing observed behavior from a printed success claim.

## Vocabulary and concepts

**Compiler:** A tool checking source and producing executable code.

**Macro:** Syntax expanded before ordinary compilation.

**Panic:** An execution failure indicating an unrecovered violated assumption.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`fn main` declares the entry function. `let` introduces a binding. `println!` is a macro, indicated by the exclamation mark. `assert_eq!` compares actual and expected values and panics on disagreement. A semicolon turns an expression into a statement whose value is discarded.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Check a greeting

The explicit check connects a value to its expected observation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let greeting = "Hello, Rust";
        assert_eq!(greeting, "Hello, Rust");
        println!("{greeting}");
    }
    println!("rust-001: passed");
    Ok(())
}
```

**Observe:** Hello, Rust appears before the lesson marker.

### Example B: Calculate instead of copying output

A second check rejects a plausible wrong operator rather than merely confirming that printing works.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let rows = 4;
        let seats_per_row = 6;
        let seats = rows * seats_per_row;
        assert_eq!(seats, 24);
        assert_ne!(seats, rows + seats_per_row);
    }
    println!("rust-001: passed");
    Ok(())
}
```

**Observe:** The calculated capacity is 24, while addition would give 10.

## Exercises

1. **Predict and explain.** Predict the greeting and final marker order.

2. **Guided modification.** Change the greeting and keep its expected value independent.

3. **Independent construction.** Compute the capacity of three shelves with eight books each.

4. **Diagnose a defect.** Remove a closing brace temporarily and classify the compiler diagnostic.

5. **Boundary evidence.** Check zero shelves and one shelf.

6. **Transfer and justify.** Model a three-level capacity calculation and explain every intermediate value.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A compiler success does not establish business correctness. Do not replace a failing assertion with a success print. The Result-returning main wrapper is scaffolding for later error propagation; its full meaning is taught in the error chapters.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Compiler, Macro, Panic without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-001: Source, compilation and the first Rust program.
Read courses/rust/guides/rust-001.md and courses/rust/lessons/rust-001.rs. Prerequisites: none.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-001_solution.rs and
courses/rust/solutions/rust-001_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
