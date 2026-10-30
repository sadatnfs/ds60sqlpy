# rust-046: Diagnostics, security boundaries and safe output

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-045`

## Learning objectives

Instrument an importer with submitted, accepted and rejected counts. Then design a fixed-operation boundary that separates validated data from executable instructions.

## Purpose and mental model

Operational evidence should explain an outcome without exposing raw private input. Use stable stages, result categories and bounded counters. A parsing error, rejected domain value and unknown external effect are different categories. Correlation identity connects observations of one operation without embedding credentials or payloads.

Security boundaries appear wherever data gains authority: paths reach files, text becomes commands, or requests select resources. Prefer fixed reviewed operations and typed parsing over string-built commands. Rust memory safety does not provide authentication, authorization or an input-size policy. Keep those responsibilities visible in system design.

## Vocabulary and concepts

**Correlation identity:** A value connecting observations of one operation.

**Authorization:** A decision about permitted actions on a resource.

**Allowlist:** An explicit set of admitted values or operations.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A diagnostic record can contain a fixed operation ID, stage, outcome and count. Match exact allowed actions rather than executing arbitrary input. Format only reviewed fields and bound output volume.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Describe outcome without raw payload

The field set is intentionally small and reviewable.

```rust
struct Event {
    operation: &'static str,
    stage: &'static str,
    outcome: &'static str,
    count: usize,
}
impl Event {
    fn render(&self) -> String {
        format!("{} {} {} count={}", self.operation, self.stage, self.outcome, self.count)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let event = Event {
            operation: "fixture-1",
            stage: "validate",
            outcome: "rejected",
            count: 2,
        };
        assert_eq!(event.render(), "fixture-1 validate rejected count=2");
    }
    println!("rust-046: passed");
    Ok(())
}
```

**Observe:** The event retains useful context without echoing input contents.

### Example B: Reject unlisted actions

A missing policy entry is not implicit permission.

```rust
struct Event {
    operation: &'static str,
    stage: &'static str,
    outcome: &'static str,
    count: usize,
}
impl Event {
    fn render(&self) -> String {
        format!("{} {} {} count={}", self.operation, self.stage, self.outcome, self.count)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let allowed = ["report:read", "report:list"];
        assert!(allowed.contains(&"report:read"));
        assert!(!allowed.contains(&"report:delete"));
    }
    println!("rust-046: passed");
    Ok(())
}
```

**Observe:** Only explicitly listed actions are admitted.

## Exercises

1. **Predict and explain.** Identify every field safe to emit in the event.

2. **Guided modification.** Add a fixed stage category without adding raw input.

3. **Independent construction.** Instrument an importer with submitted, accepted and rejected counts.

4. **Diagnose a defect.** Diagnose including a token or entire source record in an error message.

5. **Boundary evidence.** Test missing permissions and empty workloads.

6. **Transfer and justify.** Design a fixed-operation boundary that separates validated data from executable instructions.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Memory safety does not make arbitrary command execution safe. Do not log secrets or unbounded payloads. A successful process exit can still contain domain rejections that need explicit reporting.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Correlation identity, Authorization, Allowlist without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-046: Diagnostics, security boundaries and safe output.
Read courses/rust/guides/rust-046.md and courses/rust/lessons/rust-046.rs. Prerequisites: rust-045.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-046_solution.rs and
courses/rust/solutions/rust-046_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
