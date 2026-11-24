# csharp-021: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-021_solution.cs](csharp-021_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate at a declared grain:** Grouping changes grain while preserving the sum across all groups. Three event rows become two category totals.

**Expose duplicate-key multiplication:** A key relationship does not imply one-to-one cardinality. Validate uniqueness if the domain requires exactly one match. One left row becomes two joined rows.

## Task answers

### Task 1: Predict and explain

State the input and output grain for each example.

**Written answer.** Example A: the input grain is one row per sale event (`Kind`, `Amount`); the output grain is one row per kind, two totals from three events. Example B: `left` has one row per key and `right` has one row per value event for a key; the joined output has one row per matching left-right pair, so one left row with two matches becomes two rows.

**Why it is correct.** Grain is what one row represents. `GroupBy` with `Sum` deliberately coarsens the grain to the grouping key. `Join` produces the product of matches per key, so its output grain is a pair, and it is finer than the left input whenever the right side repeats a key.

**Plausible wrong approach.** Describing B's output as one row per key assumes `Join` behaves like a lookup. That expectation is what leads to doubled totals when the right side has repeated keys.

**How to verify.** Check `rows.Length == 3` and `totals.Count == 2` in A, and `left.Length == 1` and `joined.Length == 2` in B. Each count is the number of rows at that grain.

### Task 2: Guided modification

Add a third category and verify total conservation.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var rows = new List<(string Kind, int Amount)> { ("a", 2), ("a", 3) };
rows.Add(("b", 4));
rows.Add(("c", 7));
var groups = rows.GroupBy(row => row.Kind);
var totals = groups.ToDictionary(g => g.Key, g => g.Sum(r => r.Amount));
Check(totals.Count == 3 && totals["c"] == 7, "third category");
int eventTotal = rows.Sum(row => row.Amount);
Check(eventTotal == 16, "independent event total");
Check(totals.Values.Sum() == eventTotal, "total conserved");
```

**Observe:** Category c appears with 7, and the three category totals add up to 16, the same as the four events.

Grouping reassigns each event to exactly one category and summing adds every amount once, so the grand total must not change: 5 + 4 + 7 = 2 + 3 + 4 + 7 = 16. Checking that conservation catches lost or duplicated rows that a per-category check alone could miss.

**Plausible wrong approach.** Checking only `totals["c"] == 7` confirms the new category but not that the others survived. A filter that accidentally dropped kind `b` would still pass it.

**How to verify.** Add an event with kind `a` and amount 1 and confirm `totals["a"]` becomes 6, the count stays 3 and both sides of the conservation check become 17.

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

**Written answer.** If the item metadata contains `(Id: 1, Name: "pear")` twice, joining sales with Qty 2 and 3 for id 1 to it yields four rows instead of two, and the pear total becomes 10 instead of 5. The sales were not doubled; the metadata key was not unique, so every sale matched twice. Check uniqueness before joining, for example by building `items.ToDictionary(item => item.Id)`, which throws `ArgumentException` on the repeated id.

**Why it is correct.** A join returns one row per matching pair. With 2 sales and 2 metadata rows for the same id, there are 2 times 2 pairs, and summing over them counts each sale twice. Item metadata is supposed to have one row per id, and that assumption must be enforced, not hoped for.

**Plausible wrong approach.** Calling `Distinct()` on the joined rows hides this example only when the duplicate rows are identical, and also deletes legitimate repeated sales with the same quantity. Dividing the total by 2 fixes one key and breaks every key that was not duplicated.

**How to verify.** Reproduce the bug and check the pear total is 10. Then check `items.GroupBy(i => i.Id).All(g => g.Count() == 1)` is false for the bad metadata and true after removing the duplicate, when the total returns to 5.

### Task 5: Boundary evidence

Test an unmatched key and choose an explicit handling policy.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var names = new Dictionary<int, string>();
names.Add(1, "pear");
names.Add(2, "apple");
var sales = new[] { (Id: 1, Qty: 2), (Id: 3, Qty: 5) };
var matched = sales.Where(s => names.ContainsKey(s.Id)).ToArray();
var unmatched = sales.Where(s => !names.ContainsKey(s.Id)).ToArray();
Check(matched.Length == 1 && names[matched[0].Id] == "pear", "match");
Check(unmatched.Length == 1 && unmatched[0].Qty == 5, "reported");
int reported = matched.Sum(s => s.Qty) + unmatched.Sum(s => s.Qty);
Check(reported == sales.Sum(s => s.Qty), "nothing silently dropped");
```

**Observe:** Sale id 3 has no metadata; it is kept in a separate unmatched list with quantity 5, and matched plus unmatched still total 7.

The chosen policy is to report unmatched rows rather than drop or invent them. Splitting the sales into matched and unmatched makes the missing metadata visible, and the final check proves the split loses nothing. An inner `Join` would quietly drop the 5, and looking up `names[3]` would throw `KeyNotFoundException`.

**Plausible wrong approach.** Substituting a label such as `"unknown"` inside the report merges every unmatched id into one line, so the reader cannot tell which metadata is missing. Silently using an inner join makes the report total 2 while the sales say 7.

**How to verify.** Add `names.Add(3, "plum");` and confirm `unmatched` becomes empty and `matched` has both sales. The conservation check holds either way.

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
