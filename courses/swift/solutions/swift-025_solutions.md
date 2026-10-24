# swift-025: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-025_solution.swift](swift-025_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Measure a fixed duration:** Explicit units prevent confusing minutes with the seconds expected by the API. The elapsed interval is 5,400 seconds.

**Parse equal instants with different offsets:** Offset information must be included when comparing wall-clock representations. Both strings represent the same instant.

## Reason through the six tasks

1. **Predict and explain.** Convert the duration between seconds and minutes.

2. **Guided modification.** Add a day-sized duration and explain why this is not a universal next-local-day rule.

3. **Independent construction.** Build a report from fixed timestamp fixtures.

4. **Diagnose a defect.** Diagnose treating an offset as a complete time-zone identity.

5. **Boundary evidence.** Test an interval crossing midnight and malformed timestamp text.

6. **Transfer and justify.** Design storage, display and duration-measurement policies for an appointment app.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Date represents an instant, independent of how a user sees it. Calendar and time-zone rules translate instants into local components. A fixed offset does not capture an entire region's daylight-saving history. Adding a duration and asking for the next calendar day can therefore answer different questions.

Use fixed instants in tests rather than the current machine clock. ISO 8601 is useful for exchanging timestamps, while localized formatting serves display. For performance measurement, use a monotonic clock rather than wall-clock time, which can be adjusted. Keep the unit of every duration explicit.

Date(timeIntervalSince1970:) constructs a fixed instant. addingTimeInterval uses seconds. ISO8601DateFormatter translates an exchange representation. Calendar operations require an explicit calendar and time zone for reproducible component reasoning.

Date has no inherent display time zone. Locale-sensitive formatting should not be used as an undocumented machine-data contract. Daylight-saving changes can create missing or repeated local times.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
