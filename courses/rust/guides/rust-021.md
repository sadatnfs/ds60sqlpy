# rust-021: Closures and Fn capability bounds

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-020`

## Learning objectives

Write closures and choose Fn, FnMut or FnOnce bounds by what the closure does. The central exercise is task 3: Implement a helper accepting FnMut for repeated transformations.

## Purpose and mental model

A closure captures surrounding values according to what its body needs. It may borrow, mutate captured state or take ownership. Fn, FnMut and FnOnce describe calling capabilities: shared repeatable calls, mutable repeatable calls and at least one consuming call respectively. These traits form a relationship, not three arbitrary spellings to try until compilation succeeds.

A move closure takes ownership of captured values, useful when work outlives the creating scope. Moving a reference still moves only that reference and does not make its borrowed target live forever. Choose capture and call contracts from the intended lifetime and mutation behavior.

## Vocabulary and concepts

**Capture:** A surrounding value or reference retained by a closure.

**FnMut:** A closure capability permitting mutation during repeated calls.

**FnOnce:** A capability allowing a potentially consuming call.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`|value| value * factor` declares a closure. `move || ...` transfers captures into it. A closure mutating a captured accumulator needs mutable calling access. A function accepting FnOnce can invoke consuming behavior once.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Observe mutable capture

The scope makes the exclusive captured access visible.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut count = 0;
        {
            let mut add = |value| {
                count += value;
            };
            add(2);
            add(3);
        }
        assert_eq!(count, 5);
    }
    println!("rust-021: passed");
    Ok(())
}
```

**Observe:** The closure updates its borrowed accumulator before the borrow ends.

### Example B: Move owned data into a closure

Returning the owned capture makes this closure consuming rather than indefinitely repeatable.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("owned");
        let consume = move || text;
        let result = consume();
        assert_eq!(result, "owned");
    }
    println!("rust-021: passed");
    Ok(())
}
```

**Observe:** The closure transfers its captured String to the caller once.

## Exercises

1. **Predict and explain.** Identify capture mode and calling capability in each example.

2. **Guided modification.** Write a pure repeatable closure capturing an immutable factor.

3. **Independent construction.** Implement a helper accepting FnMut for repeated transformations.

4. **Diagnose a defect.** Diagnose attempting to call a consuming closure twice.

5. **Boundary evidence.** Test a closure with no captures and one capturing a borrowed reference.

6. **Transfer and justify.** Choose capture ownership for work that will run on another thread.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. The separate explanation gives an executed reference answer where one has been written and says plainly where none exists yet. Open it only after your own attempt, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Move does not imply deep copy. A moved reference still has a borrowed lifetime. Avoid adding static bounds when the real solution is scoped execution or owned data.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Reproduce Example A (Observe mutable capture) before changing anything, and confirm its observation: The closure updates its borrowed accumulator before the borrow ends.
2. Compare Example B (Move owned data into a closure) with Example A and name the first line whose behavior differs. Its observation is: The closure transfers its captured String to the caller once.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Move does not imply deep copy.

## Self-check and next step

Explain Capture, FnMut, FnOnce without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-021: Closures and Fn capability bounds.
Read courses/rust/guides/rust-021.md and courses/rust/lessons/rust-021.rs. Prerequisites: rust-020.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-021_solution.rs and
courses/rust/solutions/rust-021_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
