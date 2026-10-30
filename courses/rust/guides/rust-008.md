# rust-008: Ownership, moves and explicit cloning

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-007`

## Learning objectives

Write a function taking and returning an owned String. Then explain whether a function should borrow, clone or take ownership when retaining data for later use.

## Purpose and mental model

Every owned value has a responsibility for releasing its resources. Moving a non-Copy value transfers that responsibility to another binding or operation. The old binding can no longer be used as though it still owns the value. This prevents accidental double release and many use-after-free errors before execution.

Clone explicitly asks for a value-level duplication defined by the type. Cloning a String duplicates its text storage; cloning an Arc later duplicates shared ownership rather than deep-copying its contents. Copy is a stricter implicit duplication capability used by suitable simple types. Learn the semantic distinction instead of assuming every assignment copies everything.

## Vocabulary and concepts

**Owner:** The value responsible for a resource lifetime.

**Move:** Transfer of ownership that invalidates the prior use path.

**Clone:** An explicit type-defined duplication operation.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Assignment of String moves ownership. `.clone()` requests the type's duplication behavior. A function taking String owns its argument and may retain or release it. Returning the String transfers ownership back.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Move ownership to a new binding

The reference intentionally does not compile an invalid old-binding access; the practice task asks the learner to inspect that diagnostic separately.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let first = String::from("pear");
        let second = first;
        assert_eq!(second, "pear");
        // Using first here would be a compile error: ownership moved.
    }
    println!("rust-008: passed");
    Ok(())
}
```

**Observe:** The new binding owns the text.

### Example B: Clone only when two owners are needed

The explicit clone makes the allocation and independent ownership decision visible.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let first = String::from("pear");
        let mut second = first.clone();
        second.push('s');
        assert_eq!(first, "pear");
        assert_eq!(second, "pears");
    }
    println!("rust-008: passed");
    Ok(())
}
```

**Observe:** The cloned String can change independently.

## Exercises

1. **Predict and explain.** Draw ownership before and after the move.

2. **Guided modification.** Temporarily read first after its move and preserve the compiler diagnostic.

3. **Independent construction.** Write a function taking and returning an owned String.

4. **Diagnose a defect.** Diagnose adding clones everywhere instead of choosing a borrowed interface.

5. **Boundary evidence.** Compare String movement with copying an i32.

6. **Transfer and justify.** Explain whether a function should borrow, clone or take ownership when retaining data for later use.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Clone does not universally mean deep copy. A move can be optimized without changing its ownership semantics. Compiler rejection of a use-after-move is useful evidence, not an obstacle to suppress.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Owner, Move, Clone without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-008: Ownership, moves and explicit cloning.
Read courses/rust/guides/rust-008.md and courses/rust/lessons/rust-008.rs. Prerequisites: rust-007.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-008_solution.rs and
courses/rust/solutions/rust-008_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
