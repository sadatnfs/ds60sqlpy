# Day 12 — OOP Basics and Dataclasses

**Level:** Beginner

Use a class when data and behavior form one meaningful concept with invariants.
Use a plain function or collection when they do not.

## Learning objectives

By the end of this lesson, you can:

- define instance attributes and methods;
- use `@dataclass` to generate initialization, representation, and equality;
- validate a dataclass after initialization;
- customize user-facing `__str__` behavior;
- explain when inheritance is less clear than composition.

## Prerequisites

Complete Day 11 (`python-11`): function contracts, logging, tests, and type hints.

## Vocabulary and mental model

- **Class:** definition of a data-and-behavior type; **instance:** one value of
  that type.
- **Attribute:** data associated with an instance.
- **Method:** function resolved through an instance or class.
- **Invariant:** rule that must remain true for every valid instance.
- **Dataclass:** class decorator that generates repetitive data-model methods.
- **Composition:** an object contains collaborators; **inheritance:** an object
  specializes another type.

## Worked example

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Temperature:
    celsius: float

    def as_fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32

    def __str__(self) -> str:
        return f"{self.celsius:.1f} °C"
```

`frozen=True` prevents normal reassignment; it does not make every possible
nested value deeply immutable. `slots=True` avoids a per-instance attribute
dictionary and rejects unexpected attributes.

## Exercises and progressive hints

1. Model an `Order` and compute its total after discounts. **Hint:** represent
   the input fields first, then put the pricing rule in a method; state whether
   discounts are fractions or currency amounts.
2. Add readable `__str__` output and explore generated representation/equality.
   **Hint:** dataclass equality compares declared fields between compatible
   instances; create two equivalent and one different instance.

### Additional mastery practice

Put behavior with the data it protects, while keeping ownership and mutation explicit. Prefer composition unless the subtype truly is-a base.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict how a class attribute shared by instances differs from an instance attribute assigned through `self`.
   **Progressive hint:** Class lookup is shared until an instance shadows the name.
4. **Tracing:** Trace dataclass equality for two separately constructed values with equal fields and compare it with object identity using `is`.
   **Progressive hint:** Value equality and identity answer different questions.
5. **Implementation:** Create immutable `OrderLine` and `Order` dataclasses whose total sums quantity × unit price and applies a validated fractional discount.
   **Progressive hint:** Validate non-negative values in `__post_init__`.
6. **Debugging:** Repair a dataclass field declared as `items: list[str] = []`.
   **Progressive hint:** Use `field(default_factory=list)` to create one list per instance.
7. **Edge case and explanation:** Decide whether a discount policy should be a subclass of `Order` or a composed callable; justify the dependency direction.
   **Progressive hint:** A replaceable rule is usually behavior the order uses, not a kind of order.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- What methods does `@dataclass` generate by default?
- Where should an invariant involving multiple fields be validated?
- What is the difference between `__repr__` and `__str__` audiences?
- Why might an `Order` contain line items instead of inherit from a list?

Expected behavior: invalid order values cannot silently create nonsensical
totals, equal orders compare equal, and the display string is informative.

## Common pitfalls and diagnosis

- **Instances share a mutable default:** use `field(default_factory=list)`.
- **Validation never runs:** place post-construction checks in `__post_init__`
  or a factory, and test invalid values.
- **A property calls itself forever:** store the underlying value under a
  different attribute name.
- **A frozen dataclass contains a mutable list:** freezing blocks attribute
  assignment, not mutation inside that list.
- **Inheritance requires many overrides:** prefer a contained collaborator when
  the relationship is "has a," not genuinely "is a."

## Continue

- [Open the learner notebook](../notebooks/day12_oop_dataclasses.ipynb)
- [Check the separate solution](../solutions/day12_oop_dataclasses/day12_solutions.md)
- [Next: Day 13 — Functional tools](day13_functional_tools.md)
