# rust-014: Option and preserving missing information

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-013`

## Learning objectives

Represent missing values with Option and transform them without losing absence. The central exercise is task 3: Write a first-valid-item lookup returning Option.

## Purpose and mental model

Option represents either Some(value) or None. It is appropriate when absence is an expected outcome, such as a lookup finding no record. A real zero remains Some(0), keeping it distinct from missing information. This type-level distinction prevents sentinel values from leaking into valid calculations.

Unwrap asserts that absence is impossible and panics otherwise. Use it only when a nearby invariant or authored fixture makes that claim clear. Pattern matching, map and and_then let code retain absence through transformations until a boundary deliberately chooses a fallback. Choosing a default too early can erase information the caller needs.

## Vocabulary and concepts

**Option:** A type representing expected presence or absence.

**Some:** The present case containing a value.

**Fallback:** A deliberate replacement selected for absence.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-014: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`Option<T>` carries a present T or absence. `if let Some(value)` handles the present case. map transforms a present value; and_then chains an operation already returning Option. unwrap_or supplies a deliberate fallback.

**Reading Example A (Keep zero distinct from missing, code below).** `Some(0)` and `None` are the two variants of `Option<i32>`. The annotation on `missing` is required because a bare `None` says nothing about the type it would hold, while `measured` gets its type from the literal inside `Some`. `assert_ne!` passes when its arguments differ, and it can compare the two values because `Option<i32>` implements `PartialEq`, comparing the variant first and the payload second. `map` takes a closure, `|value| value + 1`, applies it to a `Some` payload and wraps the result in a new `Option`. `map` takes its receiver by value, but `Option<i32>` is `Copy`, so the call consumes a copy and `measured` would stay usable afterward.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Keep zero distinct from missing

Absence is a separate case, not a special numeric value.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let measured = Some(0);
        let missing: Option<i32> = None;
        assert_ne!(measured, missing);
        assert_eq!(measured.map(|value| value + 1), Some(1));
    }
    println!("rust-014: passed");
    Ok(())
}
```

**Observe:** A measured zero remains present and transforms to one.

### Example B: Propagate absence until a boundary

The fallback is not inserted into the collection and should not be mistaken for a valid measurement.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2, 4];
        assert_eq!(values.get(9).map(|value| value * 2), None);
        assert_eq!(values.get(9).copied().unwrap_or(-1), -1);
    }
    println!("rust-014: passed");
    Ok(())
}
```

**Observe:** An absent lookup stays absent until the explicit display fallback.

## Exercises

1. **Predict and explain.** Predict mapping Some(0) and None.

2. **Guided modification.** Render missing data as an unknown label instead of a numeric sentinel.

3. **Independent construction.** Write a first-valid-item lookup returning Option.

4. **Diagnose a defect.** Diagnose unwrap on an ordinary not-found path.

5. **Boundary evidence.** Test empty collections, present zero and out-of-range lookup.

6. **Transfer and justify.** Choose when absence should remain optional and when it should become a domain error.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

None does not explain a failure reason; use Result when a reason matters. A default can hide missing data. Avoid converting every optional to a panic merely to shorten control flow.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Keep zero distinct from missing) before changing anything, and confirm its observation: A measured zero remains present and transforms to one.
2. Compare Example B (Propagate absence until a boundary) with Example A and name the first line whose behavior differs. Its observation is: An absent lookup stays absent until the explicit display fallback.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: None does not explain a failure reason; use Result when a reason matters.

Tempting approaches to rule out before you compare:

- **Task 1.** Treating `None` like 0 predicts `Some(1)` for both, and treating `Some(0)` as empty predicts `None` for both. Each erases the distinction Example A's `assert_ne!(measured, missing)` establishes.
- **Task 2.** Keeping Example B's `unwrap_or(-1)` and printing the number is ambiguous wherever -1 is a valid reading, such as a temperature. `unwrap_or(0)` is worse here: a missing reading prints the same as the measured zero in Example A.
- **Task 3.** Using `find(|value| *value > 0)` treats zero as invalid, so `first_valid(&[-2, 0, 5])` returns `Some(5)` and the first assertion panics. The reference uses `>= 0` because a valid zero must be found.
- **Task 5.** Testing presence with `values.get(i).copied().unwrap_or(0) != 0` reports the stored zero as missing, collapsing the present-zero and absent cases this task separates.
- **Task 6.** Returning `Option<u16>` for the port with `raw?.parse().ok()` collapses a missing field and `port=abc` into the same `None`, so the caller cannot tell the user which problem to fix.

## Self-check and next step

What do `Some(0).map(|n| n + 1)` and `None.map(|n: i32| n + 1)` produce, and why is the first not a missing value? Where in Example B is the display fallback chosen, and what would be lost if it were chosen at the lookup? When should absence become a `Result` with a reason instead of staying `None`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::option` module documentation](https://doc.rust-lang.org/std/option/) for `map`, `and_then` and the `unwrap_or` family.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-014: Option and preserving missing information.
Read courses/rust/guides/rust-014.md and courses/rust/lessons/rust-014.rs. Prerequisites: rust-013.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-014_solution.rs and
courses/rust/solutions/rust-014_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
