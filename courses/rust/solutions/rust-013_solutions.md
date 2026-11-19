# rust-013: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-013_solution.rs](rust-013_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Render a success payload:** The rendering function borrows the state and extracts only the matching payload. The ready state carries a count rather than an unrelated optional field.

**Render a distinct failure:** The model cannot simultaneously be both ready and failed. Failure preserves its reason and remains a distinct state.

## Task answers

### Task 1: Predict and explain

Identify which payload is valid in each state.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The rendering function borrows the state and extracts only the matching payload. The ready state carries a count rather than an unrelated optional field.

### Task 2: Guided modification

Add a Loading variant and update every exhaustive consumer.

No separate reference answer has been written for this task. Start from Example B: The model cannot simultaneously be both ready and failed. Failure preserves its reason and remains a distinct state.

### Task 3: Independent construction

Model an import as pending, completed or rejected with state-specific information.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Matching an owned enum can move its String payload. Use a borrowed match when retaining the original is intended. Avoid a wildcard that silently renders new domain states as success.

### Task 5: Boundary evidence

Test every declared variant.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Render a success payload) and Example B (Render a distinct failure).

### Task 6: Transfer and justify

Design valid transitions between states and explain which transitions should be rejected.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Enum variant**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An enum represents one case from a declared set. Each case can carry the data relevant to that state. This prevents impossible combinations such as a success flag paired with an error message and no result. Match exposes the state distinction and binds the appropriate payload.

Use enums for meaningful alternatives, not merely to avoid strings. Adding a state requires reviewing transitions and consumers. Exhaustive matching helps the compiler identify affected code. A wildcard may be justified for intentionally open categories, but it weakens feedback when the domain is meant to be closed.

`enum Outcome { Ready(u32), Failed(String) }` declares alternatives. `match value` consumes or borrows according to the matched expression. Matching `&value` can inspect owned payloads without moving them.

Matching an owned enum can move its String payload. Use a borrowed match when retaining the original is intended. Avoid a wildcard that silently renders new domain states as success.

## Review before continuing

Run the reference and confirm that it prints `rust-013: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
