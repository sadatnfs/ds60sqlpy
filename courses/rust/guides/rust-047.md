# rust-047: Properties, compile-fail cases and regression design

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-046`

## Learning objectives

Write a property checking an Arrow filter's output count against its Boolean mask. Then design an external fuzzing and compile-fail plan with reproducible seeds, minimized failures and clear acceptance scope.

## Purpose and mental model

Advanced verification combines examples, properties and boundary-specific evidence. A property such as sorting preserving element multiplicity can expose mistakes that one expected list misses. Compile-fail tests can preserve an API's ownership or visibility restrictions, but they belong to a deliberately prepared test harness rather than an ordinary successful runtime reference.

Fuzzing and property-testing crates are valuable external tools, not hidden dependencies in this pad. Start with deterministic exhaustive enumeration over a small bounded domain and an independent oracle. Keep minimized counterexamples when a failure appears. Never weaken an invariant to accommodate a wrong implementation merely because a large suite is expensive.

## Vocabulary and concepts

**Property test:** A test of a relationship across many inputs.

**Counterexample:** An input disproving a claimed property.

**Compile-fail test:** Evidence that an invalid program is rejected by the intended language contract.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Nested loops can enumerate a small input space reproducibly. A sorted clone can be compared with the original through a frequency map. Compile diagnostics should be categorized by the violated rule rather than fragile full-message text.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Check a bounded algebraic property

The range avoids overflow, making the mathematical property appropriate to this representation.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        for a in 0_i32..10 { for b in 0_i32..10 { assert_eq!(a + b, b + a); } }
        assert_eq!(10 * 10, 100);
    }
    println!("rust-047: passed");
    Ok(())
}
```

**Observe:** One hundred bounded pairs satisfy the addition relation.

### Example B: Check order and multiplicity separately

Order alone would not reject a broken implementation that drops duplicates.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let original = vec![3, 1, 3, 2];
        let mut sorted = original.clone(); sorted.sort();
        assert!(sorted.windows(2).all(|pair| pair[0] <= pair[1]));
        for value in 1..=3 { assert_eq!(original.iter().filter(|item| **item == value).count(), sorted.iter().filter(|item| **item == value).count()); }
    }
    println!("rust-047: passed");
    Ok(())
}
```

**Observe:** Sorting establishes order without losing the repeated three.

## Exercises

1. **Predict and explain.** State the assumptions making the bounded arithmetic property valid.

2. **Guided modification.** Add a small exhaustive test for checked quantity addition.

3. **Independent construction.** Write a property checking an Arrow filter's output count against its Boolean mask.

4. **Diagnose a defect.** Diagnose a sortedness test that never checks retained values.

5. **Boundary evidence.** Preserve empty, duplicate and all-null regression fixtures.

6. **Transfer and justify.** Design an external fuzzing and compile-fail plan with reproducible seeds, minimized failures and clear acceptance scope.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A property can be too weak to distinguish incorrect implementations. Integer overflow can invalidate a mathematical law's assumed domain. Compiler message wording may change even when the underlying rule remains correct.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Property test, Counterexample, Compile-fail test without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-047: Properties, compile-fail cases and regression design.
Read courses/rust/guides/rust-047.md and courses/rust/lessons/rust-047.rs. Prerequisites: rust-046.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-047_solution.rs and
courses/rust/solutions/rust-047_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
