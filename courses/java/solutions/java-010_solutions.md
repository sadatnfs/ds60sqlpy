# java-010: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An interface describes behavior a caller can rely on without depending on one implementation. Polymorphism lets a reference typed as that interface dispatch to the concrete object method at runtime. The caller should depend on the contract rather than inspect implementation class names. Composition builds a new behavior by holding another object and delegating to it, often making policy combinations clearer than a deep inheritance tree. Substitution requires preserving accepted inputs and promised outputs; matching a method signature alone is insufficient. This lesson uses pricing functions over integer cents so rounding and external services do not obscure the design.

**Interface:** A named behavioral contract implemented by different objects.

**Dynamic dispatch:** Selecting an implementation from the runtime receiver object.

**Composition:** Building behavior by delegating to contained collaborators.

**Sealed interface:** An interface that names every permitted implementation, enabling exhaustive pattern switches.

## Reading the reference

An interface declares a method; implementing classes or lambdas supply its body. A variable of interface type can hold different implementations. The receiver object selects the overridden method at runtime. A composed wrapper validates its own policy, delegates to the inner implementation and checks arithmetic with Math.addExact. Keep domain validation consistent across all implementations so callers do not need class-specific exceptions. A sealed interface lists its permitted implementations, so a switch over it can be exhaustive without a default branch, and a record pattern such as Percent(int percent) tests the type and binds the record component in one case label (Java 21).

## Exercise 1: Call through an interface: change one input

Task: Copy Example A into a scratch `Main.java` and change `return amount / 2;` to `return amount / 3;`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

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

**Expected:** The changed run fails with an `AssertionError` from the assertion on `regular.price(100) == 100 && half.price(100) == 50`. Restoring the original line brings back the worked observation: 100 and 50.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `regular.price(100) == 100 && half.price(100) == 50` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Compose a fee policy: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `Pricing withFee = new Fee(half, 11);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The wrapper delegates first and then adds its policy. It does not duplicate the half-price calculation, so the two concerns can change independently.

The unchanged code is the part that Example B adds:

```java
Pricing withFee = new Fee(half, 10);
assert withFee.price(100) == 60;
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `withFee.price(100) == 60`; after it the line reads `Pricing withFee = new Fee(half, 10);` again and price 100 becomes 60.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `withFee.price(100) == 60` for this input.

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

**Verify:** Keep an assertion equivalent to `discountedPrices.equals(List.of(200, 150, 0))`. As a control, change `for (Discount discount : List.of(new NoDiscount(), new Percent(25), new Fixed(250))) {` to `for (Discount discount : List.of(new NoDiscount(), new Percent(26), new Fixed(250))) {`: the run must fail with an `AssertionError` from the assertion on `discountedPrices.equals(List.of(200, 150, 0))`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `rejected`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

## Exercise 5: Change a collaborator without changing caller code

Task: Iterate over the three policies and collect prices for 100.

The loop depends only on Pricing. Adding another valid implementation does not require a class-name conditional in the caller.

```java
List<Integer> prices = new ArrayList<>();
for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));
assert prices.equals(List.of(100, 50, 60));
```

**Expected:** results 100, 50, 60.

**Verify:** Keep an assertion equivalent to `prices.equals(List.of(100, 50, 60))`. As a control, change `for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));` to `for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(101));`: the run must fail with an `AssertionError` from the assertion on `prices.equals(List.of(100, 50, 60))`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `feeRejected && delegateRejected`. As a control, change `feeRejected = true;` to `feeRejected = false;`: the run must fail with an `AssertionError` from the assertion on `feeRejected && delegateRejected`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
