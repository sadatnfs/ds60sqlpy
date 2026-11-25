# rust-007: Functions, return values and contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-006`

## Learning objectives

Write pure functions with documented valid ranges and checks for them. The central exercise is task 3: Write a pure rectangle-area function with a documented valid range.

## Purpose and mental model

A function should expose accepted inputs, result meaning, mutation and failure. A compact signature cannot tell the whole story, so write the domain contract beside it. Begin with pure computations that return a value; their behavior is easy to test because they do not depend on hidden state.

Rust makes ownership transfer part of an argument type. Passing an integer copies it, while passing an owned String normally moves it. Borrowing can let a function inspect text while leaving ownership with the caller. Choose the signature from the needed capability rather than adding clones until the compiler is quiet.

## Vocabulary and concepts

**Parameter:** A typed input in a function declaration.

**Return type:** The type of a function result.

**Borrowed interface:** An interface accepting temporary access rather than ownership.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-007: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`fn double(value: i32) -> i32` declares input and output types. A final expression returns its value without a semicolon. `&str` accepts borrowed text, including literals and owned String views.

**Reading Example A (Return a derived integer, code below).** `fn double(value: i32) -> i32 { value * 2 }` is an item declared inside the block, and an item is visible throughout its enclosing block, even on lines written before it. Its signature is the contract: one `i32` in by value, one `i32` out. The body is a block whose last expression, `value * 2`, becomes the return value, so no `return` keyword is needed. At the call `double(original)`, the argument is evaluated and bound to the parameter `value`. Because `i32` implements `Copy`, that binding duplicates the bits, and `original` keeps its own 7. The function cannot reach the caller's variable at all; it sees only its parameter. The first assertion checks the returned value, and the second checks that the caller's binding is unchanged after the call. Rust performs no implicit integer conversion at a call, so `double(7_i64)` is rejected with E0308, mismatched types, expected `i32`, found `i64`.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Return a derived integer

The Copy semantics of this small value permit reuse without transferring an owned allocation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn double(value: i32) -> i32 {
            value * 2
        }
        let original = 7;
        assert_eq!(double(original), 14);
        assert_eq!(original, 7);
    }
    println!("rust-007: passed");
    Ok(())
}
```

**Observe:** The integer remains available after the call.

### Example B: Accept different text owners

The function needs only a read-only text view, so taking String would impose unnecessary ownership transfer.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn starts_with_p(text: &str) -> bool {
            text.starts_with('p')
        }
        let owned = String::from("pear");
        assert!(starts_with_p(&owned));
        assert!(!starts_with_p("apple"));
        assert_eq!(owned, "pear");
    }
    println!("rust-007: passed");
    Ok(())
}
```

**Observe:** One borrowed interface accepts owned text and a literal.

## Exercises

1. **Predict and explain.** Identify which arguments are copied and which are borrowed.

2. **Guided modification.** Add a function computing a labeled length from &str.

3. **Independent construction.** Write a pure rectangle-area function with a documented valid range.

4. **Diagnose a defect.** Diagnose an accidental semicolon on the final return expression.

5. **Boundary evidence.** Test empty text and zero dimensions.

6. **Transfer and justify.** Choose owned or borrowed inputs for an API that stores data after the call.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A reference is not permission to retain data beyond its lifetime. Pure-looking names can hide side effects. Do not clone an entire buffer when a borrow expresses the actual requirement.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Return a derived integer) before changing anything, and confirm its observation: The integer remains available after the call.
2. Compare Example B (Accept different text owners) with Example A and name the first line whose behavior differs. Its observation is: One borrowed interface accepts owned text and a literal.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A reference is not permission to retain data beyond its lifetime.

Tempting approaches to rule out before you compare:

- **Task 1.** Saying `owned` is copied into the function would require a `.clone()` that the code does not contain. Saying `original` is borrowed misses that `double` has a value parameter `value: i32`.
- **Task 2.** Labeling the result as characters while still calling `len` gives `note: 5 characters` for the four-letter café; the café fixture exposes the mismatch.
- **Task 5.** Treating empty input as invalid with `assert!(!text.is_empty())` makes the function panic on a legitimate empty field instead of reporting length 0.

## Self-check and next step

Which arguments in Example A and Example B are copied and which are borrowed? What does a function body produce if its last line ends with a semicolon, and why does an `i32` return type then fail to compile? When should a parameter be `String` rather than `&str`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 3.3 Functions](https://doc.rust-lang.org/book/ch03-03-how-functions-work.html) for statements versus a function's tail expression.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-007: Functions, return values and contracts.
Read courses/rust/guides/rust-007.md and courses/rust/lessons/rust-007.rs. Prerequisites: rust-006.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-007_solution.rs and
courses/rust/solutions/rust-007_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
