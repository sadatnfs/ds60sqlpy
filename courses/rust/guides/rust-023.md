# rust-023: Modules, visibility and a stable public surface

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-022`

## Learning objectives

Move a pure domain operation into an inline module. Then split a future library and executable crate by responsibility and document dependency direction.

## Purpose and mental model

Modules organize names and control visibility. A private implementation can change without forcing every consumer to understand it. Public items form a compatibility boundary and should expose domain meaning rather than internal representation. A crate is a compilation unit; a package can contain a library crate and executable crates.

The classroom can demonstrate modules inside one source file. A real multi-file Cargo project has separate preparation and is not uploaded through the pad. Keep that distinction explicit when a lesson introduces src/lib.rs and integration tests. Good module boundaries follow responsibilities and dependency direction, not a fixed rule that every type needs its own file.

## Vocabulary and concepts

**Module:** A namespace and visibility boundary.

**Crate:** A Rust compilation unit.

**Public API:** The surface consumers may depend on.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The later [InventoryLab Cargo project](../fixtures/InventoryLab/README.md) supplies actual multi-file source and integration tests outside the single-file pad.

## Syntax anatomy and execution trace

`mod domain { ... }` declares a module. pub exposes an item to permitted external paths. use imports a name into scope without copying its implementation. pub(crate) limits visibility to the current crate.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Call a reviewed public function

The implementation details remain behind its named boundary.

```rust
mod domain { pub fn double(value: i32) -> i32 { value * 2 } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(domain::double(4), 8);
        assert_eq!(domain::double(0), 0);
    }
    println!("rust-023: passed");
    Ok(())
}
```

**Observe:** The consumer uses the domain module interface.

### Example B: Import a name without changing ownership

Use changes name resolution, not execution or data ownership.

```rust
mod domain { pub fn double(value: i32) -> i32 { value * 2 } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use domain::double;
        assert_eq!(double(3), 6);
    }
    println!("rust-023: passed");
    Ok(())
}
```

**Observe:** The shorter imported name refers to the same function.

## Exercises

1. **Predict and explain.** Identify the public and private items.

2. **Guided modification.** Add a private helper used by the public function.

3. **Independent construction.** Move a pure domain operation into an inline module.

4. **Diagnose a defect.** Diagnose a consumer accessing a private representation field.

5. **Boundary evidence.** Test the public contract without relying on internal helper names.

6. **Transfer and justify.** Split a future library and executable crate by responsibility and document dependency direction.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Modules are not runtime services. Excessive pub can freeze accidental implementation details into an API. A use declaration does not install a dependency.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Module, Crate, Public API without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-023: Modules, visibility and a stable public surface.
Read courses/rust/guides/rust-023.md and courses/rust/lessons/rust-023.rs. Prerequisites: rust-022.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-023_solution.rs and
courses/rust/solutions/rust-023_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
