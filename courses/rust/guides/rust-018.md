# rust-018: Generics, bounds and associated types

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-017`

## Learning objectives

Write generic functions and types with the trait bounds they actually need. The central exercise is task 3: Create a generic pair that swaps owned elements.

## Purpose and mental model

Generics retain relationships between input and output types without duplicating source. A trait bound states which operations are available on the parameter. A maximum function needs ordering; a container may need no capability beyond storing its element. Excessive bounds make an API harder to reuse.

Associated types express a type chosen by an implementation, as Iterator does with Item. A generic parameter instead lets a caller choose a type for a use. These are complementary tools. Preserve meaningful relationships rather than erasing everything to a trait object and recovering types through runtime checks.

## Vocabulary and concepts

**Generic parameter:** A type selected for a generic use.

**Trait bound:** A capability required of an admissible type.

**Associated type:** A type selected by a trait implementation.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-018: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`T: Ord` constrains a type parameter. Returning T preserves the selected type. `type Item = i32` defines an associated type in an implementation. where clauses can make complex bounds easier to read.

**Reading Example A (Retain the result type, code below).** `fn larger<T: Ord>(left: T, right: T) -> T` declares a type parameter `T` in angle brackets and a bound after the colon. The bound is a promise the caller must keep: whatever `T` is, it implements `Ord`, which supplies a total order and, through its `PartialOrd` supertrait, the `>=` operator the body uses. Both parameters and the result share the single name `T`, so the function cannot mix types or return a different one. At each call the compiler infers `T` from the arguments and generates a separate copy of the function for that type, a process called monomorphization; no boxing or run-time type check is involved. The two calls in Example A therefore produce two specialized versions. Because the parameters are taken by value, the call with `String` arguments moves both strings into `larger`, and the one not returned is dropped inside the function.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Retain the result type

The function moves its chosen result, preserving the concrete type rather than returning an untyped object.

```rust
fn larger<T: Ord>(left: T, right: T) -> T {
    if left >= right { left } else { right }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(larger(3, 8), 8);
        assert_eq!(larger(String::from("apple"), String::from("pear")), "pear");
    }
    println!("rust-018: passed");
    Ok(())
}
```

**Observe:** The same function returns an integer or owned String.

### Example B: Use an associated iterator item

The consumer knows which values the iterator yields and chooses a compatible aggregation.

```rust
fn larger<T: Ord>(left: T, right: T) -> T {
    if left >= right { left } else { right }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2, 3, 4];
        let total: i32 = values.into_iter().sum();
        assert_eq!(total, 9);
        assert_eq!(larger(5, 5), 5);
    }
    println!("rust-018: passed");
    Ok(())
}
```

**Observe:** The iterator's item relationship supports a typed sum.

## Exercises

1. **Predict and explain.** Identify each inferred type and required bound.

2. **Guided modification.** Use larger with a custom ordered value type.

3. **Independent construction.** Create a generic pair that swaps owned elements.

4. **Diagnose a defect.** Diagnose calling an unavailable method on an unconstrained T.

5. **Boundary evidence.** State tie behavior and test equal values.

6. **Transfer and justify.** Choose a generic parameter or associated type for a producer relationship and explain who selects it.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Generic code still has ownership and failure contracts. Deriving Ord chooses a field-order policy that may not match domain meaning. A broad bound should not replace an explicit comparator when multiple orderings are useful.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Retain the result type) before changing anything, and confirm its observation: The same function returns an integer or owned String.
2. Compare Example B (Use an associated iterator item) with Example A and name the first line whose behavior differs. Its observation is: The iterator's item relationship supports a typed sum.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Generic code still has ownership and failure contracts.

Tempting approaches to rule out before you compare:

- **Task 1.** Thinking `larger(3, String::from("x"))` should work because both types are `Ord` misses that the signature uses one `T` for both parameters; the call is E0308, mismatched types.
- **Task 2.** Declaring `minor` before `major` still compiles, but the derived order would then rank 1.9 above 2.0.
- **Task 5.** Testing ties only with `larger(5, 5)` passes for both `>=` and `>`, so it cannot detect a change in the policy.

## Self-check and next step

Why does `larger(3, 8)` compile while `larger(3, String::from("x"))` does not, even though both types are `Ord`? Which bound on `larger` makes its comparison compile, and which argument does it return for `larger(5, 5)`? Why does an iterator fix its `Item` as an associated type instead of letting each caller choose one?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 10.1 Generic Data Types](https://doc.rust-lang.org/book/ch10-01-syntax.html) for bounds and monomorphization.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-018: Generics, bounds and associated types.
Read courses/rust/guides/rust-018.md and courses/rust/lessons/rust-018.rs. Prerequisites: rust-017.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-018_solution.rs and
courses/rust/solutions/rust-018_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
