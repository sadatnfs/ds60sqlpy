# rust-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-036_solution.rs](rust-036_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep build policy explicit:** This metadata kernel supports reasoning; the real Cargo fixture supplies build evidence. Edition and compiler version remain different policy fields.

**Retain an error rather than hide a failed gate:** Release accounting should retain a failed check instead of substituting an older successful result. One failed gate prevents a claimed complete release.

## Reason through the six tasks

1. **Predict and explain.** Explain edition, compiler version and dependency version separately.

2. **Guided modification.** Build InventoryLab with its checked-in lockfile.

3. **Independent construction.** Run its tests and inspect a deliberately changed public contract.

4. **Diagnose a defect.** Diagnose offline mode failing because a dependency was never prepared.

5. **Boundary evidence.** Remove only owned target output and perform a clean build.

6. **Transfer and justify.** Design a dependency upgrade review including lock diff, licenses, compile tests and runtime evidence.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Cargo describes packages, targets, dependencies and build profiles. A Rust edition selects language compatibility rules while the compiler version selects available implementations and library APIs. These are related but distinct. Pinning an edition does not pin a dependency graph or a compiler toolchain.

Cargo.lock records selected dependency versions for reproducible resolution under a project policy. Locked and offline modes answer different questions: locked rejects graph changes, while offline forbids network access and requires prepared assets. The classroom bypasses per-attempt Cargo resolution by linking a reviewed read-only Arrow library. External projects use their own explicit preparation and lock review.

Cargo.toml declares package and dependency intent. Cargo.lock records a resolved graph. cargo build --locked checks lock consistency; --offline requires cached dependencies. cargo test and cargo clippy are distinct verification tools.

A successful dependency download is not successful compilation. Do not edit checksums manually to force a lockfile pass. A native binary is platform- and architecture-specific.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
