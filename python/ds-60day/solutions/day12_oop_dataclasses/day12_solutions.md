# Day 12 Solutions: Classes and Dataclasses

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Create a `BankAccount` class with owner and private-by-convention balance state plus `deposit`, `withdraw`, and `balance` behavior. **Contract:** deposits are positive, withdrawals cannot exceed the balance, and invalid operations raise `ValueError` without changing state. **Verify:** assert the starting balance, exact balance after one deposit and one withdrawal, and unchanged balance plus `ValueError` after a zero deposit and an overdraw.

**Reasoning:** All changes to the balance go through `deposit` and `withdraw`, which validate before they modify, so a rejected operation leaves the balance exactly as it was; the loop at the end checks that for a zero deposit and an overdraft. `_balance` signals "internal, do not assign directly" by convention, and the read-only `balance` property lets callers see the value without a setter. Checking `amount > self._balance` before subtracting is what keeps the balance from going negative. A float balance is acceptable for this exercise, but real money uses `decimal.Decimal` or integer cents to avoid rounding errors.

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

### Exercise 2: worked answer

**Learner contract:** Convert a plain product record to `@dataclass Product(name: str, price: float, quantity: int = 0)`. Add `__post_init__` validation and a `stock_value()` method. **Expected behavior:** `Product('tea', 4.0, 3).stock_value() == 12.0`; negative values raise. **Constraint:** use `field(default_factory=...)` if you add any mutable collection field. **Verify:** Assert `stock_value()` is `12.0`, equality uses field values, and separate negative-price and negative-quantity constructions raise.

**Reasoning:** `@dataclass` generates `__init__`, `__repr__`, and `__eq__` from the annotated fields, and `__post_init__` runs right after the generated `__init__`, which makes it the place for validation. Every check raises before the object can be used, so an invalid `Product` never exists. `stock_value()` is behavior that belongs with the data it uses. `quantity: int = 0` is a safe default because integers are immutable; a list default would need `field(default_factory=list)`, which the sixth exercise covers.

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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict how a class attribute shared by instances differs from an instance attribute assigned through `self`. **Progressive hint:** Class lookup is shared until an instance shadows the name. **Verify:** Construct two instances, mutate/shadow one instance field, and assert shared class lookup versus independent instance values explicitly.

**Reasoning:** Python looks up an attribute on the instance first and then on the class, so a class attribute is shared by every instance until one instance assigns the same name. In the shared implementation for Exercises 3-4, `Visit.created` counts objects at class level, and assigning `first.created = 99` creates an instance attribute that hides the class value for `first` only; `second` and the class still see 2. The common bug is meaning to update the shared value with `self.created = ...`, which silently creates a per-instance copy instead. Write `Visit.created += 1` when the shared value must change.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace dataclass equality for two separately constructed values with equal fields and compare it with object identity using `is`. **Progressive hint:** Value equality and identity answer different questions. **Verify:** Assert two equal-field dataclass values satisfy `==` but not `is`; mutate or replace a field and confirm equality changes as expected.

**Reasoning:** A dataclass generates `__eq__` from its fields, so two separately constructed `Point(1, 2)` objects compare equal while remaining distinct objects: `p == q` is `True` and `p is q` is `False`. Identity asks whether two names refer to the same object; equality asks whether their values match. Changing `q.y` makes them unequal and leaves `p` alone, because they never shared state. Use `is` only for identity questions such as `is None`; using it to compare values is a common bug.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Create immutable `OrderLine` and `Order` dataclasses whose total sums quantity × unit price and applies a validated fractional discount. **Progressive hint:** Validate non-negative values in `__post_init__`. **Verify:** Assert exact order total for multiple lines and a discount, then assert negative quantity/price and out-of-range discount construction each fail.

