# rust-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-023_solution.rs](rust-023_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Call a reviewed public function:** The implementation details remain behind its named boundary. The consumer uses the domain module interface.

**Import a name without changing ownership:** Use changes name resolution, not execution or data ownership. The shorter imported name refers to the same function.

## Task answers

### Task 1: Predict and explain

Identify the public and private items.

**Written answer.** `mod domain` has no `pub`, so it is private to the crate root, which is also where `main` lives and calls it. Inside it, `pub fn double` is public, so any code that can name `domain` can call `domain::double`. Example B's `use domain::double;` is a private import that only adds a shorter local name.

**Why it is correct.** Rust visibility is relative to modules: a private item is visible in its parent module and that module's descendants, and `pub` opens an item to everything that can reach its parent. `main` is in the parent of `domain`, so it needs only `double` to be `pub`.

**Plausible wrong approach.** Assuming `domain` must be `pub mod` before `main` can use it confuses crate-level privacy with export. That change compiles, but it would only matter for code outside this crate, and it widens the surface for no caller here.

**How to verify.** Remove `pub` from `double` and read E0603, function `double` is private, at `domain::double(4)`. Restore it and both examples pass.

### Task 2: Guided modification

Add a private helper used by the public function.

**Written answer.** Write `mod domain { fn factor() -> i32 { 2 } pub fn double(value: i32) -> i32 { value * factor() } }`. `double(4)` is still 8 and `double(0)` still 0, and `factor` cannot be named from `main`.

**Why it is correct.** `factor` is private to `domain`, and `double` is in the same module, so it can call the helper while consumers only see the unchanged `pub fn` signature.

**Plausible wrong approach.** Marking the helper `pub fn factor` "just in case" compiles, but it lets `main` write `domain::factor()`. Renaming or inlining the helper later then breaks that caller, which is exactly the accidental surface the lesson warns about.

**How to verify.** Run both examples, then add `domain::factor();` to `main` and read E0603, function `factor` is private.

### Task 3: Independent construction

Move a pure domain operation into an inline module.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    mod pricing {
        pub fn total(unit: u32, quantity: u32) -> Option<u32> {
            unit.checked_mul(quantity)
        }
    }
    assert_eq!(pricing::total(4, 5), Some(20));
    assert_eq!(pricing::total(u32::MAX, 2), None);
    Ok(())
}
```

**Observe:** pricing::total(4, 5) is Some(20); an overflowing total is None.

Only the pub function is visible outside the module, so the module can change its internals without breaking callers.

**Plausible wrong approach.** Returning `unit * quantity` as a plain `u32` hides the overflow: `total(u32::MAX, 2)` panics with attempt to multiply with overflow when overflow checks are on and wraps to 4294967294 otherwise, so the `None` contract cannot be expressed at all.

**How to verify.** Add the neighbors of the limit: `assert_eq!(pricing::total(65535, 65537), Some(u32::MAX));` and `assert_eq!(pricing::total(65536, 65536), None);`, plus `pricing::total(0, u32::MAX) == Some(0)`.

### Task 4: Diagnose a defect

Diagnose a consumer accessing a private representation field.

**Written answer.** Suppose `domain` holds `pub struct Quantity { value: u32 }` with `pub fn new(value: u32) -> Option<Quantity>` that refuses values above 1000, and `pub fn get(&self) -> u32`. A consumer writing `quantity.value` gets E0616, field `value` of struct `Quantity` is private. The fix is to call `quantity.get()`.

**Why it is correct.** The private field is the representation, and `new` is the only path that checks the 1000 limit. Keeping the field private guarantees every `Quantity` a consumer holds went through that check.

**Plausible wrong approach.** Making the field `pub value` silences E0616, but then `domain::Quantity { value: 5000 }` also compiles, bypassing `new` and producing a quantity the domain promised could not exist.

**How to verify.** Read E0616 for `.value` and E0451 for a struct literal from `main`. With `get`, assert `domain::Quantity::new(5).unwrap().get() == 5` and `domain::Quantity::new(5000).is_none()`.

### Task 5: Boundary evidence

Test the public contract without relying on internal helper names.

**Written answer.** Test only through the public name: `for (input, expected) in [(-3, -6), (0, 0), (4, 8)] { assert_eq!(domain::double(input), expected); }`. No assertion mentions the private `factor` helper from task 2.

**Why it is correct.** The table pins what callers observe, so the module can rename, inline or delete its helpers and the tests still describe the same contract.

**Plausible wrong approach.** Asserting `domain::factor() == 2` fails to compile from `main` with E0603. Making `factor` public to satisfy the test turns a refactoring detail into API that every later change must preserve.

**How to verify.** Replace `value * factor()` with `value + value` and delete `factor`. The table still passes and `rust-023: passed` prints.

### Task 6: Transfer and justify

Split a future library and executable crate by responsibility and document dependency direction.

**Written answer.** In the separately prepared InventoryLab Cargo project, put pure domain code in `src/lib.rs` (for example `pub mod domain;`) and keep argument parsing, file reading and printing in `src/main.rs`, which calls the library by crate name. Dependencies point one way: the binary uses the library, and the library never refers to the binary.

**Why it is correct.** The library stays free of I/O and testable, and each file in `tests/` compiles as a separate crate that can reach only `pub` library items, so integration tests exercise the real public surface. A limitation is that anything those tests need must be `pub`, which pressures the API to grow.

**Plausible wrong approach.** Keeping the domain logic in `src/main.rs` and adding `tests/report.rs` fails: an integration test links against the library target, and a package with only a binary has no library for the test to `use`.

**How to verify.** In that project, `cargo test` runs the unit tests and every `tests/*.rs` file, and `cargo run` exercises the binary. The pad cannot show this, because it compiles a single `main.rs`.

## Mechanism and diagnostic reasoning

Modules organize names and control visibility. A private implementation can change without forcing every consumer to understand it. Public items form a compatibility boundary and should expose domain meaning rather than internal representation. A crate is a compilation unit; a package can contain a library crate and executable crates.

The classroom can demonstrate modules inside one source file. A real multi-file Cargo project has separate preparation and is not uploaded through the pad. Keep that distinction explicit when a lesson introduces src/lib.rs and integration tests. Good module boundaries follow responsibilities and dependency direction, not a fixed rule that every type needs its own file.

`mod domain { ... }` declares a module. pub exposes an item to permitted external paths. use imports a name into scope without copying its implementation. pub(crate) limits visibility to the current crate.

Modules are not runtime services. Excessive pub can freeze accidental implementation details into an API. A use declaration does not install a dependency.

## Review before continuing

Run the reference and confirm that it prints `rust-023: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
