# Day 12 — Solutions: OOP Basics and Dataclasses

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **objects that keep related state and behavior together**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **objects that keep related state and behavior together** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Create a `BankAccount` class with owner and private-by-convention balance state plus `deposit`, `withdraw`, and `balance` behavior. **Contract:** deposits are positive, withdrawals cannot exceed the balance, and invalid operations raise `ValueError` without changing state. **Verify:** assert the starting balance, exact balance after one deposit and one withdrawal, and unchanged balance plus `ValueError` after a zero deposit and an overdraw.

**Reasoning:** Implement this exact contract as written: Create a `BankAccount` class with owner and private-by-convention balance state plus `deposit`, `withdraw`, and `balance` behavior. Contract: deposits are positive, withdrawals cannot exceed the balance, and invalid operations raise `ValueError` without changing state. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert the starting balance, exact balance after one deposit and one withdrawal, and unchanged balance plus `ValueError` after a zero deposit and an overdraw. That connects the answer to objects that keep related state and behavior together.

```python
class BankAccount:
    def __init__(self, owner: str, opening_balance: float = 0.0) -> None:
        if not owner.strip():
            raise ValueError("owner must not be blank")
        if opening_balance < 0:
            raise ValueError("opening balance must be non-negative")
        self.owner = owner.strip()
        self._balance = float(opening_balance)

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount


account = BankAccount("Ada", 10.0)
account.deposit(5.0)
assert account.balance == 15.0
account.withdraw(4.0)
assert account.balance == 11.0

for invalid_operation in (
    lambda: account.deposit(0),
    lambda: account.withdraw(12.0),
):
    before = account.balance
    try:
        invalid_operation()
    except ValueError:
        pass
    else:
        raise AssertionError("invalid operation should raise ValueError")
    assert account.balance == before
```

`_balance` communicates internal state by convention. The property
allows read access while all mutation passes through validated methods.

**Verification evidence:** assert the starting balance, exact balance after one deposit and one withdrawal, and unchanged balance plus `ValueError` after a zero deposit and an overdraw.

### Exercise 2 — worked answer

**Learner contract:** Convert a plain product record to `@dataclass Product(name: str, price: float, quantity: int = 0)`. Add `__post_init__` validation and a `stock_value()` method. **Expected behavior:** `Product('tea', 4.0, 3).stock_value() == 12.0`; negative values raise. **Constraint:** use `field(default_factory=...)` if you add any mutable collection field. **Verify:** Assert `stock_value()` is `12.0`, equality uses field values, and separate negative-price and negative-quantity constructions raise.

**Reasoning:** Implement this exact contract as written: Convert a plain product record to `@dataclass Product(name: str, price: float, quantity: int = 0)`. Add `__post_init__` validation and a `stock_value()` method. Expected behavior: `Product('tea', 4.0, 3).stock_value() == 12.0`; negative values raise. Constraint: use `field(default_factory=...)` if you add any mutable collection field. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert `stock_value()` is `12.0`, equality uses field values, and separate negative-price and negative-quantity constructions raise. That connects the answer to objects that keep related state and behavior together.

```python
from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be blank")
        if self.price < 0:
            raise ValueError("price must be non-negative")
        if self.quantity < 0:
            raise ValueError("quantity must be non-negative")

    def stock_value(self) -> float:
        return self.price * self.quantity


tea = Product("tea", 4.0, 3)
assert tea.stock_value() == 12.0
assert Product("cup", 2.5).quantity == 0

for arguments in (("tea", -0.01, 1), ("tea", 4.0, -1)):
    try:
        Product(*arguments)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid product should fail: {arguments!r}")
```

No collection field is needed here. If one is added later, use
`field(default_factory=list)` so instances do not share one mutable
default.

**Verification evidence:** Assert `stock_value()` is `12.0`, equality uses field values, and separate negative-price and negative-quantity constructions raise.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict how a class attribute shared by instances differs from an instance attribute assigned through `self`. **Progressive hint:** Class lookup is shared until an instance shadows the name. **Verify:** Construct two instances, mutate/shadow one instance field, and assert shared class lookup versus independent instance values explicitly.

