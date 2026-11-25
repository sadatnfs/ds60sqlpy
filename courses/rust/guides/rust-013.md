# rust-013: Enums and state-specific payloads

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-012`

## Learning objectives

Model states with enums whose variants carry only their own data, handled by exhaustive matches. The central exercise is task 3: Model an import as pending, completed or rejected with state-specific information.

## Purpose and mental model

An enum represents one case from a declared set. Each case can carry the data relevant to that state. This prevents impossible combinations such as a success flag paired with an error message and no result. Match exposes the state distinction and binds the appropriate payload.

Use enums for meaningful alternatives, not merely to avoid strings. Adding a state requires reviewing transitions and consumers. Exhaustive matching helps the compiler identify affected code. A wildcard may be justified for intentionally open categories, but it weakens feedback when the domain is meant to be closed.

## Vocabulary and concepts

**Enum variant:** One allowed alternative of an enum type.

**Payload:** Data associated with a particular state.

**Exhaustive match:** Handling every declared alternative.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-013: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`enum Outcome { Ready(u32), Failed(String) }` declares alternatives. `match value` consumes or borrows according to the matched expression. Matching `&value` can inspect owned payloads without moving them.

**Reading Example A (Render a success payload, code below).** `enum Outcome { Ready(u32), Failed(String) }` declares a type with exactly two variants, and each variant carries its own payload: a `u32` count for `Ready` and a `String` reason for `Failed`. A value is always exactly one variant, so an `Outcome` can never hold both a count and a reason. `render(value: &Outcome)` borrows the value and uses `match` to choose an arm. The patterns `Outcome::Ready(count)` and `Outcome::Failed(reason)` both test the variant and bind its payload to a name that is in scope only inside that arm. Because `value` is a reference, match ergonomics make those bindings references too, and nothing is moved out. `format!` builds a new `String` in each arm. The `match` is exhaustive: adding a third variant without a new arm is rejected with E0004, non-exhaustive patterns. Example A constructs `Outcome::Ready(4)`, so only the first arm runs.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Render a success payload

The rendering function borrows the state and extracts only the matching payload.

```rust
enum Outcome {
    Ready(u32),
    Failed(String),
}
fn render(value: &Outcome) -> String {
    match value {
        Outcome::Ready(count) => format!("count:{count}"),
        Outcome::Failed(reason) => format!("error:{reason}"),
    }
}

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
enum Outcome {
    Ready(u32),
    Failed(String),
}
fn render(value: &Outcome) -> String {
    match value {
        Outcome::Ready(count) => format!("count:{count}"),
        Outcome::Failed(reason) => format!("error:{reason}"),
    }
}

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

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Matching an owned enum can move its String payload. Use a borrowed match when retaining the original is intended. Avoid a wildcard that silently renders new domain states as success.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Render a success payload) before changing anything, and confirm its observation: The ready state carries a count rather than an unrelated optional field.
2. Compare Example B (Render a distinct failure) with Example A and name the first line whose behavior differs. Its observation is: Failure preserves its reason and remains a distinct state.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Matching an owned enum can move its String payload.

Tempting approaches to rule out before you compare:

- **Task 1.** Assuming every `Outcome` has both a count and a reason, with one of them empty, describes a struct with optional fields rather than this enum.
- **Task 2.** Adding `_ => String::from("count:0")` instead of a `Loading` arm compiles but reports an unfinished import as a successful one with zero rows.
- **Task 5.** Testing only `Outcome::Ready(4)` and calling the enum covered leaves the `Failed` arm unexercised, so a typo such as `eror:` would ship unnoticed.

## Self-check and next step

Which payload does each variant of the lesson's enum carry, and why can a failed outcome never also report a count? After adding a `Loading` variant, which code does the compiler force you to revisit, and which code would a `_` arm hide? Why does matching on an owned enum value move its `String` payload?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 6.1 Defining an Enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html) for variants that carry different payloads.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
