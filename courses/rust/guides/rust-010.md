# rust-010: Exclusive borrowing and mutation boundaries

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-009`

## Learning objectives

Write a function swapping the ends of a mutable slice safely. Then design an API that exposes only the smallest mutable region needed by a transformation.

## Purpose and mental model

An exclusive reference grants mutation while preventing conflicting access to the same storage. The common rule is either shared readers or one exclusive borrower at a time. This is a capability rule about access, not a claim that the operating system has locked memory.

Small scopes make mutation ownership easier to see. After an exclusive borrow's last use, the owner can be used again. APIs such as split_at_mut safely produce disjoint mutable regions because they establish that the regions do not overlap. Do not reach for unsafe code merely because the compiler cannot infer a relationship you have not expressed.

## Vocabulary and concepts

**Exclusive borrow:** Temporary access permitting mutation without conflicting aliases.

**Aliasing:** Several paths referring to the same storage.

**Disjoint regions:** Storage ranges that do not overlap.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`&mut value` creates exclusive access and the original binding must permit mutation. A function taking &mut T may update the borrowed value but does not own its eventual destruction. split_at_mut proves disjoint slices.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Mutate through one explicit borrower

The function receives mutation capability for the duration of the call.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn append_mark(text: &mut String) { text.push('!'); }
        let mut text = String::from("ready");
        append_mark(&mut text);
        assert_eq!(text, "ready!");
    }
    println!("rust-010: passed");
    Ok(())
}
```

**Observe:** The caller retains ownership and observes the deliberate mutation.

### Example B: Mutate two proven-disjoint regions

The standard library API establishes disjointness instead of relying on two potentially overlapping index borrows.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut values = [1, 2, 3, 4];
        let (left, right) = values.split_at_mut(2);
        left[0] = 9;
        right[0] = 8;
        assert_eq!(values, [9, 2, 8, 4]);
    }
    println!("rust-010: passed");
    Ok(())
}
```

**Observe:** The two slices mutate separate halves safely.

## Exercises

1. **Predict and explain.** Trace who may access text during the mutable call.

2. **Guided modification.** Add a second mutation after the first borrow ends.

3. **Independent construction.** Write a function swapping the ends of a mutable slice safely.

4. **Diagnose a defect.** Create conflicting mutable borrows and explain the compiler diagnostic.

5. **Boundary evidence.** Test an empty slice and a split at either endpoint.

6. **Transfer and justify.** Design an API that exposes only the smallest mutable region needed by a transformation.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An exclusive borrow is not a thread lock. More mut annotations do not solve aliasing conflicts. Prefer safe disjointness APIs to manually asserting pointer safety.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Exclusive borrow, Aliasing, Disjoint regions without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-010: Exclusive borrowing and mutation boundaries.
Read courses/rust/guides/rust-010.md and courses/rust/lessons/rust-010.rs. Prerequisites: rust-009.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-010_solution.rs and
courses/rust/solutions/rust-010_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
