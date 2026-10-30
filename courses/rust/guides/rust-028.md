# rust-028: Arc, Mutex and compound shared invariants

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-027`

## Learning objectives

Implement a locked bounded reservation operation. Then choose message passing or shared locking for a service and justify the invariant owner.

## Purpose and mental model

Arc provides atomically reference-counted shared ownership. It does not make the stored value safely mutable by itself. Mutex provides mutually exclusive access to a protected value, and its guard releases the lock when dropped. Put the whole invariant inside that protected transition.

Several separately protected fields can still violate a relationship if updated under different locks or at different times. Lock ordering matters when several locks are involved. Keep protected work small and avoid calling unknown code while holding a lock. Poisoning reports a panic while a lock was held and requires an explicit recovery policy.

## Vocabulary and concepts

**Arc:** Thread-safe reference-counted shared ownership.

**Mutex:** A synchronization primitive granting exclusive protected access.

**Poisoning:** A signal that a panic occurred while a lock was held.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Arc::clone shares ownership rather than deep-copying the value. Mutex::lock returns a result containing a guard. Dereferencing the mutable guard grants access until its scope ends.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Protect concurrent increments

The lock protects the complete read-modify-write transition, not merely its final assignment.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::{Arc, Mutex};
        let count = Arc::new(Mutex::new(0));
        std::thread::scope(|scope| {
            for _ in 0..4 {
                let count = Arc::clone(&count);
                scope.spawn(move || {
                    for _ in 0..100 {
                        *count.lock().unwrap() += 1;
                    }
                });
            }
        });
        assert_eq!(*count.lock().unwrap(), 400);
    }
    println!("rust-028: passed");
    Ok(())
}
```

**Observe:** All four hundred increments are retained.

### Example B: Protect a relationship in one value

Grouping related state makes the invariant's synchronization boundary visible.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let balances = std::sync::Mutex::new((10, 0));
        {
            let mut guard = balances.lock().unwrap();
            guard.0 -= 3;
            guard.1 += 3;
        }
        let guard = balances.lock().unwrap();
        assert_eq!(*guard, (7, 3));
        assert_eq!(guard.0 + guard.1, 10);
    }
    println!("rust-028: passed");
    Ok(())
}
```

**Observe:** The transfer preserves the total under one protected tuple.

## Exercises

1. **Predict and explain.** Draw shared ownership separately from mutable access.

2. **Guided modification.** Add another worker while keeping the exact expected total.

3. **Independent construction.** Implement a locked bounded reservation operation.

4. **Diagnose a defect.** Diagnose protecting each half of a transfer with unrelated locks.

5. **Boundary evidence.** Test zero operations and an explicitly handled poisoned lock in a separate controlled case.

6. **Transfer and justify.** Choose message passing or shared locking for a service and justify the invariant owner.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Arc is not a lock and clone does not copy its inner state. Holding a guard longer than needed can block unrelated work. Do not ignore poisoning without understanding whether the invariant survived.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Arc, Mutex, Poisoning without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-028: Arc, Mutex and compound shared invariants.
Read courses/rust/guides/rust-028.md and courses/rust/lessons/rust-028.rs. Prerequisites: rust-027.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-028_solution.rs and
courses/rust/solutions/rust-028_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
