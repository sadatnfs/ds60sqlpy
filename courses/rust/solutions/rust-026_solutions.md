# rust-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-026_solution.rs](rust-026_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count repeated identities:** Aggregation and presentation order are explicit parts of the chosen representation. Duplicate b accumulates and output keys are sorted.

**Distinguish first and duplicate insertion:** Membership is a domain decision that can guide duplicate rejection or deduplication. The set reports a duplicate without creating a second entry.

## Task answers

### Task 1: Predict and explain

State the grain and identity policy of each result.

**Written answer.** Example A's grain is one row per distinct label, identity is exact case-sensitive string equality, duplicates aggregate into a count, and order is the sorted key order. Example B's grain is one entry per distinct name, a duplicate is detected by `insert` returning `false` and not stored again, and no order is promised.

**Why it is correct.** `BTreeMap` and `HashSet` both compare keys with `Eq`, so `"b"` twice is one identity, while the map's value records how many times it appeared and the set records only presence.

**Plausible wrong approach.** Calling Example A's grain one row per input record predicts three rows. Three labels produce two keys, because the second `"b"` updates the existing entry.

**How to verify.** Add `"B"` to Example A's labels. Assert `counts.len() == 3` and keys `vec!["B", "a", "b"]`: uppercase is a separate identity and sorts first in byte order.

### Task 2: Guided modification

Change duplicate handling from counting to rejection.

**Written answer.** Replace the counter with a set and a rejection list: `let mut accepted = BTreeSet::new(); let mut duplicates = Vec::new(); for label in ["b", "a", "b"] { if !accepted.insert(label) { duplicates.push(label); } }`.

**Why it is correct.** `insert` returns `false` when the label is already present, so the first `"b"` is kept and the second is recorded as rejected instead of being counted.

**Plausible wrong approach.** Writing `counts.insert(label, 1)` is a replace policy, not rejection: the second `"b"` silently overwrites the first and nothing tells the caller a duplicate arrived.

**How to verify.** Assert `accepted.iter().copied().collect::<Vec<_>>() == vec!["a", "b"]` and `duplicates == vec!["b"]`. With all-distinct labels, `duplicates` stays empty.

### Task 3: Independent construction

Build a deterministic frequency report.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let words = ["pear", "fig", "pear", "apple"];
    let mut counts = std::collections::BTreeMap::new();
    for word in words {
        *counts.entry(word).or_insert(0) += 1;
    }
    let report: Vec<String> = counts.iter().map(|(w, n)| format!("{w}={n}")).collect();
    assert_eq!(report, ["apple=1", "fig=1", "pear=2"]);
    Ok(())
}
```

**Observe:** The report is apple=1, fig=1, pear=2, always in that order.

A BTreeMap keeps keys sorted, so the output does not depend on hashing or insertion order.

**Plausible wrong approach.** Writing `*counts.entry(word).or_insert(1) += 1` starts each new word at 1 and then adds 1, so every count is one too high and the assertion fails with `apple=2`, `fig=2`, `pear=3` on the left.

**How to verify.** Add `assert_eq!(counts.values().sum::<i32>(), 4);` (one per input word) and `assert_eq!(counts.len(), 3);` beside the report check.

### Task 4: Diagnose a defect

Diagnose relying on HashMap iteration order for a saved report.

**Written answer.** The defect is building the saved report from `HashMap<&str, i32>` iteration. Its default hasher is seeded randomly, so the same counts can be written as `pear=2, apple=1, fig=1` in one run and another order in the next, and saved files differ with no data change.

**Why it is correct.** `HashMap` promises lookup by key, not any order. Use a `BTreeMap`, as in task 3, or collect the lines and call `report.sort()` before saving.

**Plausible wrong approach.** Inserting the words in sorted order does not fix it: a `HashMap` ignores insertion order entirely, so the output order still depends on hash values.

**How to verify.** Build the report from a `HashMap`, call `report.sort()`, and assert it equals `["apple=1", "fig=1", "pear=2"]`. Without the sort, the exact comparison can fail on some runs.

### Task 5: Boundary evidence

Test empty input and repeated keys.

**Written answer.** Empty input: `let words: [&str; 0] = [];` through task 3's loop gives an empty map and `report == Vec::<String>::new()`. Repeated keys: `["fig", "fig", "fig"]` gives `vec!["fig=3"]`.

**Why it is correct.** With no input the loop body never runs, so no entry is created. Every repeat goes through `entry` on the same key, so one row carries the whole count.

**Plausible wrong approach.** Writing `let words = [];` without a type fails with E0282, type annotations needed, because an empty array literal gives no element type to infer.

**How to verify.** Assert both reports and `counts.is_empty()` for the empty case; the run ends with `rust-026: passed`.

### Task 6: Transfer and justify

Compare repeated linear membership checks with a built index, including construction and memory costs.

**Written answer.** Checking 10,000 incoming SKUs against a 50,000-item `Vec` with `contains` can compare up to 500 million strings. Building a `HashSet` first costs 50,000 insertions and extra memory for its table, then each lookup has expected constant cost; a `BTreeSet` lookup descends a tree only a few nodes deep, so its cost grows with the logarithm of the catalog size, and it keeps sorted order.

**Why it is correct.** The index pays a one-time construction and memory cost in exchange for cheap repeated lookups. For three lookups the plain scan is cheaper, and hash lookup cost is an expectation, not a worst-case guarantee.

**Plausible wrong approach.** Building the `HashSet` inside the loop, once per SKU, pays the full construction for every lookup and ends up slower than the linear scan it was meant to replace.

**How to verify.** On a small fixture, `let catalog = vec!["apple", "fig", "pear"];` and an index collected from it, assert `catalog.contains(&sku) == index.contains(&sku)` for `"pear"` and `"kiwi"`. Timing belongs in a release-mode Cargo benchmark, not the pad.

## Mechanism and diagnostic reasoning

Collection choice follows operations and identity policy. HashMap supports expected efficient lookup; BTreeMap keeps keys ordered. HashSet represents unique membership. A list scan can be appropriate for tiny data, but repeated scans over growing inputs can dominate a workload.

Define the grain of the result and the equality rule before choosing a container. Duplicate keys may aggregate, reject or replace, and those are different contracts. Stable report order should be deliberate. Big-O explains growth under a cost model, not an exact time guarantee on every machine.

The entry API provides one lookup/update boundary. BTreeMap iteration is key-ordered. HashSet insert reports whether membership changed. Borrowed lookup can avoid allocating a new key.

Expected hash lookup cost is not a hard real-time guarantee. Do not persist hash values as stable identities. A collection choice does not by itself validate input or prevent overflow.

## Review before continuing

Run the reference and confirm that it prints `rust-026: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
