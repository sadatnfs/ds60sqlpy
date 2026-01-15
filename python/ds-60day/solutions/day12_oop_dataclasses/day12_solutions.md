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
