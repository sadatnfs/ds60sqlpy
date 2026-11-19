# csharp-021: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-021_solution.cs](csharp-021_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate at a declared grain:** Grouping changes grain while preserving the sum across all groups. Three event rows become two category totals.

**Expose duplicate-key multiplication:** A key relationship does not imply one-to-one cardinality. Validate uniqueness if the domain requires exactly one match. One left row becomes two joined rows.

## Task answers

### Task 1: Predict and explain

State the input and output grain for each example.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Grouping changes grain while preserving the sum across all groups. Three event rows become two category totals.

### Task 2: Guided modification

Add a third category and verify total conservation.

No separate reference answer has been written for this task. Start from Example B: A key relationship does not imply one-to-one cardinality. Validate uniqueness if the domain requires exactly one match. One left row becomes two joined rows.

### Task 3: Independent construction

Build a report joining unique item metadata to item totals.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var items = new[] { (Id: 1, Name: "pear"), (Id: 2, Name: "apple") };
var sales = new[] { (Id: 1, Qty: 2), (Id: 1, Qty: 3), (Id: 2, Qty: 4) };
var groups = sales.GroupBy(sale => sale.Id);
var totals = groups.ToDictionary(g => g.Key, g => g.Sum(s => s.Qty));
var report = items.Select(item => $"{item.Name}={totals[item.Id]}");
Check(report.SequenceEqual(new[] { "pear=5", "apple=4" }), "joined");
```

**Observe:** Each item appears once with its total: pear=5 and apple=4.

Grouping first reduces sales to one row per item, so joining with the unique metadata cannot duplicate an item.

### Task 4: Diagnose a defect

Diagnose a doubled total caused by duplicate metadata keys.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Aggregating after an unintended many-to-many join can inflate totals. ToDictionary throws on duplicate keys rather than choosing a winner. Sorting is needed when presentation order is part of the contract.

### Task 5: Boundary evidence

Test an unmatched key and choose an explicit handling policy.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Aggregate at a declared grain) and Example B (Expose duplicate-key multiplication).

### Task 6: Transfer and justify

Design checks that distinguish one-to-one, one-to-many and many-to-many joins before aggregation.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Grain**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Aggregation changes the grain of data. A row-per-event input can become a row-per-category result. State that grain before writing GroupBy so the result keys and totals have a meaning. Joining two sequences can multiply rows when keys are duplicated. This is a modeling issue that appears in LINQ just as it does in SQL.

An inner join drops keys with no partner. A left join needs an explicit absence policy. Before trusting a total after a join, inspect key uniqueness and count the expected matches. A tiny fixture with duplicate keys reveals accidental multiplication far more clearly than a large realistic dataset.

`GroupBy(keySelector)` returns groups with Key and enumerable members. `Join` uses one key selector per side. A grouped lookup such as ToLookup preserves all matches, while ToDictionary requires unique keys.

Aggregating after an unintended many-to-many join can inflate totals. ToDictionary throws on duplicate keys rather than choosing a winner. Sorting is needed when presentation order is part of the contract.

## Review before continuing

Run the reference and confirm that it prints `csharp-021: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
