# rust-016: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-016_solution.rs](rust-016_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate repeated valid items:** Duplicate identities accumulate only after their values are admitted. Pear totals six and apple totals three.

**Retain valid zero and rejection counts:** This preserves absence, zero and rejection as different meanings. A valid zero remains present while three malformed records are excluded.

## Task answers

### Task 1: Predict and explain

Trace each record through parsing and accumulation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Duplicate identities accumulate only after their values are admitted. Pear totals six and apple totals three.

### Task 2: Guided modification

Add one duplicate and predict its new total.

No separate reference answer has been written for this task. Start from Example B: This preserves absence, zero and rejection as different meanings. A valid zero remains present while three malformed records are excluded.

### Task 3: Independent construction

Render the sorted map with an explicit rejected count.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file. It uses `import_rows` from the lesson's helpers, defined in the reference program.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (totals, rejected) = import_rows(&["pear,2", "apple,3", "bad"]);
    let mut report = String::new();
    for (name, total) in &totals {
        report.push_str(&format!("{name}: {total}\n"));
    }
    report.push_str(&format!("rejected: {rejected}"));
    assert_eq!(report, "apple: 3\npear: 2\nrejected: 1");
    Ok(())
}
```

**Observe:** The report lists apple: 3, pear: 2 and rejected: 1.

A BTreeMap iterates in key order, so the report is sorted without a separate sort step, and the rejection count is printed explicitly.

### Task 4: Diagnose a defect

Diagnose silently replacing a parse error with zero.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting. Do not advertise split_once as general CSV support. The later Arrow CSV chapter uses an actual parser.

### Task 5: Boundary evidence

Test empty names, extra separators, overflow and empty input.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Aggregate repeated valid items) and Example B (Retain valid zero and rejection counts).

### Task 6: Transfer and justify

Design a structured import result retaining safe per-record failure categories.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Admission**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The first project joins parsing, ownership, collection lookup and aggregation. Input validation decides which records enter the domain. Accepted duplicate names accumulate; rejected records are counted separately. A missing or malformed quantity must not become a valid zero merely because zero is convenient.

The fixture uses in-memory text and a sorted map so it remains deterministic and offline. BTreeMap provides ordered keys, while a HashMap would need explicit sorting for presentation. Keep parsing and calculation separate enough to diagnose the first incorrect state. Later chapters extend this kernel with files, concurrency and Arrow arrays.

split_once separates a simple two-field fixture. A second comma is rejected by integer parsing. BTreeMap entry gives one owned update point for a key. checked_add preserves overflow as a rejected record.

This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting. Do not advertise split_once as general CSV support. The later Arrow CSV chapter uses an actual parser.

## Review before continuing

Run the reference and confirm that it prints `rust-016: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
