# rust-006: Loops, iterators and termination evidence

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-005`

## Learning objectives

Implement a first-match search with Option output. Then design a bounded retry loop and state both its progress measure and its effect policy.

## Purpose and mental model

A loop repeats a state transition. An invariant explains what remains true, and a termination argument explains why repetition stops. For a sum, the accumulator equals the values already processed. For a search, the inspected prefix contains no earlier match before the chosen result.

For-in consumes an iterable, so ownership of the sequence or its borrowed view matters. Iterating an array of small Copy values can look similar to borrowing a vector, but the types determine what remains available. Use iterator adapters when they expose intent, and use an explicit loop when intermediate state or early exits need explanation.

## Vocabulary and concepts

**Invariant:** A property preserved by every iteration.

**Iterator:** A producer of successive values.

**Termination:** A reason the repeated process eventually stops.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`for value in &values` borrows elements. `enumerate` supplies traversal positions. `break` exits a loop, and loop itself can return a value through break value. An exclusive range uses `0..n`.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Maintain a sum invariant

The loop changes only its accumulator, not the source ownership.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 4, 6];
        let mut total = 0;
        for value in &values { total += value; }
        assert_eq!(total, 12);
        assert_eq!(values.len(), 3);
    }
    println!("rust-006: passed");
    Ok(())
}
```

**Observe:** The borrowed traversal totals twelve and retains the vector.

### Example B: Find the first position

Position stops at the first matching element rather than returning the last repeated match.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [3, 8, 8];
        assert_eq!(values.iter().position(|value| *value == 8), Some(1));
        assert_eq!(values.iter().position(|value| *value == 9), None);
    }
    println!("rust-006: passed");
    Ok(())
}
```

**Observe:** The first match is position one and absence stays explicit.

## Exercises

1. **Predict and explain.** Write the accumulator before and after every iteration.

2. **Guided modification.** Skip negative values while preserving a clear invariant.

3. **Independent construction.** Implement a first-match search with Option output.

4. **Diagnose a defect.** Diagnose an inclusive loop bound used as an array index.

5. **Boundary evidence.** Test empty, singleton and repeated-match sequences.

6. **Transfer and justify.** Design a bounded retry loop and state both its progress measure and its effect policy.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An iterator can consume values or borrow them depending on its construction. A position is not automatically a valid index in a different collection. Avoid unbounded loops without a deliberate stop and cancellation policy.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Invariant, Iterator, Termination without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-006: Loops, iterators and termination evidence.
Read courses/rust/guides/rust-006.md and courses/rust/lessons/rust-006.rs. Prerequisites: rust-005.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-006_solution.rs and
courses/rust/solutions/rust-006_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
