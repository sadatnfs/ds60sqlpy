# java-004: Methods and explicit contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-003`

## Learning objectives

Write methods with explicit preconditions and predict what a call can change for primitive and object arguments. Along the way, explain parameter, return value, pass by value using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Pass int 5 to a helper that reassigns its local parameter to 99. The final exercise transfers the mechanism to inspect overload selection.

## Purpose and mental model

A method packages a computation behind a contract: which inputs it accepts, what it returns, what state it changes and how it reports invalid input. Parameters are local variables initialized from argument values. Java always passes values. For an object argument, the copied value is a reference, so both caller and callee can refer to the same mutable object. Reassigning the parameter changes only the local reference; mutating the referenced object can be visible to the caller. Overloading selects among methods by parameter types at compile time, while overriding is a different runtime mechanism introduced later. Small explicit contracts make methods testable without reading every caller.

## Vocabulary and concepts

**Parameter:** A local variable receiving an argument value.

**Return value:** The result passed back when a method completes.

**Pass by value:** Copying argument values into method parameters.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-004/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Call a pure calculation: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert doubleValue(0) == 0;` to `assert doubleValue(1) == 0;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `doubleValue(0) == 0`. Restoring the original line brings back the worked observation: 14 and 0.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `doubleValue(0) == 0`. After restoring the line, the program completes without an `AssertionError` again.

2. **Validate a precondition: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `positiveArea(1, 4);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `badArea`; after it the line reads `positiveArea(0, 4);` again and 3 by 4 gives 12; zero width throws IllegalArgumentException.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `badArea` for this input.

3. **Observe copied primitive values.** Pass int 5 to a helper that reassigns its local parameter to 99.
   **Expected:** caller value remains 5.
   **Verify:** Keep an assertion equivalent to `original == 5`. As a control, change `int original = 5;` to `int original = 6;`: the run must fail with an `AssertionError` from the assertion on `original == 5`. Restore the line before continuing.

4. **Observe shared object mutation.** Pass a list containing 1 to a helper that appends 2.
   **Expected:** caller list becomes 1, 2.
   **Verify:** Keep an assertion equivalent to `list.equals(List.of(1, 2))`. As a control, change `List<Integer> list = new ArrayList<>(List.of(1));` to `List<Integer> list = new ArrayList<>(List.of(2));`: the run must fail with an `AssertionError` from the assertion on `list.equals(List.of(1, 2))`. Restore the line before continuing.

5. **Distinguish reference reassignment.** Pass the list to a helper that replaces only its local parameter with a new list.
   **Expected:** caller list remains 1, 2.
   **Verify:** Keep an assertion equivalent to `list.equals(List.of(1, 2))`. As a control, change `assert list.equals(List.of(1, 2));` to `assert list.equals(List.of(2, 2));` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

6. **Inspect overload selection.** Call describe with int 1 and long 1L using two overloads.
   **Expected:** int and long respectively.
   **Verify:** Keep an assertion equivalent to `describe(1L).equals("long")`. As a control, change `assert describe(1L).equals("long");` to `assert describe(1L).equals("long!");` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: 14 and 0. Then list the values read by `doubleValue(0) == 0` and trace each one from its declaration. Finally, compute the asserted value with `assert doubleValue(1) == 0;` in place before running.
- **Exercise 2:** First restate the expected observation: 3 by 4 gives 12; zero width throws IllegalArgumentException. Then list the values read by `badArea` and trace each one from its declaration. Finally, compare `positiveArea(1, 4);` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: caller value remains 5. Then list the values read by `original == 5` and trace each one from its declaration. Finally, predict the effect of changing `int original = 5;` to `int original = 6;` before running anything.
- **Exercise 4:** First restate the expected observation: caller list becomes 1, 2. Then list the values read by `list.equals(List.of(1, 2))` and trace each one from its declaration. Finally, predict the effect of changing `List<Integer> list = new ArrayList<>(List.of(1));` to `List<Integer> list = new ArrayList<>(List.of(2));` before running anything.
- **Exercise 5:** First restate the expected observation: caller list remains 1, 2. Then list the values read by `list.equals(List.of(1, 2))` and trace each one from its declaration. Finally, name one input that would make `list.equals(List.of(1, 2))` false.
- **Exercise 6:** First restate the expected observation: int and long respectively. Then list the values read by `describe(1L).equals("long")` and trace each one from its declaration. Finally, name one input that would make `describe(1L).equals("long")` false.

## Self-check and retrieval

Close the solution and explain Parameter, Return value, Pass by value in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
