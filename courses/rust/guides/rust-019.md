# rust-019: Lifetime parameters and borrowed API design

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-018`

## Learning objectives

Write a borrowed prefix parser with the narrowest lifetime relationship. Then choose a borrowed or owned result for a cache boundary and justify cost and lifetime.

## Purpose and mental model

A lifetime parameter expresses a relationship between references. It does not allocate storage or extend an owner's life. A function returning one of two borrowed inputs must describe that the output is valid only where both candidate input borrows are valid. The caller and compiler then check actual uses against that relationship.

Prefer simple ownership first. Lifetime annotations become useful when an API deliberately returns views or stores borrowed data. Returning an owned value can simplify a boundary when independent lifetime is required, at an explicit copying cost. Do not force static lifetime onto data merely to suppress a diagnostic.

## Vocabulary and concepts

**Lifetime parameter:** A name for a reference-validity relationship.

**Elision:** Compiler rules inferring common lifetime relationships.

**Borrowed result:** A result whose storage remains owned by another value.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`fn choose<'a>(left: &'a str, right: &'a str) -> &'a str` relates the output borrow to both inputs. Elision handles common simple cases automatically. A struct field containing a reference also needs its lifetime relationship.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Return one input view

The annotation prevents a caller from using the view after a required owner is gone.

```rust
fn longer<'a>(left: &'a str, right: &'a str) -> &'a str { if left.len() >= right.len() { left } else { right } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let left = String::from("pear");
        let right = String::from("watermelon");
        assert_eq!(longer(&left, &right), "watermelon");
    }
    println!("rust-019: passed");
    Ok(())
}
```

**Observe:** The output is a borrowed view of the longer input.

### Example B: Own a result when lifetime must separate

A deliberate owned copy changes the lifetime contract rather than pretending the borrow is static.

```rust
fn longer<'a>(left: &'a str, right: &'a str) -> &'a str { if left.len() >= right.len() { left } else { right } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let result = { let temporary = String::from("retained"); temporary.to_owned() };
        assert_eq!(result, "retained");
    }
    println!("rust-019: passed");
    Ok(())
}
```

**Observe:** The independent owned result survives the temporary scope.

## Exercises

1. **Predict and explain.** Draw the valid-use regions of both inputs and the output.

2. **Guided modification.** Test the tie policy of longer.

3. **Independent construction.** Write a borrowed prefix parser with the narrowest lifetime relationship.

4. **Diagnose a defect.** Try returning a local reference and explain why annotations cannot make it valid.

5. **Boundary evidence.** Test empty inputs and use after one candidate owner leaves scope.

6. **Transfer and justify.** Choose a borrowed or owned result for a cache boundary and justify cost and lifetime.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Lifetime names describe relationships, not durations in seconds. Static is not a universal fix. A lifetime annotation cannot rescue a reference to destroyed local storage.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Lifetime parameter, Elision, Borrowed result without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-019: Lifetime parameters and borrowed API design.
Read courses/rust/guides/rust-019.md and courses/rust/lessons/rust-019.rs. Prerequisites: rust-018.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-019_solution.rs and
courses/rust/solutions/rust-019_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
