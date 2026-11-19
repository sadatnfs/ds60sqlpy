# csharp-048: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-048_solution.cs](csharp-048_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Build a stable valid report:** Sorting and aggregation have independent responsibilities and both are observable. The sorted report is a=3;b=6.

**Preserve rejected data accounting:** A correct result preserves domain distinctions instead of hiding them behind a plausible total. A valid zero remains in the report while two invalid rows are counted.

## Task answers

### Task 1: Predict and explain

Trace every input to an accepted total or a rejection.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Sorting and aggregation have independent responsibilities and both are observable. The sorted report is a=3;b=6.

### Task 2: Guided modification

Add an item and update only independently derived expected output.

No separate reference answer has been written for this task. Start from Example B: A correct result preserves domain distinctions instead of hiding them behind a plausible total. A valid zero remains in the report while two invalid rows are counted.

### Task 3: Independent construction

Build the external DomainLab and expose the domain contract through the ApiLab adapter.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Acceptance criteria** and the lesson notes.

### Task 4: Diagnose a defect

Introduce and diagnose a duplicate-aggregation, nullability or cancellation defect.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Do not equate a kernel assertion with API, persistence or deployment acceptance. Retain learner data and use owned temporary state for tests. A useful capstone documents what remains intentionally unsupported.

### Task 5: Boundary evidence

Document and test empty, malformed, overflow and repeated-operation boundaries.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Build a stable valid report) and Example B (Preserve rejected data accounting).

### Task 6: Transfer and justify

Deliver a project README with build commands, architecture, failure policies, tests, operational limits and a proposed next extension.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Acceptance criteria**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The final project combines validated input, a pure domain core, deterministic reporting and explicit operational outcomes. A complete application is more than a successful algorithm: it needs a documented build, input contract, failure policy, resource ownership and evidence that its output remains meaningful after changes.

The classroom reference is the portable kernel, and the DomainLab and ApiLab fixtures provide actual multi-file boundaries. Extend them deliberately rather than pasting an entire server into the single source pad. Review normal, rejected and unknown outcomes separately. Expert practice means being able to explain the limits and diagnose an unfamiliar failure, not claiming that a finite tutorial covers every production circumstance.

Compose small functions around explicit record types. Keep parsing, validation, aggregation and presentation separate. Sort output when order is part of the contract; retain rejection evidence alongside accepted totals.

Do not equate a kernel assertion with API, persistence or deployment acceptance. Retain learner data and use owned temporary state for tests. A useful capstone documents what remains intentionally unsupported.

## Review before continuing

Run the reference and confirm that it prints `csharp-048: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
