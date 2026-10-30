# rust-016: Foundation project: a validated inventory report

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-015`

## Learning objectives

Render the sorted map with an explicit rejected count. Then design a structured import result retaining safe per-record failure categories.

## Purpose and mental model

The first project joins parsing, ownership, collection lookup and aggregation. Input validation decides which records enter the domain. Accepted duplicate names accumulate; rejected records are counted separately. A missing or malformed quantity must not become a valid zero merely because zero is convenient.

The fixture uses in-memory text and a sorted map so it remains deterministic and offline. BTreeMap provides ordered keys, while a HashMap would need explicit sorting for presentation. Keep parsing and calculation separate enough to diagnose the first incorrect state. Later chapters extend this kernel with files, concurrency and Arrow arrays.

## Vocabulary and concepts

**Admission:** The decision to accept a record into domain processing.

**Aggregation:** Combining accepted values by identity.

**Deterministic report:** Output whose ordering and meaning are explicitly controlled.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

split_once separates a simple two-field fixture. A second comma is rejected by integer parsing. BTreeMap entry gives one owned update point for a key. checked_add preserves overflow as a rejected record.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting. Do not advertise split_once as general CSV support. The later Arrow CSV chapter uses an actual parser.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Admission, Aggregation, Deterministic report without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
