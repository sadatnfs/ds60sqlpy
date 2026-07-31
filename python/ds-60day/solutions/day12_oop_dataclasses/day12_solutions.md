# Day 12 — Solutions: OOP Basics and Dataclasses

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**objects that keep related state and behavior together**.

A class defines how a family of objects is constructed and behaves; an
instance is one concrete object. Instance attributes hold per-object
state, and methods are functions retrieved through an instance so that
the instance is passed as `self`. Use a class when state and invariant-
preserving behavior genuinely belong together, not merely to wrap a
dictionary.

A dataclass generates common record behavior such as initialization,
representation, and equality from annotated fields. It does not validate
values automatically. Use `__post_init__` for small invariant checks and
distinguish class attributes shared by all instances from fields owned
by each instance.

### Vocabulary used in the worked answers

- **class:** a definition of construction and behavior for related objects.
- **instance:** one concrete object created from a class.
- **attribute:** a named value stored on or resolved through an object.
- **method:** a function accessed through an object, normally receiving `self`.
- **invariant:** a condition that must remain true for a valid object.
- **dataclass:** a class whose record-oriented methods are generated from fields.

### Reference pattern 1 — Model a validated record with a computed method

Keep line-item state and its subtotal behavior together.

```python
from dataclasses import dataclass

@dataclass
class LineItem:
    name: str
    unit_price: float
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.unit_price < 0 or self.quantity < 0:
            raise ValueError("price and quantity must be non-negative")

    def subtotal(self) -> float:
        return self.unit_price * self.quantity

item = LineItem("notebook", 4.5, 3)
(item, item.subtotal())
```

**Expected observation:** `LineItem(name='notebook', unit_price=4.5, quantity=3)` and `13.5`. Construction enforces the invariant.

### Reference pattern 2 — Show that fields belong to each instance

Mutating one instance should not alter another independent record.

```python
first = LineItem("pen", 1.5, 2)
second = LineItem("pen", 1.5, 2)
first.quantity = 5
(first.quantity, second.quantity, first == second)
```

**Expected observation:** `(5, 2, False)`. Each instance owns its quantity; dataclass equality compares current field values.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Create a `BankAccount` class with owner and private-by-convention balance state plus `deposit`, `withdraw`, and `balance` behavior. **Contract:** deposits are positive, withdrawals cannot exceed the balance, and invalid operations raise `ValueError` without changing state. **Verify:** trace a new account through one deposit, one withdrawal, and two rejected boundary cases.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the objects that keep related state and behavior together model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Edge case:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.

**Solution evidence to inspect:** trace a new account through one deposit, one withdrawal, and two rejected boundary cases.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Convert a plain product record to `@dataclass Product(name: str, price: float, quantity: int = 0)`. Add `__post_init__` validation and a `stock_value()` method. **Expected behavior:** `Product('tea', 4.0, 3).stock_value() == 12.0`; negative values raise. **Constraint:** use `field(default_factory=...)` if you add any mutable collection field. **Verify:** Assert `stock_value()` is `12.0`, equality uses field values, and separate negative-price and negative-quantity constructions raise.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies objects that keep related state and behavior together.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Edge case:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.

**Solution evidence to inspect:** Assert `stock_value()` is `12.0`, equality uses field values, and separate negative-price and negative-quantity constructions raise.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict how a class attribute shared by instances differs from an instance attribute assigned through `self`. **Progressive hint:** Class lookup is shared until an instance shadows the name. **Verify:** Construct two instances, mutate/shadow one instance field, and assert shared class lookup versus independent instance values explicitly.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying objects that keep related state and behavior together.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Edge case:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.

**Solution evidence to inspect:** Construct two instances, mutate/shadow one instance field, and assert shared class lookup versus independent instance values explicitly.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace dataclass equality for two separately constructed values with equal fields and compare it with object identity using `is`. **Progressive hint:** Value equality and identity answer different questions. **Verify:** Assert two equal-field dataclass values satisfy `==` but not `is`; mutate or replace a field and confirm equality changes as expected.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the objects that keep related state and behavior together model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Edge case:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.

**Solution evidence to inspect:** Assert two equal-field dataclass values satisfy `==` but not `is`; mutate or replace a field and confirm equality changes as expected.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Create immutable `OrderLine` and `Order` dataclasses whose total sums quantity × unit price and applies a validated fractional discount. **Progressive hint:** Validate non-negative values in `__post_init__`. **Verify:** Assert exact order total for multiple lines and a discount, then assert negative quantity/price and out-of-range discount construction each fail.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies objects that keep related state and behavior together.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Edge case:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.

**Solution evidence to inspect:** Assert exact order total for multiple lines and a discount, then assert negative quantity/price and out-of-range discount construction each fail.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a dataclass field declared as `items: list[str] = []`. **Progressive hint:** Use `field(default_factory=list)` to create one list per instance. **Verify:** Create two default instances, mutate one `items` list, and assert the other remains empty and the list objects are not identical.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in objects that keep related state and behavior together.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Edge case:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.

