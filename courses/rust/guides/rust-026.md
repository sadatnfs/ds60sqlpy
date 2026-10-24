# rust-026: Maps, sets and algorithmic cost

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-025`

## Learning objectives

Build a deterministic frequency report. Then compare repeated linear membership checks with a built index, including construction and memory costs.

## Purpose and mental model

Collection choice follows operations and identity policy. HashMap supports expected efficient lookup; BTreeMap keeps keys ordered. HashSet represents unique membership. A list scan can be appropriate for tiny data, but repeated scans over growing inputs can dominate a workload.

Define the grain of the result and the equality rule before choosing a container. Duplicate keys may aggregate, reject or replace, and those are different contracts. Stable report order should be deliberate. Big-O explains growth under a cost model, not an exact time guarantee on every machine.

## Vocabulary and concepts

**Identity policy:** The equality rule determining whether keys represent the same entity.

**Complexity:** Growth of resource work with input size.

**Ordered map:** A map whose traversal follows a key ordering.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

The entry API provides one lookup/update boundary. BTreeMap iteration is key-ordered. HashSet insert reports whether membership changed. Borrowed lookup can avoid allocating a new key.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Count repeated identities

Aggregation and presentation order are explicit parts of the chosen representation.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut counts = std::collections::BTreeMap::new();
        for label in ["b", "a", "b"] { *counts.entry(label).or_insert(0) += 1; }
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

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Expected hash lookup cost is not a hard real-time guarantee. Do not persist hash values as stable identities. A collection choice does not by itself validate input or prevent overflow.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Identity policy, Complexity, Ordered map without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
