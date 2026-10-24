# rust-016: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-016_solution.rs](rust-016_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate repeated valid items:** Duplicate identities accumulate only after their values are admitted. Pear totals six and apple totals three.

**Retain valid zero and rejection counts:** This preserves absence, zero and rejection as different meanings. A valid zero remains present while three malformed records are excluded.

## Reason through the six tasks

1. **Predict and explain.** Trace each record through parsing and accumulation.

2. **Guided modification.** Add one duplicate and predict its new total.

3. **Independent construction.** Render the sorted map with an explicit rejected count.

4. **Diagnose a defect.** Diagnose silently replacing a parse error with zero.

5. **Boundary evidence.** Test empty names, extra separators, overflow and empty input.

6. **Transfer and justify.** Design a structured import result retaining safe per-record failure categories.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

The first project joins parsing, ownership, collection lookup and aggregation. Input validation decides which records enter the domain. Accepted duplicate names accumulate; rejected records are counted separately. A missing or malformed quantity must not become a valid zero merely because zero is convenient.

The fixture uses in-memory text and a sorted map so it remains deterministic and offline. BTreeMap provides ordered keys, while a HashMap would need explicit sorting for presentation. Keep parsing and calculation separate enough to diagnose the first incorrect state. Later chapters extend this kernel with files, concurrency and Arrow arrays.

split_once separates a simple two-field fixture. A second comma is rejected by integer parsing. BTreeMap entry gives one owned update point for a key. checked_add preserves overflow as a rejected record.

This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting. Do not advertise split_once as general CSV support. The later Arrow CSV chapter uses an actual parser.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
