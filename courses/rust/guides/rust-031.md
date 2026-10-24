# rust-031: Box, Rc, Weak and recursive structures

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-030`

## Learning objectives

Model a parent-child relationship with a weak back-reference. Then choose Box, Rc or Arc for unique, local-shared and cross-thread ownership scenarios.

## Purpose and mental model

Box provides owned indirection, useful when a recursive structure needs a finite-sized outer representation. Rc provides shared ownership within one thread, while Weak provides a non-owning link that may no longer upgrade to a live owner. These pointers express different lifetime contracts and should not be chosen interchangeably.

Cycles of strong reference counts can leak resources even in memory-safe Rust. A parent-child structure often needs owning edges in one direction and weak back-references in the other. RefCell permits checked interior mutation in a single thread; violating its dynamic borrowing rules panics. It does not make Rc suitable for concurrent access.

## Vocabulary and concepts

**Box:** A uniquely owned heap allocation with a known pointer-sized handle.

**Rc:** Single-threaded reference-counted shared ownership.

**Weak:** A non-owning link whose target may no longer exist.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Box::new stores an owned value behind a pointer. Rc::clone increments shared ownership. Rc::downgrade creates Weak, and upgrade returns Option because the owner may have disappeared.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Represent recursion through indirection

Each node owns the next node and releases that chain through ordinary ownership.

```rust
enum Node { End, More(i32, Box<Node>) }
impl Node { fn total(&self) -> i32 { match self { Self::End => 0, Self::More(value, next) => value + next.total() } } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let list = Node::More(2, Box::new(Node::More(3, Box::new(Node::End))));
        assert_eq!(list.total(), 5);
    }
    println!("rust-031: passed");
    Ok(())
}
```

**Observe:** Box makes the recursive type have a finite outer size.

### Example B: Observe a weak target disappearing

Upgrade makes absence explicit after the final strong owner is released.

```rust
enum Node { End, More(i32, Box<Node>) }
impl Node { fn total(&self) -> i32 { match self { Self::End => 0, Self::More(value, next) => value + next.total() } } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let owner = std::rc::Rc::new(String::from("value"));
        let weak = std::rc::Rc::downgrade(&owner);
        assert!(weak.upgrade().is_some());
        drop(owner);
        assert!(weak.upgrade().is_none());
    }
    println!("rust-031: passed");
    Ok(())
}
```

**Observe:** The weak reference does not keep the String alive.

## Exercises

1. **Predict and explain.** Draw the owning edges of the recursive list.

2. **Guided modification.** Add another node and predict its total.

3. **Independent construction.** Model a parent-child relationship with a weak back-reference.

4. **Diagnose a defect.** Diagnose an Rc cycle that keeps both objects alive.

5. **Boundary evidence.** Test an empty list and upgrading a dead weak reference.

6. **Transfer and justify.** Choose Box, Rc or Arc for unique, local-shared and cross-thread ownership scenarios.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Memory safety does not guarantee absence of leaks. Deep recursive drops can have stack costs. RefCell moves borrow checking to runtime and remains single-threaded.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Box, Rc, Weak without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-031: Box, Rc, Weak and recursive structures.
Read courses/rust/guides/rust-031.md and courses/rust/lessons/rust-031.rs. Prerequisites: rust-030.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-031_solution.rs and
courses/rust/solutions/rust-031_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
