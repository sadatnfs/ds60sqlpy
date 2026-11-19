# rust-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-017_solution.rs](rust-017_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a declared capability:** The consumer needs the capability rather than the concrete field layout. The borrowed trait object exposes pricing behavior.

**Substitute a second policy:** Both implementations preserve input and output units while varying the rule. The same interface admits an uncapped and capped policy.

## Task answers

### Task 1: Predict and explain

Trace the method call to each implementation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The consumer needs the capability rather than the concrete field layout. The borrowed trait object exposes pricing behavior.

### Task 2: Guided modification

Add another flat-price value without changing the consumer.

No separate reference answer has been written for this task. Start from Example B: Both implementations preserve input and output units while varying the rule. The same interface admits an uncapped and capped policy.

### Task 3: Independent construction

Define a small trait for a deterministic formatter.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    trait Formatter {
        fn format(&self, value: u32) -> String;
    }
    struct Units;
    impl Formatter for Units {
        fn format(&self, value: u32) -> String {
            format!("{value} units")
        }
    }
    let formatter: &dyn Formatter = &Units;
    assert_eq!(formatter.format(3), "3 units");
    assert_eq!(formatter.format(3), formatter.format(3));
    Ok(())
}
```

**Observe:** The formatter turns 3 into 3 units, identically on every call.

The trait states the contract, and the implementation depends only on its input, so repeated calls agree.

### Task 4: Diagnose a defect

Diagnose conforming implementations that disagree about units.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A matching signature does not establish compatible semantics. Traits and inheritance are different mechanisms. Avoid exposing implementation details merely to make a trait larger.

### Task 5: Boundary evidence

Test zero units and the exact cap.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use a declared capability) and Example B (Substitute a second policy).

### Task 6: Transfer and justify

Choose a trait boundary for a file adapter while keeping the domain core pure.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Trait**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A trait describes capabilities a type provides. A consumer can depend on the capability instead of one representation. A trait implementation must preserve units, valid inputs and failure meaning, not merely compile with the right method names. This makes substitution a behavioral question.

Static dispatch through generics can retain concrete type information, while a trait object supports runtime substitution behind a pointer. Choose based on the API relationship and storage needs. Start with a small pricing capability whose implementations share one clear contract; avoid inventing a trait for every trivial function.

`trait Pricer` declares a method. `impl Pricer for FlatPrice` supplies behavior. `&dyn Pricer` borrows a trait object and uses dynamic dispatch. The receiver &self permits inspection without consuming the implementation.

A matching signature does not establish compatible semantics. Traits and inheritance are different mechanisms. Avoid exposing implementation details merely to make a trait larger.

## Review before continuing

Run the reference and confirm that it prints `rust-017: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
