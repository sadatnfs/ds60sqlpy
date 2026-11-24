# rust-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-046_solution.rs](rust-046_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Describe outcome without raw payload:** The field set is intentionally small and reviewable. The event retains useful context without echoing input contents.

**Reject unlisted actions:** A missing policy entry is not implicit permission. Only explicitly listed actions are admitted.

## Task answers

### Task 1: Predict and explain

Identify every field safe to emit in the event.

**Written answer.** Every field is safe: `operation` "fixture-1" is a fixed correlation identifier, `stage` "validate" and `outcome` "rejected" come from small fixed vocabularies, and `count` is a number. None of them carries the content of a submitted record.

**Why it is correct.** Each field answers what happened, where and how often, without repeating what was submitted. The `&'static str` field type also keeps ordinary runtime strings out, because a borrowed local `String` does not live long enough.

**Plausible wrong approach.** Treating `&'static str` as proof of safety goes too far: `Box::leak` can turn any input into a `&'static str`. The type is a strong hint; the reviewed fixed vocabulary is the actual rule.

**How to verify.** Try `let input = String::from("token=abc"); Event { operation: &input, stage: "validate", outcome: "rejected", count: 2 }` and read E0597, `input` does not live long enough. The literal-only event still renders `fixture-1 validate rejected count=2`.

### Task 2: Guided modification

Add a fixed stage category without adding raw input.

**Written answer.** Introduce `#[derive(Clone, Copy)] enum Stage { Validate, Aggregate }` with `fn name(self) -> &'static str { match self { Stage::Validate => "validate", Stage::Aggregate => "aggregate" } }`, change the field to `stage: Stage` and render `self.stage.name()`.

**Why it is correct.** An enum closes the set of stages: the only strings that can appear are the two in the `match`, so a new stage is a reviewed code change and never comes from input.

**Plausible wrong approach.** Adding a `detail: String` field to hold text such as the rejected line widens the event to raw input, which is exactly what this lesson's events are designed to exclude.

**How to verify.** Assert an `Event` with `stage: Stage::Aggregate`, outcome "accepted" and count 3 renders `fixture-1 aggregate accepted count=3`. A misspelled `Stage::Agregate` fails with E0599.

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

**Plausible wrong approach.** Parsing with `parse::<i32>()` accepts `"-1"`, so the counts become accepted 3 and rejected 1 and the event assertion fails, even though a negative quantity is not a valid record.

**How to verify.** Add `""` as a fifth input: it fails to parse, so the event becomes `submitted=5 accepted=2 rejected=3` and `accepted + rejected == submitted` still holds.

### Task 4: Diagnose a defect

Diagnose including a token or entire source record in an error message.

**Written answer.** The defect is an error built as `format!("bad record: {line}")` where the line is `pear,2,token=secret-123`, or `format!("auth failed for {token}")`. The message flows into logs and user output, leaking the secret and an unbounded amount of input. Report position and category instead: `format!("line {number}: bad quantity")`.

**Why it is correct.** A line number and category are enough to find the record in the source, which already has its own access controls, while the error text itself holds nothing sensitive and has a bounded length.

**Plausible wrong approach.** Truncating the record to its first 20 characters bounds the size but not the leak: for `pear,2,token=secret-123` the kept prefix is `pear,2,token=secret-`, so most of the secret still reaches the log.

**How to verify.** Assert `message == "line 3: bad quantity"` and `!message.contains("secret")` for an input line containing `token=secret-123`.

### Task 5: Boundary evidence

Test missing permissions and empty workloads.

**Written answer.** Missing permission: with Example B's list, assert `"report:delete"`, `"Report:read"` and `"report:read "` are all refused, and with `let allowed: [&str; 0] = [];` even `"report:read"` is refused. Empty workload: task 3's importer with `let inputs: [&str; 0] = [];` produces `submitted=0 accepted=0 rejected=0`.

**Why it is correct.** `contains` is exact string equality, so case and trailing-space variants are different actions, and an empty allowlist admits nothing. An empty batch still emits an event, so the operator can tell it ran with no work rather than not at all.

**Plausible wrong approach.** Checking `action.starts_with("report:")` to cover both listed actions also admits `"report:delete"`, turning a missing entry into implicit permission.

**How to verify.** Run the assertions; each refused action is checked like `assert!(!allowed.contains(&"Report:read"))`, and the empty event equals the zero-count string.

### Task 6: Transfer and justify

Design a fixed-operation boundary that separates validated data from executable instructions.

**Written answer.** Parse requests into `enum Operation { ReadReport(ReportId), ListReports }`, where `struct ReportId(u32)` comes from `parse::<u32>()`, and check the caller's allowlist before dispatch. The executor `match`es the enum and calls fixed functions. If an external program is unavoidable, use `Command::new` with a fixed program and pass the id through `.arg(id.0.to_string())`, never a shell string.

**Why it is correct.** Data can only select among reviewed operations and fill typed parameters, so no input can add a new instruction. `.arg` passes one argument without shell interpretation. A limitation is that each new operation needs a code change and review, which is the point.

**Plausible wrong approach.** Running `Command::new("sh").arg("-c").arg(format!("report {id}"))` lets an id of `1; echo injected` run a second command. Rust's memory safety does nothing to prevent that.

**How to verify.** Assert `parse("report:read", "7")` matches `Ok(Operation::ReadReport(ReportId(7)))`, while `parse("report:read", "1; echo injected")` and `parse("report:delete", "7")` are both `Err`. No shell is run in the pad.

## Mechanism and diagnostic reasoning

Operational evidence should explain an outcome without exposing raw private input. Use stable stages, result categories and bounded counters. A parsing error, rejected domain value and unknown external effect are different categories. Correlation identity connects observations of one operation without embedding credentials or payloads.

Security boundaries appear wherever data gains authority: paths reach files, text becomes commands, or requests select resources. Prefer fixed reviewed operations and typed parsing over string-built commands. Rust memory safety does not provide authentication, authorization or an input-size policy. Keep those responsibilities visible in system design.

A diagnostic record can contain a fixed operation ID, stage, outcome and count. Match exact allowed actions rather than executing arbitrary input. Format only reviewed fields and bound output volume.

Memory safety does not make arbitrary command execution safe. Do not log secrets or unbounded payloads. A successful process exit can still contain domain rejections that need explicit reporting.

## Review before continuing

Run the reference and confirm that it prints `rust-046: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
