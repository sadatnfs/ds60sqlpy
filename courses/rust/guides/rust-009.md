# rust-009: Shared borrowing and scope

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-008`

## Learning objectives

Write functions that borrow shared data and return slices tied to their input. The central exercise is task 3: Write a last-word function returning a borrowed slice.

## Purpose and mental model

A shared reference grants temporary read access without taking ownership. Several shared borrows can coexist when no conflicting mutation occurs. The owner must remain alive while borrowed data can still be used. Rust's borrow checker tracks these relationships through control flow, often ending a borrow after its last use rather than the end of the entire lexical block.

A borrowed API is useful for inspection, searching and parsing views. It avoids unnecessary allocation while preserving caller ownership. The lifetime constraint is not a runtime timer: it is a compile-time relationship between valid uses. Returning a reference to a local value is invalid because the owner disappears when the function returns.

## Vocabulary and concepts

**Shared borrow:** Temporary read access without ownership transfer.

**Lifetime:** The region in which a reference remains valid.

**Last use:** The final operation requiring a borrow to remain active.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-009: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`&value` creates a shared reference. Dereferencing with `*reference` accesses a referenced scalar when needed. Auto-dereferencing makes many method calls convenient. A return type `&str` must refer to storage owned elsewhere for a sufficient lifetime.

**Reading Example A (Borrow more than once, code below).** `let first = &text;` and `let second = &text;` create two shared references, of type `&String`, to the same owner. Shared borrows are read-only, so any number may exist at once; the compiler checks only that none outlives `text` and that no mutable borrow overlaps them. `first.len() + second.len()` reads through both references, and auto-dereference lets each method call reach the `String` without a `*`. A borrow lasts until its last use, not until the end of the block, so by the final assertion both readers are finished and `text` is compared directly. No text was copied at any point.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Borrow more than once

Both references inspect the same allocation without taking release responsibility.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("pear");
        let first = &text;
        let second = &text;
        assert_eq!(first.len() + second.len(), 8);
        assert_eq!(text, "pear");
    }
    println!("rust-009: passed");
    Ok(())
}
```

**Observe:** Two readers coexist and the owner remains intact.

### Example B: Return a borrowed view

The function returns a slice whose validity depends on the input owner.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn first_word(text: &str) -> &str {
            text.split_whitespace().next().unwrap_or("")
        }
        let sentence = String::from("pear apple");
        assert_eq!(first_word(&sentence), "pear");
        assert_eq!(first_word(""), "");
    }
    println!("rust-009: passed");
    Ok(())
}
```

**Observe:** The result is a view into caller-owned text, with an explicit empty policy.

## Exercises

1. **Predict and explain.** Identify the owner and both readers.

2. **Guided modification.** Add another read-only inspection without cloning.

3. **Independent construction.** Write a last-word function returning a borrowed slice.

4. **Diagnose a defect.** Try returning a reference to a local String and explain the compiler rejection.

5. **Boundary evidence.** Test empty text and a single word.

6. **Transfer and justify.** Choose a borrowed view or owned result for a parser whose caller may discard the input immediately.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A reference cannot make its owner live longer by declaration alone. Borrow duration follows actual use constraints. Avoid converting every slice to String unless independent ownership is needed.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Borrow more than once) before changing anything, and confirm its observation: Two readers coexist and the owner remains intact.
2. Compare Example B (Return a borrowed view) with Example A and name the first line whose behavior differs. Its observation is: The result is a view into caller-owned text, with an explicit empty policy.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A reference cannot make its owner live longer by declaration alone.

Tempting approaches to rule out before you compare:

- **Task 1.** Calling `first` an owner implies `let first = &text;` moved the string. If it had been written `let first = text;`, the next line `let second = &text;` would be rejected with E0382, borrow of moved value.
- **Task 2.** `let third = text.clone();` also passes the check but allocates a second `pear` and inspects the copy, the habit the pitfall warns against. Reaching for `&mut text` instead fails with E0596, because `text` is not declared mutable.
- **Task 3.** Splitting on a single space, `text.split(' ').last()`, looks equivalent but returns the empty piece after a trailing space: for `"pear apple "` it yields `""` instead of `apple`. `split_whitespace` skips runs of whitespace, so it returns the real last word.
- **Task 5.** Replacing `unwrap_or("")` with `unwrap()` passes every one-word and two-word case but panics on `""` with `called Option::unwrap() on a None value`, so the empty-text check never completes.
- **Task 6.** Returning `&str` and then dropping the input fails: `let name = { let line = String::from("pear 3"); first_word(&line) };` is rejected with E0597, `line` does not live long enough, because the view would outlive its owner.

## Self-check and next step

In Example A, where does each shared borrow of the text end, and why may both readers coexist? Why can `first_word` return a `&str` tied to its argument but never one pointing into a `String` created inside the function? What does `first_word("")` return, and is that `unwrap_or("")` a policy or an accident?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 4.2 References and Borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) for dangling references and shared borrows.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-009: Shared borrowing and scope.
Read courses/rust/guides/rust-009.md and courses/rust/lessons/rust-009.rs. Prerequisites: rust-008.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-009_solution.rs and
courses/rust/solutions/rust-009_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
