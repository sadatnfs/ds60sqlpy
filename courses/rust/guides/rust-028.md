# rust-028: Arc, Mutex and compound shared invariants

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-027`

## Learning objectives

Share state across threads with Arc and Mutex while protecting compound invariants. The central exercise is task 3: Implement a locked bounded reservation operation.

## Purpose and mental model

Arc provides atomically reference-counted shared ownership. It does not make the stored value safely mutable by itself. Mutex provides mutually exclusive access to a protected value, and its guard releases the lock when dropped. Put the whole invariant inside that protected transition.

Several separately protected fields can still violate a relationship if updated under different locks or at different times. Lock ordering matters when several locks are involved. Keep protected work small and avoid calling unknown code while holding a lock. Poisoning reports a panic while a lock was held and requires an explicit recovery policy.

## Vocabulary and concepts

**Arc:** Thread-safe reference-counted shared ownership.

**Mutex:** A synchronization primitive granting exclusive protected access.

**Poisoning:** A signal that a panic occurred while a lock was held.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::sync` and `std::thread`. A passing run prints `rust-028: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Arc::clone shares ownership rather than deep-copying the value. Mutex::lock returns a result containing a guard. Dereferencing the mutable guard grants access until its scope ends.

**Reading Example A (Protect concurrent increments, code below).** `use std::sync::{Arc, Mutex};` imports both types. `Arc::new(Mutex::new(0))` puts a mutex-protected integer behind an atomically reference-counted pointer. Inside the scope the loop runs four times; each pass calls `Arc::clone(&count)`, which copies the pointer and increments the reference count without copying the integer, and the inner `let count` shadows the outer name. `move` transfers that clone into the spawned closure. Each worker runs its own loop of increments, and every increment calls `count.lock()`, which blocks until the mutex is free and returns a guard, and `unwrap` handles the poisoned case where an earlier holder panicked. `*count.lock().unwrap() += 1` writes through the guard, which is a temporary dropped at the end of the statement, releasing the lock. The scope joins all four workers automatically before the final read.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

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

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Arc is not a lock and clone does not copy its inner state. Holding a guard longer than needed can block unrelated work. Do not ignore poisoning without understanding whether the invariant survived.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Protect concurrent increments) before changing anything, and confirm its observation: All four hundred increments are retained.
2. Compare Example B (Protect a relationship in one value) with Example A and name the first line whose behavior differs. Its observation is: The transfer preserves the total under one protected tuple.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Arc is not a lock and clone does not copy its inner state.

Tempting approaches to rule out before you compare:

- **Task 1.** Drawing each `Arc::clone` as a copy of the counter predicts four separate counts of 100. The final 400 shows that all clones point to the same protected integer.
- **Task 2.** Locking once to read, releasing, and locking again to write the incremented value can lose updates between the two locks, and the total falls below 500 on some runs.
- **Task 5.** Recovering with `lock().unwrap_or_else(|p| p.into_inner())` everywhere and carrying on treats (7, 0) as a valid state and silently loses three units.

## Self-check and next step

In Example A, what does `Arc` share and what does `Mutex` protect, and why are all 400 increments retained? In Example B, why is the (7, 3) pair kept in one `Mutex` tuple rather than behind two separate locks? What does a poisoned lock tell you about the invariant it protected?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 16.3 Shared-State Concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html) for `Arc<Mutex<T>>` and lock guards.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
