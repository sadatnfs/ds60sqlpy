# rust-041: Variable-width arrays, nested values and zero-copy slices

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-040`

## Learning objectives

Build a nested column from a small ragged dataset. Then explain when retaining a tiny shared slice may retain excessive memory and when copying is justified.

## Purpose and mental model

Variable-width arrays use offsets to locate each logical value in a shared data region. Nested list arrays add another layer: a parent position can be null, an empty list, or a nonempty list whose children may themselves be null. These states carry different meanings and must not be flattened indiscriminately.

Arrow slices often share underlying buffers instead of copying all data. This makes views cheap, but a small retained slice can keep a large allocation alive. Logical offsets and validity still matter. Zero-copy is a specific ownership and representation property, not a blanket claim that an entire analytical pipeline performs no allocations.

## Vocabulary and concepts

**Offset buffer:** Positions locating variable-width logical values.

**Nested validity:** Separate nullability at parent and child levels.

**Zero-copy view:** A view sharing existing storage rather than duplicating its payload.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

ListBuilder<Int32Builder> appends child values, then append(true) closes a valid parent list. append(false) adds a null parent. Array::slice creates a logical view over a selected region.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Distinguish nonempty, empty and null lists

The first row even contains a null child, demonstrating independent validity levels.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Builder, ListBuilder};
        let mut builder = ListBuilder::new(Int32Builder::new());
        builder.values().append_value(2);
        builder.values().append_null();
        builder.append(true);
        builder.append(true);
        builder.append(false);
        let lists = builder.finish();
        assert_eq!(lists.len(), 3);
        assert_eq!(lists.value_length(0), 2);
        assert_eq!(lists.value_length(1), 0);
        assert!(lists.is_null(2));
    }
    println!("rust-041: passed");
    Ok(())
}
```

**Observe:** The three rows are a two-child list, an empty list and a null list.

### Example B: Slice without confusing logical positions

A view's logical indices are interpreted relative to the sliced array rather than the original source positions.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, StringArray};
        let values = StringArray::from(vec!["first", "middle", "last"]);
        let slice = values.slice(1, 1);
        let typed = slice.as_any().downcast_ref::<StringArray>().unwrap();
        assert_eq!(typed.len(), 1);
        assert_eq!(typed.value(0), "middle");
    }
    println!("rust-041: passed");
    Ok(())
}
```

**Observe:** The sliced array exposes middle at its logical index zero.

## Exercises

1. **Predict and explain.** Classify parent-null, empty and child-null states.

2. **Guided modification.** Add another valid list with two non-null children.

3. **Independent construction.** Build a nested column from a small ragged dataset.

4. **Diagnose a defect.** Diagnose treating an empty list as equivalent to a missing list.

5. **Boundary evidence.** Test zero-length slices and nonzero source offsets.

6. **Transfer and justify.** Explain when retaining a tiny shared slice may retain excessive memory and when copying is justified.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Nested nullability has several layers. Zero-copy views can extend buffer lifetime. Do not manually manipulate offset buffers without validating every format invariant.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Offset buffer, Nested validity, Zero-copy view without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://arrow.apache.org/docs/format/Columnar.html). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-041: Variable-width arrays, nested values and zero-copy slices.
Read courses/rust/guides/rust-041.md and courses/rust/lessons/rust-041.rs. Prerequisites: rust-040.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-041_solution.rs and
courses/rust/solutions/rust-041_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
