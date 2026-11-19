# rust-032: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-032_solution.rs](rust-032_solution.rs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Create a stable report:** The core chooses data semantics while presentation can remain a separate adapter. The report accumulates duplicates and orders keys.

**Retain rejected input evidence:** The library contract preserves information needed by every future adapter. Two invalid rows are counted and a valid zero remains present.

## Task answers

### Task 1: Predict and explain

Trace validation and accumulation as separate responsibilities.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The core chooses data semantics while presentation can remain a separate adapter. The report accumulates duplicates and orders keys.

### Task 2: Guided modification

Add a report-rendering function without changing the core representation.

No separate reference answer has been written for this task. Start from Example B: The library contract preserves information needed by every future adapter. Two invalid rows are counted and a valid zero remains present.

### Task 3: Independent construction

Build and test InventoryLab through its documented Cargo commands.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Library crate** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose moving console output into a reusable domain method.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A multi-file Cargo project is not accepted by the single-file pad. Keep generated target output out of source packaging. A dependency-free project still needs the prepared compiler and standard library.

### Task 5: Boundary evidence

Test empty, duplicate, invalid and overflow cases.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Create a stable report) and Example B (Retain rejected input evidence).

### Task 6: Transfer and justify

Design a second adapter that reuses the same validated library without copying its implementation.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Library crate**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The intermediate project separates a pure domain library from an executable adapter and integration tests. A library can expose validated operations without knowing whether its caller is a command-line tool, a browser worker or a future service. The adapter owns presentation and process behavior.

The checked-in InventoryLab is a real Cargo package using only the standard library. The pad runs the same kind of portable kernel, while Cargo build and Cargo test are deliberately separate project commands. Preserve input accounting, deterministic output and overflow behavior when extracting modules. A successful library test is not a claim that an external service or deployment is configured.

A BTreeMap result preserves sorted identity. A report record carries accepted totals and rejected count. Integration tests use the library public API, which catches accidental exposure or missing exports.

A multi-file Cargo project is not accepted by the single-file pad. Keep generated target output out of source packaging. A dependency-free project still needs the prepared compiler and standard library.

## Review before continuing

Run the reference and confirm that it prints `rust-032: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
