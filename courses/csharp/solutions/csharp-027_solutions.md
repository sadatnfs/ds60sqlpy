# csharp-027: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-027_solution.cs](csharp-027_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Different offsets, same instant:** Comparing wall-clock components would miss the offset information. The values denote the same instant despite different offsets.

**Measure a fixed duration:** A fixed fixture keeps evidence independent of the host clock and locale. The elapsed duration is 90 minutes and the timestamp round-trips.

## Reason through the six tasks

1. **Predict and explain.** Explain why the two offset timestamps compare equal.

2. **Guided modification.** Change one instant by one minute and predict the comparison.

3. **Independent construction.** Build a duration report using fixed UTC timestamps.

4. **Diagnose a defect.** Diagnose treating an offset as a complete time-zone identity.

5. **Boundary evidence.** Test intervals across midnight and reject an end before its start when the domain forbids it.

6. **Transfer and justify.** Design storage and display policies for appointments in a named time zone.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An instant, a local wall-clock time and a duration are different concepts. DateTimeOffset combines a date-time with an offset, making an instant comparison explicit. A time-zone identifier carries additional historical daylight-saving rules that a fixed offset does not. Do not infer a region from its offset alone.

A duration measures elapsed time; a calendar rule such as next month follows calendar boundaries. Persist machine-readable data using a stable format and parse with an explicit culture. User-facing formatting may intentionally vary by locale. Tests should fix their clock inputs rather than depend on the date or local zone of the machine running them.

`DateTimeOffset.Parse` with an explicit round-trip string creates a known instant. `ToUniversalTime` changes its display offset while retaining the instant. Subtraction produces TimeSpan. InvariantCulture avoids environment-dependent machine-data parsing.

DateTime kind and unspecified local values can introduce ambiguity. Daylight-saving transitions can produce invalid or repeated local times. Use elapsed-time clocks for performance measurement, not wall-clock timestamps.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
