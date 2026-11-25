# rust-005: Expressions, branches and exhaustive matches

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-004`

## Learning objectives

Write exhaustive match and if expressions that cover every case, including boundaries. The central exercise is task 3: Write a negative, zero and positive classifier.

## Purpose and mental model

Rust treats many control-flow constructs as expressions producing values. An if expression must return compatible types from its branches. This encourages deriving one result instead of initializing a mutable variable and assigning it inconsistently on several paths.

Match handles patterns and requires coverage of possibilities. A broad wildcard can be useful for invalid numeric ranges but can hide newly added enum cases. Make boundaries explicit and test adjacent inputs. A correct normal example does not prove that an inclusive versus exclusive threshold is right.

## Vocabulary and concepts

**Expression:** Code that produces a value.

**Pattern:** A rule matching a value shape or category.

**Exhaustiveness:** Coverage of every possible input category.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-005: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`let label = if condition { "yes" } else { "no" };` uses a branch result. The final expression in a block has no semicolon when it supplies the value. `0..=59` is an inclusive pattern range.

**Reading Example A (Choose a value with if, code below).** On line 2, `if count > 0 { "present" } else { "empty" }` is an expression, not a statement, and its value initializes `label`. The condition must have type `bool`; Rust never treats a number as true or false, so a bare `if count` is a type error. Each arm is a block whose final expression supplies the arm's value, and both arms must agree on one type, here `&str`, because `label` gets exactly one type at compile time. Only the arm whose condition holds is evaluated. Because the value is chosen during initialization, `label` needs no `mut` and never holds a placeholder that a later line overwrites. Removing the `else` arm is rejected with E0317, because an `if` without `else` can only produce `()`.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Choose a value with if

Both branches return the same kind of value, so the result has one static type.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let count = 3;
        let label = if count > 0 { "present" } else { "empty" };
        assert_eq!(label, "present");
    }
    println!("rust-005: passed");
    Ok(())
}
```

**Observe:** The branch expression supplies one immutable label.

### Example B: Classify explicit boundaries

A tiny boundary fixture rejects an off-by-one policy error.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let classify = |score| match score {
            0..=59 => "retry",
            60..=100 => "pass",
            _ => "invalid",
        };
        assert_eq!(classify(59), "retry");
        assert_eq!(classify(60), "pass");
        assert_eq!(classify(101), "invalid");
    }
    println!("rust-005: passed");
    Ok(())
}
```

**Observe:** The transition at sixty and the invalid upper range are distinct.

## Exercises

1. **Predict and explain.** Identify the value produced by each branch.

2. **Guided modification.** Change the threshold and update neighboring tests.

3. **Independent construction.** Write a negative, zero and positive classifier.

4. **Diagnose a defect.** Diagnose a semicolon that changes a branch result into unit.

5. **Boundary evidence.** Test both valid endpoints and one value beyond each.

6. **Transfer and justify.** Choose explicit enum matches or a wildcard for a finite application state model.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A semicolon can change a block value. Match arm order matters when patterns overlap. A wildcard that hides an unhandled domain state weakens maintenance feedback.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Choose a value with if) before changing anything, and confirm its observation: The branch expression supplies one immutable label.
2. Compare Example B (Classify explicit boundaries) with Example A and name the first line whose behavior differs. Its observation is: The transition at sixty and the invalid upper range are distinct.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A semicolon can change a block value.

Tempting approaches to rule out before you compare:

- **Task 1.** Reading `0..=59` as exclusive predicts that 59 is not retry. With an exclusive pattern `0..59`, 59 would match neither range and fall to `_`, returning `"invalid"`, not `"pass"`.
- **Task 2.** Editing only the second arm to `70..=100` leaves 60 through 69 unmatched by either range. The wildcard keeps the match exhaustive, so it compiles, and `classify(65)` silently returns `"invalid"`.
- **Task 3.** Writing the first arm as `i32::MIN..=0` is an off-by-one: 0 matches it first and is classified negative. rustc warns that the later `0` arm is an unreachable pattern, and `assert_eq!(classify(0), "zero")` panics.
- **Task 5.** Testing 1 and 99 instead of 0 and 100 passes a classifier written as `1..=59` and `60..=99`, which wrongly sends 0 and 100 to `"invalid"`.
- **Task 6.** Writing `Order::Shipped => false, _ => true` is correct today, but when `Refunded` is added it silently becomes cancellable. The wildcard removes the compiler feedback the lesson's pitfall warns about.

## Self-check and next step

When `count` is 0, which string does `if count > 0 { "present" } else { "empty" }` bind, and what type error appears if a semicolon follows `"empty"`? What do `classify(59)`, `classify(60)` and `classify(101)` return, and which result changes if the first arm is written `0..59`? Why does a `_` arm stop the compiler from pointing at code that ignores a newly added enum variant?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 6.2 The match Control Flow Construct](https://doc.rust-lang.org/book/ch06-02-match.html) for exhaustiveness and the catch-all arm.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-005: Expressions, branches and exhaustive matches.
Read courses/rust/guides/rust-005.md and courses/rust/lessons/rust-005.rs. Prerequisites: rust-004.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-005_solution.rs and
courses/rust/solutions/rust-005_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
