# rust-030: Send, Sync and type-driven concurrency safety

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-029`

## Learning objectives

Use Send and Sync to explain which types the compiler lets cross thread boundaries. The central exercise is task 3: Choose a safe shared-state type for a small concurrent counter.

## Purpose and mental model

Send describes whether ownership of a value can cross thread boundaries. Sync describes whether shared references can be safely used across threads, with the relationship that a shared reference to T is Send when T is Sync. These marker traits express safety properties, not performance or automatic synchronization.

Rc is single-threaded shared ownership; Arc supports concurrent reference counts. Interior-mutability types have different synchronization rules. The compiler rejects unsafe combinations, but user-defined unsafe implementations can bypass that protection only under a rigorous invariant. Prefer composing known safe types before declaring manual marker implementations.

## Vocabulary and concepts

**Send:** A marker permitting ownership transfer across threads.

**Sync:** A marker permitting safe shared-reference access across threads.

**Marker trait:** A trait expressing a property without ordinary callable methods.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::sync` and `std::thread`. A passing run prints `rust-030: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

A generic bound `T: Send` requires cross-thread transfer capability. `T: Sync` requires safe shared access. Thread spawn also imposes a lifetime requirement; Send and static solve different constraints.

**Reading Example A (Transfer owned data, code below).** `std::thread::spawn` takes a closure and starts an operating-system thread that may outlive the function that created it. For that reason its signature requires the closure to be `'static` and `Send`: it may not borrow local data, and everything it captures must be safe to transfer to another thread. The `move` keyword makes the closure take ownership of `text`, which satisfies the first requirement, and `String` implements `Send`, which satisfies the second. The closure's result, `text.len()`, becomes the thread's return value. `spawn` returns a `JoinHandle<usize>`, and `join` waits for the thread and gives back `Result<usize, _>`, where `Err` would carry a panic payload. `unwrap` is acceptable in this fixture because a panic in the worker is a bug. After the move, the parent cannot use `text`; the string is freed in the worker when its closure finishes.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Transfer owned data

String's ownership and Send contract make the transfer valid without shared mutation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("owned");
        let worker = std::thread::spawn(move || text.len());
        assert_eq!(worker.join().unwrap(), 5);
    }
    println!("rust-030: passed");
    Ok(())
}
```

**Observe:** Owned text crosses the thread boundary and returns its length.

### Example B: Check capabilities at compile time

Compile-time capability evidence is different from a runtime stress test.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn require_send<T: Send>() {}
        fn require_sync<T: Sync>() {}
        require_send::<String>();
        require_sync::<String>();
        require_send::<std::sync::Arc<std::sync::Mutex<i32>>>();
        assert_eq!(std::sync::Arc::strong_count(&std::sync::Arc::new(1)), 1);
    }
    println!("rust-030: passed");
    Ok(())
}
```

**Observe:** The compiler accepts the declared safe capability combinations.

## Exercises

1. **Predict and explain.** Separate ownership transfer from shared access.

2. **Guided modification.** Move a Vec into a worker and return a derived value.

3. **Independent construction.** Choose a safe shared-state type for a small concurrent counter.

4. **Diagnose a defect.** Try sending Rc across threads and explain the diagnostic rather than adding unsafe.

5. **Boundary evidence.** Test a scoped borrowed input and compare its lifetime requirement with spawn.

6. **Transfer and justify.** Document why a proposed custom type is or is not Send and Sync from its members.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Send does not mean simultaneous mutation is safe. Static does not mean allocated forever; it constrains borrowed references in the value. Never add unsafe impl solely to silence a compiler error.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Transfer owned data) before changing anything, and confirm its observation: Owned text crosses the thread boundary and returns its length.
2. Compare Example B (Check capabilities at compile time) with Example A and name the first line whose behavior differs. Its observation is: The compiler accepts the declared safe capability combinations.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Send does not mean simultaneous mutation is safe.

Tempting approaches to rule out before you compare:

- **Task 1.** Treating `move` as making a copy for the thread predicts that `text` is still usable in `main`; using it after the spawn is E0382.
- **Task 2.** Dropping `move` makes the closure borrow `readings`, and `std::thread::spawn` rejects that with E0373 because the thread could outlive the vector.
- **Task 5.** Assuming `'static` means the data must live for the whole program leads to leaking or using global data. It only means the closure holds no borrowed references that could expire.

## Self-check and next step

Why can `text` move into the spawned thread in Example A, and what does `join` hand back? What do `require_send::<String>()` and `require_sync::<String>()` prove, and when is that proof checked? Which line would fail to compile if you added `require_send::<std::rc::Rc<i32>>()`, and why is `Rc` not `Send`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 16.4 Send and Sync](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html) for why `Rc` is neither.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-030: Send, Sync and type-driven concurrency safety.
Read courses/rust/guides/rust-030.md and courses/rust/lessons/rust-030.rs. Prerequisites: rust-029.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-030_solution.rs and
courses/rust/solutions/rust-030_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
