# rust-011: Slices, arrays and vector growth

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-010`

## Learning objectives

Implement a maximum function accepting a slice and returning Option. Then choose an array, Vec or slice for stored state, function input and fixed-size coordinates.

## Purpose and mental model

An array has a compile-time length as part of its type. A Vec owns a growable allocation. A slice borrows a contiguous region and carries its length without owning that allocation. Accepting &[T] lets a function read arrays and vectors through one interface.

Vector growth can reallocate storage, which explains why a borrow into a vector cannot remain live while a conflicting push changes its allocation. Capacity reserves room but does not create initialized logical elements. Indexing panics outside the valid range; get returns Option when absence is a normal possibility.

## Vocabulary and concepts

**Array:** A fixed-length value whose type includes its length.

**Vector:** An owned growable contiguous sequence.

**Slice:** A borrowed contiguous view carrying a length.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`[i32; 3]` is an array of exactly three integers. `Vec<i32>` owns a variable-length sequence. `&[i32]` is a borrowed slice. len and capacity describe different properties.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Accept arrays and vectors uniformly

The function requires read access, not a particular allocation strategy.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn total(values: &[i32]) -> i32 { values.iter().sum() }
        assert_eq!(total(&[2, 3, 4]), 9);
        assert_eq!(total(&vec![1, 2]), 3);
        assert_eq!(total(&[]), 0);
    }
    println!("rust-011: passed");
    Ok(())
}
```

**Observe:** One slice interface accepts several owning representations.

### Example B: Separate capacity from logical elements

The optional lookup exposes absence instead of indexing uninitialized capacity.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut values: Vec<i32> = Vec::with_capacity(10);
        assert_eq!(values.len(), 0);
        assert!(values.capacity() >= 10);
        values.push(7);
        assert_eq!(values.get(0), Some(&7));
        assert_eq!(values.get(1), None);
    }
    println!("rust-011: passed");
    Ok(())
}
```

**Observe:** Reserved storage still contains zero logical elements until push.

## Exercises

1. **Predict and explain.** Identify owner, length and borrowed view in each call.

2. **Guided modification.** Use a subslice and predict its total.

3. **Independent construction.** Implement a maximum function accepting a slice and returning Option.

4. **Diagnose a defect.** Diagnose keeping an element reference live across a conflicting vector push.

5. **Boundary evidence.** Test empty, singleton and out-of-range get cases.

6. **Transfer and justify.** Choose an array, Vec or slice for stored state, function input and fixed-size coordinates.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Capacity is not a valid index limit. A slice does not extend its owner's lifetime. Avoid accepting &Vec when a slice expresses the actual requirement.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Array, Vector, Slice without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-011: Slices, arrays and vector growth.
Read courses/rust/guides/rust-011.md and courses/rust/lessons/rust-011.rs. Prerequisites: rust-010.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-011_solution.rs and
courses/rust/solutions/rust-011_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
