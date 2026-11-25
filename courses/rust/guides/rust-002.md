# rust-002: Bindings, mutability and type inference

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-001`

## Learning objectives

Use immutable and mutable bindings deliberately and read the types the compiler infers. The central exercise is task 3: Write a running total with fixed input and mutable accumulator.

## Purpose and mental model

Rust bindings are immutable by default. `mut` grants permission to change a binding's value. Immutability reduces the number of state transitions a reader must consider, but it is not a substitute for understanding ownership and interior mutability introduced later. Prefer a new derived value when that expresses the operation clearly.

Type inference remains static: the compiler determines a concrete type from context. Shadowing introduces a new binding with the same name and can deliberately change its type. Reassignment instead changes the value of an existing mutable binding and must preserve its type. Use either technique to expose meaning rather than obscure where a value came from.

## Vocabulary and concepts

**Binding:** A name associated with a value.

**Mutability:** Permission to change a value through a particular binding or reference.

**Shadowing:** Introducing a new binding with an existing name.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-002: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`let count: i32 = 3` annotates a type. `let mut total = 0` allows reassignment. `let text = text.len()` shadows the earlier name with a new binding. Integer suffixes such as `3_u64` constrain inference.

**Reading Example A (Expose an accumulator, code below).** Neither `per_box` nor `total` has a type annotation, so the compiler infers one from use; with no other constraint, an integer literal defaults to `i32`. `per_box` is bound once and only read. `total` is declared with `let mut`, and `mut` is a property of the binding, not of the value: it is what permits the two `+=` lines, each of which reads `total`, adds `per_box` and stores the sum back in the same place. Track `total` by hand through the block before you run it. The final `assert_eq!` checks the accumulated value, and because `per_box` is never reassigned, nothing in the block can have changed the input.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Expose an accumulator

Only the value requiring state transitions is declared mutable.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let per_box = 4;
        let mut total = 0;
        total += per_box;
        total += per_box;
        assert_eq!(total, 8);
    }
    println!("rust-002: passed");
    Ok(())
}
```

**Observe:** The mutable total changes while the fixed input remains 4.

### Example B: Shadow after a representation change

Shadowing can change type, but names must still explain whether a value is text, length or parsed quantity.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let count = "12";
        let count: usize = count.len();
        assert_eq!(count, 2);
        let explicit = 3_u64;
        assert_eq!(explicit + 1, 4);
    }
    println!("rust-002: passed");
    Ok(())
}
```

**Observe:** The new count is the text length, not the number twelve.

## Exercises

1. **Predict and explain.** Identify the static type and mutability of each binding.

2. **Guided modification.** Remove unnecessary mut declarations in a small program.

3. **Independent construction.** Write a running total with fixed input and mutable accumulator.

4. **Diagnose a defect.** Diagnose assigning a String to a mutable integer binding.

5. **Boundary evidence.** Test an empty input string and a zero accumulator.

6. **Transfer and justify.** Choose shadowing or distinct names for parsing stages and justify readability.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Immutable does not mean every object reachable through a type is deeply frozen. Shadowing can conceal a units change. Type inference is not dynamic typing.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Expose an accumulator) before changing anything, and confirm its observation: The mutable total changes while the fixed input remains 4.
2. Compare Example B (Shadow after a representation change) with Example A and name the first line whose behavior differs. Its observation is: The new count is the text length, not the number twelve.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Immutable does not mean every object reachable through a type is deeply frozen.

Tempting approaches to rule out before you compare:

- **Task 1.** Describing `count` as one variable that changed from text to a number misreads shadowing. The second `let` creates a new binding and neither is mutable; writing `count = count.len();` without `let` would be rejected with a type mismatch.
- **Task 2.** Removing `mut` from every binding also strips it from `total`, and `total += per_box` then fails with E0384, cannot assign twice to an immutable variable. Silencing the warning with `#[allow(unused_mut)]` keeps the unneeded permission.
- **Task 3.** Switching the input to `let deliveries = vec![3, 5, 2];` with the same loop fails to compile: `for amount in deliveries` moves the `Vec`, so the later `assert_eq!(deliveries, ...)` is E0382, borrow of moved value. The array version works because `[i32; 3]` is `Copy`; the `Vec` version needs `for amount in &deliveries`.
- **Task 5.** Expecting `"".parse::<i32>()` to give 0 confuses empty with zero. It returns an `Err` whose kind is `Empty`, and calling `.unwrap()` on it panics with `ParseIntError { kind: Empty }`.
- **Task 6.** Following Example B literally, `let quantity = quantity_text.len();` compiles and yields 2, the number of digits, instead of 12. Both are `usize`-compatible values, so only a check on the value exposes the mix-up.

## Self-check and next step

Which binding in Example A stops compiling if you delete its `mut`, and what does the compiler suggest? After `let count = count.len();`, what is the type of the new `count`, and what happened to the earlier text binding? Explain why that is still static typing even though the name changed type.

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 3.1 Variables and Mutability](https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html) for `mut` and shadowing side by side.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-002: Bindings, mutability and type inference.
Read courses/rust/guides/rust-002.md and courses/rust/lessons/rust-002.rs. Prerequisites: rust-001.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-002_solution.rs and
courses/rust/solutions/rust-002_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
