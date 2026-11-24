# rust-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-017_solution.rs](rust-017_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a declared capability:** The consumer needs the capability rather than the concrete field layout. The borrowed trait object exposes pricing behavior.

**Substitute a second policy:** Both implementations preserve input and output units while varying the rule. The same interface admits an uncapped and capped policy.

## Task answers

### Task 1: Predict and explain

Trace the method call to each implementation.

**Written answer.** `view.cost(4)` goes through the `&dyn Pricer` vtable to `FlatPrice::cost`, giving 3 times 4 = 12. In Example B, `prices[0]` dispatches to `FlatPrice::cost` (12) and `prices[1]` to `CappedPrice::cost`, where 12 is capped at 10.

**Why it is correct.** A `&dyn Pricer` is a data pointer plus a vtable pointer, and each element carries the vtable of its own concrete type. The call site is the same; the implementation is chosen at run time per element.

**Plausible wrong approach.** Predicting `[12, 12]` because the array holds one type confuses the element type `&dyn Pricer` with the concrete types behind it. Each element still knows it is a `FlatPrice` or a `CappedPrice`.

**How to verify.** Assert `std::mem::size_of::<&dyn Pricer>() == 2 * std::mem::size_of::<usize>()` to see the two pointers, and `CappedPrice(3, 10).cost(3) == 9` to confirm the cap applies only above 10.

### Task 2: Guided modification

Add another flat-price value without changing the consumer.

**Written answer.** Add `let premium = FlatPrice(5);` and extend the array to `let prices: [&dyn Pricer; 3] = [&flat, &capped, &premium];`. The consumer `prices.map(|price| price.cost(4))` is unchanged and now yields `[12, 10, 20]`.

**Why it is correct.** The closure depends only on the `Pricer` contract, so a new value of an existing implementation needs no change in the code that prices.

**Plausible wrong approach.** Dropping the annotation, `let prices = [&flat, &capped, &premium];`, fails with E0308: inference takes `&FlatPrice` from the first element and then finds `&CappedPrice`. Keeping `; 2` with three elements also fails, with a length mismatch.

**How to verify.** Assert `prices.map(|price| price.cost(4)) == [12, 10, 20]`; the run then reaches `rust-017: passed`.

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

**Plausible wrong approach.** Giving the formatter state, such as a `&mut self` call counter appended to the output, breaks the contract: the second call returns a different string and the `formatter.format(3) == formatter.format(3)` assertion panics.

**How to verify.** Add `assert_eq!(formatter.format(0), "0 units");` and `assert_eq!(formatter.format(u32::MAX), "4294967295 units");` to cover both ends of the input type.

### Task 4: Diagnose a defect

Diagnose conforming implementations that disagree about units.

**Written answer.** Suppose `struct DollarPrice(u32)` implements `cost` as `self.0 * units` with the field meaning dollars, while `FlatPrice` means cents. Both satisfy `fn cost(&self, units: u32) -> u32`, so the compiler accepts both, yet `DollarPrice(3).cost(4)` returns 12 dollars where callers expect 12 cents.

**Why it is correct.** A trait checks signatures, not meaning. Fix it by putting the unit in the type: `struct Cents(u32);` and `fn cost(&self, units: u32) -> Cents;`, so the dollar implementation must write `Cents(self.0 * units * 100)` explicitly.

**Plausible wrong approach.** Converting at the call site with `if is_dollars { cost * 100 }` requires the consumer to know the concrete type behind `&dyn Pricer`, which defeats the substitution the trait exists for.

**How to verify.** With the `Cents` return type, assert `DollarPrice(1).cost(4).0 == 400` and `FlatPrice(3).cost(4).0 == 12`. An implementation that forgets the conversion no longer compiles.

### Task 5: Boundary evidence

Test zero units and the exact cap.

**Written answer.** Zero units: `FlatPrice(3).cost(0) == 0` and `CappedPrice(5, 10).cost(0) == 0`. Exact cap: `CappedPrice(5, 10).cost(2) == 10`, with neighbors `cost(1) == 5` and `cost(3) == 10`.

**Why it is correct.** Any price times zero units is zero, and `min` returns the cap when the raw cost equals it. With a unit price of 5, two units land exactly on 10, so the equality case is actually exercised.

**Plausible wrong approach.** Reusing Example B's `CappedPrice(3, 10)` for the exact-cap test never hits equality: 3 units cost 9 and 4 units cost 12, so no unit count produces exactly 10.

**How to verify.** Run the five assertions; each prints nothing on success, and the marker follows.

### Task 6: Transfer and justify

Choose a trait boundary for a file adapter while keeping the domain core pure.

**Written answer.** Keep the core as `fn import_rows(lines: &[&str]) -> ...` with no I/O, and put the trait at the edge: `trait LineSource { fn lines(&self) -> std::io::Result<Vec<String>>; }`, implemented by an in-memory fixture in the pad and by a file reader in a separately prepared Cargo project.

**Why it is correct.** The core stays deterministic and testable offline, and disk errors stay in the adapter's `io::Result`, separate from validation rejections. A limitation is that loading every line into a `Vec` does not stream very large files.

**Plausible wrong approach.** Making the core take a `std::fs::File` mixes I/O failures into validation and means every test needs a real file. Adding file methods to `Pricer` widens a pricing trait with an unrelated capability.

**How to verify.** Implement `struct Fixed(Vec<String>);` for `LineSource`, feed its lines into the core and assert the same totals as Example A. The file-backed adapter is checked in the external project.

## Mechanism and diagnostic reasoning

A trait describes capabilities a type provides. A consumer can depend on the capability instead of one representation. A trait implementation must preserve units, valid inputs and failure meaning, not merely compile with the right method names. This makes substitution a behavioral question.

Static dispatch through generics can retain concrete type information, while a trait object supports runtime substitution behind a pointer. Choose based on the API relationship and storage needs. Start with a small pricing capability whose implementations share one clear contract; avoid inventing a trait for every trivial function.

`trait Pricer` declares a method. `impl Pricer for FlatPrice` supplies behavior. `&dyn Pricer` borrows a trait object and uses dynamic dispatch. The receiver &self permits inspection without consuming the implementation.

A matching signature does not establish compatible semantics. Traits and inheritance are different mechanisms. Avoid exposing implementation details merely to make a trait larger.

## Review before continuing

Run the reference and confirm that it prints `rust-017: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
