# rust-032: Composition project: a reusable inventory library

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-031`

## Learning objectives

Build and test a reusable library crate through its documented Cargo commands. The central exercise is task 3: Build and test InventoryLab through its documented Cargo commands.

## Purpose and mental model

The intermediate project separates a pure domain library from an executable adapter and integration tests. A library can expose validated operations without knowing whether its caller is a command-line tool, a browser worker or a future service. The adapter owns presentation and process behavior.

The checked-in InventoryLab is a real Cargo package using only the standard library. The pad runs the same kind of portable kernel, while Cargo build and Cargo test are deliberately separate project commands. Preserve input accounting, deterministic output and overflow behavior when extracting modules. A successful library test is not a claim that an external service or deployment is configured.

## Vocabulary and concepts

**Library crate:** A reusable Rust compilation unit exposing a public API.

**Adapter:** Code translating external input/output into core contracts.

**Integration test:** A test exercising a public boundary as a consumer.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::collections`. A passing run prints `rust-032: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).

Use the actual [InventoryLab](../fixtures/InventoryLab/README.md) for a library, executable and integration-test workflow. It requires no third-party crates.

## Syntax anatomy and execution trace

A BTreeMap result preserves sorted identity. A report record carries accepted totals and rejected count. Integration tests use the library public API, which catches accidental exposure or missing exports.

**Reading Example A (Create a stable report, code below).** `summarize<'a>` ties the returned map's keys to the input rows: the map stores `&'a str` names borrowed from the caller's slice instead of allocating copies. The loop pattern `for &(name, value) in rows` destructures each borrowed tuple, copying the `&str` and the `i32` out of it. The guard rejects empty names and negative values with `continue`. `*totals.get(name).unwrap_or(&0)` reads an existing total or a borrowed zero, and `checked_add` rejects a sum that would overflow `i32` instead of wrapping. In Example A, `report.0` reads the first element of the returned tuple, the map.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Create a stable report

The core chooses data semantics while presentation can remain a separate adapter.

```rust
fn summarize<'a>(rows: &[(&'a str, i32)]) -> (std::collections::BTreeMap<&'a str, i32>, usize) {
    let mut totals = std::collections::BTreeMap::new();
    let mut rejected = 0;
    for &(name, value) in rows {
        if name.is_empty() || value < 0 {
            rejected += 1;
            continue;
        }
        let previous: i32 = *totals.get(name).unwrap_or(&0);
        if let Some(total) = previous.checked_add(value) {
            totals.insert(name, total);
        } else {
            rejected += 1;
        }
    }
    (totals, rejected)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let report = summarize(&[("b", 2), ("a", 3), ("b", 4)]);
        assert_eq!(report.0.get("b"), Some(&6));
        assert_eq!(report.0.keys().copied().collect::<Vec<_>>(), vec!["a", "b"]);
    }
    println!("rust-032: passed");
    Ok(())
}
```

**Observe:** The report accumulates duplicates and orders keys.

### Example B: Retain rejected input evidence

The library contract preserves information needed by every future adapter.

```rust
fn summarize<'a>(rows: &[(&'a str, i32)]) -> (std::collections::BTreeMap<&'a str, i32>, usize) {
    let mut totals = std::collections::BTreeMap::new();
    let mut rejected = 0;
    for &(name, value) in rows {
        if name.is_empty() || value < 0 {
            rejected += 1;
            continue;
        }
        let previous: i32 = *totals.get(name).unwrap_or(&0);
        if let Some(total) = previous.checked_add(value) {
            totals.insert(name, total);
        } else {
            rejected += 1;
        }
    }
    (totals, rejected)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let report = summarize(&[("", 2), ("a", -1), ("b", 0)]);
        assert_eq!(report.1, 2);
        assert_eq!(report.0.get("b"), Some(&0));
    }
    println!("rust-032: passed");
    Ok(())
}
```

**Observe:** Two invalid rows are counted and a valid zero remains present.

## Exercises

1. **Predict and explain.** Trace validation and accumulation as separate responsibilities.

2. **Guided modification.** Add a report-rendering function without changing the core representation.

3. **Independent construction.** Build and test InventoryLab through its documented Cargo commands.

4. **Diagnose a defect.** Diagnose moving console output into a reusable domain method.

5. **Boundary evidence.** Test empty, duplicate, invalid and overflow cases.

6. **Transfer and justify.** Design a second adapter that reuses the same validated library without copying its implementation.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A multi-file Cargo project is not accepted by the single-file pad. Keep generated target output out of source packaging. A dependency-free project still needs the prepared compiler and standard library.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Create a stable report) before changing anything, and confirm its observation: The report accumulates duplicates and orders keys.
2. Compare Example B (Retain rejected input evidence) with Example A and name the first line whose behavior differs. Its observation is: Two invalid rows are counted and a valid zero remains present.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A multi-file Cargo project is not accepted by the single-file pad.

Tempting approaches to rule out before you compare:

- **Task 1.** Moving the overflow check into row validation, for example rejecting values near `i32::MAX`, cannot work: `("b", i32::MAX)` is a valid row on its own and only overflows after an earlier `("b", 1)`.
- **Task 2.** Changing `summarize` to return the rendered `String` breaks every existing caller: `report.0.get("b")` in Example A then fails with E0609, no field `0` on type `String`.
- **Task 3.** Pasting `src/lib.rs` and `src/main.rs` into the pad fails: the pad compiles one `main.rs`, so `inventory_lab::summarize` names a crate that does not exist there and rustc reports E0433, failed to resolve.
- **Task 5.** Expecting the overflow row to wrap to `i32::MIN`, or to replace the total with 1, assumes plain addition or a replace policy. `checked_add` refuses the sum, so the map keeps the last valid total.
- **Task 6.** Copying `summarize` into the new binary to tweak its output creates a second validator that drifts: a later fix to the library's overflow handling would not reach the copy.

## Self-check and next step

What does `summarize` return for Example A, and why are its keys ordered? In Example B, why do the empty name and the negative value only raise the rejected count while `b` keeps a valid zero? Which conversion must a second adapter perform before calling `summarize`, so that it reuses the library rather than copying it?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 11.3 Test Organization](https://doc.rust-lang.org/book/ch11-03-test-organization.html) for unit tests versus integration tests against a library.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-032: Composition project: a reusable inventory library.
Read courses/rust/guides/rust-032.md and courses/rust/lessons/rust-032.rs. Prerequisites: rust-031.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-032_solution.rs and
courses/rust/solutions/rust-032_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
