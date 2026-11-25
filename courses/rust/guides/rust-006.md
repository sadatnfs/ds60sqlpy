# rust-006: Loops, iterators and termination evidence

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-005`

## Learning objectives

Write loops and iterator searches that terminate and report not-found with Option. The central exercise is task 3: Implement a first-match search with Option output.

## Purpose and mental model

A loop repeats a state transition. An invariant explains what remains true, and a termination argument explains why repetition stops. For a sum, the accumulator equals the values already processed. For a search, the inspected prefix contains no earlier match before the chosen result.

For-in consumes an iterable, so ownership of the sequence or its borrowed view matters. Iterating an array of small Copy values can look similar to borrowing a vector, but the types determine what remains available. Use iterator adapters when they expose intent, and use an explicit loop when intermediate state or early exits need explanation.

## Vocabulary and concepts

**Invariant:** A property preserved by every iteration.

**Iterator:** A producer of successive values.

**Termination:** A reason the repeated process eventually stops.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-006: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`for value in &values` borrows elements. `enumerate` supplies traversal positions. `break` exits a loop, and loop itself can return a value through break value. An exclusive range uses `0..n`.

**Reading Example A (Maintain a sum invariant, code below).** `vec![2, 4, 6]` allocates a vector of three `i32` values on the heap. The loop header `for value in &values` iterates over a shared reference, so the loop borrows the vector instead of consuming it, and each `value` has type `&i32`. `total += value` still compiles because `i32` implements `AddAssign<&i32>`, so no explicit `*value` is needed. The loop has no index and no explicit condition: it asks the iterator for the next item and stops when the iterator returns `None`, which must happen after the last element of a finite vector. That is the termination argument. Write down what `total` holds at the top of each iteration; that relationship is the invariant. The last line checks that the vector still exists with its length unchanged. Writing `for value in values` would move the vector into the loop, and that line would fail with E0382, borrow of moved value.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Maintain a sum invariant

The loop changes only its accumulator, not the source ownership.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 4, 6];
        let mut total = 0;
        for value in &values {
            total += value;
        }
        assert_eq!(total, 12);
        assert_eq!(values.len(), 3);
    }
    println!("rust-006: passed");
    Ok(())
}
```

**Observe:** The borrowed traversal totals twelve and retains the vector.

### Example B: Find the first position

Position stops at the first matching element rather than returning the last repeated match.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [3, 8, 8];
        assert_eq!(values.iter().position(|value| *value == 8), Some(1));
        assert_eq!(values.iter().position(|value| *value == 9), None);
    }
    println!("rust-006: passed");
    Ok(())
}
```

**Observe:** The first match is position one and absence stays explicit.

## Exercises

1. **Predict and explain.** Write the accumulator before and after every iteration.

2. **Guided modification.** Skip negative values while preserving a clear invariant.

3. **Independent construction.** Implement a first-match search with Option output.

4. **Diagnose a defect.** Diagnose an inclusive loop bound used as an array index.

5. **Boundary evidence.** Test empty, singleton and repeated-match sequences.

6. **Transfer and justify.** Design a bounded retry loop and state both its progress measure and its effect policy.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

An iterator can consume values or borrow them depending on its construction. A position is not automatically a valid index in a different collection. Avoid unbounded loops without a deliberate stop and cancellation policy.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Maintain a sum invariant) before changing anything, and confirm its observation: The borrowed traversal totals twelve and retains the vector.
2. Compare Example B (Find the first position) with Example A and name the first line whose behavior differs. Its observation is: The first match is position one and absence stays explicit.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An iterator can consume values or borrow them depending on its construction.

Tempting approaches to rule out before you compare:

- **Task 1.** Listing the values 2, 4, 6 as the accumulator's states confuses the element with the running total. Writing `for value in values` would also change the answer to the later check: it moves the vector, and `values.len()` becomes E0382.
- **Task 2.** Clamping with `total += value.max(0)` gets the same 10 but loses the count of discarded readings, so a batch that was mostly negative looks as healthy as a clean one.
- **Task 5.** Returning the last matching index by keeping a `found = Some(index)` variable without stopping passes the empty and singleton cases but returns Some(2) for the repeated case.

## Self-check and next step

State Example A's loop invariant in one sentence. Why does `for value in &values` leave `values` usable after the loop while `for value in values` does not? What should the first-match search return for an empty slice, and why is position 0 the wrong answer? Name the quantity that strictly decreases in a bounded retry loop.

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 13.2 Iterators](https://doc.rust-lang.org/book/ch13-02-iterators.html) for the difference between `iter`, `iter_mut` and `into_iter`.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-006: Loops, iterators and termination evidence.
Read courses/rust/guides/rust-006.md and courses/rust/lessons/rust-006.rs. Prerequisites: rust-005.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-006_solution.rs and
courses/rust/solutions/rust-006_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
