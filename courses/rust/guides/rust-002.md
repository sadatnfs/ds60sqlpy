# rust-002: Bindings, mutability and type inference

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-001`

## Learning objectives

Write a running total with fixed input and mutable accumulator. Then choose shadowing or distinct names for parsing stages and justify readability.

## Purpose and mental model

Rust bindings are immutable by default. `mut` grants permission to change a binding's value. Immutability reduces the number of state transitions a reader must consider, but it is not a substitute for understanding ownership and interior mutability introduced later. Prefer a new derived value when that expresses the operation clearly.

Type inference remains static: the compiler determines a concrete type from context. Shadowing introduces a new binding with the same name and can deliberately change its type. Reassignment instead changes the value of an existing mutable binding and must preserve its type. Use either technique to expose meaning rather than obscure where a value came from.

## Vocabulary and concepts

**Binding:** A name associated with a value.

**Mutability:** Permission to change a value through a particular binding or reference.

**Shadowing:** Introducing a new binding with an existing name.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`let count: i32 = 3` annotates a type. `let mut total = 0` allows reassignment. `let text = text.len()` shadows the earlier name with a new binding. Integer suffixes such as `3_u64` constrain inference.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Expose an accumulator

Only the value requiring state transitions is declared mutable.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let per_box = 4;
        let mut total = 0;
        total += per_box;
        total += per_box;
        assert_eq!(total, 8);
    }
    println!("rust-002: passed");
    Ok(())
}
```

**Observe:** The mutable total changes while the fixed input remains 4.

### Example B: Shadow after a representation change

Shadowing can change type, but names must still explain whether a value is text, length or parsed quantity.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let count = "12";
        let count: usize = count.len();
        assert_eq!(count, 2);
        let explicit = 3_u64;
        assert_eq!(explicit + 1, 4);
    }
    println!("rust-002: passed");
    Ok(())
}
```

**Observe:** The new count is the text length, not the number twelve.

## Exercises

1. **Predict and explain.** Identify the static type and mutability of each binding.

2. **Guided modification.** Remove unnecessary mut declarations in a small program.

3. **Independent construction.** Write a running total with fixed input and mutable accumulator.

4. **Diagnose a defect.** Diagnose assigning a String to a mutable integer binding.

5. **Boundary evidence.** Test an empty input string and a zero accumulator.

6. **Transfer and justify.** Choose shadowing or distinct names for parsing stages and justify readability.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Immutable does not mean every object reachable through a type is deeply frozen. Shadowing can conceal a units change. Type inference is not dynamic typing.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Binding, Mutability, Shadowing without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-002: Bindings, mutability and type inference.
Read courses/rust/guides/rust-002.md and courses/rust/lessons/rust-002.rs. Prerequisites: rust-001.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-002_solution.rs and
courses/rust/solutions/rust-002_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
