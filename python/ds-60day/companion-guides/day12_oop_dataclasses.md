# Day 12 — OOP Basics and Dataclasses (Companion Guide)

## Learning objectives
- Define classes with attributes, methods, and properties
- Use `@dataclass` to reduce boilerplate
- Understand equality, ordering, and immutability options

## Why this matters
Data models make code expressive and safe. Dataclasses offer ergonomic, typed containers with comparison and representation for free.

## Dataclass fundamentals
```python
from dataclasses import dataclass
from datetime import date

@dataclass
class Customer:
    id: int
    name: str
    joined: date

    def age_days(self) -> int:
        return (date.today() - self.joined).days
```
Options: `frozen=True` (immutability), `order=True` (comparison), `slots=True` (memory/perf).

## When to use OOP
- Entities with identity and behavior (Orders, Accounts)
- Encapsulate invariants and domain rules in methods

## Common pitfalls
- Over‑modeling (YAGNI: you aren’t gonna need it). Start simple
- Putting heavy logic in `__init__` instead of factory methods/classmethods

## Practice exercises
1) Model an `OrderItem` with price/quantity/discount and a method `total()`
2) Add `@classmethod from_dict(cls, data)` to build from row dicts
3) Make a `frozen` dataclass and explore the behavior of attempted mutation

## Further reading
- dataclasses: https://docs.python.org/3/library/dataclasses.html
