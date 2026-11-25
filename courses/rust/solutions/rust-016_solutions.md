# rust-016: explanation and comparison

Executable reference: [rust-016_solution.rs](rust-016_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Aggregate repeated valid items:** Duplicate identities accumulate only after their values are admitted. Pear totals six and apple totals three.

**Retain valid zero and rejection counts:** This preserves absence, zero and rejection as different meanings. A valid zero remains present while three malformed records are excluded.

## Task answers

### Task 1: Predict and explain

Trace each record through parsing and accumulation.

**Written answer.** Example A: `"pear,2"` splits into `pear` and `2`, parses, and inserts 2; `"apple,3"` inserts 3; `"pear,4"` reads the previous 2 and stores 6. Example B: `"pear,0"` is admitted with 0; `"bad"` has no comma, `"apple,-1"` fails the `u32` parse, and `"pear,no"` fails it too, so `rejected` ends at 3.

**Why it is correct.** Each `let ... else` either binds the next value or counts a rejection and `continue`s, so a record reaches `totals.insert` only after splitting, parsing, the name check and `checked_add` have all succeeded.

**Plausible wrong approach.** Predicting that `apple` appears with 0, or that `-1` lowers a total, misreads the parse step. `"-1".parse::<u32>()` is an error, so the apple record never reaches the map at all.

**How to verify.** In Example B add `assert_eq!(totals.get("apple"), None);` and `assert_eq!(totals.len(), 1);`. Both pass: only `pear` was admitted.

### Task 2: Guided modification

Add one duplicate and predict its new total.

**Written answer.** Append `"pear,1"` to Example A's input. Pear's total becomes 2 + 4 + 1 = 7, apple stays 3, and `rejected` stays 0.

**Why it is correct.** The helper reads the previous total with `totals.get(name)`, adds through `checked_add`, and inserts the sum, so a repeated name accumulates instead of starting over.

**Plausible wrong approach.** Predicting 1 assumes the map keeps the last record per key. That is what a simplified loop writing `totals.insert(name.to_owned(), quantity)` would do, discarding the earlier 6.

**How to verify.** Assert `totals.get("pear") == Some(&7)`, `totals.len() == 2` and `rejected == 0`.

### Task 3: Independent construction

Render the sorted map with an explicit rejected count.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block. Helpers used: `import_rows`.

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

**Plausible wrong approach.** Collecting into a `HashMap` instead makes iteration order depend on a randomly seeded hasher, so the report can come out as `pear: 2` before `apple: 3` and the exact-string assertion fails on some runs but not others.

**How to verify.** Run the block several times; the string is identical each time. Add `"banana,1"` to the input and the expected report becomes `apple: 3`, `banana: 1`, `pear: 2`, then `rejected: 1`, still in key order.

### Task 4: Diagnose a defect

Diagnose silently replacing a parse error with zero.

**Written answer.** The defect is `let quantity = quantity.parse::<u32>().unwrap_or(0);` in place of the `let Ok(...) else` line. On Example B it admits `"apple,-1"` and `"pear,no"` as zero quantities, so `apple` appears with 0 and `rejected` drops from 3 to 1.

**Why it is correct.** A failed parse and a valid `0` both become the number 0, so the import invents an apple record and undercounts rejections. The lesson's rule is that absence, zero and rejection must stay distinct.

**Plausible wrong approach.** Switching to `.unwrap()` removes the invented zeros but panics on `"apple,-1"` with an `InvalidDigit` parse error, aborting the whole import for one bad row instead of counting it.

**How to verify.** Run Example B with the defect: `assert_eq!(rejected, 3)` panics with `left: 1` and `right: 3`. Restore the `let Ok(quantity) = ... else` form and all checks pass.

### Task 5: Boundary evidence

Test empty names, extra separators, overflow and empty input.

**Written answer.** Check `import_rows(&[",3"]).1 == 1` for an empty name and `import_rows(&["pear,2,3"]).1 == 1` for an extra separator. For overflow, `import_rows(&["pear,4294967295", "pear,1"])` keeps `pear` at `u32::MAX` with one rejection. `import_rows(&[])` returns an empty map and 0.

**Why it is correct.** `split_once` splits only at the first comma, so `2,3` reaches the parser and fails. The trimmed empty name is refused, and `checked_add` returns `None` instead of wrapping, so the second pear row is rejected and the first total is kept.

**Plausible wrong approach.** Using `line.split(',')` and taking the first two pieces would accept `"pear,2,3"` as pear 2, silently dropping the third field instead of rejecting a record the fixture format does not allow.

**How to verify.** Assert each result above, including `totals.get("pear") == Some(&u32::MAX)` for the overflow case. All pass and `rust-016: passed` prints.

### Task 6: Transfer and justify

Design a structured import result retaining safe per-record failure categories.

**Written answer.** Return a structure: `#[derive(Debug, PartialEq)] enum Rejection { MissingSeparator, BadQuantity, EmptyName, Overflow }` and `struct ImportReport { totals: BTreeMap<String, u32>, rejected: Vec<(usize, Rejection)> }`, recording the one-based line number and category for each refused record.

**Why it is correct.** Categories can be counted and explained without echoing raw input, which may hold sensitive or very long text. The old `rejected` count is just `rejected.len()`. A limitation is memory that grows with the number of bad rows; a cap or per-category counters bound it.

**Plausible wrong approach.** Collecting `format!("bad line: {line}")` strings copies untrusted input into the report and forces callers to parse messages to count categories.

**How to verify.** For Example B's input, assert `report.rejected == vec![(2, Rejection::MissingSeparator), (3, Rejection::BadQuantity), (4, Rejection::BadQuantity)]` and that `pear` still totals 0.

## Mechanism and diagnostic reasoning

The first project joins parsing, ownership, collection lookup and aggregation. Input validation decides which records enter the domain. Accepted duplicate names accumulate; rejected records are counted separately. A missing or malformed quantity must not become a valid zero merely because zero is convenient.

The fixture uses in-memory text and a sorted map so it remains deterministic and offline. BTreeMap provides ordered keys, while a HashMap would need explicit sorting for presentation. Keep parsing and calculation separate enough to diagnose the first incorrect state. Later chapters extend this kernel with files, concurrency and Arrow arrays.

split_once separates a simple two-field fixture. A second comma is rejected by integer parsing. BTreeMap entry gives one owned update point for a key. checked_add preserves overflow as a rejected record.

This is a deliberately simple comma-separated fixture, not a complete CSV parser with quoting. Do not advertise split_once as general CSV support. The later Arrow CSV chapter uses an actual parser.

## Review before continuing

Rebuild Example B (Retain valid zero and rejection counts) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
