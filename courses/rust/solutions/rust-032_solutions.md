# rust-032: explanation and comparison

Executable reference: [rust-032_solution.rs](rust-032_solution.rs), which runs both examples.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Create a stable report:** The core chooses data semantics while presentation can remain a separate adapter. The report accumulates duplicates and orders keys.

**Retain rejected input evidence:** The library contract preserves information needed by every future adapter. Two invalid rows are counted and a valid zero remains present.

## Task answers

### Task 1: Predict and explain

Trace validation and accumulation as separate responsibilities.

**Written answer.** Validation is the guard `if name.is_empty() || value < 0`, which looks at one row alone. Accumulation is the `get`, `checked_add` and `insert` sequence, which depends on earlier rows. In Example B, `("", 2)` fails the empty-name check, `("a", -1)` fails the negative check, and `("b", 0)` passes and is inserted as 0, so `report.1` is 2. In Example A, `"b"` becomes 2 and then 6.

**Why it is correct.** A row can be judged valid in isolation, but whether adding it overflows depends on the running total, so the overflow rejection has to live in the accumulation step.

**Plausible wrong approach.** Moving the overflow check into row validation, for example rejecting values near `i32::MAX`, cannot work: `("b", i32::MAX)` is a valid row on its own and only overflows after an earlier `("b", 1)`.

**How to verify.** Assert `summarize(&[("b", 1), ("b", i32::MAX)])` keeps `"b"` at 1 with `report.1 == 1`, and that the reverse order keeps `"b"` at `i32::MAX`, also with one rejection.

### Task 2: Guided modification

Add a report-rendering function without changing the core representation.

**Written answer.** Add `fn render(report: &(std::collections::BTreeMap<&str, i32>, usize)) -> String { let mut parts: Vec<String> = report.0.iter().map(|(name, total)| format!("{name}={total}")).collect(); parts.push(format!("rejected={}", report.1)); parts.join(";") }`. `summarize` is unchanged.

**Why it is correct.** `render` only borrows the report and reads it, and the `BTreeMap` already iterates in key order, so the text is deterministic while the core keeps returning the map and the rejection count.

**Plausible wrong approach.** Changing `summarize` to return the rendered `String` breaks every existing caller: `report.0.get("b")` in Example A then fails with E0609, no field `0` on type `String`.

**How to verify.** Assert `render(&summarize(&[("b", 2), ("a", 3), ("b", 4)])) == "a=3;b=6;rejected=0"` and that Example B renders as `"b=0;rejected=2"`. Both examples' original assertions still pass.

### Task 3: Independent construction

Build and test InventoryLab through its documented Cargo commands.

**Written answer.** Copy `courses/rust/fixtures/InventoryLab` into your own ignored workspace and, in a prepared Rust environment, run `rustc --version`, `cargo build --locked --offline`, `cargo test --locked --offline` and `cargo run --locked --offline` from the copy.

**Why it is correct.** `--locked` refuses to change the checked-in Cargo.lock and `--offline` forbids downloads, so success shows the package builds from the standard library alone. `tests/contracts.rs` exercises only the public `summarize` and `render`, so it checks the library surface the executable also uses.

**Plausible wrong approach.** Pasting `src/lib.rs` and `src/main.rs` into the pad fails: the pad compiles one `main.rs`, so `inventory_lab::summarize` names a crate that does not exist there and rustc reports E0433, failed to resolve.

**How to verify.** `cargo test` reports four passing tests in the `contracts` target (aggregation order, rejected rows, overflow and empty or extra-field input) and zero unit tests for the library and executable targets. `cargo run` prints `apple=3;pear=6;rejected=1`.

### Task 4: Diagnose a defect

Diagnose moving console output into a reusable domain method.

**Written answer.** The defect is `summarize` calling `println!("rejected {name}")` for each refused row, or a library method such as `fn print(&self)` that writes the report to stdout. Every adapter now prints whether it wants to or not, and raw input names reach the console. Keep the library returning data and strings, and let `main` decide to print `render(&report)`.

**Why it is correct.** A reusable core cannot know whether its caller is a terminal, a test or another program, so output belongs to the adapter. Returning values also lets tests assert on exactly what would be shown.

**Plausible wrong approach.** Adding a `verbose: bool` parameter to silence the print still ties the library to stdout, changes the signature every caller must use, and still echoes raw names when it is switched on.

**How to verify.** With output moved to `main`, assert on `render` results as in task 2. Running the pad shows no lines from `summarize`, only what `main` prints and the `rust-032: passed` marker.

### Task 5: Boundary evidence

Test empty, duplicate, invalid and overflow cases.

**Written answer.** Empty: `summarize(&[])` gives an empty map and 0. Duplicate: Example A gives `"b"` = 6. Invalid: `("", 2)` and `("a", -1)` add 2 rejections. Overflow: `summarize(&[("b", i32::MAX), ("b", 1)])` keeps `"b"` at `i32::MAX` and counts 1 rejection. Note that `(" ", 1)` is accepted, because this helper checks `is_empty` without trimming, unlike InventoryLab's library.

**Why it is correct.** Each case reaches a different branch: no iterations, the existing-key path, the validation guard, and the `checked_add` returning `None`, which skips the insert and keeps the earlier total.

**Plausible wrong approach.** Expecting the overflow row to wrap to `i32::MIN`, or to replace the total with 1, assumes plain addition or a replace policy. `checked_add` refuses the sum, so the map keeps the last valid total.

**How to verify.** Assert all four cases plus `summarize(&[(" ", 1)]).0.get(" ") == Some(&1)`, which documents the whitespace gap rather than hiding it.

### Task 6: Transfer and justify

Design a second adapter that reuses the same validated library without copying its implementation.

**Written answer.** Add a second binary, `src/bin/check.rs`, that reads lines from standard input, calls `inventory_lab::summarize` on them and exits with status 1 when `report.rejected > 0`, printing only the counts. It reuses the library's validation and never copies `summarize`.

**Why it is correct.** Both binaries depend on the same validated library, so a later fix such as trimming names before they are counted reaches both, and the existing integration tests cover the shared contract. A limitation: with two binaries, `cargo run` needs `--bin inventory-lab` or `--bin check`, and `summarize` takes a slice, so input is collected before it is processed.

**Plausible wrong approach.** Copying `summarize` into the new binary to tweak its output creates a second validator that drifts: a later fix to the library's overflow handling would not reach the copy.

**How to verify.** In the copied project, `cargo run --locked --offline --bin check` with a fixture piped in should print the counts, and `echo $?` shows 1 when any row was rejected. `cargo test --locked --offline` still passes the four contract tests.

## Mechanism and diagnostic reasoning

The intermediate project separates a pure domain library from an executable adapter and integration tests. A library can expose validated operations without knowing whether its caller is a command-line tool, a browser worker or a future service. The adapter owns presentation and process behavior.

The checked-in InventoryLab is a real Cargo package using only the standard library. The pad runs the same kind of portable kernel, while Cargo build and Cargo test are deliberately separate project commands. Preserve input accounting, deterministic output and overflow behavior when extracting modules. A successful library test is not a claim that an external service or deployment is configured.

A BTreeMap result preserves sorted identity. A report record carries accepted totals and rejected count. Integration tests use the library public API, which catches accidental exposure or missing exports.

A multi-file Cargo project is not accepted by the single-file pad. Keep generated target output out of source packaging. A dependency-free project still needs the prepared compiler and standard library.

## Review before continuing

Rebuild Example B (Retain rejected input evidence) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
