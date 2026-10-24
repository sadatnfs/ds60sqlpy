# rust-032: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-032_solution.rs](rust-032_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Create a stable report:** The core chooses data semantics while presentation can remain a separate adapter. The report accumulates duplicates and orders keys.

**Retain rejected input evidence:** The library contract preserves information needed by every future adapter. Two invalid rows are counted and a valid zero remains present.

## Reason through the six tasks

1. **Predict and explain.** Trace validation and accumulation as separate responsibilities.

2. **Guided modification.** Add a report-rendering function without changing the core representation.

3. **Independent construction.** Build and test InventoryLab through its documented Cargo commands.

4. **Diagnose a defect.** Diagnose moving console output into a reusable domain method.

5. **Boundary evidence.** Test empty, duplicate, invalid and overflow cases.

6. **Transfer and justify.** Design a second adapter that reuses the same validated library without copying its implementation.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

The intermediate project separates a pure domain library from an executable adapter and integration tests. A library can expose validated operations without knowing whether its caller is a command-line tool, a browser worker or a future service. The adapter owns presentation and process behavior.

The checked-in InventoryLab is a real Cargo package using only the standard library. The pad runs the same kind of portable kernel, while Cargo build and Cargo test are deliberately separate project commands. Preserve input accounting, deterministic output and overflow behavior when extracting modules. A successful library test is not a claim that an external service or deployment is configured.

A BTreeMap result preserves sorted identity. A report record carries accepted totals and rejected count. Integration tests use the library public API, which catches accidental exposure or missing exports.

A multi-file Cargo project is not accepted by the single-file pad. Keep generated target output out of source packaging. A dependency-free project still needs the prepared compiler and standard library.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
