# rust-012: explanation and comparison

Executable reference: [rust-012_solution.rs](rust-012_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Reserve within an invariant:** The method owns both the affordability check and the subtraction. A successful reservation leaves three units.

**Reject without partial mutation:** Validation occurs before changing state, preserving the prior valid value. Excess demand is rejected and zero is an allowed no-op.

## Task answers

### Task 1: Predict and explain

Explain the capability expressed by each method receiver.

**Written answer.** `new(stock)` has no receiver: it is an associated constructor that returns a fresh `Inventory`. `stock(&self)` borrows the value read-only to report the count. `reserve(&mut self, amount)` borrows it exclusively because it may lower the stock.

**Why it is correct.** The receiver states the capability a caller must grant. `&self` works from any binding, while `&mut self` requires a mutable binding and no other live borrows, which is why both examples declare `let mut inventory`.

**Plausible wrong approach.** Dropping `mut` from `let mut inventory` because only methods touch the stock fails at the first `reserve` call with E0596, cannot borrow `inventory` as mutable. Calls to `stock()` on the same binding still compile.

**How to verify.** Declare `let inventory = Inventory::new(5);` and call `inventory.stock()`: it compiles. Add `inventory.reserve(1)` and read E0596; restore `mut` and both examples pass.

### Task 2: Guided modification

Add a checked restock method.

**Written answer.** Add a second impl block: `impl Inventory { fn restock(&mut self, amount: u32) -> bool { match self.stock.checked_add(amount) { Some(total) => { self.stock = total; true } None => false } } }`.

**Why it is correct.** `checked_add` returns `None` when the sum would exceed `u32::MAX`, 4294967295, and the field is written only in the `Some` arm. A rejected restock therefore leaves the previous stock untouched.

**Plausible wrong approach.** Writing `self.stock += amount;` panics with `attempt to add with overflow` when overflow checks are enabled and silently wraps to a tiny stock when they are not. Either way the method cannot report the rejection.

**How to verify.** With `let mut inv = Inventory::new(u32::MAX - 1);`, assert `inv.restock(1)` and `inv.stock() == u32::MAX`, then `!inv.restock(1)` and that the stock is still `u32::MAX`.

### Task 3: Independent construction

Create a bounded counter with private state and validated operations.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    struct Counter {
        value: u32,
        limit: u32,
    }
    impl Counter {
        fn new(limit: u32) -> Self {
            Self { value: 0, limit }
        }
        fn increment(&mut self) -> bool {
            if self.value == self.limit {
                return false;
            }
            self.value += 1;
            true
        }
    }
    let mut counter = Counter::new(2);
    assert!(counter.increment() && counter.increment());
    assert!(!counter.increment());
    assert_eq!(counter.value, 2);
    Ok(())
}
```

**Observe:** Two increments succeed, the third is refused, and the value stays at the limit 2.

The fields are private to the defining module, so callers can change the counter only through increment, which checks the limit first.

**Plausible wrong approach.** Testing the limit with `self.value > self.limit` is an off-by-one: at 2 of 2 the test is false, so the third call increments to 3 and returns true, and `assert!(!counter.increment())` panics. The `==` check stops exactly at the limit.

**How to verify.** Run the block, then add `let mut zero = Counter::new(0); assert!(!zero.increment()); assert_eq!(zero.value, 0);`. A zero-limit counter must refuse its very first increment.

### Task 4: Diagnose a defect

Diagnose subtracting before checking available stock.

**Written answer.** The defect subtracts first: `self.stock -= amount; if self.stock ... { return false; }`. For Example B, 3 minus 4 underflows the `u32`: it panics with `attempt to subtract with overflow` under overflow checks, or wraps to 4294967295 without them. Either way the rejection is not atomic. Check first, or write `match self.stock.checked_sub(amount)` and assign only on `Some`.

**Why it is correct.** Failure atomicity requires every rejection condition to be decided before the field changes. The helper's `if amount > self.stock { return false; }` runs before the subtraction, so a rejected reserve never touches `stock`.

**Plausible wrong approach.** Swapping in `self.stock = self.stock.saturating_sub(amount);` before the check removes the panic but still mutates: the rejected request drains the stock to 0, and Example B's `assert_eq!(inventory.stock(), 3)` fails with `left: 0`.

**How to verify.** Run Example B against the subtract-first version and observe the overflow panic or the failed stock check. Restore check-first order and the stock stays 3 after the refused reservation.

### Task 5: Boundary evidence

Test zero, exact-stock and excess reservations.

**Written answer.** On `Inventory::new(3)`: `reserve(0)` returns true and the stock stays 3; `reserve(3)` returns true and leaves 0; a following `reserve(1)` returns false and the stock stays 0.

**Why it is correct.** The guard is `amount > self.stock`, so a request equal to the stock passes (3 is not greater than 3) and selling the last units is allowed. Zero passes trivially and subtracts nothing.

**Plausible wrong approach.** Writing the guard as `amount >= self.stock` refuses the exact-stock reservation, so `reserve(3)` returns false and the last three units can never be sold.

**How to verify.** Assert the three results and the stock after each: 3, 0, 0. Change `>` to `>=` temporarily and the exact-stock assertion panics.

### Task 6: Transfer and justify

Choose a consuming method when an operation should make the prior state unavailable.

**Written answer.** Take `self` by value when the old state must become unusable: `struct Order { items: Vec<String> }` with `fn submit(self) -> Submitted { Submitted { items: self.items } }`. After `let submitted = order.submit();`, any later use of `order` is a compile error.

**Why it is correct.** A `self` receiver moves the value into the method, so the compiler, not a runtime flag, rejects editing an order after submission. A limitation is that it does nothing for `Copy` types, where passing `self` copies instead of moving.

**Plausible wrong approach.** Using `fn submit(&mut self)` with a `submitted: bool` field leaves `order` usable, so `add_item` after `submit` compiles and every method needs its own runtime check.

**How to verify.** Assert `submitted.items.len()` matches the items added. Then add `order.items.len()` after the `submit` call and read E0382, borrow of moved value.

## Mechanism and diagnostic reasoning

A struct groups named fields into a domain value. Methods express operations on that value, and their receiver states whether they borrow, mutate or consume it. A constructor function can validate inputs before creating a valid instance. Private fields prevent callers from bypassing that constructor or later invariants.

Failure atomicity means a rejected operation leaves the prior valid state unchanged. Check all rejection conditions before mutation or build a candidate value and commit it only after validation. Encapsulation is useful because it keeps this reasoning in one place rather than requiring every caller to remember the rule.

`impl Inventory` contains associated functions and methods. `&self` reads, `&mut self` mutates, and `self` consumes. An associated constructor such as new can return Option or Result.

Public writable fields can bypass invariants. Unsigned types prevent negative representation but do not prevent overflow. A method taking &mut self is not automatically safe for unsynchronized sharing across threads.

## Review before continuing

Rebuild Example B (Reject without partial mutation) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
