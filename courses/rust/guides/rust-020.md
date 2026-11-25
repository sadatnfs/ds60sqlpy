# rust-020: Iterators, laziness and consumption

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-019`

## Learning objectives

Build lazy iterator pipelines and know when consumption happens. The central exercise is task 3: Write a borrowed transformation returning a collected result.

## Purpose and mental model

Iterator adapters describe transformations that execute when consumed. Map and filter generally build a recipe; collect, sum or a loop drives it. Repeated iteration is possible only if the source can be recreated or borrowed appropriately. An iterator itself holds progress and may be exhausted.

The three common vector forms make ownership visible: iter yields shared references, iter_mut yields exclusive references, and into_iter consumes owned elements. Choose the form matching the work. A lazily executed closure with side effects is harder to reason about, so keep transformations pure unless the side effect is explicitly the lesson.

## Vocabulary and concepts

**Adapter:** An iterator transformation producing another iterator.

**Consumer:** An operation driving iteration to obtain a result.

**Exhaustion:** The state where an iterator returns no more values.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-020: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`iter().filter(...).map(...)` chains borrowed transformations. collect needs an inferred or annotated target. next advances one iterator instance. into_iter consumes the collection when the collection owns non-Copy elements.

**Reading Example A (Consume a transformation recipe, code below).** The chain on line 2 reads left to right. `values.iter()` borrows the vector and yields `&i32` items. `copied()` turns each `&i32` into an `i32`, so later closures work with plain integers. `filter` keeps the items for which its closure returns `true`, and `value % 2 == 0` tests evenness. `map` transforms each kept item. Each adapter only wraps the one before it, and `collect` is the consumer that drives the whole chain, pulling one item at a time through every stage. The annotation `Vec<_>` tells `collect` which collection to build, and the `_` lets the compiler infer the element type. The final assertion shows the source vector is intact.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Consume a transformation recipe

Copied turns referenced integers into independent small values before filtering and mapping.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![1, 2, 3, 4];
        let result: Vec<_> = values
            .iter()
            .copied()
            .filter(|value| value % 2 == 0)
            .map(|value| value * 10)
            .collect();
        assert_eq!(result, vec![20, 40]);
        assert_eq!(values.len(), 4);
    }
    println!("rust-020: passed");
    Ok(())
}
```

**Observe:** The recipe selects and transforms while retaining the borrowed source.

### Example B: Observe iterator progress

Calling next again does not restart the source automatically.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut iterator = [2, 3].into_iter();
        assert_eq!(iterator.next(), Some(2));
        assert_eq!(iterator.next(), Some(3));
        assert_eq!(iterator.next(), None);
    }
    println!("rust-020: passed");
    Ok(())
}
```

**Observe:** The iterator advances and eventually exhausts.

## Exercises

1. **Predict and explain.** Identify adapters and the final consumer.

2. **Guided modification.** Add a take limit and predict how much work is demanded.

3. **Independent construction.** Write a borrowed transformation returning a collected result.

4. **Diagnose a defect.** Diagnose constructing a lazy map and expecting it to execute immediately.

5. **Boundary evidence.** Test empty input and a partially consumed iterator.

6. **Transfer and justify.** Choose iter, iter_mut or into_iter for three operations and justify ownership.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Laziness does not mean no allocation if a later consumer collects. Reusing an exhausted iterator does not recreate it. A chain with hidden effects can execute at an unexpected boundary.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Consume a transformation recipe) before changing anything, and confirm its observation: The recipe selects and transforms while retaining the borrowed source.
2. Compare Example B (Observe iterator progress) with Example A and name the first line whose behavior differs. Its observation is: The iterator advances and eventually exhausts.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Laziness does not mean no allocation if a later consumer collects.

Tempting approaches to rule out before you compare:

- **Task 1.** Calling `filter` the consumer because it removes items gets the roles backwards. Without `collect`, the filter never runs, and the compiler warns that iterators are lazy and do nothing unless consumed.
- **Task 2.** Placing `take(1)` before `filter` takes only the first source item, 1, which is odd, so the result is empty. Adapter order changes which items the limit counts.
- **Task 3.** Ending the function body at `.map(|name| name.to_uppercase())` without `collect` fails with E0308: the body is a lazy `Map` iterator, not the `Vec<String>` the signature promises.
- **Task 5.** Expecting `collect` to restart and return `[2, 3, 4]` treats the iterator as the array. Calling `iterator.next()` after `collect` fails to compile with E0382, because `collect` took the iterator by value.
- **Task 6.** Using `into_iter()` for the sum consumes `prices`, so the discount loop then fails with E0382. Using `iter()` for the discount fails instead, because `*price -= ...` cannot assign through a `&` reference.

## Self-check and next step

Why does `values.iter().map(|v| v * 10);` on its own do no work and draw a compiler warning? Which call in Example A consumes the recipe, and why is the source still usable afterwards? In what order do the filter and map closures run for Example A's first two elements? Once Example B's iterator has returned `None`, what would collecting the rest produce?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 13.2 Iterators](https://doc.rust-lang.org/book/ch13-02-iterators.html) for lazy adapters and consuming methods.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-020: Iterators, laziness and consumption.
Read courses/rust/guides/rust-020.md and courses/rust/lessons/rust-020.rs. Prerequisites: rust-019.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-020_solution.rs and
courses/rust/solutions/rust-020_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
