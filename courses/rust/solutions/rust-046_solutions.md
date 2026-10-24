# rust-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-046_solution.rs](rust-046_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Describe outcome without raw payload:** The field set is intentionally small and reviewable. The event retains useful context without echoing input contents.

**Reject unlisted actions:** A missing policy entry is not implicit permission. Only explicitly listed actions are admitted.

## Reason through the six tasks

1. **Predict and explain.** Identify every field safe to emit in the event.

2. **Guided modification.** Add a fixed stage category without adding raw input.

3. **Independent construction.** Instrument an importer with submitted, accepted and rejected counts.

4. **Diagnose a defect.** Diagnose including a token or entire source record in an error message.

5. **Boundary evidence.** Test missing permissions and empty workloads.

6. **Transfer and justify.** Design a fixed-operation boundary that separates validated data from executable instructions.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Operational evidence should explain an outcome without exposing raw private input. Use stable stages, result categories and bounded counters. A parsing error, rejected domain value and unknown external effect are different categories. Correlation identity connects observations of one operation without embedding credentials or payloads.

Security boundaries appear wherever data gains authority: paths reach files, text becomes commands, or requests select resources. Prefer fixed reviewed operations and typed parsing over string-built commands. Rust memory safety does not provide authentication, authorization or an input-size policy. Keep those responsibilities visible in system design.

A diagnostic record can contain a fixed operation ID, stage, outcome and count. Match exact allowed actions rather than executing arbitrary input. Format only reviewed fields and bound output volume.

Memory safety does not make arbitrary command execution safe. Do not log secrets or unbounded payloads. A successful process exit can still contain domain rejections that need explicit reporting.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