**Reasoning:** `frozen=True` makes instances immutable after construction, so a validated line or order cannot later become invalid, and frozen dataclasses with immutable fields are hashable. Validation in `__post_init__` rejects negative quantities, negative prices, and discounts outside 0 to 1 before the object exists. The order stores its lines as a tuple to match that immutability and computes the total on demand, so the total can never disagree with the lines: lines worth 8 and 2 with a 25 percent discount give 7.5. Storing a precomputed total as a field is the design that drifts.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a dataclass field declared as `items: list[str] = []`. **Progressive hint:** Use `field(default_factory=list)` to create one list per instance. **Verify:** Create two default instances, mutate one `items` list, and assert the other remains empty and the list objects are not identical.

**Reasoning:** A mutable default such as `[]` would be created once and shared by every instance, so appending to one object's list would change all of them. Dataclasses refuse that declaration outright: `items: list[str] = []` raises `ValueError` when the class is defined and points to `default_factory`. `field(default_factory=list)` calls `list()` for each new instance, so two default baskets get independent lists, which the shared implementation for Exercises 5-7 asserts with `is not`. The same rule applies to dictionaries and sets.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Decide whether a discount policy should be a subclass of `Order` or a composed callable; justify the dependency direction. **Progressive hint:** A replaceable rule is usually behavior the order uses, not a kind of order. **Verify:** Swap two discount callables without changing `Order`; assert totals follow each policy and explain why composition preserves the dependency direction.

**Reasoning:** A discount rule is something an order uses, not a kind of order, so passing it in as a callable leaves `Order` unchanged when the pricing policy changes. Subclassing `Order` for each rule multiplies classes and makes rules hard to combine. In the shared implementation for Exercises 5-7, `checkout` accepts any function from a total to a total, and swapping `no_discount` for `bulk_discount` changes the result from 60.0 to 55.0 without touching `Order`. The dependency points from checkout to the policy, which keeps the data class small and easy to test.

## Expanded mastery lab solutions

Put behavior with the data it protects, while keeping ownership and mutation explicit. Prefer composition unless the subtype truly is-a base.

### Shared implementation for Exercises 3-4: Shared state, equality, and identity

Class attributes are found through the class and shared by default; assigning
`self.name` creates/updates an instance attribute. Dataclasses compare declared
fields by default, so equal values can still be distinct objects.

```python
from dataclasses import dataclass


class Visit:
    created = 0  # class attribute: one value shared through the class

    def __init__(self, label: str) -> None:
        self.label = label  # instance attribute: one value per object
        Visit.created += 1


first = Visit("a")
second = Visit("b")
assert Visit.created == 2 and first.created == 2
first.created = 99  # creates an instance attribute that hides the class value
assert first.created == 99 and second.created == 2 and Visit.created == 2


@dataclass
class Point:
    x: int
    y: int


p = Point(1, 2)
q = Point(1, 2)
assert p == q and p is not q
q.y = 3
assert p != q
```

### Shared implementation for Exercises 5-7: Validated value objects and composition

```python
from collections.abc import Callable
from dataclasses import dataclass, field


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


@dataclass(frozen=True)
class Order:
    lines: tuple[OrderLine, ...] = ()
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
assert Order((first, OrderLine("B", 1, 2.0)), discount=0.25).total == 7.5
for invalid in (
    lambda: OrderLine("C", -1, 1.0),
    lambda: OrderLine("C", 1, -1.0),
    lambda: Order((), discount=1.5),
):
    try:
        invalid()
    except ValueError:
        pass
    else:
        raise AssertionError("invalid construction should raise ValueError")


@dataclass
class Basket:
    # Declaring `items: list[str] = []` is rejected when the class is created.
    items: list[str] = field(default_factory=list)


left, right = Basket(), Basket()
left.items.append("tea")
assert right.items == [] and left.items is not right.items

# A replaceable pricing policy composes with Order instead of subclassing it.
DiscountPolicy = Callable[[float], float]


def no_discount(total: float) -> float:
    return total


def bulk_discount(total: float) -> float:
    return total - 5.0 if total >= 50 else total


def checkout(order: Order, policy: DiscountPolicy) -> float:
    return policy(order.total)


big_order = Order((OrderLine("D", 10, 6.0),))
assert checkout(big_order, no_discount) == 60.0
assert checkout(big_order, bulk_discount) == 55.0
```

Composition lets an order use a policy without claiming every pricing rule is a
new kind of order.
