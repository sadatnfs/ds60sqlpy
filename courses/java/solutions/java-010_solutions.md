# java-010: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An interface describes behavior a caller can rely on without depending on one implementation. Polymorphism lets a reference typed as that interface dispatch to the concrete object method at runtime. The caller should depend on the contract rather than inspect implementation class names. Composition builds a new behavior by holding another object and delegating to it, often making policy combinations clearer than a deep inheritance tree. Substitution requires preserving accepted inputs and promised outputs; matching a method signature alone is insufficient. This lesson uses pricing functions over integer cents so rounding and external services do not obscure the design.

**Interface:** A named behavioral contract implemented by different objects.

**Dynamic dispatch:** Selecting an implementation from the runtime receiver object.

**Composition:** Building behavior by delegating to contained collaborators.

## Reading the reference

An interface declares a method; implementing classes or lambdas supply its body. A variable of interface type can hold different implementations. The receiver object selects the overridden method at runtime. A composed wrapper validates its own policy, delegates to the inner implementation and checks arithmetic withMath.addExact. Keep domain validation consistent across all implementations so callers do not need class-specific exceptions.

## Exercise 1: Call through an interface

Task: Use Pricing references to identity and half-price implementations on 100 cents.

The caller invokes the same method name while the concrete behavior differs. The shared nonnegative-input contract keeps both implementations substitutable.

```java
Pricing regular = amount -> { requireNonnegative(amount); return amount; };
Pricing half = amount -> { requireNonnegative(amount); return amount / 2; };
assert regular.price(100) == 100 && half.price(100) == 50;
```

**Expected:** 100 and 50.

**Verify:** Compare the program values or named exception with 100 and 50. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Compose a fee policy

Task: Wrap the half-price policy with a10-cent fee.

The wrapper delegates first and then adds its policy. It does not duplicate the half-price calculation, so the two concerns can change independently.

```java
Pricing withFee = new Fee(half, 10);
assert withFee.price(100) == 60;
```

**Expected:** price100 becomes60.

**Verify:** Compare the program values or named exception with price100 becomes60. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Inspect rounding semantics

Task: Apply integer half-price to101 cents under truncation-toward-zero.

Rounding is part of the pricing contract. A different business rule could require rounding up or preserving fractional units, but should not be hidden behind the same informal name.

```java
assert half.price(101) == 50;
```

**Expected:** 50 cents before fee.

**Verify:** Compare the program values or named exception with 50 cents before fee. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Validate every implementation

Task: Call regular,half and fee policy with-1.

A caller should not need to know the concrete type to predict whether a domain input is accepted. Consistent validation supports substitution.

```java
for (Pricing policy : List.of(regular, half, withFee)) {
    boolean rejected = false;
    try { policy.price(-1); } catch (IllegalArgumentException expected) { rejected = true; }
    assert rejected;
}
```

**Expected:** all throwIllegalArgumentException.

**Verify:** Compare the program values or named exception with all throwIllegalArgumentException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Change a collaborator without changing caller code

Task: Iterate over the three policies and collect prices for100.

The loop depends only on Pricing. Adding another valid implementation does not require a class-name conditional in the caller.

```java
List<Integer> prices = new ArrayList<>();
for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));
assert prices.equals(List.of(100, 50, 60));
```

**Expected:** results100,50,60.

**Verify:** Compare the program values or named exception with results100,50,60. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Reject an invalid wrapper

Task: Construct a fee wrapper with a negative fee or null delegate.

A composed object must establish its own valid state at construction. Deferring a null failure until the first pricing call makes the error harder to locate.

```java
boolean feeRejected=false, delegateRejected=false;
try { new Fee(regular,-1); } catch(IllegalArgumentException expected) { feeRejected=true; }
try { new Fee(null,1); } catch(NullPointerException expected) { delegateRejected=true; }
assert feeRejected && delegateRejected;
```

**Expected:** negative fee IllegalArgumentException;null delegate NullPointerException.

**Verify:** Compare the program values or named exception with negative fee IllegalArgumentException;null delegate NullPointerException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
