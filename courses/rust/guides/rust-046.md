# rust-046: Diagnostics, security boundaries and safe output

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-045`

## Learning objectives

Emit safe diagnostic events and enforce allowlisted permissions at trust boundaries. The central exercise is task 3: Instrument an importer with submitted, accepted and rejected counts.

## Purpose and mental model

Operational evidence should explain an outcome without exposing raw private input. Use stable stages, result categories and bounded counters. A parsing error, rejected domain value and unknown external effect are different categories. Correlation identity connects observations of one operation without embedding credentials or payloads.

Security boundaries appear wherever data gains authority: paths reach files, text becomes commands, or requests select resources. Prefer fixed reviewed operations and typed parsing over string-built commands. Rust memory safety does not provide authentication, authorization or an input-size policy. Keep those responsibilities visible in system design.

## Vocabulary and concepts

**Correlation identity:** A value connecting observations of one operation.

**Authorization:** A decision about permitted actions on a resource.

**Allowlist:** An explicit set of admitted values or operations.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-046: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

A diagnostic record can contain a fixed operation ID, stage, outcome and count. Match exact allowed actions rather than executing arbitrary input. Format only reviewed fields and bound output volume.

**Reading Example A (Describe outcome without raw payload, code below).** `struct Event` holds three `&'static str` fields and a `usize` count, so an event can carry only labels fixed in the program text and a number, never a borrowed piece of input read at run time. `render(&self)` formats the fields with `format!`, using positional `{}` placeholders filled in order by `self.operation`, `self.stage`, `self.outcome` and `self.count`. The literal `count=` before the last placeholder labels the number so the line can be searched. Example A constructs the event with struct literal syntax, naming every field. The assertion compares the whole rendered line, so an extra field or changed wording fails the check.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

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

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Memory safety does not make arbitrary command execution safe. Do not log secrets or unbounded payloads. A successful process exit can still contain domain rejections that need explicit reporting.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Describe outcome without raw payload) before changing anything, and confirm its observation: The event retains useful context without echoing input contents.
2. Compare Example B (Reject unlisted actions) with Example A and name the first line whose behavior differs. Its observation is: Only explicitly listed actions are admitted.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Memory safety does not make arbitrary command execution safe.

Tempting approaches to rule out before you compare:

- **Task 1.** Treating `&'static str` as proof of safety goes too far: `Box::leak` can turn any input into a `&'static str`. The type is a strong hint; the reviewed fixed vocabulary is the actual rule.
- **Task 2.** Adding a `detail: String` field to hold text such as the rejected line widens the event to raw input, which is exactly what this lesson's events are designed to exclude.
- **Task 3.** Parsing with `parse::<i32>()` accepts `"-1"`, so the counts become accepted 3 and rejected 1 and the event assertion fails, even though a negative quantity is not a valid record.
- **Task 5.** Checking `action.starts_with("report:")` to cover both listed actions also admits `"report:delete"`, turning a missing entry into implicit permission.
- **Task 6.** Running `Command::new("sh").arg("-c").arg(format!("report {id}"))` lets an id of `1; echo injected` run a second command. Rust's memory safety does nothing to prevent that.

## Self-check and next step

Which fields does `Event::render` include in "fixture-1 validate rejected count=2", and what does it deliberately leave out? Why does Example B admit `report:read` through an allowlist instead of listing `report:delete` as forbidden? How does a fixed identifier such as `fixture-1` help an operator without echoing a user's data?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::fmt::Debug` documentation](https://doc.rust-lang.org/std/fmt/trait.Debug.html) for why derived `Debug` output can leak secret fields.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
