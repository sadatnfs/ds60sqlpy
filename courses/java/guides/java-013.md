# java-013: Lambdas and functional interfaces

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-012`

## Learning objectives

Use lambdas and functional interfaces, compose functions in the intended order, and avoid mutable captured state. Along the way, explain functional interface, capture, pure transformation using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Compose add 1 and multiply 2 using andThen and compose on 3. The final exercise transfers the mechanism to use a named function for a contract.

## Purpose and mental model

A lambda supplies the behavior of a functional interface, an interface with one abstract method. It can make a small transformation or predicate easier to pass around, but it does not remove the need for a contract. Captured local variables must be final or effectively final, meaning their binding is not reassigned after initialization. Capturing a reference does not make the referenced object immutable. A lambda that appends to a shared list still has a side effect and may be unsafe in a parallel stream. Separate pure transformations from actions when possible, and use named methods when a lambda becomes difficult to explain.

## Vocabulary and concepts

**Functional interface:** An interface with one abstract method that a lambda can implement.

**Capture:** Using a surrounding local value from inside a lambda.

**Pure transformation:** A computation that returns a value without changing external state.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-013/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Use a predicate: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert positive.test(3) && !positive.test(0) && !positive.test(-1);` to `assert positive.test(3) && !positive.test(1) && !positive.test(-1);` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `positive.test(3) && !positive.test(0) && !positive.test(-1)`. Restoring the original line brings back the worked observation: true, false, false.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `positive.test(3) && !positive.test(0) && !positive.test(-1)`. After restoring the line, the program completes without an `AssertionError` again.

2. **Compose transformations: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert strip.andThen(upper).apply(" red !").equals("RED");`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `strip.andThen(upper).apply(" red ").equals("RED")`; after it the line reads `assert strip.andThen(upper).apply(" red ").equals("RED");` again and input space red space becomes RED.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `strip.andThen(upper).apply(" red ").equals("RED")` accepts.

3. **Distinguish composition order.** Compose add 1 and multiply 2 using andThen and compose on 3.
   **Expected:** andThen gives 8; compose 7.
   **Verify:** Keep an assertion equivalent to `addOne.compose(twice).apply(3) == 7`. As a control, change `assert addOne.compose(twice).apply(3) == 7;` to `assert addOne.compose(twice).apply(4) == 7;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

4. **Capture a stable threshold.** Capture local threshold 10 in a predicate and test 9, 10, 11.
   **Expected:** false, true, true under>=.
   **Verify:** Keep an assertion equivalent to `!enough.test(9) && enough.test(10) && enough.test(11)`. As a control, change `java.util.function.Predicate<Integer> enough = value -> value >= threshold;` to `java.util.function.Predicate<Integer> enough = value -> value > threshold;`: the run must fail with an `AssertionError` from the assertion on `!enough.test(9) && enough.test(10) && enough.test(11)`. Restore the line before continuing.

5. **Expose mutable captured state.** Capture a list in a Consumer and append two values.
   **Expected:** captured list becomes a, b.
   **Verify:** Keep an assertion equivalent to `captured.equals(List.of("a", "b"))`. As a control, change `append.accept("a");` to `append.accept("a!");`: the run must fail with an `AssertionError` from the assertion on `captured.equals(List.of("a", "b"))`. Restore the line before continuing.

6. **Use a named function for a contract.** Pass a method reference to a parser that rejects blank input and parses a positive integer.
   **Expected:** 7 accepted; blank rejected.
   **Verify:** Keep an assertion equivalent to `blank`. As a control, change `blank = true;` to `blank = false;`: the run must fail with an `AssertionError` from the assertion on `blank`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: true, false, false. Then list the values read by `positive.test(3) && !positive.test(0) && !positive.test(-1)` and trace each one from its declaration. Finally, compute the asserted value with `assert positive.test(3) && !positive.test(1) && !positive.test(-1);` in place before running.
- **Exercise 2:** First restate the expected observation: input space red space becomes RED. Then list the values read by `strip.andThen(upper).apply(" red ").equals("RED")` and trace each one from its declaration. Finally, compare `assert strip.andThen(upper).apply(" red !").equals("RED");` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: andThen gives 8; compose 7. Then list the values read by `addOne.compose(twice).apply(3) == 7` and trace each one from its declaration. Finally, name one input that would make `addOne.compose(twice).apply(3) == 7` false.
- **Exercise 4:** First restate the expected observation: false, true, true under>=. Then list the values read by `!enough.test(9) && enough.test(10) && enough.test(11)` and trace each one from its declaration. Finally, predict the effect of changing `java.util.function.Predicate<Integer> enough = value -> value >= threshold;` to `java.util.function.Predicate<Integer> enough = value -> value > threshold;` before running anything.
- **Exercise 5:** First restate the expected observation: captured list becomes a, b. Then list the values read by `captured.equals(List.of("a", "b"))` and trace each one from its declaration. Finally, predict the effect of changing `append.accept("a");` to `append.accept("a!");` before running anything.
- **Exercise 6:** First restate the expected observation: 7 accepted; blank rejected. Then list the values read by `blank` and trace each one from its declaration. Finally, predict the effect of changing `blank = true;` to `blank = false;` before running anything.

## Self-check and retrieval

Close the solution and explain Functional interface, Capture, Pure transformation in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
