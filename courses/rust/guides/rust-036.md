# rust-036: Cargo, editions and reproducible release workflows

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-035`

## Learning objectives

Explain editions, lockfiles and offline builds, and show an edition 2024 rule that changes compilation. The central exercise is task 3: Run its tests and inspect a deliberately changed public contract.

## Purpose and mental model

Cargo describes packages, targets, dependencies and build profiles. A Rust edition selects language compatibility rules while the compiler version selects available implementations and library APIs. These are related but distinct. Pinning an edition does not pin a dependency graph or a compiler toolchain.

Cargo.lock records selected dependency versions for reproducible resolution under a project policy. Locked and offline modes answer different questions: locked rejects graph changes, while offline forbids network access and requires prepared assets. The classroom bypasses per-attempt Cargo resolution by linking a reviewed read-only Arrow library. External projects use their own explicit preparation and lock review.

The classroom compiles every pad with edition 2024, and editions change real language rules. Edition 2024 drops temporaries in a block's tail expression before the block's locals, iterates a Box<[T]> by value, reserves the gen keyword, requires unsafe extern blocks and treats std::env::set_var as unsafe. The two examples compile only under edition 2024; edition 2021 rejects them with E0597 and E0277.

## Vocabulary and concepts

**Edition:** A language compatibility mode for a crate.

**Lockfile:** A record of the selected dependency graph.

**Offline build:** A build restricted to already prepared dependency assets.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The complete [InventoryLab](../fixtures/InventoryLab/README.md) demonstrates Cargo without external dependencies. Arrow dependencies are prepared by the classroom image, not installed by learner source.

## Syntax anatomy and execution trace

Cargo.toml declares package and dependency intent, including edition = "2024". Cargo.lock records a resolved graph. cargo build --locked checks lock consistency; --offline requires cached dependencies. cargo test and cargo clippy are distinct verification tools. cargo fix --edition migrates code mechanically, but the migrated code still needs review.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Observe an edition 2024 scope rule

Edition 2024 drops a temporary in a block's tail expression before the block's local variables, so the Ref returned by borrow() no longer outlives cell. The edition selects this rule; the compiler version only has to implement it.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn name_length() -> usize {
            let cell = std::cell::RefCell::new(String::from("pear"));
            cell.borrow().len()
        }
        assert_eq!(name_length(), 4);
    }
    println!("rust-036: passed");
    Ok(())
}
```

**Observe:** name_length compiles and returns 4 under edition 2024; edition 2021 rejects the same function with E0597.

### Example B: Iterate a boxed slice by value

Edition 2024 changes which IntoIterator implementation a method call on Box<[T]> selects. Code can change meaning or stop compiling across editions, which is why Cargo.toml records the edition explicitly and why an upgrade deserves review.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let boxed: Box<[String]> = vec![String::from("a"), String::from("b")].into_boxed_slice();
        let owned: Vec<String> = boxed.into_iter().collect();
        assert_eq!(owned, ["a", "b"]);
    }
    println!("rust-036: passed");
    Ok(())
}
```

**Observe:** into_iter on a Box<[String]> yields owned Strings under edition 2024; under edition 2021 the same call yields &String and the collect fails with E0277.

## Exercises

1. **Predict and explain.** Explain edition, compiler version and dependency version separately.

2. **Guided modification.** Build InventoryLab with its checked-in lockfile.

3. **Independent construction.** Run its tests and inspect a deliberately changed public contract.

4. **Diagnose a defect.** Diagnose offline mode failing because a dependency was never prepared.

5. **Boundary evidence.** Remove only owned target output and perform a clean build.

6. **Transfer and justify.** Design a dependency upgrade review including lock diff, licenses, compile tests and runtime evidence.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. The separate explanation gives an executed reference answer where one has been written and says plainly where none exists yet. Open it only after your own attempt, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A successful dependency download is not successful compilation. Do not edit checksums manually to force a lockfile pass. A native binary is platform- and architecture-specific.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Reproduce Example A (Observe an edition 2024 scope rule) before changing anything, and confirm its observation: name_length compiles and returns 4 under edition 2024; edition 2021 rejects the same function with E0597.
2. Compare Example B (Iterate a boxed slice by value) with Example A and name the first line whose behavior differs. Its observation is: into_iter on a Box<[String]> yields owned Strings under edition 2024; under edition 2021 the same call yields &String and the collect fails with E0277.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A successful dependency download is not successful compilation.

## Self-check and next step

Explain Edition, Lockfile, Offline build without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/cargo/guide/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-036: Cargo, editions and reproducible release workflows.
Read courses/rust/guides/rust-036.md and courses/rust/lessons/rust-036.rs. Prerequisites: rust-035.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-036_solution.rs and
courses/rust/solutions/rust-036_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
