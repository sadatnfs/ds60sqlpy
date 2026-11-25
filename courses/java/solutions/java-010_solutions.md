# java-010: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

An interface describes behavior a caller can rely on without depending on one implementation. Polymorphism lets a reference typed as that interface dispatch to the concrete object method at runtime. The caller should depend on the contract rather than inspect implementation class names. Composition builds a new behavior by holding another object and delegating to it, often making policy combinations clearer than a deep inheritance tree. Substitution requires preserving accepted inputs and promised outputs; matching a method signature alone is insufficient. This lesson uses pricing functions over integer cents so rounding and external services do not obscure the design.

**Interface:** A named behavioral contract implemented by different objects.

**Dynamic dispatch:** Selecting an implementation from the runtime receiver object.

**Composition:** Building behavior by delegating to contained collaborators.

**Sealed interface:** An interface that names every permitted implementation, enabling exhaustive pattern switches.

## Reading the reference

An interface declares a method; implementing classes or lambdas supply its body. A variable of interface type can hold different implementations. The receiver object selects the overridden method at runtime. A composed wrapper validates its own policy, delegates to the inner implementation and checks arithmetic with Math.addExact. Keep domain validation consistent across all implementations so callers do not need class-specific exceptions. A sealed interface lists its permitted implementations, so a switch over it can be exhaustive without a default branch, and a record pattern such as Percent(int percent) tests the type and binds the record component in one case label (Java 21).

## Exercise 1: Call through an interface: change one input

Task: Change `return amount / 2;` to `return amount / 3;` in Example A and predict which assertion fails and why.

The caller invokes the same method name while the concrete behavior differs. The shared nonnegative-input contract keeps both implementations substitutable.

The unchanged code is the part that Example A adds:

```java
Pricing regular = amount -> {
  requireNonnegative(amount);
  return amount;
};
Pricing half = amount -> {
  requireNonnegative(amount);
  return amount / 2;
};
assert regular.price(100) == 100 && half.price(100) == 50;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `regular.price(100) == 100 && half.price(100) == 50`.

**Verify:** Name the value that makes `regular.price(100) == 100 && half.price(100) == 50` false, then restore the line.

## Exercise 2: Compose a fee policy: debug a regression

Task: A regression in Example B's new code makes one line read `Pricing withFee = new Fee(half, 11);`. Repair it using the failing assertion.

The wrapper delegates first and then adds its policy. It does not duplicate the half-price calculation, so the two concerns can change independently.

The unchanged code is the part that Example B adds:

```java
Pricing withFee = new Fee(half, 10);
assert withFee.price(100) == 60;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `withFee.price(100) == 60`; the repaired line reads `Pricing withFee = new Fee(half, 10);`.

**Verify:** Explain how the changed token alters the value that `withFee.price(100) == 60` tests.

## Exercise 3: Switch exhaustively over a sealed type

Task: Price 200 cents with NoDiscount, Percent(25) and Fixed(250) through one pattern-matching switch over the sealed Discount interface.

Discount is sealed, so the compiler knows every implementation and the switch in discounted covers each permitted record without a default branch. Each record pattern, such as Percent(int percent), checks the type and binds its component in one step. Adding a fourth permitted record would make discounted fail to compile until the new case is handled, rather than silently using a fallback. The fixed discount is clamped at zero so a large discount cannot produce a negative price.

```java
List<Integer> discountedPrices = new ArrayList<>();
for (Discount discount : List.of(new NoDiscount(), new Percent(25), new Fixed(250))) {
  discountedPrices.add(discounted(200, discount));
}
assert discountedPrices.equals(List.of(200, 150, 0));
```

**Expected:** 200, 150 and 0.

**Verify:** Control: changing `for (Discount discount : List.of(new NoDiscount(), new Percent(25), new Fixed(250))) {` to `for (Discount discount : List.of(new NoDiscount(), new Percent(26), new Fixed(250))) {` must fail the assertion on `discountedPrices.equals(List.of(200, 150, 0))`.

## Exercise 4: Validate every implementation

Task: Call regular, half and fee policy with -1.

A caller should not need to know the concrete type to predict whether a domain input is accepted. Consistent validation supports substitution.

```java
for (Pricing policy : List.of(regular, half, withFee)) {
  boolean rejected = false;
  try {
    policy.price(-1);
  } catch (IllegalArgumentException expected) {
    rejected = true;
  }
  assert rejected;
}
```

**Expected:** all throw IllegalArgumentException.

**Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected`.

## Exercise 5: Change a collaborator without changing caller code

Task: Iterate over the three policies and collect prices for 100.

The loop depends only on Pricing. Adding another valid implementation does not require a class-name conditional in the caller.

```java
List<Integer> prices = new ArrayList<>();
for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));
assert prices.equals(List.of(100, 50, 60));
```

**Expected:** results 100, 50, 60.

**Verify:** Control: changing `for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));` to `for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(101));` must fail the assertion on `prices.equals(List.of(100, 50, 60))`.

## Exercise 6: Reject an invalid wrapper

Task: Construct a fee wrapper with a negative fee or null delegate.

A composed object must establish its own valid state at construction. Deferring a null failure until the first pricing call makes the error harder to locate.

```java
boolean feeRejected = false,
  delegateRejected = false;
try {
  new Fee(regular, -1);
} catch (IllegalArgumentException expected) {
  feeRejected = true;
}
try {
  new Fee(null, 1);
} catch (NullPointerException expected) {
  delegateRejected = true;
}
assert feeRejected && delegateRejected;
```

**Expected:** negative fee IllegalArgumentException; null delegate NullPointerException.

**Verify:** Control: changing `feeRejected = true;` to `feeRejected = false;` must fail the assertion on `feeRejected && delegateRejected`.

## After comparing the answer

Add a fourth `Discount` record to your copy, list it in `permits`, and read the compiler error from `discounted` before adding the missing case.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
