# rust-040: Compute kernels, filtering and row selection

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-039`

## Learning objectives

Filter every column of a batch consistently under one row mask. Then choose filter or take for a sampling procedure and explain duplicate-row consequences.

## Purpose and mental model

Arrow compute kernels operate on arrays while respecting their logical representation. A Boolean mask selects rows; take selects positions by an index array. These are different operations with different output ordering. Filtering normally preserves the order of admitted rows, while take can repeat or reorder positions.

Type erasure means a kernel can return ArrayRef. Inspect or validate the logical type before downcasting to a concrete array. An unwrap can be justified only by a nearby known kernel/type contract in a controlled fixture. Production generic code should return a useful error for an unexpected type. Preserve null and index bounds policies explicitly.

## Vocabulary and concepts

**Kernel:** A reusable array computation.

**Filter mask:** A Boolean decision per input row.

**Take indices:** Positions selecting and potentially reordering rows.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

compute::filter accepts an array and BooleanArray mask. compute::take selects by integer indices. as_any().downcast_ref recovers a known concrete array after the type contract has been established.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Filter with an explicit mask

The mask expresses one admission decision for every original position.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{BooleanArray, Int32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        let mask = BooleanArray::from(vec![true, false, true]);
        let result = arrow::compute::filter(&values, &mask)?;
        let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
        assert_eq!(typed.iter().collect::<Vec<_>>(), vec![Some(2), Some(6)]);
    }
    println!("rust-040: passed");
    Ok(())
}
```

**Observe:** Filtering retains two and six in input order.

### Example B: Reorder and repeat with take

A selected row can appear more than once, so cardinality and aggregation assumptions need review.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Int32Array, UInt32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        let indices = UInt32Array::from(vec![2, 0, 2]);
        let result = arrow::compute::take(&values, &indices, None)?;
        let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
        assert_eq!(typed.iter().collect::<Vec<_>>(), vec![Some(6), Some(2), Some(6)]);
    }
    println!("rust-040: passed");
    Ok(())
}
```

**Observe:** Take repeats and reorders values according to the index sequence.

## Exercises

1. **Predict and explain.** Predict row count and order for both operations.

2. **Guided modification.** Change one mask value and independently derive the result.

3. **Independent construction.** Filter every column of a batch consistently under one row mask.

4. **Diagnose a defect.** Diagnose filtering one column while leaving others unfiltered.

5. **Boundary evidence.** Test empty selection, all-selected rows and checked invalid indices.

6. **Transfer and justify.** Choose filter or take for a sampling procedure and explain duplicate-row consequences.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Downcast failure is possible in generic code. A mask and array must have compatible lengths. A kernel result does not establish a domain-level ordering guarantee unless the operation contract does.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Kernel, Filter mask, Take indices without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.rs/arrow/60.0.0/arrow/compute/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-040: Compute kernels, filtering and row selection.
Read courses/rust/guides/rust-040.md and courses/rust/lessons/rust-040.rs. Prerequisites: rust-039.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-040_solution.rs and
courses/rust/solutions/rust-040_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
