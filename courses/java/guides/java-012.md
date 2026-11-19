# java-012: Generics and variance

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-011`

## Learning objectives

Use generic types and bounded wildcards so producers, consumers and return types stay type-safe. Along the way, explain type parameter, invariance, wildcard bound using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Copy List<Integer> into List<Number> with a bounded generic method. The final exercise transfers the mechanism to observe erasure carefully.

## Purpose and mental model

Generics express type relationships so many errors can be detected before execution. List<Integer> is not a subtype of List<Number>, because a caller holding List<Number> could insert a Double and violate the original integer list. A producer wildcard?extends Number permits reading numbers but generally forbids adding a specific numeric subtype. A consumer wildcard ? super Integer permits adding integers, while reads are only known as Object. A generic method can connect input and output types through a type parameter. Java implements most generics through erasure, so runtime class identity does not distinguish ArrayList<String> from ArrayList<Integer>. Avoid raw types that bypass these checks.

## Vocabulary and concepts

**Type parameter:** A named placeholder relating types in a declaration.

**Invariance:** Different generic arguments do not imply a subtype relationship.

**Wildcard bound:** A restriction describing safe reads or writes through a generic reference.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-012/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

The<T> before a method return type declares a method type parameter. List<?extends Number> can be iterated as Number for summation. List<? super Integer> can accept Integer values. Use <T> void copy(List<? extends T> source, List<? super T> target) to connect a producer and consumer. Wildcards describe allowed operations through a reference; they do not freeze the underlying object or create a runtime conversion.

## Worked example / walkthrough

### Example A: Read from a producer

The method needs only to read Number values, so an extends bound accepts both integer and double lists without permitting unsafe insertion.

```java
import java.util.*;

public class Main {

  static double sum(List<? extends Number> values) {
    double total = 0;
    for (Number value : values) total += value.doubleValue();
    return total;
  }

  static void addTwo(List<? super Integer> values) {
    values.add(1);
    values.add(2);
  }

  static <T> void copy(List<? extends T> source, List<? super T> target) {
    target.addAll(source);
  }

  static <T> T first(List<T> values) {
    if (values.isEmpty()) throw new NoSuchElementException("empty list");
    return values.get(0);
  }

  public static void main(String[] args) throws Exception {
    assert sum(List.of(1, 2, 3)) == 6.0;
    assert sum(List.of(1.5, 2.5)) == 4.0;
  }
}
```

**Expected:** sums 6.0 and 4.0.

### Example B: Write to a consumer

A Number list can safely receive Integer values. Reading through the super-bounded reference offers less precise type information because the actual list may contain other supertypes.

```java
import java.util.*;

public class Main {

  static double sum(List<? extends Number> values) {
    double total = 0;
    for (Number value : values) total += value.doubleValue();
    return total;
  }

  static void addTwo(List<? super Integer> values) {
    values.add(1);
    values.add(2);
  }

  static <T> void copy(List<? extends T> source, List<? super T> target) {
    target.addAll(source);
  }

  static <T> T first(List<T> values) {
    if (values.isEmpty()) throw new NoSuchElementException("empty list");
    return values.get(0);
  }

  public static void main(String[] args) throws Exception {
    assert sum(List.of(1, 2, 3)) == 6.0;
    assert sum(List.of(1.5, 2.5)) == 4.0;

    List<Number> numbers = new ArrayList<>();
    addTwo(numbers);
    assert numbers.equals(List.of(1, 2));
  }
}
```

**Expected:** list contains 1, 2.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Read from a producer: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert sum(List.of(1, 2, 3)) == 6.0;` to `assert sum(List.of(2, 2, 3)) == 6.0;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `sum(List.of(1, 2, 3)) == 6.0`. Restoring the original line brings back the worked observation: sums 6.0 and 4.0.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `sum(List.of(1, 2, 3)) == 6.0`. After restoring the line, the program completes without an `AssertionError` again.

2. **Write to a consumer: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert numbers.equals(List.of(2, 2));`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `numbers.equals(List.of(1, 2))`; after it the line reads `assert numbers.equals(List.of(1, 2));` again and list contains 1, 2.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `numbers.equals(List.of(1, 2))` accepts.

3. **Connect source and destination types.** Copy List<Integer> into List<Number> with a bounded generic method.
   **Expected:** destination contains 3, 4.
   **Verify:** Keep an assertion equivalent to `destination.equals(List.of(3, 4))`. As a control, change `copy(List.of(3, 4), destination);` to `copy(List.of(4, 4), destination);`: the run must fail with an `AssertionError` from the assertion on `destination.equals(List.of(3, 4))`. Restore the line before continuing.

4. **Preserve generic return type.** Call first on a String list and assign it directly to a String.
   **Expected:** result alpha.
   **Verify:** Keep an assertion equivalent to `value.equals("alpha")`. As a control, change `String value = first(List.of("alpha", "beta"));` to `String value = first(List.of("alpha!", "beta"));`: the run must fail with an `AssertionError` from the assertion on `value.equals("alpha")`. Restore the line before continuing.

5. **Handle an empty input contract.** Call first on an empty list and require a named failure.
   **Expected:** NoSuchElementException.
   **Verify:** Keep an assertion equivalent to `empty`. As a control, change `empty = true;` to `empty = false;`: the run must fail with an `AssertionError` from the assertion on `empty`. Restore the line before continuing.

6. **Observe erasure carefully.** Compare runtime classes of ArrayList<String> and ArrayList<Integer>;explain why this does not permit unsafe assignments.
   **Expected:** runtime classes equal; compile-time contracts remain distinct.
   **Verify:** Keep an assertion equivalent to `strings.isEmpty() && integers.isEmpty()` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: sums 6.0 and 4.0. Then list the values read by `sum(List.of(1, 2, 3)) == 6.0` and trace each one from its declaration. Finally, compute the asserted value with `assert sum(List.of(2, 2, 3)) == 6.0;` in place before running.
- **Exercise 2:** First restate the expected observation: list contains 1, 2. Then list the values read by `numbers.equals(List.of(1, 2))` and trace each one from its declaration. Finally, compare `assert numbers.equals(List.of(2, 2));` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: destination contains 3, 4. Then list the values read by `destination.equals(List.of(3, 4))` and trace each one from its declaration. Finally, predict the effect of changing `copy(List.of(3, 4), destination);` to `copy(List.of(4, 4), destination);` before running anything.
- **Exercise 4:** First restate the expected observation: result alpha. Then list the values read by `value.equals("alpha")` and trace each one from its declaration. Finally, predict the effect of changing `String value = first(List.of("alpha", "beta"));` to `String value = first(List.of("alpha!", "beta"));` before running anything.
- **Exercise 5:** First restate the expected observation: noSuchElementException. Then list the values read by `empty` and trace each one from its declaration. Finally, predict the effect of changing `empty = true;` to `empty = false;` before running anything.
- **Exercise 6:** First restate the expected observation: runtime classes equal; compile-time contracts remain distinct. Then list the values read by `strings.isEmpty() && integers.isEmpty()` and trace each one from its declaration. Finally, name one input that would make `strings.isEmpty() && integers.isEmpty()` false.

## Self-check and retrieval

Close the solution and explain Type parameter, Invariance, Wildcard bound in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-012: Generics and variance.
Read courses/java/guides/java-012.md and courses/java/lessons/java-012.java. Direct prerequisites: `java-011`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
