# rust-014: Option and preserving missing information

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-013`

## Learning objectives

Write a first-valid-item lookup returning Option. Then choose when absence should remain optional and when it should become a domain error.

## Purpose and mental model

Option represents either Some(value) or None. It is appropriate when absence is an expected outcome, such as a lookup finding no record. A real zero remains Some(0), keeping it distinct from missing information. This type-level distinction prevents sentinel values from leaking into valid calculations.

Unwrap asserts that absence is impossible and panics otherwise. Use it only when a nearby invariant or authored fixture makes that claim clear. Pattern matching, map and and_then let code retain absence through transformations until a boundary deliberately chooses a fallback. Choosing a default too early can erase information the caller needs.

## Vocabulary and concepts

**Option:** A type representing expected presence or absence.

**Some:** The present case containing a value.

**Fallback:** A deliberate replacement selected for absence.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Option<T>` carries a present T or absence. `if let Some(value)` handles the present case. map transforms a present value; and_then chains an operation already returning Option. unwrap_or supplies a deliberate fallback.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Keep zero distinct from missing

Absence is a separate case, not a special numeric value.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let measured = Some(0);
        let missing: Option<i32> = None;
        assert_ne!(measured, missing);
        assert_eq!(measured.map(|value| value + 1), Some(1));
    }
    println!("rust-014: passed");
    Ok(())
}
```

**Observe:** A measured zero remains present and transforms to one.

### Example B: Propagate absence until a boundary

The fallback is not inserted into the collection and should not be mistaken for a valid measurement.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2, 4];
        assert_eq!(values.get(9).map(|value| value * 2), None);
        assert_eq!(values.get(9).copied().unwrap_or(-1), -1);
    }
    println!("rust-014: passed");
    Ok(())
}
```

**Observe:** An absent lookup stays absent until the explicit display fallback.

## Exercises

1. **Predict and explain.** Predict mapping Some(0) and None.

2. **Guided modification.** Render missing data as an unknown label instead of a numeric sentinel.

3. **Independent construction.** Write a first-valid-item lookup returning Option.

4. **Diagnose a defect.** Diagnose unwrap on an ordinary not-found path.

5. **Boundary evidence.** Test empty collections, present zero and out-of-range lookup.

6. **Transfer and justify.** Choose when absence should remain optional and when it should become a domain error.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

None does not explain a failure reason; use Result when a reason matters. A default can hide missing data. Avoid converting every optional to a panic merely to shorten control flow.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Option, Some, Fallback without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-014: Option and preserving missing information.
Read courses/rust/guides/rust-014.md and courses/rust/lessons/rust-014.rs. Prerequisites: rust-013.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-014_solution.rs and
courses/rust/solutions/rust-014_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
