# rust-013: explanation and comparison

Executable reference: [rust-013_solution.rs](rust-013_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Render a success payload:** The rendering function borrows the state and extracts only the matching payload. The ready state carries a count rather than an unrelated optional field.

**Render a distinct failure:** The model cannot simultaneously be both ready and failed. Failure preserves its reason and remains a distinct state.

## Task answers

### Task 1: Predict and explain

Identify which payload is valid in each state.

**Written answer.** `Outcome::Ready` carries only a `u32` count and `Outcome::Failed` carries only a `String` reason. A ready value such as `Outcome::Ready(4)` has no reason field to read, and a failed value has no count, so `render` can only reach `count` in the `Ready` arm and `reason` in the `Failed` arm.

**Why it is correct.** Each variant declares its own payload, and a `match` arm binds only the fields of the variant it matched. The type system therefore rules out a failed outcome that also claims a count.

**Plausible wrong approach.** Assuming every `Outcome` has both a count and a reason, with one of them empty, describes a struct with optional fields rather than this enum.

**How to verify.** Try `if let Outcome::Ready(reason) = &value { let _ = reason.len(); }`: it fails with E0599 because `reason` is a `&u32`, not a String.

### Task 2: Guided modification

Add a Loading variant and update every exhaustive consumer.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    enum Status {
        Loading,
        Ready(u32),
        Failed(String),
    }
    fn describe(value: &Status) -> String {
        match value {
            Status::Loading => String::from("loading"),
            Status::Ready(count) => format!("count:{count}"),
            Status::Failed(reason) => format!("error:{reason}"),
        }
    }
    assert_eq!(describe(&Status::Loading), "loading");
    assert_eq!(describe(&Status::Ready(4)), "count:4");
    assert_eq!(
        describe(&Status::Failed(String::from("invalid"))),
        "error:invalid"
    );
    Ok(())
}
```

**Observe:** Loading renders as loading, while Ready(4) and Failed(invalid) still render as count:4 and error:invalid.

The new variant has no payload because nothing is known yet. Adding it to the enum without the new arm makes `describe` fail with E0004, non-exhaustive patterns: `&Status::Loading` not covered, which is how the compiler lists every consumer to update.

**Plausible wrong approach.** Adding `_ => String::from("count:0")` instead of a `Loading` arm compiles but reports an unfinished import as a successful one with zero rows.

**How to verify.** Run the block. Delete the `Status::Loading` arm and read E0004 naming the missing variant.

### Task 3: Independent construction

Model an import as pending, completed or rejected with state-specific information.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    enum Import {
        Pending { queued: usize },
        Completed { rows: usize },
        Rejected { reason: String },
    }
    fn describe(state: &Import) -> String {
        match state {
            Import::Pending { queued } => format!("pending:{queued}"),
            Import::Completed { rows } => format!("done:{rows}"),
            Import::Rejected { reason } => format!("rejected:{reason}"),
        }
    }
    assert_eq!(describe(&Import::Pending { queued: 2 }), "pending:2");
    assert_eq!(describe(&Import::Completed { rows: 5 }), "done:5");
    let rejected = Import::Rejected {
        reason: String::from("bad header"),
    };
    assert_eq!(describe(&rejected), "rejected:bad header");
    Ok(())
}
```

**Observe:** The three states render as pending:2, done:5 and rejected:bad header.

Each variant carries only the data that makes sense in that state, and the exhaustive match must handle all three.

### Task 4: Diagnose a defect

Diagnose a collection of optional fields that permits contradictory states.

**Written answer.** The defect is `struct Import { pending: bool, rows: Option<usize>, reason: Option<String> }`. Nothing stops `Import { pending: true, rows: Some(5), reason: Some(String::from("bad header")) }`, which is pending, completed and rejected at once, and every reader must guess which field wins. Replace it with task 3's enum, where each state holds only its own data.

**Why it is correct.** An enum value is exactly one variant, so contradictory combinations cannot be constructed. With optional fields, every consumer repeats the same validity checks and some will forget one.

**Plausible wrong approach.** Adding a `fn is_valid(&self) -> bool` check documents the rule but still lets invalid values be created and passed around before anyone calls it.

**How to verify.** Construct the contradictory struct and note that it compiles. Then try to give `Import::Pending` a `rows` field in the enum version: E0559, variant has no field named `rows`.

### Task 5: Boundary evidence

Test every declared variant.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block. Helpers used: `Outcome` and `render`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cases = [
        (Outcome::Ready(0), "count:0"),
        (Outcome::Ready(u32::MAX), "count:4294967295"),
        (Outcome::Failed(String::new()), "error:"),
        (
            Outcome::Failed(String::from("bad header")),
            "error:bad header",
        ),
    ];
    for (value, expected) in &cases {
        assert_eq!(render(value), *expected);
    }
    Ok(())
}
```

**Observe:** Ready(0) and Ready(u32::MAX) render their counts, an empty failure reason renders as error:, and a real reason is appended after error:.

Both declared variants are covered, each with an ordinary and an edge payload. The table borrows every case with `&cases`, so `render` receives a `&Outcome` and no String is moved out of the array.

**Plausible wrong approach.** Testing only `Outcome::Ready(4)` and calling the enum covered leaves the `Failed` arm unexercised, so a typo such as `eror:` would ship unnoticed.

**How to verify.** Run the block. Change the `Failed` arm of `render` to produce `failed:{reason}` and the third case fails, naming both strings.

### Task 6: Transfer and justify

Design valid transitions between states and explain which transitions should be rejected.

**Judging criteria.** List each state and the events that move it, for example `Pending` to `Completed { rows }` or `Rejected { reason }`, and make the transition function return `Result` so an illegal move such as `Completed` back to `Pending` is an explicit error. Terminal states should accept no further transitions. A strong answer matches on `(state, event)` pairs without a wildcard, so a new state forces review, and states one limitation, such as transitions that depend on time or outside data.

## Mechanism and diagnostic reasoning

An enum represents one case from a declared set. Each case can carry the data relevant to that state. This prevents impossible combinations such as a success flag paired with an error message and no result. Match exposes the state distinction and binds the appropriate payload.

Use enums for meaningful alternatives, not merely to avoid strings. Adding a state requires reviewing transitions and consumers. Exhaustive matching helps the compiler identify affected code. A wildcard may be justified for intentionally open categories, but it weakens feedback when the domain is meant to be closed.

`enum Outcome { Ready(u32), Failed(String) }` declares alternatives. `match value` consumes or borrows according to the matched expression. Matching `&value` can inspect owned payloads without moving them.

Matching an owned enum can move its String payload. Use a borrowed match when retaining the original is intended. Avoid a wildcard that silently renders new domain states as success.

## Review before continuing

Rebuild Example B (Render a distinct failure) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
