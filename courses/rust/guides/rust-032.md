# rust-032: Composition project: a reusable inventory library

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-031`

## Learning objectives

Build and test InventoryLab through its documented Cargo commands. Then design a second adapter that reuses the same validated library without copying its implementation.

## Purpose and mental model

The intermediate project separates a pure domain library from an executable adapter and integration tests. A library can expose validated operations without knowing whether its caller is a command-line tool, a browser worker or a future service. The adapter owns presentation and process behavior.

The checked-in InventoryLab is a real Cargo package using only the standard library. The pad runs the same kind of portable kernel, while Cargo build and Cargo test are deliberately separate project commands. Preserve input accounting, deterministic output and overflow behavior when extracting modules. A successful library test is not a claim that an external service or deployment is configured.

## Vocabulary and concepts

**Library crate:** A reusable Rust compilation unit exposing a public API.

**Adapter:** Code translating external input/output into core contracts.

**Integration test:** A test exercising a public boundary as a consumer.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Use the actual [InventoryLab](../fixtures/InventoryLab/README.md) for a library, executable and integration-test workflow. It requires no third-party crates.

## Syntax anatomy and execution trace

A BTreeMap result preserves sorted identity. A report record carries accepted totals and rejected count. Integration tests use the library public API, which catches accidental exposure or missing exports.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Create a stable report

The core chooses data semantics while presentation can remain a separate adapter.

```rust
fn summarize<'a>(rows: &[( &'a str, i32)]) -> (std::collections::BTreeMap<&'a str, i32>, usize) { let mut totals = std::collections::BTreeMap::new(); let mut rejected = 0; for &(name, value) in rows { if name.is_empty() || value < 0 { rejected += 1; continue; } let previous: i32 = *totals.get(name).unwrap_or(&0); if let Some(total) = previous.checked_add(value) { totals.insert(name, total); } else { rejected += 1; } } (totals, rejected) }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let report = summarize(&[("b", 2), ("a", 3), ("b", 4)]);
        assert_eq!(report.0.get("b"), Some(&6));
        assert_eq!(report.0.keys().copied().collect::<Vec<_>>(), vec!["a", "b"]);
    }
    println!("rust-032: passed");
    Ok(())
}
```

**Observe:** The report accumulates duplicates and orders keys.

### Example B: Retain rejected input evidence

The library contract preserves information needed by every future adapter.

```rust
fn summarize<'a>(rows: &[( &'a str, i32)]) -> (std::collections::BTreeMap<&'a str, i32>, usize) { let mut totals = std::collections::BTreeMap::new(); let mut rejected = 0; for &(name, value) in rows { if name.is_empty() || value < 0 { rejected += 1; continue; } let previous: i32 = *totals.get(name).unwrap_or(&0); if let Some(total) = previous.checked_add(value) { totals.insert(name, total); } else { rejected += 1; } } (totals, rejected) }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let report = summarize(&[("", 2), ("a", -1), ("b", 0)]);
        assert_eq!(report.1, 2);
        assert_eq!(report.0.get("b"), Some(&0));
    }
    println!("rust-032: passed");
    Ok(())
}
```

**Observe:** Two invalid rows are counted and a valid zero remains present.

## Exercises

1. **Predict and explain.** Trace validation and accumulation as separate responsibilities.

2. **Guided modification.** Add a report-rendering function without changing the core representation.

3. **Independent construction.** Build and test InventoryLab through its documented Cargo commands.

4. **Diagnose a defect.** Diagnose moving console output into a reusable domain method.

5. **Boundary evidence.** Test empty, duplicate, invalid and overflow cases.

6. **Transfer and justify.** Design a second adapter that reuses the same validated library without copying its implementation.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A multi-file Cargo project is not accepted by the single-file pad. Keep generated target output out of source packaging. A dependency-free project still needs the prepared compiler and standard library.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Library crate, Adapter, Integration test without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-032: Composition project: a reusable inventory library.
Read courses/rust/guides/rust-032.md and courses/rust/lessons/rust-032.rs. Prerequisites: rust-031.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-032_solution.rs and
courses/rust/solutions/rust-032_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
