# rust-003: Integer range, checked arithmetic and numerical intent

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-002`

## Learning objectives

Write a checked quantity-total calculation returning an explicit failure. Then choose numeric representation, units and rounding rules for a pricing contract.

## Purpose and mental model

Fixed-width integers have finite ranges. Rust provides explicit checked, wrapping, saturating and overflowing arithmetic so an API can state what happens at a boundary. Do not rely on differences between debug and optimized overflow settings for business correctness. Choose the intended policy directly.

Floating-point arithmetic approximates many decimal fractions. A tolerance should reflect scale and numerical error, not hide a unit mismatch. Money often needs an integer smallest-unit representation or a separately prepared decimal library with a documented rounding policy. The standard library does not make every numerical domain exact automatically.

## Vocabulary and concepts

**Overflow:** A mathematical result outside the representation range.

**Checked arithmetic:** Arithmetic reporting an unrepresentable result explicitly.

**Saturation:** Clamping an overflowing result to a type boundary.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`checked_add` returns Option and reports overflow as None. `wrapping_add` performs modular arithmetic. `saturating_add` stays at the limit. An explicit integer type makes the tested range unambiguous.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Choose a visible overflow policy

The choice is semantic and should not depend on a compiler optimization setting.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(255_u8.checked_add(1), None);
        assert_eq!(255_u8.wrapping_add(1), 0);
        assert_eq!(255_u8.saturating_add(1), 255);
        assert_eq!(2_u8.checked_add(3), Some(5));
    }
    println!("rust-003: passed");
    Ok(())
}
```

**Observe:** The same boundary produces absence, zero or 255 under three distinct policies.

### Example B: Keep numeric units explicit

Integer smallest units avoid accidental decimal approximation in this bounded pricing example.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let cents_per_item: u64 = 125;
        let quantity: u64 = 3;
        assert_eq!(cents_per_item.checked_mul(quantity), Some(375));
        let approximate = 0.1_f64 + 0.2;
        assert!((approximate - 0.3).abs() < 1e-12);
    }
    println!("rust-003: passed");
    Ok(())
}
```

**Observe:** Three items cost 375 cents, while the floating fixture uses an explicit tolerance.

## Exercises

1. **Predict and explain.** Predict the three overflow policies.

2. **Guided modification.** Repeat the investigation with subtraction at zero.

3. **Independent construction.** Write a checked quantity-total calculation returning an explicit failure.

4. **Diagnose a defect.** Diagnose relying on debug-mode overflow behavior in production logic.

5. **Boundary evidence.** Test zero, maximum and one beyond an accepted application range.

6. **Transfer and justify.** Choose numeric representation, units and rounding rules for a pricing contract.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Wrapping is usually wrong for counts even when it avoids a panic. A tolerance does not repair unit conversion errors. Converting with as can truncate or reinterpret values; use checked conversion when range matters.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Overflow, Checked arithmetic, Saturation without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-003: Integer range, checked arithmetic and numerical intent.
Read courses/rust/guides/rust-003.md and courses/rust/lessons/rust-003.rs. Prerequisites: rust-002.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-003_solution.rs and
courses/rust/solutions/rust-003_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
