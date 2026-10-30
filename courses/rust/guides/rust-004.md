# rust-004: String ownership, UTF-8 and text boundaries

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-003`

## Learning objectives

Write a function accepting &str and returning its byte length. Then design a text limit and state whether it counts bytes, scalars or graphemes requiring an external library.

## Purpose and mental model

String owns a growable UTF-8 buffer; str is a string slice, commonly borrowed as &str. A text literal has static storage and can be borrowed without allocating an owned String. This distinction lets APIs accept text without unnecessarily copying it.

UTF-8 byte length differs from Unicode scalar count and user-perceived grapheme count. Rust's standard chars iterator visits Unicode scalar values, not full grapheme clusters. Byte slicing must use valid UTF-8 boundaries or it panics. Choose the unit required by a task before counting, slicing or limiting input.

## Vocabulary and concepts

**String:** An owned growable UTF-8 string.

**str slice:** A borrowed view of valid UTF-8 text.

**Unicode scalar:** A code point excluding surrogate values, distinct from a grapheme cluster.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`String::from("text")` creates owned text. `&text` can borrow it as &str. `len()` counts UTF-8 bytes, `chars().count()` counts scalars, and `get(range)` returns an optional slice if boundaries are valid.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Borrow without consuming ownership

Borrowing reads the existing storage without transferring its lifetime responsibility.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let owned = String::from("pear");
        let borrowed: &str = &owned;
        assert_eq!(borrowed, "pear");
        assert_eq!(owned.len(), 4);
    }
    println!("rust-004: passed");
    Ok(())
}
```

**Observe:** Both views observe pear while the owner remains usable.

### Example B: Respect byte boundaries

The optional slicing API makes invalid boundaries observable without panicking.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = "é";
        assert_eq!(text.len(), 2);
        assert_eq!(text.chars().count(), 1);
        assert_eq!(text.get(0..1), None);
        assert_eq!(text.get(0..2), Some("é"));
    }
    println!("rust-004: passed");
    Ok(())
}
```

**Observe:** The scalar uses two bytes, and its first byte alone is not a valid string slice.

## Exercises

1. **Predict and explain.** Predict byte and scalar counts for the accented character.

2. **Guided modification.** Compare an emoji and a combining-mark sequence.

3. **Independent construction.** Write a function accepting &str and returning its byte length.

4. **Diagnose a defect.** Diagnose indexing a string as if every character were one byte.

5. **Boundary evidence.** Test empty text and an invalid byte boundary through get.

6. **Transfer and justify.** Design a text limit and state whether it counts bytes, scalars or graphemes requiring an external library.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Chars are not always user-visible characters. A borrowed slice cannot outlive its owner. Use a Unicode segmentation crate only in a separately prepared project, not an undeclared pad dependency.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain String, str slice, Unicode scalar without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-004: String ownership, UTF-8 and text boundaries.
Read courses/rust/guides/rust-004.md and courses/rust/lessons/rust-004.rs. Prerequisites: rust-003.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-004_solution.rs and
courses/rust/solutions/rust-004_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
