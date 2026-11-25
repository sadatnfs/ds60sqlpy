# Rust study guide

Every Rust lesson guide in this track uses the same classroom pad, the same
answer-free learner file and the same six-task structure. This page explains
those shared routines once. Each lesson keeps what is specific to its own
mechanism: the mental model, the syntax anatomy, two worked examples, the six
tasks, the mistakes that lesson invites and the questions that test it.

## Run a lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned
Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and
`assert_eq!` remain active in normal builds, so a reference check is never
compiled away. The fixed pad accepts one source file without arbitrary
arguments, interactive input, Cargo manifests or package installation.

Every program's `main` returns `Result<(), Box<dyn std::error::Error>>`, so
later examples can propagate errors with `?`. The final `Ok(())` means the
fixture completed successfully. Standard library and Arrow examples remain
offline after image preparation. Multi-file Cargo and external ecosystem
projects have separate, explicit preparation workflows, and a lesson says so
when a task needs one.

## Attempt a lesson

Start with the answer-free learner file in `courses/rust/lessons/`. It lists
the six tasks as comments and stops with `todo!`, so running it unchanged
reports that the work remains unfinished. Replace that stop with your own
implementation.

The two worked programs in each guide are independently complete. Copy one at
a time into a separate exploratory pad when you want to experiment with it.
The executable reference in `courses/rust/solutions/` combines both scenarios,
their checked boundary observations and any reference task answers. Successful
checks are silent; the final `rust-NNN: passed` marker appears only after all of
them complete. The marker is execution evidence for those fixtures, not an
automatic assessment of your understanding.

## Trace a program

Read the operations in dependency order. Record which values exist before each
line, which expression produces a new value, and which operation changes shared
state.

Separate the two kinds of failure. When the compiler rejects source, no later
runtime observation exists, so the repair is to the types, ownership or syntax
the diagnostic names. When a check fails during execution, preserve the first
incorrect value and the smallest input that produced it, and repair the logic
that computed it.

## Keep evidence for each task

For each task, keep a short evidence table: input or initial state, your
prediction, the observed value or diagnostic, and the rule that explains it.
The guided examples establish mechanisms; the independent and transfer tasks
require your own representation and explanation.

The explanation page for each lesson gives an executed reference answer where
one has been written, a written answer where execution cannot show the point,
and says plainly where no single answer exists. Open it only after your own
attempt, then close it and reconstruct one boundary case from memory.

## Design a regression case

A useful regression case distinguishes the intended rule from the tempting
wrong rule. After a repair, check both the original example and the smallest
counterexample. Do not convert an error into a plausible default unless the
contract explicitly assigns that meaning. Keep resource cleanup and failure
propagation visible whenever the example owns a file, task or other resource.
Each lesson's pitfalls section lists tempting approaches drawn from its own
tasks; a good regression case rejects each of them.

## Self-check and review

Explain the lesson's vocabulary without reading the definitions. Reconstruct a
small example from a blank file, choose an input the chapter did not use, and
state one cost or limitation of the technique. Each guide ends with questions
specific to its mechanism; answer them before moving on.

When you finish a lesson, run the reference and confirm its marker, then
explain which check would reject a plausible wrong implementation. Save the
working pad and your reasoning; later chapters build on these contracts.

## Sources and execution boundary

The prose, small fixtures and task designs in this track are original. Each
lesson links the official documentation page that covers its mechanism. Those
links provide additional API detail; the classroom never fetches them.

Reading a guide, compiling a reference, running its assertions and completing
an external project are distinct achievements. External project steps need
their own build and platform evidence; a passing portable reference does not
establish them.
