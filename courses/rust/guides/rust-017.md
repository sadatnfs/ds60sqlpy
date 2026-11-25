# rust-017: Traits and behavioral contracts

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-016`

## Learning objectives

Define traits as behavioral contracts and use them through generics and trait objects. The central exercise is task 3: Define a small trait for a deterministic formatter.

## Purpose and mental model

A trait describes capabilities a type provides. A consumer can depend on the capability instead of one representation. A trait implementation must preserve units, valid inputs and failure meaning, not merely compile with the right method names. This makes substitution a behavioral question.

Static dispatch through generics can retain concrete type information, while a trait object supports runtime substitution behind a pointer. Choose based on the API relationship and storage needs. Start with a small pricing capability whose implementations share one clear contract; avoid inventing a trait for every trivial function.

## Vocabulary and concepts

**Trait:** A named capability contract.

**Implementation:** A type-specific realization of a trait.

**Dynamic dispatch:** Selecting behavior through a trait object at runtime.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-017: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`trait Pricer` declares a method. `impl Pricer for FlatPrice` supplies behavior. `&dyn Pricer` borrows a trait object and uses dynamic dispatch. The receiver &self permits inspection without consuming the implementation.

**Reading Example A (Use a declared capability, code below).** `trait Pricer` declares one method signature with no body; any type that provides `cost` with that signature can implement it. `FlatPrice(3)` is a tuple struct, so its single field is read as `self.0`. `let view: &dyn Pricer = &price;` coerces a reference to the concrete type into a trait object: a pointer to the value plus a pointer to a table of `FlatPrice`'s method implementations. The call `view.cost(4)` looks up `cost` in that table at run time, which is dynamic dispatch. `CappedPrice` is declared but not used in Example A; its `min` clamps the product to the second field.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Use a declared capability

The consumer needs the capability rather than the concrete field layout.

```rust
trait Pricer {
    fn cost(&self, units: u32) -> u32;
}
struct FlatPrice(u32);
impl Pricer for FlatPrice {
    fn cost(&self, units: u32) -> u32 {
        self.0 * units
    }
}
struct CappedPrice(u32, u32);
impl Pricer for CappedPrice {
    fn cost(&self, units: u32) -> u32 {
        (self.0 * units).min(self.1)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let price = FlatPrice(3);
        let view: &dyn Pricer = &price;
        assert_eq!(view.cost(4), 12);
    }
    println!("rust-017: passed");
    Ok(())
}
```

**Observe:** The borrowed trait object exposes pricing behavior.

### Example B: Substitute a second policy

Both implementations preserve input and output units while varying the rule.

```rust
trait Pricer {
    fn cost(&self, units: u32) -> u32;
}
struct FlatPrice(u32);
impl Pricer for FlatPrice {
    fn cost(&self, units: u32) -> u32 {
        self.0 * units
    }
}
struct CappedPrice(u32, u32);
impl Pricer for CappedPrice {
    fn cost(&self, units: u32) -> u32 {
        (self.0 * units).min(self.1)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let flat = FlatPrice(3);
        let capped = CappedPrice(3, 10);
        let prices: [&dyn Pricer; 2] = [&flat, &capped];
        assert_eq!(prices.map(|price| price.cost(4)), [12, 10]);
    }
    println!("rust-017: passed");
    Ok(())
}
```

**Observe:** The same interface admits an uncapped and capped policy.

## Exercises

1. **Predict and explain.** Trace the method call to each implementation.

2. **Guided modification.** Add another flat-price value without changing the consumer.

3. **Independent construction.** Define a small trait for a deterministic formatter.

4. **Diagnose a defect.** Diagnose conforming implementations that disagree about units.

5. **Boundary evidence.** Test zero units and the exact cap.

6. **Transfer and justify.** Choose a trait boundary for a file adapter while keeping the domain core pure.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A matching signature does not establish compatible semantics. Traits and inheritance are different mechanisms. Avoid exposing implementation details merely to make a trait larger.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use a declared capability) before changing anything, and confirm its observation: The borrowed trait object exposes pricing behavior.
2. Compare Example B (Substitute a second policy) with Example A and name the first line whose behavior differs. Its observation is: The same interface admits an uncapped and capped policy.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A matching signature does not establish compatible semantics.

Tempting approaches to rule out before you compare:

- **Task 1.** Predicting `[12, 12]` because the array holds one type confuses the element type `&dyn Pricer` with the concrete types behind it. Each element still knows it is a `FlatPrice` or a `CappedPrice`.
- **Task 2.** Dropping the annotation, `let prices = [&flat, &capped, &premium];`, fails with E0308: inference takes `&FlatPrice` from the first element and then finds `&CappedPrice`. Keeping `; 2` with three elements also fails, with a length mismatch.
- **Task 3.** Giving the formatter state, such as a `&mut self` call counter appended to the output, breaks the contract: the second call returns a different string and the `formatter.format(3) == formatter.format(3)` assertion panics.
- **Task 5.** Reusing Example B's `CappedPrice(3, 10)` for the exact-cap test never hits equality: 3 units cost 9 and 4 units cost 12, so no unit count produces exactly 10.
- **Task 6.** Making the core take a `std::fs::File` mixes I/O failures into validation and means every test needs a real file. Adding file methods to `Pricer` widens a pricing trait with an unrelated capability.

## Self-check and next step

Example A calls `view.cost(4)` through `&dyn Pricer`: how does the call reach `FlatPrice::cost` at run time, and what would change if the parameter were a generic `P: Pricer`? Why does `CappedPrice(3, 10)` return 10 rather than 12 for four units? What must the `Pricer` documentation promise so that a third implementation cannot satisfy the signature yet surprise callers?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 18.2 Trait Objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) for when `dyn Trait` replaces a generic parameter.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-017: Traits and behavioral contracts.
Read courses/rust/guides/rust-017.md and courses/rust/lessons/rust-017.rs. Prerequisites: rust-016.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-017_solution.rs and
courses/rust/solutions/rust-017_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
