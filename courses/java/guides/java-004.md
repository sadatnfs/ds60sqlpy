# java-004: Methods and explicit contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-003`

## Learning objectives

Write methods with explicit preconditions and predict what a call can change for primitive and object arguments.

The six exercises practice these steps:

- Call a pure calculation.
- Validate a precondition.
- Observe copied primitive values.
- Observe shared object mutation.
- Distinguish reference reassignment.
- Inspect overload selection.

## Purpose and mental model

A method packages a computation behind a contract: which inputs it accepts, what it returns, what state it changes and how it reports invalid input. Parameters are local variables initialized from argument values. Java always passes values. For an object argument, the copied value is a reference, so both caller and callee can refer to the same mutable object. Reassigning the parameter changes only the local reference; mutating the referenced object can be visible to the caller. Overloading selects among methods by parameter types at compile time, while overriding is a different runtime mechanism introduced later. Small explicit contracts make methods testable without reading every caller.

## Vocabulary and concepts

**Parameter:** A local variable receiving an argument value.

**Return value:** The result passed back when a method completes.

**Pass by value:** Copying argument values into method parameters.

## How to run this lesson

All helpers in this lesson are `static` methods declared beside `main`, so each example stays one file; Example B calls a method that throws on purpose, and its check catches the exception.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

A method declaration includes return type, name and parameter list. return sends one value to the caller and ends that invocation. Validate a domain precondition before calculating. Overloaded methods need different parameter signatures, not merely different return types. A defensive copy can prevent a helper from changing caller-owned mutable data. Use named exceptions when an argument violates the contract.

## Worked example / walkthrough

### Example A: Call a pure calculation

The result depends only on the argument and the method changes no external state. That makes normal and boundary cases easy to test independently.

```java
import java.util.*;

public class Main {

  static int doubleValue(int x) {
    return Math.multiplyExact(x, 2);
  }

  static int positiveArea(int width, int height) {
    if (width <= 0 || height <= 0) throw new IllegalArgumentException(
      "positive dimensions required"
    );
    return Math.multiplyExact(width, height);
  }

  static void reassignInt(int value) {
    value = 99;
  }

  static void append(List<Integer> values) {
    values.add(2);
  }

  static void replace(List<Integer> values) {
    values = new ArrayList<>();
  }

  static String describe(int value) {
    return "int";
  }

  static String describe(long value) {
    return "long";
  }

  public static void main(String[] args) throws Exception {
    assert doubleValue(7) == 14;
    assert doubleValue(0) == 0;
  }
}
```

**Expected:** 14 and 0.

### Example B: Validate a precondition

A zero dimension is rejected because this method models a strictly positive rectangle. Another domain could allow zero, but its contract must say so.

```java
import java.util.*;

public class Main {

  static int doubleValue(int x) {
    return Math.multiplyExact(x, 2);
  }

  static int positiveArea(int width, int height) {
    if (width <= 0 || height <= 0) throw new IllegalArgumentException(
      "positive dimensions required"
    );
    return Math.multiplyExact(width, height);
  }

  static void reassignInt(int value) {
    value = 99;
  }

  static void append(List<Integer> values) {
    values.add(2);
  }

  static void replace(List<Integer> values) {
    values = new ArrayList<>();
  }

  static String describe(int value) {
    return "int";
  }

  static String describe(long value) {
    return "long";
  }

  public static void main(String[] args) throws Exception {
    assert doubleValue(7) == 14;
    assert doubleValue(0) == 0;

    assert positiveArea(3, 4) == 12;
    boolean badArea = false;
    try {
      positiveArea(0, 4);
    } catch (IllegalArgumentException expected) {
      badArea = true;
    }
    assert badArea;
  }
}
```

**Expected:** 3 by 4 gives 12; zero width throws IllegalArgumentException.

## Prediction before your attempt

Before running Example A, evaluate `doubleValue(7)` and `doubleValue(0)` and decide whether calling the method twice could ever give different results. For Example B, predict what `positiveArea(3, 4)` returns and which call throws. Before Exercises 3 to 5, predict for each helper whether the caller can see its change: reassigning an `int` parameter, appending to a list argument, and replacing the list parameter with a new list.

