# rust-013: Enums and state-specific payloads

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-012`

## Learning objectives

Model an import as pending, completed or rejected with state-specific information. Then design valid transitions between states and explain which transitions should be rejected.

## Purpose and mental model

An enum represents one case from a declared set. Each case can carry the data relevant to that state. This prevents impossible combinations such as a success flag paired with an error message and no result. Match exposes the state distinction and binds the appropriate payload.

Use enums for meaningful alternatives, not merely to avoid strings. Adding a state requires reviewing transitions and consumers. Exhaustive matching helps the compiler identify affected code. A wildcard may be justified for intentionally open categories, but it weakens feedback when the domain is meant to be closed.

## Vocabulary and concepts

**Enum variant:** One allowed alternative of an enum type.

**Payload:** Data associated with a particular state.

**Exhaustive match:** Handling every declared alternative.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`enum Outcome { Ready(u32), Failed(String) }` declares alternatives. `match value` consumes or borrows according to the matched expression. Matching `&value` can inspect owned payloads without moving them.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Render a success payload

The rendering function borrows the state and extracts only the matching payload.

```rust
enum Outcome { Ready(u32), Failed(String) }
fn render(value: &Outcome) -> String { match value { Outcome::Ready(count) => format!("count:{count}"), Outcome::Failed(reason) => format!("error:{reason}") } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let value = Outcome::Ready(4);
        assert_eq!(render(&value), "count:4");
    }
    println!("rust-013: passed");
    Ok(())
}
```

**Observe:** The ready state carries a count rather than an unrelated optional field.

### Example B: Render a distinct failure

The model cannot simultaneously be both ready and failed.

```rust
enum Outcome { Ready(u32), Failed(String) }
fn render(value: &Outcome) -> String { match value { Outcome::Ready(count) => format!("count:{count}"), Outcome::Failed(reason) => format!("error:{reason}") } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let value = Outcome::Failed(String::from("invalid"));
        assert_eq!(render(&value), "error:invalid");
        assert!(matches!(value, Outcome::Failed(_)));
    }
    println!("rust-013: passed");
    Ok(())
}
```

**Observe:** Failure preserves its reason and remains a distinct state.

## Exercises

1. **Predict and explain.** Identify which payload is valid in each state.

2. **Guided modification.** Add a Loading variant and update every exhaustive consumer.

3. **Independent construction.** Model an import as pending, completed or rejected with state-specific information.

4. **Diagnose a defect.** Diagnose a collection of optional fields that permits contradictory states.

5. **Boundary evidence.** Test every declared variant.

6. **Transfer and justify.** Design valid transitions between states and explain which transitions should be rejected.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Matching an owned enum can move its String payload. Use a borrowed match when retaining the original is intended. Avoid a wildcard that silently renders new domain states as success.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Enum variant, Payload, Exhaustive match without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-013: Enums and state-specific payloads.
Read courses/rust/guides/rust-013.md and courses/rust/lessons/rust-013.rs. Prerequisites: rust-012.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-013_solution.rs and
courses/rust/solutions/rust-013_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