**Solution evidence to inspect:** Create two default instances, mutate one `items` list, and assert the other remains empty and the list objects are not identical.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Decide whether a discount policy should be a subclass of `Order` or a composed callable; justify the dependency direction. **Progressive hint:** A replaceable rule is usually behavior the order uses, not a kind of order. **Verify:** Swap two discount callables without changing `Order`; assert totals follow each policy and explain why composition preserves the dependency direction.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from objects that keep related state and behavior together.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Edge case:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.

**Solution evidence to inspect:** Swap two discount callables without changing `Order`; assert totals follow each policy and explain why composition preserves the dependency direction.
<!-- END BEGINNER SOLUTION REVIEW -->

We model Orders with dataclasses, compute totals with discounts, and add rich representations and equality.

Contents
- Exercise 1: Order model with total and discounts
- Exercise 2: __repr__/__str__ and equality checks

---

Exercise 1 — Order model
```python
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable

@dataclass(frozen=True)
class OrderItem:
    sku: str
    price: float
    qty: int
    discount: float = 0.0  # per-item absolute discount

    def total(self) -> float:
        # price*qty minus discount*qty, not dropping below 0
        gross = self.price * self.qty
        net = max(gross - self.discount * self.qty, 0.0)
        return round(net, 2)


@dataclass
class Order:
    id: int
    customer: str
    placed: date
    items: list[OrderItem]
    percent_off: float = 0.0  # order-level percent discount (0..1)

    def subtotal(self) -> float:
        return round(sum(it.total() for it in self.items), 2)

    def total(self) -> float:
        sub = self.subtotal()
        total = sub * (1.0 - self.percent_off)
        return round(total, 2)

# Demo
order = Order(
    id=1, customer="Ada", placed=date(2025,1,1),
    items=[OrderItem("A", 10.0, 2, discount=1.0), OrderItem("B", 5.0, 1)] ,
    percent_off=0.10,
)
print(order.subtotal(), order.total())  #  (10*2-1*2)+5 = 23 -> 20.7
```
Line-by-line
- OrderItem is frozen (immutable) so it can be safely used in sets/dicts.
- total clamps at zero to prevent negative totals when discounts exceed price.
- Order applies an additional percent discount at the order level.

Validation (optional): use __post_init__ to validate fields.
```python
@dataclass(frozen=True)
class OrderItem:
    sku: str
    price: float
    qty: int
    discount: float = 0.0
    def __post_init__(self):
        if self.price < 0 or self.qty < 0 or self.discount < 0:
            raise ValueError("price/qty/discount must be non-negative")
```

---

Exercise 2 — __repr__/__str__ and equality
Dataclasses generate nice __repr__ and equality by default. Customize __str__ for user-friendly printing.

```python
@dataclass
class Order:
    id: int
    customer: str
    placed: date
    items: list[OrderItem]
    percent_off: float = 0.0

    def __str__(self) -> str:
        return f"Order #{self.id} for {self.customer} on {self.placed:%Y-%m-%d}: total=${self.total():.2f}"

# Equality demo
o1 = Order(1, "Ada", date(2025,1,1), [OrderItem("A", 10.0, 1)])
o2 = Order(1, "Ada", date(2025,1,1), [OrderItem("A", 10.0, 1)])
assert o1 == o2                # dataclass compares field-by-field
print(str(o1))
```
Notes
- dataclass eq=True by default; set order=True if you want ordering comparisons.
- For performance and memory, consider slots=True on large models.

---

## Expanded mastery lab solutions

Put behavior with the data it protects, while keeping ownership and mutation explicit. Prefer composition unless the subtype truly is-a base.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Shared state, equality, and identity

Class attributes are found through the class and shared by default; assigning
`self.name` creates/updates an instance attribute. Dataclasses compare declared
fields by default, so equal values can still be distinct objects.

### Practices 3–5 — Validated value objects and composition

```python
from dataclasses import dataclass, field
from collections.abc import Callable


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price: float

    def __post_init__(self) -> None:
        if self.quantity < 0 or self.unit_price < 0:
            raise ValueError("quantity and unit_price must be non-negative")

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order:
    lines: list[OrderLine] = field(default_factory=list)
    discount: float = 0.0

    def __post_init__(self) -> None:
        if not 0 <= self.discount <= 1:
            raise ValueError("discount must be a fraction from 0 to 1")

    @property
    def total(self) -> float:
        gross = sum(line.subtotal for line in self.lines)
        return gross * (1 - self.discount)


first = OrderLine("A", 2, 4.0)
same_value = OrderLine("A", 2, 4.0)
assert first == same_value and first is not same_value
assert Order([first], discount=0.25).total == 6.0

# A replaceable pricing policy composes cleanly:
DiscountPolicy = Callable[[float], float]
no_discount: DiscountPolicy = lambda total: total
assert no_discount(8.0) == 8.0
```

Composition lets an order use a policy without claiming every pricing rule is a
new kind of order.
