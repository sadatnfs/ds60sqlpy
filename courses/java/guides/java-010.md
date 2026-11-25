# java-010: Interfaces and polymorphism

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-009`

## Learning objectives

Program to an interface, compose behavior by delegation, and switch exhaustively over a sealed type with record patterns.

The six exercises practice these steps:

- Call through an interface.
- Compose a fee policy.
- Switch exhaustively over a sealed type.
- Validate every implementation.
- Change a collaborator without changing caller code.
- Reject an invalid wrapper.

## Purpose and mental model

An interface describes behavior a caller can rely on without depending on one implementation. Polymorphism lets a reference typed as that interface dispatch to the concrete object method at runtime. The caller should depend on the contract rather than inspect implementation class names. Composition builds a new behavior by holding another object and delegating to it, often making policy combinations clearer than a deep inheritance tree. Substitution requires preserving accepted inputs and promised outputs; matching a method signature alone is insufficient. This lesson uses pricing functions over integer cents so rounding and external services do not obscure the design.

## Vocabulary and concepts

**Interface:** A named behavioral contract implemented by different objects.

**Dynamic dispatch:** Selecting an implementation from the runtime receiver object.

**Composition:** Building behavior by delegating to contained collaborators.

**Sealed interface:** An interface that names every permitted implementation, enabling exhaustive pattern switches.

## How to run this lesson

`Pricing`, the `Fee` record and the sealed `Discount` hierarchy are declared inside `Main`; Exercise 3 relies on Java 21 record patterns in `switch`, so an older JDK rejects it at compile time.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

An interface declares a method; implementing classes or lambdas supply its body. A variable of interface type can hold different implementations. The receiver object selects the overridden method at runtime. A composed wrapper validates its own policy, delegates to the inner implementation and checks arithmetic with Math.addExact. Keep domain validation consistent across all implementations so callers do not need class-specific exceptions. A sealed interface lists its permitted implementations, so a switch over it can be exhaustive without a default branch, and a record pattern such as Percent(int percent) tests the type and binds the record component in one case label (Java 21).

## Worked example / walkthrough

### Example A: Call through an interface

The caller invokes the same method name while the concrete behavior differs. The shared nonnegative-input contract keeps both implementations substitutable.

```java
import java.util.*;

public class Main {

  interface Pricing {
    int price(int amount);
  }

  static void requireNonnegative(int amount) {
    if (amount < 0) throw new IllegalArgumentException("negative amount");
  }

  record Fee(Pricing delegate, int cents) implements Pricing {
    Fee {
      Objects.requireNonNull(delegate);
      requireNonnegative(cents);
    }

    public int price(int amount) {
      return Math.addExact(delegate.price(amount), cents);
    }
  }

  sealed interface Discount permits NoDiscount, Percent, Fixed {}

  record NoDiscount() implements Discount {}

  record Percent(int percent) implements Discount {}

  record Fixed(int cents) implements Discount {}

  static int discounted(int price, Discount discount) {
    return switch (discount) {
      case NoDiscount() -> price;
      case Percent(int percent) -> (price * (100 - percent)) / 100;
      case Fixed(int cents) -> Math.max(0, price - cents);
    };
  }

  public static void main(String[] args) throws Exception {
    Pricing regular = amount -> {
      requireNonnegative(amount);
      return amount;
    };
    Pricing half = amount -> {
      requireNonnegative(amount);
      return amount / 2;
    };
    assert regular.price(100) == 100 && half.price(100) == 50;
  }
}
```

**Expected:** 100 and 50.

### Example B: Compose a fee policy

The wrapper delegates first and then adds its policy. It does not duplicate the half-price calculation, so the two concerns can change independently.

```java
import java.util.*;

public class Main {

  interface Pricing {
    int price(int amount);
  }

  static void requireNonnegative(int amount) {
    if (amount < 0) throw new IllegalArgumentException("negative amount");
  }

  record Fee(Pricing delegate, int cents) implements Pricing {
    Fee {
      Objects.requireNonNull(delegate);
      requireNonnegative(cents);
    }

    public int price(int amount) {
      return Math.addExact(delegate.price(amount), cents);
    }
  }

  sealed interface Discount permits NoDiscount, Percent, Fixed {}

  record NoDiscount() implements Discount {}

  record Percent(int percent) implements Discount {}

  record Fixed(int cents) implements Discount {}

  static int discounted(int price, Discount discount) {
    return switch (discount) {
      case NoDiscount() -> price;
      case Percent(int percent) -> (price * (100 - percent)) / 100;
      case Fixed(int cents) -> Math.max(0, price - cents);
    };
  }

