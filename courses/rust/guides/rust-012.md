# rust-012: Structs, methods and validated state

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-011`

## Learning objectives

Encapsulate state in structs with private fields and methods that keep invariants. The central exercise is task 3: Create a bounded counter with private state and validated operations.

## Purpose and mental model

A struct groups named fields into a domain value. Methods express operations on that value, and their receiver states whether they borrow, mutate or consume it. A constructor function can validate inputs before creating a valid instance. Private fields prevent callers from bypassing that constructor or later invariants.

Failure atomicity means a rejected operation leaves the prior valid state unchanged. Check all rejection conditions before mutation or build a candidate value and commit it only after validation. Encapsulation is useful because it keeps this reasoning in one place rather than requiring every caller to remember the rule.

## Vocabulary and concepts

**Struct:** A nominal type with named fields.

**Receiver:** The self parameter describing access to an instance.

**Invariant:** A rule maintained by every externally visible valid state.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-012: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`impl Inventory` contains associated functions and methods. `&self` reads, `&mut self` mutates, and `self` consumes. An associated constructor such as new can return Option or Result.

**Reading Example A (Reserve within an invariant, code below).** The helpers declare `struct Inventory { stock: u32 }` and an `impl` block with three methods whose receivers state their capabilities. `new` has no receiver, so it is called as `Inventory::new(5)` and returns `Self`. `stock(&self)` only reads. `reserve(&mut self, amount)` may change the field, so the caller's binding must be `let mut inventory`. Inside `reserve`, an early `return false` refuses a request larger than the stock and leaves the field unchanged; otherwise the method subtracts and returns `true`. `assert!` checks that boolean directly, and `assert_eq!` reads the remaining stock through the read-only method rather than the private field.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Reserve within an invariant

The method owns both the affordability check and the subtraction.

```rust
struct Inventory {
    stock: u32,
}
impl Inventory {
    fn new(stock: u32) -> Self {
        Self { stock }
    }
    fn stock(&self) -> u32 {
        self.stock
    }
    fn reserve(&mut self, amount: u32) -> bool {
        if amount > self.stock {
            return false;
        }
        self.stock -= amount;
        true
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut inventory = Inventory::new(5);
        assert!(inventory.reserve(2));
        assert_eq!(inventory.stock(), 3);
    }
    println!("rust-012: passed");
    Ok(())
}
```

**Observe:** A successful reservation leaves three units.

### Example B: Reject without partial mutation

Validation occurs before changing state, preserving the prior valid value.

```rust
struct Inventory {
    stock: u32,
}
impl Inventory {
    fn new(stock: u32) -> Self {
        Self { stock }
    }
    fn stock(&self) -> u32 {
        self.stock
    }
    fn reserve(&mut self, amount: u32) -> bool {
        if amount > self.stock {
            return false;
        }
        self.stock -= amount;
        true
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut inventory = Inventory::new(3);
        assert!(!inventory.reserve(4));
        assert_eq!(inventory.stock(), 3);
        assert!(inventory.reserve(0));
    }
    println!("rust-012: passed");
    Ok(())
}
```

**Observe:** Excess demand is rejected and zero is an allowed no-op.

## Exercises

1. **Predict and explain.** Explain the capability expressed by each method receiver.

2. **Guided modification.** Add a checked restock method.

3. **Independent construction.** Create a bounded counter with private state and validated operations.

4. **Diagnose a defect.** Diagnose subtracting before checking available stock.

5. **Boundary evidence.** Test zero, exact-stock and excess reservations.

6. **Transfer and justify.** Choose a consuming method when an operation should make the prior state unavailable.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Public writable fields can bypass invariants. Unsigned types prevent negative representation but do not prevent overflow. A method taking &mut self is not automatically safe for unsynchronized sharing across threads.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Reserve within an invariant) before changing anything, and confirm its observation: A successful reservation leaves three units.
2. Compare Example B (Reject without partial mutation) with Example A and name the first line whose behavior differs. Its observation is: Excess demand is rejected and zero is an allowed no-op.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Public writable fields can bypass invariants.

Tempting approaches to rule out before you compare:

- **Task 1.** Dropping `mut` from `let mut inventory` because only methods touch the stock fails at the first `reserve` call with E0596, cannot borrow `inventory` as mutable. Calls to `stock()` on the same binding still compile.
- **Task 2.** Writing `self.stock += amount;` panics with `attempt to add with overflow` when overflow checks are enabled and silently wraps to a tiny stock when they are not. Either way the method cannot report the rejection.
- **Task 3.** Testing the limit with `self.value > self.limit` is an off-by-one: at 2 of 2 the test is false, so the third call increments to 3 and returns true, and `assert!(!counter.increment())` panics. The `==` check stops exactly at the limit.
- **Task 5.** Writing the guard as `amount >= self.stock` refuses the exact-stock reservation, so `reserve(3)` returns false and the last three units can never be sold.
- **Task 6.** Using `fn submit(&mut self)` with a `submitted: bool` field leaves `order` usable, so `add_item` after `submit` compiles and every method needs its own runtime check.

## Self-check and next step

What capability does each receiver grant: `self`, `&self` and `&mut self`? Why does `Inventory::new(3)` followed by `reserve(4)` return false and leave the stock at 3, and what would a version that subtracted before checking do to an unsigned `stock`? Why does a private `stock` field matter when the type already uses `u32`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 5.3 Methods](https://doc.rust-lang.org/book/ch05-03-method-syntax.html) for `self`, `&self` and `&mut self` receivers.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-012: Structs, methods and validated state.
Read courses/rust/guides/rust-012.md and courses/rust/lessons/rust-012.rs. Prerequisites: rust-011.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-012_solution.rs and
courses/rust/solutions/rust-012_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
