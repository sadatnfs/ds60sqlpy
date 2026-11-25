# rust-010: Exclusive borrowing and mutation boundaries

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-009`

## Learning objectives

Mutate data through exclusive borrows, including split borrows of one slice. The central exercise is task 3: Write a function swapping the ends of a mutable slice safely.

## Purpose and mental model

An exclusive reference grants mutation while preventing conflicting access to the same storage. The common rule is either shared readers or one exclusive borrower at a time. This is a capability rule about access, not a claim that the operating system has locked memory.

Small scopes make mutation ownership easier to see. After an exclusive borrow's last use, the owner can be used again. APIs such as split_at_mut safely produce disjoint mutable regions because they establish that the regions do not overlap. Do not reach for unsafe code merely because the compiler cannot infer a relationship you have not expressed.

## Vocabulary and concepts

**Exclusive borrow:** Temporary access permitting mutation without conflicting aliases.

**Aliasing:** Several paths referring to the same storage.

**Disjoint regions:** Storage ranges that do not overlap.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-010: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`&mut value` creates exclusive access and the original binding must permit mutation. A function taking &mut T may update the borrowed value but does not own its eventual destruction. split_at_mut proves disjoint slices.

**Reading Example A (Mutate through one explicit borrower, code below).** `fn append_mark(text: &mut String)` declares a parameter that is an exclusive, mutable borrow: the function may change the `String` but does not own it and cannot free it. The caller opts in twice. `let mut text` makes the binding mutable, which is required before any `&mut` borrow can be taken from it, and the call site writes `&mut text` explicitly, so a reader of the block can see where mutation may happen. Inside the function, `text.push('!')` appends one `char`; the method may reallocate the heap buffer if capacity runs out, which is exactly why no other reference may exist during the call. When `append_mark` returns, the exclusive borrow ends, ownership never left the caller, and the assertion reads the changed value through the original owner. Passing `&text` instead is rejected with E0308, because a shared reference cannot stand where `&mut String` is expected.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Mutate through one explicit borrower

The function receives mutation capability for the duration of the call.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn append_mark(text: &mut String) {
            text.push('!');
        }
        let mut text = String::from("ready");
        append_mark(&mut text);
        assert_eq!(text, "ready!");
    }
    println!("rust-010: passed");
    Ok(())
}
```

**Observe:** The caller retains ownership and observes the deliberate mutation.

### Example B: Mutate two proven-disjoint regions

The standard library API establishes disjointness instead of relying on two potentially overlapping index borrows.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut values = [1, 2, 3, 4];
        let (left, right) = values.split_at_mut(2);
        left[0] = 9;
        right[0] = 8;
        assert_eq!(values, [9, 2, 8, 4]);
    }
    println!("rust-010: passed");
    Ok(())
}
```

**Observe:** The two slices mutate separate halves safely.

## Exercises

1. **Predict and explain.** Trace who may access text during the mutable call.

2. **Guided modification.** Add a second mutation after the first borrow ends.

3. **Independent construction.** Write a function swapping the ends of a mutable slice safely.

4. **Diagnose a defect.** Create conflicting mutable borrows and explain the compiler diagnostic.

5. **Boundary evidence.** Test an empty slice and a split at either endpoint.

6. **Transfer and justify.** Design an API that exposes only the smallest mutable region needed by a transformation.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

An exclusive borrow is not a thread lock. More mut annotations do not solve aliasing conflicts. Prefer safe disjointness APIs to manually asserting pointer safety.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Mutate through one explicit borrower) before changing anything, and confirm its observation: The caller retains ownership and observes the deliberate mutation.
2. Compare Example B (Mutate two proven-disjoint regions) with Example A and name the first line whose behavior differs. Its observation is: The two slices mutate separate halves safely.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An exclusive borrow is not a thread lock.

Tempting approaches to rule out before you compare:

- **Task 1.** Thinking the function receives a copy predicts that `main` still sees `ready`; the passing assertion shows the change happened in place through the borrow.
- **Task 2.** Placing `values[3] = 7;` between `left[0] = 9;` and `right[0] = 8;` is rejected with E0506, cannot assign to `values[_]` because it is borrowed, because `right` is still used afterwards and so its borrow of `values` is still live.
- **Task 5.** Assuming a split at 0 is invalid and guarding with `if mid > 0` skips the legitimate whole-slice case; using `split_at_mut(4)` to probe the far edge panics instead of observing it.

## Self-check and next step

While a function holds `&mut text`, what may the caller do with `text`, and when does that permission come back? Why does `split_at_mut` succeed where two separate `&mut slice[..]` borrows fail? What does `split_at_mut(0)` return, and why is that a valid split rather than an error?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `split_at_mut` documentation](https://doc.rust-lang.org/std/primitive.slice.html#method.split_at_mut) for how a safe API proves two mutable regions disjoint.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-010: Exclusive borrowing and mutation boundaries.
Read courses/rust/guides/rust-010.md and courses/rust/lessons/rust-010.rs. Prerequisites: rust-009.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-010_solution.rs and
courses/rust/solutions/rust-010_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