  public static void main(String[] args) throws Exception {
    Pricing regular = amount -> {
      requireNonnegative(amount);
      return amount;
    };
    Pricing half = amount -> {
      requireNonnegative(amount);
      return amount / 2;
    };
    assert regular.price(100) == 100 && half.price(100) == 50;

    Pricing withFee = new Fee(half, 10);
    assert withFee.price(100) == 60;
  }
}
```

**Expected:** price 100 becomes 60.

## Prediction before your attempt

Before running Example A, write `regular.price(100)` and `half.price(100)` and say which class the JVM chooses for each call, given that both variables have the type `Pricing`. For Example B, predict the price of 100 after the half-price policy is wrapped in a 10-cent `Fee`, and whether the fee is added before or after halving (it is after: 50 plus 10). Before Exercise 3, predict what `javac` does if a fourth record is added to `permits` but not to the `switch`.

## Exercises

1. **Call through an interface: change one input.** Change `return amount / 2;` to `return amount / 3;` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `regular.price(100) == 100 && half.price(100) == 50`.
   **Verify:** Name the value that makes `regular.price(100) == 100 && half.price(100) == 50` false, then restore the line.

2. **Compose a fee policy: debug a regression.** A regression in Example B's new code makes one line read `Pricing withFee = new Fee(half, 11);`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `withFee.price(100) == 60`; the repaired line reads `Pricing withFee = new Fee(half, 10);`.
   **Verify:** Explain how the changed token alters the value that `withFee.price(100) == 60` tests.

3. **Switch exhaustively over a sealed type.** Price 200 cents with NoDiscount, Percent(25) and Fixed(250) through one pattern-matching switch over the sealed Discount interface.
   **Expected:** 200, 150 and 0.
   **Verify:** Control: changing `for (Discount discount : List.of(new NoDiscount(), new Percent(25), new Fixed(250))) {` to `for (Discount discount : List.of(new NoDiscount(), new Percent(26), new Fixed(250))) {` must fail the assertion on `discountedPrices.equals(List.of(200, 150, 0))`.

4. **Validate every implementation.** Call regular, half and fee policy with -1.
   **Expected:** all throw IllegalArgumentException.
   **Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected`.

5. **Change a collaborator without changing caller code.** Iterate over the three policies and collect prices for 100.
   **Expected:** results 100, 50, 60.
   **Verify:** Control: changing `for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));` to `for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(101));` must fail the assertion on `prices.equals(List.of(100, 50, 60))`.

6. **Reject an invalid wrapper.** Construct a fee wrapper with a negative fee or null delegate.
   **Expected:** negative fee IllegalArgumentException; null delegate NullPointerException.
   **Verify:** Control: changing `feeRejected = true;` to `feeRejected = false;` must fail the assertion on `feeRejected && delegateRejected`.

## Common pitfalls and diagnosis

A common smell is a caller that tests `instanceof` or class names to decide how to price; that breaks every time an implementation is added, while a call through `Pricing` does not. Substitution also needs the same contract, not just the same signature: if one implementation accepted -1 while another threw, callers could not rely on the interface. For sealed types, a `default` branch in the `switch` hides a missing case that the compiler would otherwise report.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First compute `half.price(100)` with the edited divisor, using integer division. Then compare that value with the 50 the assertion expects, while `regular` still returns 100. Finally, explain why a change in one implementation leaves the calling code untouched.
- **Exercise 2:** First evaluate the wrapped policy for 100 in order: the half-price delegate returns 50 and the fee is added afterward. Then compare 50 plus 11 with the 60 in the assertion. Finally, explain why the defect lives in the fee amount and not in the delegate.
- **Exercise 3:** First compute each discount for 200 by hand: no discount, 25 percent, and a fixed 250 that is clamped at zero. Then loop over the three records and add `discounted(200, discount)` to a list. Finally, compare the list with 200, 150 and 0, and say which record pattern bound each component.
- **Exercise 4:** First call `price(-1)` on each of the three policies inside separate `try` blocks. Then catch `IllegalArgumentException` from each and record the rejections. Finally, explain why `Fee` must also reject -1 before it delegates, so callers see one contract.
- **Exercise 5:** First put `regular`, `half` and `withFee` into one `List<Pricing>`. Then loop and add each `price(100)` to a result list without testing any class. Finally, compare the list with 100, 50 and 60, and explain why a new policy needs no change to this loop.
- **Exercise 6:** First construct a `Fee` with -1 cents inside a `try` block and catch `IllegalArgumentException`. Then construct one with a null delegate and catch `NullPointerException`. Finally, explain why the compact constructor reports both problems before the first `price` call could.

## Self-check and retrieval

Without the guide, explain the difference between the declared type of a variable and the class of the object it refers to, and which one selects `price` at run time. Describe how `Fee` composes another policy without repeating its arithmetic, and why the `discounted` switch needs no `default` branch.

## Next step

Continue with `java-011`: Equality, hashing and ordering. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-010: Interfaces and polymorphism.
Read courses/java/guides/java-010.md and courses/java/lessons/java-010.java. Direct prerequisites: `java-009`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