## Exercises

1. **Call a pure calculation: predict an edited check.** Change Example A's assertion to `assert doubleValue(1) == 0;`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `doubleValue(0) == 0`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `doubleValue(0) == 0`.

2. **Validate a precondition: debug a regression.** A regression in Example B's new code makes one line read `positiveArea(1, 4);`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `badArea`; the repaired line reads `positiveArea(0, 4);`.
   **Verify:** Explain how the changed token alters the value that `badArea` tests.

3. **Observe copied primitive values.** Pass int 5 to a helper that reassigns its local parameter to 99.
   **Expected:** caller value remains 5.
   **Verify:** Control: changing `int original = 5;` to `int original = 6;` must fail the assertion on `original == 5`.

4. **Observe shared object mutation.** Pass a list containing 1 to a helper that appends 2.
   **Expected:** caller list becomes 1, 2.
   **Verify:** Control: changing `List<Integer> list = new ArrayList<>(List.of(1));` to `List<Integer> list = new ArrayList<>(List.of(2));` must fail the assertion on `list.equals(List.of(1, 2))`.

5. **Distinguish reference reassignment.** Pass the list to a helper that replaces only its local parameter with a new list.
   **Expected:** caller list remains 1, 2.
   **Verify:** Control: changing `assert list.equals(List.of(1, 2));` to `assert list.equals(List.of(2, 2));` inside the assertion must make it fail.

6. **Inspect overload selection.** Call describe with int 1 and long 1L using two overloads.
   **Expected:** int and long respectively.
   **Verify:** Control: changing `assert describe(1L).equals("long");` to `assert describe(1L).equals("long!");` inside the assertion must make it fail.

## Common pitfalls and diagnosis

The misconception this lesson targets is "Java passes objects by reference". Java passes every argument by value; for an object, the value is a reference. So `list.add(2)` inside a helper is visible to the caller, while `list = new ArrayList<>()` inside the helper is not. A related mistake is returning a sentinel such as -1 for a bad dimension instead of throwing `IllegalArgumentException`, which lets an invalid area flow into later arithmetic.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First evaluate `doubleValue(1)`, the call the edited assertion now makes. Then compare that result with the 0 the assertion still expects. Finally, decide whether the method or the edited claim is wrong, and restore the boundary case `doubleValue(0)`.
- **Exercise 2:** First notice that `positiveArea(1, 4)` satisfies the precondition, so no exception is thrown. Then follow what happens to `badArea` when the `catch` block never runs. Finally, explain why the rejection test must use a zero dimension to reach the failure path.
- **Exercise 3:** First write a helper that takes an `int` parameter and assigns 99 to it. Then call it with a caller variable holding 5 and compare the caller's value afterward. Finally, explain why the assignment changed only the helper's own copy.
- **Exercise 4:** First pass a mutable `ArrayList` holding 1 to a helper that calls `add(2)`. Then compare the caller's list with `List.of(1, 2)`. Finally, explain which value the call copied and which object both variables now share.
- **Exercise 5:** First reuse the list from Exercise 4, which holds 1 and 2. Then write a helper that assigns a new list to its parameter and changes only that new list. Finally, assert that the caller's list still equals `List.of(1, 2)` and explain why no caller variable was reassigned.
- **Exercise 6:** First declare `describe(int)` and `describe(long)` returning "int" and "long". Then call it with the literals `1` and `1L` and keep both strings. Finally, explain that the choice was fixed at compile time from the argument types, before the program ran.

## Self-check and retrieval

Explain without notes why the caller's `int` stays 5 after the helper assigns 99, why the caller's list gains 2 after `add`, and why it does not become empty when the helper reassigns its parameter. Then say how the compiler chooses between `describe(int)` and `describe(long)` for the literals `1` and `1L`.

## Next step

Continue with `java-005`: Arrays, strings and Unicode. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-004: Methods and explicit contracts.
Read courses/java/guides/java-004.md and courses/java/lessons/java-004.java. Direct prerequisites: `java-003`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
