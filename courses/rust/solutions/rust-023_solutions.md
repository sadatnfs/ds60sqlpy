# rust-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-023_solution.rs](rust-023_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Call a reviewed public function:** The implementation details remain behind its named boundary. The consumer uses the domain module interface.

**Import a name without changing ownership:** Use changes name resolution, not execution or data ownership. The shorter imported name refers to the same function.

## Task answers

### Task 1: Predict and explain

Identify the public and private items.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The implementation details remain behind its named boundary. The consumer uses the domain module interface.

### Task 2: Guided modification

Add a private helper used by the public function.

No separate reference answer has been written for this task. Start from Example B: Use changes name resolution, not execution or data ownership. The shorter imported name refers to the same function.

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

### Task 4: Diagnose a defect

Diagnose a consumer accessing a private representation field.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Modules are not runtime services. Excessive pub can freeze accidental implementation details into an API. A use declaration does not install a dependency.

### Task 5: Boundary evidence

Test the public contract without relying on internal helper names.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Call a reviewed public function) and Example B (Import a name without changing ownership).

### Task 6: Transfer and justify

Split a future library and executable crate by responsibility and document dependency direction.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Module**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Modules organize names and control visibility. A private implementation can change without forcing every consumer to understand it. Public items form a compatibility boundary and should expose domain meaning rather than internal representation. A crate is a compilation unit; a package can contain a library crate and executable crates.

The classroom can demonstrate modules inside one source file. A real multi-file Cargo project has separate preparation and is not uploaded through the pad. Keep that distinction explicit when a lesson introduces src/lib.rs and integration tests. Good module boundaries follow responsibilities and dependency direction, not a fixed rule that every type needs its own file.

`mod domain { ... }` declares a module. pub exposes an item to permitted external paths. use imports a name into scope without copying its implementation. pub(crate) limits visibility to the current crate.

Modules are not runtime services. Excessive pub can freeze accidental implementation details into an API. A use declaration does not install a dependency.

## Review before continuing

Run the reference and confirm that it prints `rust-023: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
