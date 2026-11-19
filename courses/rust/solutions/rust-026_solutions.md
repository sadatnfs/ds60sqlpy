# rust-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-026_solution.rs](rust-026_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count repeated identities:** Aggregation and presentation order are explicit parts of the chosen representation. Duplicate b accumulates and output keys are sorted.

**Distinguish first and duplicate insertion:** Membership is a domain decision that can guide duplicate rejection or deduplication. The set reports a duplicate without creating a second entry.

## Task answers

### Task 1: Predict and explain

State the grain and identity policy of each result.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Aggregation and presentation order are explicit parts of the chosen representation. Duplicate b accumulates and output keys are sorted.

### Task 2: Guided modification

Change duplicate handling from counting to rejection.

No separate reference answer has been written for this task. Start from Example B: Membership is a domain decision that can guide duplicate rejection or deduplication. The set reports a duplicate without creating a second entry.

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

### Task 4: Diagnose a defect

Diagnose relying on HashMap iteration order for a saved report.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Expected hash lookup cost is not a hard real-time guarantee. Do not persist hash values as stable identities. A collection choice does not by itself validate input or prevent overflow.

### Task 5: Boundary evidence

Test empty input and repeated keys.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Count repeated identities) and Example B (Distinguish first and duplicate insertion).

### Task 6: Transfer and justify

Compare repeated linear membership checks with a built index, including construction and memory costs.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Identity policy**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Collection choice follows operations and identity policy. HashMap supports expected efficient lookup; BTreeMap keeps keys ordered. HashSet represents unique membership. A list scan can be appropriate for tiny data, but repeated scans over growing inputs can dominate a workload.

Define the grain of the result and the equality rule before choosing a container. Duplicate keys may aggregate, reject or replace, and those are different contracts. Stable report order should be deliberate. Big-O explains growth under a cost model, not an exact time guarantee on every machine.

The entry API provides one lookup/update boundary. BTreeMap iteration is key-ordered. HashSet insert reports whether membership changed. Borrowed lookup can avoid allocating a new key.

Expected hash lookup cost is not a hard real-time guarantee. Do not persist hash values as stable identities. A collection choice does not by itself validate input or prevent overflow.

## Review before continuing

Run the reference and confirm that it prints `rust-026: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
