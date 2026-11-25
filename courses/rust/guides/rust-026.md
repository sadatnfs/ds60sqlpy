# rust-026: Maps, sets and algorithmic cost

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-025`

## Learning objectives

Choose BTreeMap, HashMap and sets for deterministic output and predictable cost. The central exercise is task 3: Build a deterministic frequency report.

## Purpose and mental model

Collection choice follows operations and identity policy. HashMap supports expected efficient lookup; BTreeMap keeps keys ordered. HashSet represents unique membership. A list scan can be appropriate for tiny data, but repeated scans over growing inputs can dominate a workload.

Define the grain of the result and the equality rule before choosing a container. Duplicate keys may aggregate, reject or replace, and those are different contracts. Stable report order should be deliberate. Big-O explains growth under a cost model, not an exact time guarantee on every machine.

## Vocabulary and concepts

**Identity policy:** The equality rule determining whether keys represent the same entity.

**Complexity:** Growth of resource work with input size.

**Ordered map:** A map whose traversal follows a key ordering.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::collections`. A passing run prints `rust-026: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

The entry API provides one lookup/update boundary. BTreeMap iteration is key-ordered. HashSet insert reports whether membership changed. Borrowed lookup can avoid allocating a new key.

**Reading Example A (Count repeated identities, code below).** `BTreeMap::new()` creates an empty map whose key type is inferred later from the first insertion, here `&str`. `counts.entry(label)` looks up the key once and returns an `Entry`, which is either occupied or vacant. `or_insert(0)` inserts 0 when the key is vacant and in both cases returns a `&mut i32` to the stored count; the leading `*` dereferences it so `+= 1` updates the value inside the map. That single lookup replaces a separate `get` followed by `insert`. `counts.get("b")` returns `Option<&i32>`, which is why the expected value is written `Some(&2)`. `keys()` yields keys in sorted order because a `BTreeMap` is ordered by key, and `copied()` turns each `&&str` into `&str` before collecting.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Count repeated identities

Aggregation and presentation order are explicit parts of the chosen representation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut counts = std::collections::BTreeMap::new();
        for label in ["b", "a", "b"] {
            *counts.entry(label).or_insert(0) += 1;
        }
        assert_eq!(counts.get("b"), Some(&2));
        assert_eq!(counts.keys().copied().collect::<Vec<_>>(), vec!["a", "b"]);
    }
    println!("rust-026: passed");
    Ok(())
}
```

**Observe:** Duplicate b accumulates and output keys are sorted.

### Example B: Distinguish first and duplicate insertion

Membership is a domain decision that can guide duplicate rejection or deduplication.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut seen = std::collections::HashSet::new();
        assert!(seen.insert("pear"));
        assert!(!seen.insert("pear"));
        assert!(!seen.contains("apple"));
    }
    println!("rust-026: passed");
    Ok(())
}
```

**Observe:** The set reports a duplicate without creating a second entry.

## Exercises

1. **Predict and explain.** State the grain and identity policy of each result.

2. **Guided modification.** Change duplicate handling from counting to rejection.

3. **Independent construction.** Build a deterministic frequency report.

4. **Diagnose a defect.** Diagnose relying on HashMap iteration order for a saved report.

5. **Boundary evidence.** Test empty input and repeated keys.

6. **Transfer and justify.** Compare repeated linear membership checks with a built index, including construction and memory costs.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Expected hash lookup cost is not a hard real-time guarantee. Do not persist hash values as stable identities. A collection choice does not by itself validate input or prevent overflow.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Count repeated identities) before changing anything, and confirm its observation: Duplicate b accumulates and output keys are sorted.
2. Compare Example B (Distinguish first and duplicate insertion) with Example A and name the first line whose behavior differs. Its observation is: The set reports a duplicate without creating a second entry.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Expected hash lookup cost is not a hard real-time guarantee.

Tempting approaches to rule out before you compare:

- **Task 1.** Calling Example A's grain one row per input record predicts three rows. Three labels produce two keys, because the second `"b"` updates the existing entry.
- **Task 2.** Writing `counts.insert(label, 1)` is a replace policy, not rejection: the second `"b"` silently overwrites the first and nothing tells the caller a duplicate arrived.
- **Task 3.** Writing `*counts.entry(word).or_insert(1) += 1` starts each new word at 1 and then adds 1, so every count is one too high and the assertion fails with `apple=2`, `fig=2`, `pear=3` on the left.
- **Task 5.** Writing `let words = [];` without a type fails with E0282, type annotations needed, because an empty array literal gives no element type to infer.
- **Task 6.** Building the `HashSet` inside the loop, once per SKU, pays the full construction for every lookup and ends up slower than the linear scan it was meant to replace.

## Self-check and next step

In Example A, why does the `BTreeMap` count for `b` reach 2 while the key appears once, and why are the keys listed as a then b? What does `HashSet::insert` return for the second "pear", and why is that return value worth checking? When does building a set or map pay for itself compared with repeated linear `contains` scans of a `Vec`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::collections` overview](https://doc.rust-lang.org/std/collections/index.html) for the cost table of each map and set.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-026: Maps, sets and algorithmic cost.
Read courses/rust/guides/rust-026.md and courses/rust/lessons/rust-026.rs. Prerequisites: rust-025.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-026_solution.rs and
courses/rust/solutions/rust-026_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
