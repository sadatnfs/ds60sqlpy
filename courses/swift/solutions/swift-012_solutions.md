# swift-012: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-012_solution.swift](swift-012_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep copied value state independent:** The struct contains value state and its mutation is explicit. Reserving from the copied inventory does not change the original.

**Reject without partial mutation:** Checking every rejection condition before subtraction preserves failure atomicity. Rejected requests retain the previous valid stock.

## Task answers

### Task 1: Predict and explain

Trace both inventory copies through reservation.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
var first = Inventory(stock: 5)
var second = first
precondition(first.stock == 5 && second.stock == 5)
precondition(second.reserve(2))
precondition(first.stock == 5 && second.stock == 3)
precondition(first.reserve(0) && first.stock == 5)
```

**Observe:** Both copies start at 5; reserving 2 from second leaves first at 5 and second at 3, and reserving 0 from first keeps 5.

Inventory is a struct, so var second = first copies the stock, and each mutating reserve changes only the copy it is called on.

### Task 2: Guided modification

Add a validated restock operation.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
var inventory = Inventory(stock: 3)
precondition(inventory.restock(4) && inventory.stock == 7)
precondition(!inventory.restock(0) && !inventory.restock(-2))
precondition(!inventory.restock(Int.max) && inventory.stock == 7)
```

**Observe:** Restocking 4 raises 3 to 7; 0, -2 and an overflowing Int.max are refused and the stock stays 7.

The extension lives in the same file, so it may use the private setter, and it validates before writing, so a refused restock never changes stock.

### Task 3: Independent construction

Build a bounded counter with private mutation.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct BoundedCounter {
  private(set) var value = 0
  let limit: Int
  mutating func increment() -> Bool {
    guard value < limit else { return false }
    value += 1
    return true
  }
}
var counter = BoundedCounter(limit: 2)
precondition(counter.increment() && counter.increment())
precondition(!counter.increment() && counter.value == 2)
```

**Observe:** Two increments succeed, the third is refused, and the value stays at 2.

private(set) lets callers read value but change it only through increment, which enforces the limit.

### Task 4: Diagnose a defect

Diagnose subtracting stock before checking the requested amount.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
struct Careless {
  var stock: Int
  mutating func reserve(_ amount: Int) -> Bool {
    stock -= amount
    return stock >= 0
  }
}
var careless = Careless(stock: 3)
precondition(!careless.reserve(4) && careless.stock == -1)
var inventory = Inventory(stock: 3)
precondition(!inventory.reserve(4) && inventory.stock == 3)
```

**Observe:** Subtracting first reports failure but leaves stock at -1; Inventory refuses the same request and keeps 3.

The careless version mutates before validating, so a rejected request still corrupts state; the guard in Inventory.reserve checks the amount first and changes stock only on success.

### Task 5: Boundary evidence

Test zero, exact-stock and excess reservations.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
var inventory = Inventory(stock: 3)
precondition(inventory.reserve(0) && inventory.stock == 3)
precondition(!inventory.reserve(4) && inventory.stock == 3)
precondition(inventory.reserve(3) && inventory.stock == 0)
```

**Observe:** Reserving 0 succeeds without change, 4 is refused, and exactly 3 succeeds and leaves 0.

amount <= stock admits the exact-stock case, and amount >= 0 admits zero, so the only refusal is the request that exceeds the stock.

### Task 6: Transfer and justify

Choose a value model for an editable form and explain how cancel can restore an earlier snapshot.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Build a bounded counter with private mutation) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A copies an `Inventory` struct and reserves 2 units from the copy. Example B asks for 4 units from stock 3 and for -1 units, both of which must be refused. The `reserve` method checks both conditions in one guard before subtracting. The task 3 answer builds a bounded counter whose mutation is private.

**Why it is correct.** Struct assignment copies `stock`, so the copy drops to 3 while the original keeps 5. In Example B the guard rejects 4 because it exceeds 3 and rejects -1 because it is negative, returning false before any subtraction, so stock stays 3. Reserving 0 is allowed and leaves stock at 5. In task 3 the third increment is refused at the limit 2.

**A plausible wrong approach.** Writing `stock -= amount` first and then checking whether stock went negative looks efficient, but a rejected request has already changed state; `reserve(4)` would leave -1 or require a fragile undo. The `inventory.stock == 3` check catches it. Making `stock` publicly settable lets callers bypass the guard entirely.

**How to verify.** Swap the guard and subtraction in a scratch copy and confirm the stock check fails. For task 5, test reserve(0), reserve(3) on stock 3 (succeeds, leaves 0) and reserve(4) (refused, stock unchanged).

## Mechanism and diagnostic reasoning

A struct models a value with named properties and operations. Assignment follows value semantics, making independent state snapshots straightforward when its stored members also have appropriate semantics. A mutating method explicitly changes self or its stored properties. Methods without mutating cannot silently alter a value-type instance.

Constructors should establish valid state, and operations should preserve it. Do not expose unrestricted writable fields if they allow callers to bypass the rule. A small value type can be a strong domain boundary, but wrapping a primitive without adding meaning or validation is only extra syntax.

`struct Inventory` defines a value type. `private(set)` exposes reading but restricts assignment. A `mutating func` may update stored state. An initializer can reject invalid input with a throwing or failable contract in later chapters.

A struct can contain shared class references. Private setters are useful only when methods enforce invariants. The public memberwise initializer in a small fixture is not a substitute for validating external state.

## Review before continuing

Run the reference and confirm that it prints `swift-012: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
