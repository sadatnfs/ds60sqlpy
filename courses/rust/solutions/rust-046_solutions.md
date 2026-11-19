# rust-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-046_solution.rs](rust-046_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Describe outcome without raw payload:** The field set is intentionally small and reviewable. The event retains useful context without echoing input contents.

**Reject unlisted actions:** A missing policy entry is not implicit permission. Only explicitly listed actions are admitted.

## Task answers

### Task 1: Predict and explain

Identify every field safe to emit in the event.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The field set is intentionally small and reviewable. The event retains useful context without echoing input contents.

### Task 2: Guided modification

Add a fixed stage category without adding raw input.

No separate reference answer has been written for this task. Start from Example B: A missing policy entry is not implicit permission. Only explicitly listed actions are admitted.

### Task 3: Independent construction

Instrument an importer with submitted, accepted and rejected counts.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let inputs = ["2", "x", "5", "-1"];
    let mut accepted = 0;
    let mut rejected = 0;
    for text in inputs {
        match text.parse::<u32>() {
            Ok(_) => accepted += 1,
            Err(_) => rejected += 1,
        }
    }
    let submitted = inputs.len();
    let counts = format!("accepted={accepted} rejected={rejected}");
    let event = format!("submitted={submitted} {counts}");
    assert_eq!(event, "submitted=4 accepted=2 rejected=2");
    assert_eq!(accepted + rejected, submitted);
    Ok(())
}
```

**Observe:** The event reads submitted=4 accepted=2 rejected=2.

The event reports counts only, not the rejected text itself, and the final check proves every submitted record was counted once.

### Task 4: Diagnose a defect

Diagnose including a token or entire source record in an error message.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Memory safety does not make arbitrary command execution safe. Do not log secrets or unbounded payloads. A successful process exit can still contain domain rejections that need explicit reporting.

### Task 5: Boundary evidence

Test missing permissions and empty workloads.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Describe outcome without raw payload) and Example B (Reject unlisted actions).

### Task 6: Transfer and justify

Design a fixed-operation boundary that separates validated data from executable instructions.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Correlation identity**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Operational evidence should explain an outcome without exposing raw private input. Use stable stages, result categories and bounded counters. A parsing error, rejected domain value and unknown external effect are different categories. Correlation identity connects observations of one operation without embedding credentials or payloads.

Security boundaries appear wherever data gains authority: paths reach files, text becomes commands, or requests select resources. Prefer fixed reviewed operations and typed parsing over string-built commands. Rust memory safety does not provide authentication, authorization or an input-size policy. Keep those responsibilities visible in system design.

A diagnostic record can contain a fixed operation ID, stage, outcome and count. Match exact allowed actions rather than executing arbitrary input. Format only reviewed fields and bound output volume.

Memory safety does not make arbitrary command execution safe. Do not log secrets or unbounded payloads. A successful process exit can still contain domain rejections that need explicit reporting.

## Review before continuing

Run the reference and confirm that it prints `rust-046: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
