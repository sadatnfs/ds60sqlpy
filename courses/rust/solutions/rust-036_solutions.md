# rust-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-036_solution.rs](rust-036_solution.rs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe an edition 2024 scope rule:** Edition 2024 drops a temporary in a block's tail expression before the block's local variables, so the Ref returned by borrow() no longer outlives cell. The edition selects this rule; the compiler version only has to implement it. name_length compiles and returns 4 under edition 2024; edition 2021 rejects the same function with E0597.

**Iterate a boxed slice by value:** Edition 2024 changes which IntoIterator implementation a method call on Box<[T]> selects. Code can change meaning or stop compiling across editions, which is why Cargo.toml records the edition explicitly and why an upgrade deserves review. into_iter on a Box<[String]> yields owned Strings under edition 2024; under edition 2021 the same call yields &String and the collect fails with E0277.

## Task answers

### Task 1: Predict and explain

Explain edition, compiler version and dependency version separately.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Edition 2024 drops a temporary in a block's tail expression before the block's local variables, so the Ref returned by borrow() no longer outlives cell. The edition selects this rule; the compiler version only has to implement it. name_length compiles and returns 4 under edition 2024; edition 2021 rejects the same function with E0597.

### Task 2: Guided modification

Build InventoryLab with its checked-in lockfile.

No separate reference answer has been written for this task. Start from Example B: Edition 2024 changes which IntoIterator implementation a method call on Box<[T]> selects. Code can change meaning or stop compiling across editions, which is why Cargo.toml records the edition explicitly and why an upgrade deserves review. into_iter on a Box<[String]> yields owned Strings under edition 2024; under edition 2021 the same call yields &String and the collect fails with E0277.

### Task 3: Independent construction

Run its tests and inspect a deliberately changed public contract.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Edition** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose offline mode failing because a dependency was never prepared.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A successful dependency download is not successful compilation. Do not edit checksums manually to force a lockfile pass. A native binary is platform- and architecture-specific.

### Task 5: Boundary evidence

Remove only owned target output and perform a clean build.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Observe an edition 2024 scope rule) and Example B (Iterate a boxed slice by value).

### Task 6: Transfer and justify

Design a dependency upgrade review including lock diff, licenses, compile tests and runtime evidence.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Edition**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Cargo describes packages, targets, dependencies and build profiles. A Rust edition selects language compatibility rules while the compiler version selects available implementations and library APIs. These are related but distinct. Pinning an edition does not pin a dependency graph or a compiler toolchain.

Cargo.lock records selected dependency versions for reproducible resolution under a project policy. Locked and offline modes answer different questions: locked rejects graph changes, while offline forbids network access and requires prepared assets. The classroom bypasses per-attempt Cargo resolution by linking a reviewed read-only Arrow library. External projects use their own explicit preparation and lock review.

The classroom compiles every pad with edition 2024, and editions change real language rules. Edition 2024 drops temporaries in a block's tail expression before the block's locals, iterates a Box<[T]> by value, reserves the gen keyword, requires unsafe extern blocks and treats std::env::set_var as unsafe. The two examples compile only under edition 2024; edition 2021 rejects them with E0597 and E0277.

Cargo.toml declares package and dependency intent, including edition = "2024". Cargo.lock records a resolved graph. cargo build --locked checks lock consistency; --offline requires cached dependencies. cargo test and cargo clippy are distinct verification tools. cargo fix --edition migrates code mechanically, but the migrated code still needs review.

A successful dependency download is not successful compilation. Do not edit checksums manually to force a lockfile pass. A native binary is platform- and architecture-specific.

## Review before continuing

Run the reference and confirm that it prints `rust-036: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
