# java-013: Lambdas and functional interfaces

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-012`

## Learning objectives

Use lambdas and functional interfaces, compose functions in the intended order, and avoid mutable captured state.

The six exercises practice these steps:

- Use a predicate.
- Compose transformations.
- Distinguish composition order.
- Capture a stable threshold.
- Expose mutable captured state.
- Use a named function for a contract.

## Purpose and mental model

A lambda supplies the behavior of a functional interface, an interface with one abstract method. It can make a small transformation or predicate easier to pass around, but it does not remove the need for a contract. Captured local variables must be final or effectively final, meaning their binding is not reassigned after initialization. Capturing a reference does not make the referenced object immutable. A lambda that appends to a shared list still has a side effect and may be unsafe in a parallel stream. Separate pure transformations from actions when possible, and use named methods when a lambda becomes difficult to explain.

## Vocabulary and concepts

**Functional interface:** An interface with one abstract method that a lambda can implement.

**Capture:** Using a surrounding local value from inside a lambda.

**Pure transformation:** A computation that returns a value without changing external state.

## How to run this lesson

Every lambda here targets a standard interface from `java.util.function`, such as `Predicate`, `Function` or `Consumer`, and `parsePositive` is a named helper declared beside `main`.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Predicate<T> returns boolean, Function<T, R> maps a value to another value, and Consumer<T> performs an action without returning a result. Method references such as String::strip are compact forms of compatible lambdas. Function.andThen applies the first function before the second; compose reverses that composition order. A captured primitive value is read from its stable local binding, while a captured mutable object can still change internally.

## Worked example / walkthrough

### Example A: Use a predicate

The predicate has a single purpose and no side effects. Boundary zero is checked explicitly rather than inferred from a positive example.

```java
import java.util.*;

public class Main {

  static int parsePositive(String text) {
    if (text == null || text.isBlank()) throw new IllegalArgumentException(
      "positive integer text required"
    );
    int value = Integer.parseInt(text);
    if (value <= 0) throw new IllegalArgumentException("positive value required");
    return value;
  }

  public static void main(String[] args) throws Exception {
    java.util.function.Predicate<Integer> positive = value -> value > 0;
    assert positive.test(3) && !positive.test(0) && !positive.test(-1);
  }
}
```

**Expected:** true, false, false.

### Example B: Compose transformations

The composition order is explicit. For transformations that do not commute, reversing the order changes the result.

```java
import java.util.*;

public class Main {

  static int parsePositive(String text) {
    if (text == null || text.isBlank()) throw new IllegalArgumentException(
      "positive integer text required"
    );
    int value = Integer.parseInt(text);
    if (value <= 0) throw new IllegalArgumentException("positive value required");
    return value;
  }

  public static void main(String[] args) throws Exception {
    java.util.function.Predicate<Integer> positive = value -> value > 0;
    assert positive.test(3) && !positive.test(0) && !positive.test(-1);

    java.util.function.Function<String, String> strip = String::strip;
    java.util.function.Function<String, String> upper = value -> value.toUpperCase(Locale.ROOT);
    assert strip.andThen(upper).apply(" red ").equals("RED");
  }
}
```

**Expected:** input space red space becomes RED.

## Prediction before your attempt

Before running Example A, write `positive.test` for 3, 0 and -1 and say why 0 is the case worth checking. For Example B, predict the result of stripping and then uppercasing " red ", and what reversing the order would change for this input (nothing here, but `andThen` and `compose` differ in general). Before Exercise 3, compute `addOne.andThen(twice).apply(3)` and `addOne.compose(twice).apply(3)` by hand.

## Exercises

1. **Use a predicate: predict an edited check.** Change Example A's assertion to `assert positive.test(3) && !positive.test(1) && !positive.test(-1);`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `positive.test(3) && !positive.test(0) && !positive.test(-1)`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `positive.test(3) && !positive.test(0) && !positive.test(-1)`.

2. **Compose transformations: diagnose an edited check.** Example B's new assertion was edited to `assert strip.andThen(upper).apply(" red !").equals("RED");`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `strip.andThen(upper).apply(" red ").equals("RED")`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `strip.andThen(upper).apply(" red ").equals("RED")` accepts.

3. **Distinguish composition order.** Compose add 1 and multiply 2 using andThen and compose on 3.
   **Expected:** andThen gives 8; compose 7.
   **Verify:** Control: changing `assert addOne.compose(twice).apply(3) == 7;` to `assert addOne.compose(twice).apply(4) == 7;` inside the assertion must make it fail.

4. **Capture a stable threshold.** Capture local threshold 10 in a predicate and test 9, 10, 11.
   **Expected:** false, true, true under>=.
   **Verify:** Control: changing `java.util.function.Predicate<Integer> enough = value -> value >= threshold;` to `java.util.function.Predicate<Integer> enough = value -> value > threshold;` must fail the assertion on `!enough.test(9) && enough.test(10) && enough.test(11)`.

5. **Expose mutable captured state.** Capture a list in a Consumer and append two values.
   **Expected:** captured list becomes a, b.
   **Verify:** Control: changing `append.accept("a");` to `append.accept("a!");` must fail the assertion on `captured.equals(List.of("a", "b"))`.

6. **Use a named function for a contract.** Pass a method reference to a parser that rejects blank input and parses a positive integer.
   **Expected:** 7 accepted; blank rejected.
   **Verify:** Control: changing `blank = true;` to `blank = false;` must fail the assertion on `blank`.

## Common pitfalls and diagnosis

Reading `f.compose(g)` as "f then g" is the classic error; it applies `g` first. Capture rules also confuse people: a lambda may use a local variable only if it is never reassigned, so `threshold++` after the lambda is a compile error, while adding to a captured list compiles and mutates shared state. That makes a `Consumer` that appends to a list unsafe in a parallel stream. Finally, a long lambda that hides validation is harder to test than a named method reference such as `Main::parsePositive`.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First evaluate `positive.test(1)` from the edited assertion. Then apply the `!` in front of it and see what the middle conjunct becomes. Finally, explain why the original assertion tested 0 rather than another positive number.
- **Exercise 2:** First apply `strip` and then `upper` to the edited input " red !". Then compare the result with "RED". Finally, note that the composition order is unchanged, so the input is what breaks the check.
- **Exercise 3:** First compute `addOne.andThen(twice).apply(3)` by applying `addOne` first. Then compute `addOne.compose(twice).apply(3)` by applying `twice` first. Finally, assert 8 and 7 and explain why the two results differ.
- **Exercise 4:** First store 10 in a local variable that is never reassigned and capture it in a `Predicate` that uses `>=`. Then test 9, 10 and 11. Finally, explain why the boundary value 10 decides between `>` and `>=`.
- **Exercise 5:** First create an `ArrayList` and a `Consumer<String>` that appends to it. Then accept "a" and then "b". Finally, compare the list with a, b and explain why the lambda still has a side effect even though its captured reference never changes.
- **Exercise 6:** First pass `Main::parsePositive` where a `Function<String, Integer>` is expected and apply it to "7". Then apply it to a blank string inside a `try` block and catch `IllegalArgumentException`. Finally, explain why the method reference keeps the validation rules in one named, testable place.

## Self-check and retrieval

From memory, define a functional interface and name its abstract method for `Predicate`, `Function` and `Consumer`. Explain the order in which `andThen` and `compose` apply their functions, what effectively final means, and why capturing a list does not make the list immutable.

## Next step

Continue with `java-014`: Streams and collectors. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-013: Lambdas and functional interfaces.
Read courses/java/guides/java-013.md and courses/java/lessons/java-013.java. Direct prerequisites: `java-012`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
