# rust-036: Cargo, editions and reproducible release workflows

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-035`

## Learning objectives

Explain editions, lockfiles and offline builds, and show an edition 2024 rule that changes compilation. The central exercise is task 3: Run its tests and inspect a deliberately changed public contract.

## Purpose and mental model

Cargo describes packages, targets, dependencies and build profiles. A Rust edition selects language compatibility rules while the compiler version selects available implementations and library APIs. These are related but distinct. Pinning an edition does not pin a dependency graph or a compiler toolchain.

Cargo.lock records selected dependency versions for reproducible resolution under a project policy. Locked and offline modes answer different questions: locked rejects graph changes, while offline forbids network access and requires prepared assets. The classroom bypasses per-attempt Cargo resolution by linking a reviewed read-only Arrow library. External projects use their own explicit preparation and lock review.

The classroom compiles every pad with edition 2024, and editions change real language rules. Edition 2024 drops temporaries in a block's tail expression before the block's locals, iterates a Box<[T]> by value, reserves the gen keyword, requires unsafe extern blocks and treats std::env::set_var as unsafe. The two examples compile only under edition 2024; edition 2021 rejects them with E0597 and E0277.

## Vocabulary and concepts

**Edition:** A language compatibility mode for a crate.

**Lockfile:** A record of the selected dependency graph.

**Offline build:** A build restricted to already prepared dependency assets.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::cell`. A passing run prints `rust-036: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).

The complete [InventoryLab](../fixtures/InventoryLab/README.md) demonstrates Cargo without external dependencies. Arrow dependencies are prepared by the classroom image, not installed by learner source.

## Syntax anatomy and execution trace

Cargo.toml declares package and dependency intent, including edition = "2024". Cargo.lock records a resolved graph. cargo build --locked checks lock consistency; --offline requires cached dependencies. cargo test and cargo clippy are distinct verification tools. cargo fix --edition migrates code mechanically, but the migrated code still needs review.

**Reading Example A (Observe an edition 2024 scope rule, code below).** `name_length` creates a `RefCell<String>` and ends with the tail expression `cell.borrow().len()`. `borrow()` returns a `Ref` guard, a temporary that must be dropped once the length is read. Under edition 2021, temporaries in a block's tail expression lived longer than the block's local variables, so the guard would outlive the `cell` it borrows, and the borrow checker reported E0597. Edition 2024 drops tail-expression temporaries before the block's locals, so the same source compiles. The edition is selected per crate in Cargo.toml, not by the compiler version, which is why one toolchain can build both.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Observe an edition 2024 scope rule

Edition 2024 drops a temporary in a block's tail expression before the block's local variables, so the Ref returned by borrow() no longer outlives cell. The edition selects this rule; the compiler version only has to implement it.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn name_length() -> usize {
            let cell = std::cell::RefCell::new(String::from("pear"));
            cell.borrow().len()
        }
        assert_eq!(name_length(), 4);
    }
    println!("rust-036: passed");
    Ok(())
}
```

**Observe:** name_length compiles and returns 4 under edition 2024; edition 2021 rejects the same function with E0597.

### Example B: Iterate a boxed slice by value

Edition 2024 changes which IntoIterator implementation a method call on Box<[T]> selects. Code can change meaning or stop compiling across editions, which is why Cargo.toml records the edition explicitly and why an upgrade deserves review.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let boxed: Box<[String]> = vec![String::from("a"), String::from("b")].into_boxed_slice();
        let owned: Vec<String> = boxed.into_iter().collect();
        assert_eq!(owned, ["a", "b"]);
    }
    println!("rust-036: passed");
    Ok(())
}
```

**Observe:** into_iter on a Box<[String]> yields owned Strings under edition 2024; under edition 2021 the same call yields &String and the collect fails with E0277.

## Exercises

1. **Predict and explain.** Explain edition, compiler version and dependency version separately.

2. **Guided modification.** Build InventoryLab with its checked-in lockfile.

3. **Independent construction.** Run its tests and inspect a deliberately changed public contract.

4. **Diagnose a defect.** Diagnose offline mode failing because a dependency was never prepared.

5. **Boundary evidence.** Remove only owned target output and perform a clean build.

6. **Transfer and justify.** Design a dependency upgrade review including lock diff, licenses, compile tests and runtime evidence.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A successful dependency download is not successful compilation. Do not edit checksums manually to force a lockfile pass. A native binary is platform- and architecture-specific.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Observe an edition 2024 scope rule) before changing anything, and confirm its observation: name_length compiles and returns 4 under edition 2024; edition 2021 rejects the same function with E0597.
2. Compare Example B (Iterate a boxed slice by value) with Example A and name the first line whose behavior differs. Its observation is: into_iter on a Box<[String]> yields owned Strings under edition 2024; under edition 2021 the same call yields &String and the collect fails with E0277.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A successful dependency download is not successful compilation.

Tempting approaches to rule out before you compare:

- **Task 1.** Assuming that a newer rustc compiles code under the newest edition predicts that Example A would fail on an old manifest. A crate with `edition = "2021"` keeps 2021 rules on every newer compiler, which is exactly where Example A is rejected with E0597.
- **Task 2.** Running a plain `cargo build` and committing whatever Cargo.lock it produces turns a verification step into an unreviewed dependency change.
- **Task 3.** Counting the two zero-test targets as passing evidence inflates the result; only the four integration tests check behavior.
- **Task 5.** Deleting `target` with `rm -rf` from a guessed path, or running `cargo clean` from a shared parent workspace, risks removing output or files you do not own.

## Self-check and next step

Why does `name_length` compile under edition 2024 but fail with E0597 under edition 2021? Why does `into_iter` on a `Box<[String]>` yield owned `String`s in 2024 but `&String` in 2021? What does `Cargo.lock` pin that the `edition` key does not, and why does an upgrade review need both?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Edition Guide, tail expression temporary scope](https://doc.rust-lang.org/edition-guide/rust-2024/temporary-tail-expr-scope.html) for the 2024 rule behind Example A. The broader reference is [https://doc.rust-lang.org/cargo/guide/](https://doc.rust-lang.org/cargo/guide/).

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-036: Cargo, editions and reproducible release workflows.
Read courses/rust/guides/rust-036.md and courses/rust/lessons/rust-036.rs. Prerequisites: rust-035.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-036_solution.rs and
courses/rust/solutions/rust-036_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
