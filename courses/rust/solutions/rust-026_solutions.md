# rust-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-026_solution.rs](rust-026_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count repeated identities:** Aggregation and presentation order are explicit parts of the chosen representation. Duplicate b accumulates and output keys are sorted.

**Distinguish first and duplicate insertion:** Membership is a domain decision that can guide duplicate rejection or deduplication. The set reports a duplicate without creating a second entry.

## Reason through the six tasks

1. **Predict and explain.** State the grain and identity policy of each result.

2. **Guided modification.** Change duplicate handling from counting to rejection.

3. **Independent construction.** Build a deterministic frequency report.

4. **Diagnose a defect.** Diagnose relying on HashMap iteration order for a saved report.

5. **Boundary evidence.** Test empty input and repeated keys.

6. **Transfer and justify.** Compare repeated linear membership checks with a built index, including construction and memory costs.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Collection choice follows operations and identity policy. HashMap supports expected efficient lookup; BTreeMap keeps keys ordered. HashSet represents unique membership. A list scan can be appropriate for tiny data, but repeated scans over growing inputs can dominate a workload.

Define the grain of the result and the equality rule before choosing a container. Duplicate keys may aggregate, reject or replace, and those are different contracts. Stable report order should be deliberate. Big-O explains growth under a cost model, not an exact time guarantee on every machine.

The entry API provides one lookup/update boundary. BTreeMap iteration is key-ordered. HashSet insert reports whether membership changed. Borrowed lookup can avoid allocating a new key.

Expected hash lookup cost is not a hard real-time guarantee. Do not persist hash values as stable identities. A collection choice does not by itself validate input or prevent overflow.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
