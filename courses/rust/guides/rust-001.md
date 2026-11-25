# rust-001: Source, compilation and the first Rust program

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: None. Begin with the source file and visible result.

## Learning objectives

Compile and run a Rust program and check a computed value with assert_eq! instead of trusting printed text. The central exercise is task 3: Compute the capacity of three shelves with eight books each.

## Purpose and mental model

Rust checks source before producing a native executable. A compiler diagnostic means the program has not reached its entrypoint. A panic during execution means an operation violated a checked assumption. Successful output means only the path that actually ran completed. Keep these forms of evidence separate when learning to diagnose a program.

The classroom supplies a pinned compiler and Arrow library inside Linux Docker. The browser sends a single source file, not a Cargo project or arbitrary shell command. Start by tracing a tiny calculation and independently checking its result. This builds the habit of distinguishing observed behavior from a printed success claim.

## Vocabulary and concepts

**Compiler:** A tool checking source and producing executable code.

**Macro:** Syntax expanded before ordinary compilation.

**Panic:** An execution failure indicating an unrecovered violated assumption.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-001: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`fn main` declares the entry function. `let` introduces a binding. `println!` is a macro, indicated by the exclamation mark. `assert_eq!` compares actual and expected values and panics on disagreement. A semicolon turns an expression into a statement whose value is discarded.

**Reading Example A (Check a greeting, code below).** `main` returns `Result<(), Box<dyn std::error::Error>>`, so `?` can be used inside it, and the inner `{ }` block keeps Example A's names from leaking into later code. `let greeting = "Hello, Rust";` binds a string literal of type `&'static str`, a borrowed view of text stored in the compiled binary, so nothing is allocated at run time. The trailing `!` marks `assert_eq!` and `println!` as macros, expanded into ordinary code before type checking. `assert_eq!` panics and prints both sides when they differ. In `println!("{greeting}")` the braces capture the variable by name, and the macro writes a newline after it. `Ok(())` at the end reports success to the runtime.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Check a greeting

The explicit check connects a value to its expected observation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let greeting = "Hello, Rust";
        assert_eq!(greeting, "Hello, Rust");
        println!("{greeting}");
    }
    println!("rust-001: passed");
    Ok(())
}
```

**Observe:** Hello, Rust appears before the lesson marker.

### Example B: Calculate instead of copying output

A second check rejects a plausible wrong operator rather than merely confirming that printing works.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let rows = 4;
        let seats_per_row = 6;
        let seats = rows * seats_per_row;
        assert_eq!(seats, 24);
        assert_ne!(seats, rows + seats_per_row);
    }
    println!("rust-001: passed");
    Ok(())
}
```

**Observe:** The calculated capacity is 24, while addition would give 10.

## Exercises

1. **Predict and explain.** Predict the greeting and final marker order.

2. **Guided modification.** Change the greeting and keep its expected value independent.

3. **Independent construction.** Compute the capacity of three shelves with eight books each.

4. **Diagnose a defect.** Remove a closing brace temporarily and classify the compiler diagnostic.

5. **Boundary evidence.** Check zero shelves and one shelf.

6. **Transfer and justify.** Model a three-level capacity calculation and explain every intermediate value.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A compiler success does not establish business correctness. Do not replace a failing assertion with a success print. The Result-returning main wrapper is scaffolding for later error propagation; its full meaning is taught in the error chapters.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Check a greeting) before changing anything, and confirm its observation: Hello, Rust appears before the lesson marker.
2. Compare Example B (Calculate instead of copying output) with Example A and name the first line whose behavior differs. Its observation is: The calculated capacity is 24, while addition would give 10.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A compiler success does not establish business correctness.

Tempting approaches to rule out before you compare:

- **Task 1.** Predicting a confirmation line after each assertion, or the value 24 in the output, treats a check as a print. Predicting the marker first ignores that its `println!` is the final statement before `Ok(())`.
- **Task 2.** Writing `let expected = greeting; assert_eq!(greeting, expected);` compares the binding with itself. It passes for `"Hi, Feris"` or any other text, so the check can never reject a mistake.
- **Task 3.** Writing `let capacity = 24;` and asserting 24 copies the answer instead of computing it, so the check would still pass if the operator were wrong. Writing `shelves + books_per_shelf` instead gives 11, which this assertion does reject.
- **Task 5.** Using addition, `shelves + books_per_shelf`, claims an empty bookcase holds 8 books and a single shelf holds 9. Testing only the three-shelf case would catch that too, but would not show that an empty bookcase is handled.
- **Task 6.** Skipping a level, for example `floors * shelves_per_room * books_per_shelf`, multiplies floors by a per-room figure and yields 64. Writing the whole product as one literal expression hides which level was dropped.

## Self-check and next step

Before running Example B, say what `assert_eq!` would report if the capacity used `+` instead of `*`, and why the lesson marker would then never print. A missing brace, a failed assertion and a wrong but unchecked value fail at different stages: which stage stops each one, and which can a printed marker never rule out?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 1.2 Hello, World!](https://doc.rust-lang.org/book/ch01-02-hello-world.html) for how `rustc` turns one source file into an executable.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-001: Source, compilation and the first Rust program.
Read courses/rust/guides/rust-001.md and courses/rust/lessons/rust-001.rs. Prerequisites: none.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-001_solution.rs and
courses/rust/solutions/rust-001_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
