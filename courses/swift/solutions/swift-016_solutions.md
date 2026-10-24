# swift-016: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-016_solution.swift](swift-016_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Combine repeated valid names:** Duplicate names are deliberately accumulated after validation. Pear totals 6 and apple totals 3.

**Keep rejection separate from zero:** This result preserves the difference between accepted zero, absence and invalid input. The valid zero remains present while three records are rejected.

## Reason through the six tasks

1. **Predict and explain.** Trace each line through field count, name and quantity checks.

2. **Guided modification.** Add a valid duplicate and predict the new aggregate.

3. **Independent construction.** Produce a sorted text report with accepted totals and rejected count.

4. **Diagnose a defect.** Diagnose replacing failed Int parsing with zero.

5. **Boundary evidence.** Test empty names, extra fields, zero and an empty input list.

6. **Transfer and justify.** Design a reusable result that retains safe line-specific reasons without storing raw sensitive input.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A first useful Swift project combines optional parsing, value models, loops and deterministic reporting. The critical boundary is admission: malformed or negative quantities must not become accepted zero values. A report should separately account for valid quantities and rejected records.

The fixture uses in-memory lines and produces a value result, so it runs offline and is easy to test. External file loading can be added later as an adapter. Preserve a clear contract for duplicate names and ordering. The same small project will return in later lessons with Codable, async ownership and app presentation.

Split creates field substrings; convert them deliberately when storing long-lived names. Int parsing returns an optional. Dictionary default mutation accumulates admitted duplicates. sorted fixes presentation order.

Check field count before indexing. String splitting can omit empty fields unless configured, so this fixture preserves them deliberately. Production totals also need an overflow policy.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
