# rust-009: Shared borrowing and scope

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-008`

## Learning objectives

Write a last-word function returning a borrowed slice. Then choose a borrowed view or owned result for a parser whose caller may discard the input immediately.

## Purpose and mental model

A shared reference grants temporary read access without taking ownership. Several shared borrows can coexist when no conflicting mutation occurs. The owner must remain alive while borrowed data can still be used. Rust's borrow checker tracks these relationships through control flow, often ending a borrow after its last use rather than the end of the entire lexical block.

A borrowed API is useful for inspection, searching and parsing views. It avoids unnecessary allocation while preserving caller ownership. The lifetime constraint is not a runtime timer: it is a compile-time relationship between valid uses. Returning a reference to a local value is invalid because the owner disappears when the function returns.

## Vocabulary and concepts

**Shared borrow:** Temporary read access without ownership transfer.

**Lifetime:** The region in which a reference remains valid.

**Last use:** The final operation requiring a borrow to remain active.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`&value` creates a shared reference. Dereferencing with `*reference` accesses a referenced scalar when needed. Auto-dereferencing makes many method calls convenient. A return type `&str` must refer to storage owned elsewhere for a sufficient lifetime.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Borrow more than once

Both references inspect the same allocation without taking release responsibility.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("pear");
        let first = &text;
        let second = &text;
        assert_eq!(first.len() + second.len(), 8);
        assert_eq!(text, "pear");
    }
    println!("rust-009: passed");
    Ok(())
}
```

**Observe:** Two readers coexist and the owner remains intact.

### Example B: Return a borrowed view

The function returns a slice whose validity depends on the input owner.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn first_word(text: &str) -> &str { text.split_whitespace().next().unwrap_or("") }
        let sentence = String::from("pear apple");
        assert_eq!(first_word(&sentence), "pear");
        assert_eq!(first_word(""), "");
    }
    println!("rust-009: passed");
    Ok(())
}
```

**Observe:** The result is a view into caller-owned text, with an explicit empty policy.

## Exercises

1. **Predict and explain.** Identify the owner and both readers.

2. **Guided modification.** Add another read-only inspection without cloning.

3. **Independent construction.** Write a last-word function returning a borrowed slice.

4. **Diagnose a defect.** Try returning a reference to a local String and explain the compiler rejection.

5. **Boundary evidence.** Test empty text and a single word.

6. **Transfer and justify.** Choose a borrowed view or owned result for a parser whose caller may discard the input immediately.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A reference cannot make its owner live longer by declaration alone. Borrow duration follows actual use constraints. Avoid converting every slice to String unless independent ownership is needed.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Shared borrow, Lifetime, Last use without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-009: Shared borrowing and scope.
Read courses/rust/guides/rust-009.md and courses/rust/lessons/rust-009.rs. Prerequisites: rust-008.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-009_solution.rs and
courses/rust/solutions/rust-009_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
