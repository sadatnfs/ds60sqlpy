# rust-024: Tests, assertions and useful counterexamples

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-023`

## Learning objectives

Write table-driven checks for a quantity validator. Then separate unit, integration, compile-fail and runtime evidence for a library change.

## Purpose and mental model

A test is strong when a plausible wrong implementation fails it. Derive expected results from the contract rather than copying the same formula into the assertion. Normal, boundary and invalid cases expose different assumptions. Properties such as idempotence can cover a wider relationship but do not replace concrete expected values.

Rust's built-in test harness runs functions marked test when compiling a test target. The classroom ordinary reference instead invokes always-active assertions through main. This keeps code execution distinct from a Cargo test workflow. A clean unit test does not prove filesystem configuration, network availability or deployment correctness.

## Vocabulary and concepts

**Test oracle:** An independent rule deciding whether behavior is correct.

**Regression case:** A fixture preserving a previously observed defect.

**Property:** A relationship expected across a family of values.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

assert and assert_eq remain active in ordinary builds, unlike debug_assert. A cfg(test) module belongs to a test compilation. Cargo test discovers unit, integration and documentation tests under their own contracts.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use independent expected cases

Literal expectations make the test independent of the implementation expression.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let cases = [(-2, 0), (0, 0), (3, 3)];
        for (input, expected) in cases { assert_eq!(input.max(0), expected); }
    }
    println!("rust-024: passed");
    Ok(())
}
```

**Observe:** Negative, zero and positive cases satisfy the stated clamp rule.

### Example B: Reject a plausible wrong boundary

The property alone would not necessarily distinguish every wrong constant implementation.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let wrong = |value: i32| if value <= 0 { 1 } else { value };
        assert_ne!(wrong(0), 0);
        assert_eq!((-4_i32).max(0).max(0), (-4_i32).max(0));
    }
    println!("rust-024: passed");
    Ok(())
}
```

**Observe:** Zero rejects the incorrect default while idempotence adds a second property.

## Exercises

1. **Predict and explain.** Name a wrong implementation each case catches.

2. **Guided modification.** Add an extreme integer input without negating its minimum value.

3. **Independent construction.** Write table-driven checks for a quantity validator.

4. **Diagnose a defect.** Diagnose an assertion comparing a function call with itself.

5. **Boundary evidence.** Test idempotence alongside independent boundary expectations.

6. **Transfer and justify.** Separate unit, integration, compile-fail and runtime evidence for a library change.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A disabled debug_assert is not a release invariant. Random cases require reproducibility and an oracle. A test that catches and ignores its own failure is misleading.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Test oracle, Regression case, Property without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-024: Tests, assertions and useful counterexamples.
Read courses/rust/guides/rust-024.md and courses/rust/lessons/rust-024.rs. Prerequisites: rust-023.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-024_solution.rs and
courses/rust/solutions/rust-024_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
