# rust-018: Generics, bounds and associated types

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-017`

## Learning objectives

Create a generic pair that swaps owned elements. Then choose a generic parameter or associated type for a producer relationship and explain who selects it.

## Purpose and mental model

Generics retain relationships between input and output types without duplicating source. A trait bound states which operations are available on the parameter. A maximum function needs ordering; a container may need no capability beyond storing its element. Excessive bounds make an API harder to reuse.

Associated types express a type chosen by an implementation, as Iterator does with Item. A generic parameter instead lets a caller choose a type for a use. These are complementary tools. Preserve meaningful relationships rather than erasing everything to a trait object and recovering types through runtime checks.

## Vocabulary and concepts

**Generic parameter:** A type selected for a generic use.

**Trait bound:** A capability required of an admissible type.

**Associated type:** A type selected by a trait implementation.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`T: Ord` constrains a type parameter. Returning T preserves the selected type. `type Item = i32` defines an associated type in an implementation. where clauses can make complex bounds easier to read.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Retain the result type

The function moves its chosen result, preserving the concrete type rather than returning an untyped object.

```rust
fn larger<T: Ord>(left: T, right: T) -> T { if left >= right { left } else { right } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(larger(3, 8), 8);
        assert_eq!(larger(String::from("apple"), String::from("pear")), "pear");
    }
    println!("rust-018: passed");
    Ok(())
}
```

**Observe:** The same function returns an integer or owned String.

### Example B: Use an associated iterator item

The consumer knows which values the iterator yields and chooses a compatible aggregation.

```rust
fn larger<T: Ord>(left: T, right: T) -> T { if left >= right { left } else { right } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2, 3, 4];
        let total: i32 = values.into_iter().sum();
        assert_eq!(total, 9);
        assert_eq!(larger(5, 5), 5);
    }
    println!("rust-018: passed");
    Ok(())
}
```

**Observe:** The iterator's item relationship supports a typed sum.

## Exercises

1. **Predict and explain.** Identify each inferred type and required bound.

2. **Guided modification.** Use larger with a custom ordered value type.

3. **Independent construction.** Create a generic pair that swaps owned elements.

4. **Diagnose a defect.** Diagnose calling an unavailable method on an unconstrained T.

5. **Boundary evidence.** State tie behavior and test equal values.

6. **Transfer and justify.** Choose a generic parameter or associated type for a producer relationship and explain who selects it.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Generic code still has ownership and failure contracts. Deriving Ord chooses a field-order policy that may not match domain meaning. A broad bound should not replace an explicit comparator when multiple orderings are useful.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Generic parameter, Trait bound, Associated type without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-018: Generics, bounds and associated types.
Read courses/rust/guides/rust-018.md and courses/rust/lessons/rust-018.rs. Prerequisites: rust-017.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-018_solution.rs and
courses/rust/solutions/rust-018_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
