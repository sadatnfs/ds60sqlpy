# rust-012: Structs, methods and validated state

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-011`

## Learning objectives

Create a bounded counter with private state and validated operations. Then choose a consuming method when an operation should make the prior state unavailable.

## Purpose and mental model

A struct groups named fields into a domain value. Methods express operations on that value, and their receiver states whether they borrow, mutate or consume it. A constructor function can validate inputs before creating a valid instance. Private fields prevent callers from bypassing that constructor or later invariants.

Failure atomicity means a rejected operation leaves the prior valid state unchanged. Check all rejection conditions before mutation or build a candidate value and commit it only after validation. Encapsulation is useful because it keeps this reasoning in one place rather than requiring every caller to remember the rule.

## Vocabulary and concepts

**Struct:** A nominal type with named fields.

**Receiver:** The self parameter describing access to an instance.

**Invariant:** A rule maintained by every externally visible valid state.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`impl Inventory` contains associated functions and methods. `&self` reads, `&mut self` mutates, and `self` consumes. An associated constructor such as new can return Option or Result.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Reserve within an invariant

The method owns both the affordability check and the subtraction.

```rust
struct Inventory {
    stock: u32,
}
impl Inventory {
    fn new(stock: u32) -> Self {
        Self { stock }
    }
    fn stock(&self) -> u32 {
        self.stock
    }
    fn reserve(&mut self, amount: u32) -> bool {
        if amount > self.stock {
            return false;
        }
        self.stock -= amount;
        true
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut inventory = Inventory::new(5);
        assert!(inventory.reserve(2));
        assert_eq!(inventory.stock(), 3);
    }
    println!("rust-012: passed");
    Ok(())
}
```

**Observe:** A successful reservation leaves three units.

### Example B: Reject without partial mutation

Validation occurs before changing state, preserving the prior valid value.

```rust
struct Inventory {
    stock: u32,
}
impl Inventory {
    fn new(stock: u32) -> Self {
        Self { stock }
    }
    fn stock(&self) -> u32 {
        self.stock
    }
    fn reserve(&mut self, amount: u32) -> bool {
        if amount > self.stock {
            return false;
        }
        self.stock -= amount;
        true
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut inventory = Inventory::new(3);
        assert!(!inventory.reserve(4));
        assert_eq!(inventory.stock(), 3);
        assert!(inventory.reserve(0));
    }
    println!("rust-012: passed");
    Ok(())
}
```

**Observe:** Excess demand is rejected and zero is an allowed no-op.

## Exercises

1. **Predict and explain.** Explain the capability expressed by each method receiver.

2. **Guided modification.** Add a checked restock method.

3. **Independent construction.** Create a bounded counter with private state and validated operations.

4. **Diagnose a defect.** Diagnose subtracting before checking available stock.

5. **Boundary evidence.** Test zero, exact-stock and excess reservations.

6. **Transfer and justify.** Choose a consuming method when an operation should make the prior state unavailable.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Public writable fields can bypass invariants. Unsigned types prevent negative representation but do not prevent overflow. A method taking &mut self is not automatically safe for unsynchronized sharing across threads.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Struct, Receiver, Invariant without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-012: Structs, methods and validated state.
Read courses/rust/guides/rust-012.md and courses/rust/lessons/rust-012.rs. Prerequisites: rust-011.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-012_solution.rs and
courses/rust/solutions/rust-012_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
