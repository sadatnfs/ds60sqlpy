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





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day12_oop_dataclasses.md`, then open `python/ds-60day/notebooks/day12_oop_dataclasses.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 12 — oop basics and dataclasses to practice objects that keep related state and behavior together
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **class:** a definition of construction and behavior for related objects.
- **instance:** one concrete object created from a class.
- **attribute:** a named value stored on or resolved through an object.
- **method:** a function accessed through an object, normally receiving `self`.
- **invariant:** a condition that must remain true for a valid object.
- **dataclass:** a class whose record-oriented methods are generated from fields.

### Syntax anatomy

`@dataclass` decorates the following class. In `quantity: int`, the
annotation declares a field and generated constructor parameter.
`self.quantity` refers to the current instance's field. A method that
returns a calculation without mutation is easier to reason about than
one that silently changes several attributes.

### Worked example 1 — Model a validated record with a computed method

Keep line-item state and its subtotal behavior together. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

**Expected observation**

```text
`LineItem(name='notebook', unit_price=4.5, quantity=3)` and `13.5`. Construction enforces the invariant.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Show that fields belong to each instance

Mutating one instance should not alter another independent record. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
first = LineItem("pen", 1.5, 2)
second = LineItem("pen", 1.5, 2)
first.quantity = 5
(first.quantity, second.quantity, first == second)
```

**Expected observation**

```text
`(5, 2, False)`. Each instance owns its quantity; dataclass equality compares current field values.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. When an attribute is missing, inspect whether it was assigned on every constructor path and spell it consistently.
2. Do not use a mutable object as a shared class attribute for per-instance state.
3. Put invariant checks at construction and mutation boundaries, not only in a later calculation.
4. Prefer composition when one object has another; use inheritance only for a genuine substitutable relationship.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** A dictionary suits loose, dynamic records; a named tuple suits immutable records; a dataclass suits named fields with modest behavior and validation.

**Boundary to remember:** Negative quantities, mutable default fields, equality after mutation, subclass invariants, and serialization of nested objects need explicit policy.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Create a `BankAccount` class with owner and private-by-convention balance state plus `deposit`, `withdraw`, and `balance` behavior. **Contract:** deposits are positive, withdrawals cannot exceed the balance, and invalid operations raise `ValueError` without changing state.
   **Verify:** trace a new account through one deposit, one withdrawal, and two rejected boundary cases.

2. Convert a plain product record to `@dataclass Product(name: str, price: float, quantity: int = 0)`. Add `__post_init__` validation and a `stock_value()` method.
   **Expected behavior:** `Product('tea', 4.0, 3).stock_value() == 12.0`; negative values raise. **Constraint:** use `field(default_factory=...)` if you add any mutable collection field.
   **Verify:** Assert `stock_value()` is `12.0`, equality uses field values, and separate negative-price and negative-quantity constructions raise.

### Additional mastery practice

Put behavior with the data it protects, while keeping ownership and mutation explicit. Prefer composition unless the subtype truly is-a base.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict how a class attribute shared by instances differs from an instance attribute assigned through `self`.
   **Progressive hint:** Class lookup is shared until an instance shadows the name.
   **Verify:** Construct two instances, mutate/shadow one instance field, and assert shared class lookup versus independent instance values explicitly.
4. **Tracing:** Trace dataclass equality for two separately constructed values with equal fields and compare it with object identity using `is`.
   **Progressive hint:** Value equality and identity answer different questions.
   **Verify:** Assert two equal-field dataclass values satisfy `==` but not `is`; mutate or replace a field and confirm equality changes as expected.
5. **Implementation:** Create immutable `OrderLine` and `Order` dataclasses whose total sums quantity × unit price and applies a validated fractional discount.
   **Progressive hint:** Validate non-negative values in `__post_init__`.
   **Verify:** Assert exact order total for multiple lines and a discount, then assert negative quantity/price and out-of-range discount construction each fail.
6. **Debugging:** Repair a dataclass field declared as `items: list[str] = []`.
   **Progressive hint:** Use `field(default_factory=list)` to create one list per instance.
   **Verify:** Create two default instances, mutate one `items` list, and assert the other remains empty and the list objects are not identical.
7. **Edge case and explanation:** Decide whether a discount policy should be a subclass of `Order` or a composed callable; justify the dependency direction.
   **Progressive hint:** A replaceable rule is usually behavior the order uses, not a kind of order.
   **Verify:** Swap two discount callables without changing `Order`; assert totals follow each policy and explain why composition preserves the dependency direction.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-12`
(Day 12 — OOP Basics and Dataclasses). I am a complete beginner. Emphasize objects that keep related state and behavior together.
Read `python/ds-60day/companion-guides/day12_oop_dataclasses.md` and use the learner notebook
`python/ds-60day/notebooks/day12_oop_dataclasses.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