**Reasoning:** Predict this named state change before running it: Prediction: Predict how a class attribute shared by instances differs from an instance attribute assigned through `self`. Progressive hint: Class lookup is shared until an instance shadows the name. Then compare the prediction with this proof target: Construct two instances, mutate/shadow one instance field, and assert shared class lookup versus independent instance values explicitly. This makes objects that keep related state and behavior together observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Construct two instances, mutate/shadow one instance field, and assert shared class lookup versus independent instance values explicitly.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace dataclass equality for two separately constructed values with equal fields and compare it with object identity using `is`. **Progressive hint:** Value equality and identity answer different questions. **Verify:** Assert two equal-field dataclass values satisfy `==` but not `is`; mutate or replace a field and confirm equality changes as expected.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace dataclass equality for two separately constructed values with equal fields and compare it with object identity using `is`. Progressive hint: Value equality and identity answer different questions. Record the named value, shape, label, or iterator position needed to establish: Assert two equal-field dataclass values satisfy `==` but not `is`; mutate or replace a field and confirm equality changes as expected. The trace exposes objects that keep related state and behavior together directly.

**Evidence to locate in the grouped implementation:** Assert two equal-field dataclass values satisfy `==` but not `is`; mutate or replace a field and confirm equality changes as expected.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Create immutable `OrderLine` and `Order` dataclasses whose total sums quantity × unit price and applies a validated fractional discount. **Progressive hint:** Validate non-negative values in `__post_init__`. **Verify:** Assert exact order total for multiple lines and a discount, then assert negative quantity/price and out-of-range discount construction each fail.

**Reasoning:** Implement this exact contract as written: Implementation: Create immutable `OrderLine` and `Order` dataclasses whose total sums quantity × unit price and applies a validated fractional discount. Progressive hint: Validate non-negative values in `__post_init__`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert exact order total for multiple lines and a discount, then assert negative quantity/price and out-of-range discount construction each fail. That connects the answer to objects that keep related state and behavior together.

**Evidence to locate in the grouped implementation:** Assert exact order total for multiple lines and a discount, then assert negative quantity/price and out-of-range discount construction each fail.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a dataclass field declared as `items: list[str] = []`. **Progressive hint:** Use `field(default_factory=list)` to create one list per instance. **Verify:** Create two default instances, mutate one `items` list, and assert the other remains empty and the list objects are not identical.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a dataclass field declared as `items: list[str] = []`. Progressive hint: Use `field(default_factory=list)` to create one list per instance. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Create two default instances, mutate one `items` list, and assert the other remains empty and the list objects are not identical. The diagnosis depends on objects that keep related state and behavior together.

**Evidence to locate in the grouped implementation:** Create two default instances, mutate one `items` list, and assert the other remains empty and the list objects are not identical.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Decide whether a discount policy should be a subclass of `Order` or a composed callable; justify the dependency direction. **Progressive hint:** A replaceable rule is usually behavior the order uses, not a kind of order. **Verify:** Swap two discount callables without changing `Order`; assert totals follow each policy and explain why composition preserves the dependency direction.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Decide whether a discount policy should be a subclass of `Order` or a composed callable; justify the dependency direction. Progressive hint: A replaceable rule is usually behavior the order uses, not a kind of order. Values below, at, and above the named boundary must produce the evidence Swap two discount callables without changing `Order`; assert totals follow each policy and explain why composition preserves the dependency direction. Those cases show how objects that keep related state and behavior together behaves at its edge.

**Evidence to locate in the grouped implementation:** Swap two discount callables without changing `Order`; assert totals follow each policy and explain why composition preserves the dependency direction.

## Expanded mastery lab solutions

Put behavior with the data it protects, while keeping ownership and mutation explicit. Prefer composition unless the subtype truly is-a base.

### Shared implementation for Exercises 3–4 — Shared state, equality, and identity

Class attributes are found through the class and shared by default; assigning
`self.name` creates/updates an instance attribute. Dataclasses compare declared
fields by default, so equal values can still be distinct objects.

### Shared implementation for Exercises 5–7 — Validated value objects and composition

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
