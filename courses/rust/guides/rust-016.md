# rust-016: Foundation project: a validated inventory report

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-015`

## Learning objectives

Build a validated inventory importer that reports sorted totals and rejected rows. The central exercise is task 3: Render the sorted map with an explicit rejected count.

## Purpose and mental model

The first project joins parsing, ownership, collection lookup and aggregation. Input validation decides which records enter the domain. Accepted duplicate names accumulate; rejected records are counted separately. A missing or malformed quantity must not become a valid zero merely because zero is convenient.

The fixture uses in-memory text and a sorted map so it remains deterministic and offline. BTreeMap provides ordered keys, while a HashMap would need explicit sorting for presentation. Keep parsing and calculation separate enough to diagnose the first incorrect state. Later chapters extend this kernel with files, concurrency and Arrow arrays.

## Vocabulary and concepts

**Admission:** The decision to accept a record into domain processing.

**Aggregation:** Combining accepted values by identity.

**Deterministic report:** Output whose ordering and meaning are explicitly controlled.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::collections`. A passing run prints `rust-016: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

split_once separates a simple two-field fixture. A second comma is rejected by integer parsing. BTreeMap entry gives one owned update point for a key. checked_add preserves overflow as a rejected record.

**Reading Example A (Aggregate repeated valid items, code below).** `import_rows` returns a tuple: a `BTreeMap` of totals keyed by name and a count of rejected lines. Each line passes through guards. `let Some((name, quantity)) = line.split_once(',') else { ... }` binds both halves only when a comma exists; otherwise the `else` block must leave the iteration, here with `continue` after counting the rejection. The parse, the empty-name check and `checked_add` follow the same shape, so every way to fail has a counted exit. `*totals.get(name).unwrap_or(&0)` reads a previous total or a borrowed zero, and `insert` stores the new sum under an owned copy of the name made by `to_owned`.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Aggregate repeated valid items

Duplicate identities accumulate only after their values are admitted.

```rust
fn import_rows(lines: &[&str]) -> (std::collections::BTreeMap<String, u32>, usize) {
    let mut totals = std::collections::BTreeMap::new();
    let mut rejected = 0;
    for line in lines {
        let Some((name, quantity)) = line.split_once(',') else {
            rejected += 1;
            continue;
        };
        let Ok(quantity) = quantity.parse::<u32>() else {
            rejected += 1;
            continue;
        };
        if name.trim().is_empty() {
            rejected += 1;
            continue;
        }
        let previous: u32 = *totals.get(name).unwrap_or(&0);
        let Some(total) = previous.checked_add(quantity) else {
            rejected += 1;
            continue;
        };
        totals.insert(name.to_owned(), total);
    }
    (totals, rejected)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let (totals, rejected) = import_rows(&["pear,2", "apple,3", "pear,4"]);
        assert_eq!(totals.get("pear"), Some(&6));
        assert_eq!(totals.get("apple"), Some(&3));
        assert_eq!(rejected, 0);
    }
    println!("rust-016: passed");
    Ok(())
}
```

**Observe:** Pear totals six and apple totals three.

### Example B: Retain valid zero and rejection counts

This preserves absence, zero and rejection as different meanings.

```rust
fn import_rows(lines: &[&str]) -> (std::collections::BTreeMap<String, u32>, usize) {
    let mut totals = std::collections::BTreeMap::new();
    let mut rejected = 0;
    for line in lines {
        let Some((name, quantity)) = line.split_once(',') else {
            rejected += 1;
            continue;
        };
        let Ok(quantity) = quantity.parse::<u32>() else {
            rejected += 1;
            continue;
        };
        if name.trim().is_empty() {
            rejected += 1;
            continue;
        }
        let previous: u32 = *totals.get(name).unwrap_or(&0);
        let Some(total) = previous.checked_add(quantity) else {
            rejected += 1;
            continue;
        };
        totals.insert(name.to_owned(), total);
    }
    (totals, rejected)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let (totals, rejected) = import_rows(&["pear,0", "bad", "apple,-1", "pear,no"]);
        assert_eq!(totals.get("pear"), Some(&0));
        assert_eq!(rejected, 3);
        assert!(import_rows(&[]).0.is_empty());
    }
    println!("rust-016: passed");
    Ok(())
}
```

**Observe:** A valid zero remains present while three malformed records are excluded.

## Exercises

1. **Predict and explain.** Trace each record through parsing and accumulation.

2. **Guided modification.** Add one duplicate and predict its new total.

3. **Independent construction.** Render the sorted map with an explicit rejected count.

4. **Diagnose a defect.** Diagnose silently replacing a parse error with zero.

5. **Boundary evidence.** Test empty names, extra separators, overflow and empty input.

6. **Transfer and justify.** Design a structured import result retaining safe per-record failure categories.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting. Do not advertise split_once as general CSV support. The later Arrow CSV chapter uses an actual parser.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Aggregate repeated valid items) before changing anything, and confirm its observation: Pear totals six and apple totals three.
2. Compare Example B (Retain valid zero and rejection counts) with Example A and name the first line whose behavior differs. Its observation is: A valid zero remains present while three malformed records are excluded.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting.

Tempting approaches to rule out before you compare:

- **Task 1.** Predicting that `apple` appears with 0, or that `-1` lowers a total, misreads the parse step. `"-1".parse::<u32>()` is an error, so the apple record never reaches the map at all.
- **Task 2.** Predicting 1 assumes the map keeps the last record per key. That is what a simplified loop writing `totals.insert(name.to_owned(), quantity)` would do, discarding the earlier 6.
- **Task 3.** Collecting into a `HashMap` instead makes iteration order depend on a randomly seeded hasher, so the report can come out as `pear: 2` before `apple: 3` and the exact-string assertion fails on some runs but not others.
- **Task 5.** Using `line.split(',')` and taking the first two pieces would accept `"pear,2,3"` as pear 2, silently dropping the third field instead of rejecting a record the fixture format does not allow.
- **Task 6.** Collecting `format!("bad line: {line}")` strings copies untrusted input into the report and forces callers to parse messages to count categories.

## Self-check and next step

For the input in Example A, write each record's admission decision and the running per-item totals. Why does the report use `BTreeMap` rather than `HashMap`? Why must a valid zero quantity appear in the report while a malformed record only increases the rejected count?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `BTreeMap` documentation](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html) for ordered iteration and the `entry` API.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-016: Foundation project: a validated inventory report.
Read courses/rust/guides/rust-016.md and courses/rust/lessons/rust-016.rs. Prerequisites: rust-015.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-016_solution.rs and
courses/rust/solutions/rust-016_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
