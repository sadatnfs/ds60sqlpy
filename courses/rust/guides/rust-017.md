# rust-017: Traits and behavioral contracts

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-016`

## Learning objectives

Define a small trait for a deterministic formatter. Then choose a trait boundary for a file adapter while keeping the domain core pure.

## Purpose and mental model

A trait describes capabilities a type provides. A consumer can depend on the capability instead of one representation. A trait implementation must preserve units, valid inputs and failure meaning, not merely compile with the right method names. This makes substitution a behavioral question.

Static dispatch through generics can retain concrete type information, while a trait object supports runtime substitution behind a pointer. Choose based on the API relationship and storage needs. Start with a small pricing capability whose implementations share one clear contract; avoid inventing a trait for every trivial function.

## Vocabulary and concepts

**Trait:** A named capability contract.

**Implementation:** A type-specific realization of a trait.

**Dynamic dispatch:** Selecting behavior through a trait object at runtime.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`trait Pricer` declares a method. `impl Pricer for FlatPrice` supplies behavior. `&dyn Pricer` borrows a trait object and uses dynamic dispatch. The receiver &self permits inspection without consuming the implementation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Use a declared capability

The consumer needs the capability rather than the concrete field layout.

```rust
trait Pricer { fn cost(&self, units: u32) -> u32; }
struct FlatPrice(u32); impl Pricer for FlatPrice { fn cost(&self, units: u32) -> u32 { self.0 * units } }
struct CappedPrice(u32, u32); impl Pricer for CappedPrice { fn cost(&self, units: u32) -> u32 { (self.0 * units).min(self.1) } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let price = FlatPrice(3);
        let view: &dyn Pricer = &price;
        assert_eq!(view.cost(4), 12);
    }
    println!("rust-017: passed");
    Ok(())
}
```

**Observe:** The borrowed trait object exposes pricing behavior.

### Example B: Substitute a second policy

Both implementations preserve input and output units while varying the rule.

```rust
trait Pricer { fn cost(&self, units: u32) -> u32; }
struct FlatPrice(u32); impl Pricer for FlatPrice { fn cost(&self, units: u32) -> u32 { self.0 * units } }
struct CappedPrice(u32, u32); impl Pricer for CappedPrice { fn cost(&self, units: u32) -> u32 { (self.0 * units).min(self.1) } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let flat = FlatPrice(3);
        let capped = CappedPrice(3, 10);
        let prices: [&dyn Pricer; 2] = [&flat, &capped];
        assert_eq!(prices.map(|price| price.cost(4)), [12, 10]);
    }
    println!("rust-017: passed");
    Ok(())
}
```

**Observe:** The same interface admits an uncapped and capped policy.

## Exercises

1. **Predict and explain.** Trace the method call to each implementation.

2. **Guided modification.** Add another flat-price value without changing the consumer.

3. **Independent construction.** Define a small trait for a deterministic formatter.

4. **Diagnose a defect.** Diagnose conforming implementations that disagree about units.

5. **Boundary evidence.** Test zero units and the exact cap.

6. **Transfer and justify.** Choose a trait boundary for a file adapter while keeping the domain core pure.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A matching signature does not establish compatible semantics. Traits and inheritance are different mechanisms. Avoid exposing implementation details merely to make a trait larger.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Trait, Implementation, Dynamic dispatch without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-017: Traits and behavioral contracts.
Read courses/rust/guides/rust-017.md and courses/rust/lessons/rust-017.rs. Prerequisites: rust-016.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-017_solution.rs and
courses/rust/solutions/rust-017_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
