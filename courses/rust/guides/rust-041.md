# rust-041: Variable-width arrays, nested values and zero-copy slices

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-040`

## Learning objectives

Build nested and variable-width Arrow columns and slice them without copying. The central exercise is task 3: Build a nested column from a small ragged dataset.

## Purpose and mental model

Variable-width arrays use offsets to locate each logical value in a shared data region. Nested list arrays add another layer: a parent position can be null, an empty list, or a nonempty list whose children may themselves be null. These states carry different meanings and must not be flattened indiscriminately.

Arrow slices often share underlying buffers instead of copying all data. This makes views cheap, but a small retained slice can keep a large allocation alive. Logical offsets and validity still matter. Zero-copy is a specific ownership and representation property, not a blanket claim that an entire analytical pipeline performs no allocations.

## Vocabulary and concepts

**Offset buffer:** Positions locating variable-width logical values.

**Nested validity:** Separate nullability at parent and child levels.

**Zero-copy view:** A view sharing existing storage rather than duplicating its payload.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array`. A passing run prints `rust-041: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

ListBuilder<Int32Builder> appends child values, then append(true) closes a valid parent list. append(false) adds a null parent. Array::slice creates a logical view over a selected region.

**Reading Example A (Distinguish nonempty, empty and null lists, code below).** `ListBuilder::new(Int32Builder::new())` creates a builder for a list column whose child values are 32-bit integers. Building a row takes two steps: push child values through `builder.values()`, which returns the inner `Int32Builder`, then close the row with `builder.append(valid)`. The first row appends a 2 and a null child before closing. The second `append(true)` closes a row with no children appended since the previous one. `append(false)` closes a row and marks the row itself null in the parent's validity bitmap. `finish()` produces a `ListArray`, which keeps one offsets buffer marking where each row's children start and end, so `value_length(i)` is the difference between two adjacent offsets.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Distinguish nonempty, empty and null lists

The first row even contains a null child, demonstrating independent validity levels.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Builder, ListBuilder};
        let mut builder = ListBuilder::new(Int32Builder::new());
        builder.values().append_value(2);
        builder.values().append_null();
        builder.append(true);
        builder.append(true);
        builder.append(false);
        let lists = builder.finish();
        assert_eq!(lists.len(), 3);
        assert_eq!(lists.value_length(0), 2);
        assert_eq!(lists.value_length(1), 0);
        assert!(lists.is_null(2));
    }
    println!("rust-041: passed");
    Ok(())
}
```

**Observe:** The three rows are a two-child list, an empty list and a null list.

### Example B: Slice without confusing logical positions

A view's logical indices are interpreted relative to the sliced array rather than the original source positions.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, StringArray};
        let values = StringArray::from(vec!["first", "middle", "last"]);
        let slice = values.slice(1, 1);
        let typed = slice.as_any().downcast_ref::<StringArray>().unwrap();
        assert_eq!(typed.len(), 1);
        assert_eq!(typed.value(0), "middle");
    }
    println!("rust-041: passed");
    Ok(())
}
```

**Observe:** The sliced array exposes middle at its logical index zero.

## Exercises

1. **Predict and explain.** Classify parent-null, empty and child-null states.

2. **Guided modification.** Add another valid list with two non-null children.

3. **Independent construction.** Build a nested column from a small ragged dataset.

4. **Diagnose a defect.** Diagnose treating an empty list as equivalent to a missing list.

5. **Boundary evidence.** Test zero-length slices and nonzero source offsets.

6. **Transfer and justify.** Explain when retaining a tiny shared slice may retain excessive memory and when copying is justified.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Nested nullability has several layers. Zero-copy views can extend buffer lifetime. Do not manually manipulate offset buffers without validating every format invariant.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Distinguish nonempty, empty and null lists) before changing anything, and confirm its observation: The three rows are a two-child list, an empty list and a null list.
2. Compare Example B (Slice without confusing logical positions) with Example A and name the first line whose behavior differs. Its observation is: The sliced array exposes middle at its logical index zero.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Nested nullability has several layers.

Tempting approaches to rule out before you compare:

- **Task 1.** Reading `value_length(2) == 0` as an empty list misses that row 2 is null; the length of a null row carries no meaning.
- **Task 2.** Calling `append(true)` before appending 7 and 9 closes an empty row 3 and gives the next row the two children, so `value_length(3)` is 0.
- **Task 5.** Indexing the slice with source positions, `typed.value(2)` for middle, reads last instead.

## Self-check and next step

Example A's first list holds 2 and a null child: why is its `value_length` 2, and how does that null child differ from the null third row? Why is the empty second list not the same as a null list in a count of observations? After `values.slice(1, 1)`, why does "middle" appear at index 0, and which parent buffers does the slice still keep alive?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Arrow columnar format specification](https://arrow.apache.org/docs/format/Columnar.html) for offset buffers and nested validity.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-041: Variable-width arrays, nested values and zero-copy slices.
Read courses/rust/guides/rust-041.md and courses/rust/lessons/rust-041.rs. Prerequisites: rust-040.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-041_solution.rs and
courses/rust/solutions/rust-041_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
