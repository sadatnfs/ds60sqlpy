# rust-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-036_solution.rs](rust-036_solution.rs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe an edition 2024 scope rule:** Edition 2024 drops a temporary in a block's tail expression before the block's local variables, so the Ref returned by borrow() no longer outlives cell. The edition selects this rule; the compiler version only has to implement it. name_length compiles and returns 4 under edition 2024; edition 2021 rejects the same function with E0597.

**Iterate a boxed slice by value:** Edition 2024 changes which IntoIterator implementation a method call on Box<[T]> selects. Code can change meaning or stop compiling across editions, which is why Cargo.toml records the edition explicitly and why an upgrade deserves review. into_iter on a Box<[String]> yields owned Strings under edition 2024; under edition 2021 the same call yields &String and the collect fails with E0277.

## Task answers

### Task 1: Predict and explain

Explain edition, compiler version and dependency version separately.

**Written answer.** The edition is a per-crate language setting in Cargo.toml, here `edition = "2024"`, and it decides rules such as the tail-expression drop order in Example A and the `Box<[T]>` iteration in Example B. The compiler version is the installed toolchain, for example rustc 1.99.1, which must be new enough to implement that edition but does not change its rules. Dependency versions are the crate releases Cargo selected and recorded in Cargo.lock; InventoryLab's lock lists only `inventory-lab 0.1.0` because it has no dependencies.

**Why it is correct.** The three settings change independently and fail in different ways: an edition change can alter meaning, a toolchain upgrade usually only adds diagnostics or features, and a dependency change can alter behavior without any source edit. Recording each one separately is what makes a build reproducible.

**Plausible wrong approach.** Assuming that a newer rustc compiles code under the newest edition predicts that Example A would fail on an old manifest. A crate with `edition = "2021"` keeps 2021 rules on every newer compiler, which is exactly where Example A is rejected with E0597.

**How to verify.** Run `rustc --version` and `cargo --version`, read the `edition` line in Cargo.toml and the `[[package]]` entries in Cargo.lock: three separate facts from three separate places.

### Task 2: Guided modification

Build InventoryLab with its checked-in lockfile.

**Written answer.** Copy `courses/rust/fixtures/InventoryLab` to an ignored workspace and run `cargo build --locked --offline` there. In the reference run, on rustc 1.99.1, Cargo printed `Compiling inventory-lab v0.1.0` and then `Finished dev profile`, and `cargo run --locked --offline` printed `apple=3;pear=6;rejected=1`. `--locked` makes Cargo fail rather than rewrite Cargo.lock, and `--offline` forbids network access, so a success shows that the checked-in graph was already complete.

**Why it is correct.** A build that is allowed to update the lockfile can succeed with a different graph from the one reviewed. With both flags, success means the exact recorded graph compiled with no download.

**Plausible wrong approach.** Running a plain `cargo build` and committing whatever Cargo.lock it produces turns a verification step into an unreviewed dependency change.

**How to verify.** Run `git status` on the copied project after the build: Cargo.lock is unchanged, and only the ignored `target` directory is new.

### Task 3: Independent construction

Run its tests and inspect a deliberately changed public contract.

**Written answer.** `cargo test --locked --offline` on the unchanged copy runs three targets: the library and executable unit-test targets report `running 0 tests`, and `tests/contracts.rs` reports `4 passed`. Then rename the public function, `pub fn render` to `pub fn render_report`, and test again. The reference run failed to compile with E0432, `unresolved import inventory_lab::render`, in the integration test and E0425, `cannot find function render in crate inventory_lab`, in the executable. The tests and the binary are clients of the library's public API, so a renamed item breaks them before any assertion runs.

**Why it is correct.** Integration tests compile against the crate exactly as an external user would, so they detect contract changes, not just wrong values. A rename is a breaking change and needs a major version or a compatibility shim such as a deprecated `render` that calls the new name.

**Plausible wrong approach.** Counting the two zero-test targets as passing evidence inflates the result; only the four integration tests check behavior.

**How to verify.** Restore the name and run the tests again: four pass. Add `#[deprecated] pub fn render(report: &Report) -> String { render_report(report) }` instead, and the tests compile again with a deprecation warning.

### Task 4: Diagnose a defect

Diagnose offline mode failing because a dependency was never prepared.

**Written answer.** The defect is adding a dependency to Cargo.toml, for example `tinyjson = "2"`, and then running `cargo build --offline` in an environment where that crate was never downloaded. The reference run failed with `no matching package named tinyjson found` and the note that offline mode can cause surprising resolution failures. Offline mode can only resolve against crates already in the local cache, so the fix is a deliberate preparation step with network access (`cargo fetch`), a lockfile review, and only then the offline build.

**Why it is correct.** `--offline` answers whether the build can run without the network, not whether the graph is complete. A missing crate is a preparation failure, not a code error, and no source edit will fix it.

**Plausible wrong approach.** Removing `--offline` inside the classroom or a locked-down build to make the error go away replaces a reviewed dependency step with whatever the network returns.

**How to verify.** Add a dependency that is not in the local cache and run `cargo build --offline`: the error names the package. Remove the line and the build succeeds again with an unchanged Cargo.lock.

### Task 5: Boundary evidence

Remove only owned target output and perform a clean build.

**Written answer.** From the copied project directory, run `cargo clean`, then `cargo build --locked --offline`. In the reference run `cargo clean` reported `Removed 158 files, 39.1MiB total`. Afterward the directory held only Cargo.lock, Cargo.toml, README.md, `src` and `tests`, and the clean build compiled `inventory-lab v0.1.0` again from source. `cargo clean` deletes the `target` directory of the package it runs in, so running it in the owned copy touches nothing else.

**Why it is correct.** A clean build proves the output can be recreated from source plus the lockfile alone, without relying on stale artifacts.

**Plausible wrong approach.** Deleting `target` with `rm -rf` from a guessed path, or running `cargo clean` from a shared parent workspace, risks removing output or files you do not own.

**How to verify.** List the directory before and after `cargo clean`: only `target` disappears, and `cargo run --locked --offline` again prints `apple=3;pear=6;rejected=1`.

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
