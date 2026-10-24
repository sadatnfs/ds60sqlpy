# rust-034: Unsafe code, FFI and a documented safety argument

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-033`

## Learning objectives

Write a safe wrapper specification before considering an unsafe implementation. Then design an FFI ownership document stating allocation, release, encoding and error conventions.

## Purpose and mental model

Unsafe permits a small set of operations whose correctness the compiler cannot fully establish. It does not disable every safety rule or turn wrong memory access into valid behavior. Each unsafe block needs an argument covering pointer validity, alignment, initialized length, aliasing and lifetime. Keep the block small and wrap it in a safe interface that enforces those conditions.

Foreign-function interfaces add an ABI contract: layout, calling convention, string encoding, ownership and failure signaling must agree across languages. A successful link does not prove those agreements. The ordinary fixture uses a pointer obtained from a live array and immediately reconstructs a read-only slice under a documented invariant, without calling undeclared native libraries.

## Vocabulary and concepts

**Unsafe operation:** An operation requiring caller-provided safety evidence.

**ABI:** The binary-level calling and layout agreement between compiled components.

**Safety invariant:** The conditions a safe wrapper must preserve around unsafe code.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`as_ptr` borrows an address from live storage. `slice::from_raw_parts` is unsafe because the caller supplies validity and length. A SAFETY comment explains why this exact operation satisfies its preconditions.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Reconstruct a bounded borrowed view

The safety proof is tied to the pointer origin and exact length, not merely to the pointer being non-null.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2_i32, 3, 4];
        let pointer = values.as_ptr();
        // SAFETY: pointer comes from this live initialized array; length is exact; no mutation overlaps.
        let view = unsafe { std::slice::from_raw_parts(pointer, values.len()) };
        assert_eq!(view, &[2, 3, 4]);
    }
    println!("rust-034: passed");
    Ok(())
}
```

**Observe:** The reconstructed view matches the live initialized array.

### Example B: Prefer the safe operation when available

Unsafe should be justified by a real boundary, not used because pointer syntax appears advanced.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2, 3, 4];
        let view = &values[..];
        assert_eq!(view.iter().sum::<i32>(), 9);
    }
    println!("rust-034: passed");
    Ok(())
}
```

**Observe:** A normal slice provides the same read contract without a manual safety burden.

## Exercises

1. **Predict and explain.** State every precondition needed by from_raw_parts.

2. **Guided modification.** Reduce the borrowed length while retaining valid initialized storage.

3. **Independent construction.** Write a safe wrapper specification before considering an unsafe implementation.

4. **Diagnose a defect.** Diagnose returning a pointer after its owner is dropped.

5. **Boundary evidence.** Review zero-length and alignment rules without executing undefined behavior.

6. **Transfer and justify.** Design an FFI ownership document stating allocation, release, encoding and error conventions.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Never test undefined behavior by hoping it crashes predictably. A null check is insufficient to prove pointer validity. Panics crossing an incompatible FFI boundary need a deliberate policy.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Unsafe operation, ABI, Safety invariant without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/nomicon/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-034: Unsafe code, FFI and a documented safety argument.
Read courses/rust/guides/rust-034.md and courses/rust/lessons/rust-034.rs. Prerequisites: rust-033.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-034_solution.rs and
courses/rust/solutions/rust-034_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
