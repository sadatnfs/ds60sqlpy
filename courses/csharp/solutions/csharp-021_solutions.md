# csharp-021: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-021_solution.cs](csharp-021_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate at a declared grain:** Grouping changes grain while preserving the sum across all groups. Three event rows become two category totals.

**Expose duplicate-key multiplication:** A key relationship does not imply one-to-one cardinality. Validate uniqueness if the domain requires exactly one match. One left row becomes two joined rows.

## Reason through the six tasks

1. **Predict and explain.** State the input and output grain for each example.

2. **Guided modification.** Add a third category and verify total conservation.

3. **Independent construction.** Build a report joining unique item metadata to item totals.

4. **Diagnose a defect.** Diagnose a doubled total caused by duplicate metadata keys.

5. **Boundary evidence.** Test an unmatched key and choose an explicit handling policy.

6. **Transfer and justify.** Design checks that distinguish one-to-one, one-to-many and many-to-many joins before aggregation.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Aggregation changes the grain of data. A row-per-event input can become a row-per-category result. State that grain before writing GroupBy so the result keys and totals have a meaning. Joining two sequences can multiply rows when keys are duplicated. This is a modeling issue that appears in LINQ just as it does in SQL.

An inner join drops keys with no partner. A left join needs an explicit absence policy. Before trusting a total after a join, inspect key uniqueness and count the expected matches. A tiny fixture with duplicate keys reveals accidental multiplication far more clearly than a large realistic dataset.

`GroupBy(keySelector)` returns groups with Key and enumerable members. `Join` uses one key selector per side. A grouped lookup such as ToLookup preserves all matches, while ToDictionary requires unique keys.

Aggregating after an unintended many-to-many join can inflate totals. ToDictionary throws on duplicate keys rather than choosing a winner. Sorting is needed when presentation order is part of the contract.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
