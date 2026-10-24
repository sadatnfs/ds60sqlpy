# rust-020: Iterators, laziness and consumption

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-019`

## Learning objectives

Write a borrowed transformation returning a collected result. Then choose iter, iter_mut or into_iter for three operations and justify ownership.

## Purpose and mental model

Iterator adapters describe transformations that execute when consumed. Map and filter generally build a recipe; collect, sum or a loop drives it. Repeated iteration is possible only if the source can be recreated or borrowed appropriately. An iterator itself holds progress and may be exhausted.

The three common vector forms make ownership visible: iter yields shared references, iter_mut yields exclusive references, and into_iter consumes owned elements. Choose the form matching the work. A lazily executed closure with side effects is harder to reason about, so keep transformations pure unless the side effect is explicitly the lesson.

## Vocabulary and concepts

**Adapter:** An iterator transformation producing another iterator.

**Consumer:** An operation driving iteration to obtain a result.

**Exhaustion:** The state where an iterator returns no more values.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`iter().filter(...).map(...)` chains borrowed transformations. collect needs an inferred or annotated target. next advances one iterator instance. into_iter consumes the collection when the collection owns non-Copy elements.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Consume a transformation recipe

Copied turns referenced integers into independent small values before filtering and mapping.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![1, 2, 3, 4];
        let result: Vec<_> = values.iter().copied().filter(|value| value % 2 == 0).map(|value| value * 10).collect();
        assert_eq!(result, vec![20, 40]);
        assert_eq!(values.len(), 4);
    }
    println!("rust-020: passed");
    Ok(())
}
```

**Observe:** The recipe selects and transforms while retaining the borrowed source.

### Example B: Observe iterator progress

Calling next again does not restart the source automatically.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut iterator = [2, 3].into_iter();
        assert_eq!(iterator.next(), Some(2));
        assert_eq!(iterator.next(), Some(3));
        assert_eq!(iterator.next(), None);
    }
    println!("rust-020: passed");
    Ok(())
}
```

**Observe:** The iterator advances and eventually exhausts.

## Exercises

1. **Predict and explain.** Identify adapters and the final consumer.

2. **Guided modification.** Add a take limit and predict how much work is demanded.

3. **Independent construction.** Write a borrowed transformation returning a collected result.

4. **Diagnose a defect.** Diagnose constructing a lazy map and expecting it to execute immediately.

5. **Boundary evidence.** Test empty input and a partially consumed iterator.

6. **Transfer and justify.** Choose iter, iter_mut or into_iter for three operations and justify ownership.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Laziness does not mean no allocation if a later consumer collects. Reusing an exhausted iterator does not recreate it. A chain with hidden effects can execute at an unexpected boundary.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Adapter, Consumer, Exhaustion without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-020: Iterators, laziness and consumption.
Read courses/rust/guides/rust-020.md and courses/rust/lessons/rust-020.rs. Prerequisites: rust-019.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-020_solution.rs and
courses/rust/solutions/rust-020_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
