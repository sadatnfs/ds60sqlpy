# rust-002: explanation and comparison

Executable reference: [rust-002_solution.rs](rust-002_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Expose an accumulator:** Only the value requiring state transitions is declared mutable. The mutable total changes while the fixed input remains 4.

**Shadow after a representation change:** Shadowing can change type, but names must still explain whether a value is text, length or parsed quantity. The new count is the text length, not the number twelve.

## Task answers

### Task 1: Predict and explain

Identify the static type and mutability of each binding.

**Written answer.** In Example A, `per_box` is an immutable `i32` and `total` is a mutable `i32`. In Example B, the first `count` is an immutable `&'static str`, the shadowing `count` is an immutable `usize`, and `explicit` is an immutable `u64`.

**Why it is correct.** Unsuffixed integer literals fall back to `i32` when nothing else constrains them; a string literal has type `&'static str`; the `usize` annotation matches what `len()` returns; and the `_u64` suffix fixes `explicit`. Only `total` is written after initialization, so only it carries `mut`.

**Plausible wrong approach.** Describing `count` as one variable that changed from text to a number misreads shadowing. The second `let` creates a new binding and neither is mutable; writing `count = count.len();` without `let` would be rejected with a type mismatch.

**How to verify.** Add `fn type_of<T>(_: &T) -> &'static str { std::any::type_name::<T>() }` and print `type_of(&per_box)`, `type_of(&count)` and `type_of(&explicit)`: the pad shows `i32`, `usize` and `u64`.

### Task 2: Guided modification

Remove unnecessary mut declarations in a small program.

**Written answer.** Given `let mut per_box = 4; let mut total = 0; total += per_box; total += per_box;`, delete `mut` from `per_box`, which is never written again, and keep it on `total`. The compiler's `variable does not need to be mutable` warning points at exactly that binding.

**Why it is correct.** `mut` grants permission to reassign or take a mutable borrow. Removing it where no write happens lets the compiler reject a future accidental write instead of silently accepting it.

**Plausible wrong approach.** Removing `mut` from every binding also strips it from `total`, and `total += per_box` then fails with E0384, cannot assign twice to an immutable variable. Silencing the warning with `#[allow(unused_mut)]` keeps the unneeded permission.

**How to verify.** Run the version with the extra `mut` and read the warning naming `per_box`. Remove it, run again: no warning, and `assert_eq!(total, 8)` still passes.

### Task 3: Independent construction

Write a running total with fixed input and mutable accumulator.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let deliveries = [3, 5, 2];
    let mut total = 0;
    for amount in deliveries {
        total += amount;
    }
    assert_eq!(total, 10);
    assert_eq!(deliveries, [3, 5, 2]);
    Ok(())
}
```

**Observe:** The running total ends at 10 and the input array is unchanged.

Only the accumulator is declared mut; the fixed input stays immutable, so the compiler rejects any accidental edit to it.

**Plausible wrong approach.** Switching the input to `let deliveries = vec![3, 5, 2];` with the same loop fails to compile: `for amount in deliveries` moves the `Vec`, so the later `assert_eq!(deliveries, ...)` is E0382, borrow of moved value. The array version works because `[i32; 3]` is `Copy`; the `Vec` version needs `for amount in &deliveries`.

**How to verify.** Run the block: the total is 10 and the input still equals `[3, 5, 2]`. Add `deliveries[0] = 0;` temporarily and the compiler refuses it with E0594, because `deliveries` is not declared mutable.

### Task 4: Diagnose a defect

Diagnose assigning a String to a mutable integer binding.

**Written answer.** The defect is `let mut count = 0; count = String::from("12");`. rustc reports E0308, mismatched types, expected integer, found `String`. `mut` allows a new value of the same type, and the type was fixed as an integer at the declaration. Convert instead: `count = "12".parse()?;`.

**Why it is correct.** Each binding has one static type for its whole scope; mutability controls whether the value may change, never the type. `parse` produces an integer, and `?` forwards a `ParseIntError` through `main`'s boxed error.

**Plausible wrong approach.** Changing the declaration to `let mut count = String::new();` makes the assignment compile but turns every arithmetic use of `count` into a new error. Shadowing with `let count = String::from("12");` also compiles but hides that the value is now text, not a quantity.

**How to verify.** Compile the defect and read E0308 pointing at `String::from`. After the fix, `assert_eq!(count, 12);` passes. Changing the text to `"twelve"` makes `?` return the error, so the run ends with an `invalid digit found in string` message instead of the marker.

### Task 5: Boundary evidence

Test an empty input string and a zero accumulator.

**Written answer.** Shadow an empty input exactly as Example B does: `let count = ""; let count: usize = count.len(); assert_eq!(count, 0);`. For the accumulator, sum an empty array: `let deliveries: [i32; 0] = []; let mut total = 0; for amount in deliveries { total += amount; } assert_eq!(total, 0);`.

**Why it is correct.** Empty text has zero bytes, so its length is 0 rather than an error. A loop over zero elements never runs its body, so the accumulator keeps its starting value, 0, which is the identity for addition.

**Plausible wrong approach.** Expecting `"".parse::<i32>()` to give 0 confuses empty with zero. It returns an `Err` whose kind is `Empty`, and calling `.unwrap()` on it panics with `ParseIntError { kind: Empty }`.

**How to verify.** Run both blocks and add `assert!("".parse::<i32>().is_err());`. All three checks pass silently and `rust-002: passed` prints.

### Task 6: Transfer and justify

Choose shadowing or distinct names for parsing stages and justify readability.

**Written answer.** Use shadowing when the meaning and unit stay the same, and a new name when they change: `let quantity_text = " 12 "; let quantity_text = quantity_text.trim();` then `let quantity: u32 = quantity_text.parse()?;`. Trimming keeps the value text, while parsing turns it into a count.

**Why it is correct.** The reader can trust that every `quantity_text` is text and every `quantity` is a number, so a units change is visible in the name. A limitation is that long pipelines accumulate names; at that point a small parsing function is clearer.

**Plausible wrong approach.** Following Example B literally, `let quantity = quantity_text.len();` compiles and yields 2, the number of digits, instead of 12. Both are `usize`-compatible values, so only a check on the value exposes the mix-up.

**How to verify.** Assert `assert_eq!(quantity_text, "12");` and `assert_eq!(quantity, 12);`. Replace `parse()?` with `len() as u32` and the second check panics with `left: 2` and `right: 12`.

## Mechanism and diagnostic reasoning

Rust bindings are immutable by default. `mut` grants permission to change a binding's value. Immutability reduces the number of state transitions a reader must consider, but it is not a substitute for understanding ownership and interior mutability introduced later. Prefer a new derived value when that expresses the operation clearly.

Type inference remains static: the compiler determines a concrete type from context. Shadowing introduces a new binding with the same name and can deliberately change its type. Reassignment instead changes the value of an existing mutable binding and must preserve its type. Use either technique to expose meaning rather than obscure where a value came from.

`let count: i32 = 3` annotates a type. `let mut total = 0` allows reassignment. `let text = text.len()` shadows the earlier name with a new binding. Integer suffixes such as `3_u64` constrain inference.

Immutable does not mean every object reachable through a type is deeply frozen. Shadowing can conceal a units change. Type inference is not dynamic typing.

## Review before continuing

Rebuild Example B (Shadow after a representation change) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
