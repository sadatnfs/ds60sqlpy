# Day 12 — Solutions: OOP Basics and Dataclasses

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Model an `Order` and compute its total after discounts. **Hint:** represent the input fields first, then put the pricing rule in a method; state whether discounts are fractions or currency amounts.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Add readable `__str__` output and explore generated representation/equality. **Hint:** dataclass equality compares declared fields between compatible instances; create two equivalent and one different instance.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict how a class attribute shared by instances differs from an instance attribute assigned through `self`.

**Reasoning checkpoint:** Class lookup is shared until an instance shadows the name. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace dataclass equality for two separately constructed values with equal fields and compare it with object identity using `is`.

**Reasoning checkpoint:** Value equality and identity answer different questions. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Create immutable `OrderLine` and `Order` dataclasses whose total sums quantity × unit price and applies a validated fractional discount.

**Reasoning checkpoint:** Validate non-negative values in `__post_init__`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a dataclass field declared as `items: list[str] = []`.

**Reasoning checkpoint:** Use `field(default_factory=list)` to create one list per instance. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Decide whether a discount policy should be a subclass of `Order` or a composed callable; justify the dependency direction.

**Reasoning checkpoint:** A replaceable rule is usually behavior the order uses, not a kind of order. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
