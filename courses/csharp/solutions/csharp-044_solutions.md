# csharp-044: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-044_solution.cs](csharp-044_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Emit a safe result record:** Named fields retain meaning without depending on a fragile formatted sentence. The serialized event contains an explicit rejected outcome.

**Keep outcome counts consistent:** The counts come from the emitted events, so a record that was never classified would make the first check fail. The denominator is stated explicitly; changing it changes the metric meaning. The accepted and rejected events account for all five submitted records, and the rejection rate is 0.4.

## Task answers

### Task 1: Predict and explain

Identify safe fields and the event population.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Named fields retain meaning without depending on a fragile formatted sentence. The serialized event contains an explicit rejected outcome.

### Task 2: Guided modification

Add a stage value without adding raw input content.

No separate reference answer has been written for this task. Start from Example B: The counts come from the emitted events, so a record that was never classified would make the first check fail. The denominator is stated explicitly; changing it changes the metric meaning. The accepted and rejected events account for all five submitted records, and the rejection rate is 0.4.

### Task 3: Independent construction

Instrument your import project with submitted, accepted and rejected counts.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int[] quantities = { 3, -1, 4, -2, 5 };
int submitted = quantities.Length;
int accepted = quantities.Count(quantity => quantity >= 0);
int rejected = quantities.Count(quantity => quantity < 0);
Check(submitted == 5 && accepted == 3 && rejected == 2, "counts");
Check(accepted + rejected == submitted, "every record accounted for");
```

**Observe:** 5 submitted records split into 3 accepted and 2 rejected.

All three counts come from the same input, so the accounting check would fail if a record were dropped or counted twice.

### Task 4: Diagnose a defect

Diagnose a success metric incremented before persistence completes.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Correlation identifiers should not contain credentials or private payloads. High-cardinality dimensions can overwhelm metric systems. Missing observations must not be silently counted as successful operations.

### Task 5: Boundary evidence

Test zero submitted records and choose a no-data rate representation.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Emit a safe result record) and Example B (Keep outcome counts consistent).

### Task 6: Transfer and justify

Design a latency report that includes percentiles, sample count and measurement boundaries.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Structured event**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Diagnostics should explain an operation without leaking its inputs or creating an overwhelming stream of unrelated messages. A structured event has stable fields such as operation identity, stage and outcome. These fields let a reader connect the beginning and end of one operation and distinguish a retry from a different request.

Latency, throughput and failure rate describe different aspects of a service. A low average latency can hide a bad tail. A successful process exit does not imply every record was accepted. Define observable counters from the domain contract, and ensure cancelled or unknown work is not misclassified as success. Deterministic fixtures can verify event structure while production measurements need real workloads.

Use a record for a stable event schema and serialize explicit safe fields. Stopwatch is appropriate for elapsed duration, but tests should not assert a narrow timing threshold. Keep correlation identity separate from user secrets.

Correlation identifiers should not contain credentials or private payloads. High-cardinality dimensions can overwhelm metric systems. Missing observations must not be silently counted as successful operations.

## Review before continuing

Run the reference and confirm that it prints `csharp-044: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
