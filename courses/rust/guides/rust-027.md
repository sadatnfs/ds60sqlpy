# rust-027: Scoped threads and explicit joins

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-026`

## Learning objectives

Run work on scoped threads that borrow local data and join results back to the parent. The central exercise is task 3: Build a scoped parallel computation returning values to the parent.

## Purpose and mental model

A thread can run concurrently with its creator and must have a clear lifetime owner. Unscoped thread spawn requires captured references to satisfy the required lifetime, often leading to owned move captures. Scoped threads instead guarantee joining before the scope returns, allowing safe borrowing of suitable local data.

Joining observes completion and panic outcomes. Do not infer completion from a sleep. Independent tasks can compute values and return them to one owner, avoiding shared mutable state. Threads are an execution mechanism, not an automatic speedup for tiny workloads or blocked external systems.

## Vocabulary and concepts

**Thread:** An independently scheduled execution context.

**Join:** Waiting for and observing a thread outcome.

**Scoped thread:** A thread whose lifetime is bounded by its enclosing scope.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::thread`. A passing run prints `rust-027: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

std::thread::scope bounds child lifetimes. scope.spawn creates a scoped worker. join returns its result or panic information. Immutable borrowed inputs can be shared when their types satisfy the concurrency requirements.

**Reading Example A (Borrow local input safely, code below).** `std::thread::scope` takes a closure that receives a `scope` value and does not return until every thread spawned through that value has finished. `scope.spawn(|| values.iter().sum::<i32>())` starts a worker running the inner closure. That closure is not marked `move`, so it captures `values` by shared reference, which is allowed only because the scope guarantees the worker ends before `values` could be dropped. `sum::<i32>()` uses turbofish syntax to name the result type, since `sum` can produce several types. `spawn` returns a `ScopedJoinHandle`; calling `join` waits for the worker and returns `Result<i32, _>`, where `Err` holds the panic payload if the worker panicked. `expect` turns that `Err` into a panic in the parent with a message. The outer closure ends with the `join` expression, so its value becomes `total`. After the scope returns, the borrow is over and `values.len()` is valid. Plain `std::thread::spawn` would reject the same borrowing closure, because an unscoped thread may outlive the function that created it.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Borrow local input safely

The scope guarantees the worker cannot outlive the owner of the borrowed vector.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 3, 4];
        let total = std::thread::scope(|scope| {
            let handle = scope.spawn(|| values.iter().sum::<i32>());
            handle.join().expect("fixture worker")
        });
        assert_eq!(total, 9);
        assert_eq!(values.len(), 3);
    }
    println!("rust-027: passed");
    Ok(())
}
```

**Observe:** The borrowed input remains usable after the joined scope.

### Example B: Return independent results

No shared writable accumulator is needed for this decomposition.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let total = std::thread::scope(|scope| {
            let left = scope.spawn(|| 2 + 3);
            let right = scope.spawn(|| 4 + 5);
            left.join().unwrap() + right.join().unwrap()
        });
        assert_eq!(total, 14);
    }
    println!("rust-027: passed");
    Ok(())
}
```

**Observe:** The parent combines two completed results.

## Exercises

1. **Predict and explain.** Identify who owns input and each thread handle.

2. **Guided modification.** Split an array into two borrowed halves and combine their totals.

3. **Independent construction.** Build a scoped parallel computation returning values to the parent.

4. **Diagnose a defect.** Diagnose dropping a handle and assuming the work finished.

5. **Boundary evidence.** Test empty partitions and an intentional worker panic in a controlled external test.

6. **Transfer and justify.** Choose threads or sequential work using workload size and synchronization cost.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Sleep is not a synchronization guarantee. A joined panic is a distinct failure that should not become a default successful result. More threads can increase overhead and resource pressure.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Borrow local input safely) before changing anything, and confirm its observation: The borrowed input remains usable after the joined scope.
2. Compare Example B (Return independent results) with Example A and name the first line whose behavior differs. Its observation is: The parent combines two completed results.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Sleep is not a synchronization guarantee.

Tempting approaches to rule out before you compare:

- **Task 1.** Saying the thread owns `values` would require a `move` closure and would make `values.len()` after the scope fail with E0382.
- **Task 2.** Computing the halves as `&values[..mid]` and `&values[mid - 1..]` double-counts one element and still looks plausible on small inputs.
- **Task 5.** Writing `worker.join().unwrap_or(0)` turns a crashed worker into a plausible zero, exactly the default success the lesson warns about.

## Self-check and next step

Why may the thread spawned in Example A borrow `values` when `std::thread::spawn` would need `move` and an owned vector? When does the scope join its threads, and what happens to a panic in one of them? Why is Example B's total 14 no matter which thread finishes first?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::thread::scope` documentation](https://doc.rust-lang.org/std/thread/fn.scope.html) for why scoped threads may borrow local data.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-027: Scoped threads and explicit joins.
Read courses/rust/guides/rust-027.md and courses/rust/lessons/rust-027.rs. Prerequisites: rust-026.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-027_solution.rs and
courses/rust/solutions/rust-027_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
