# java-012: Generics and variance

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-011`

## Learning objectives

Explain type parameter, invariance, wildcard bound using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Sum `List.of(1, 2, 3)` and `List.of(1.5, 2.5)` through List<?extends Number>. The final exercise transfers the mechanism to observe erasure carefully.

## Purpose and mental model

Generics express type relationships so many errors can be detected before execution. List<Integer> is not a subtype of List<Number>, because a caller holdingList<Number> could insert a Double and violate the original integer list. A producer wildcard?extends Number permits reading numbers but generally forbids adding a specific numeric subtype. A consumer wildcard?superInteger permits adding integers, while reads are only known asObject. A generic method can connect input and output types through a type parameter. Java implements most generics through erasure, so runtime class identity does not distinguish ArrayList<String> from ArrayList<Integer>. Avoid raw types that bypass these checks.

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

The<T> before a method return type declares a method type parameter. List<?extends Number> can be iterated asNumber for summation. List<?superInteger> can acceptInteger values. Use<T>void copy(List<?extendsT>source,List<?superT>target) to connect a producer and consumer. Wildcards describe allowed operations through a reference; they do not freeze the underlying object or create a runtime conversion.

## Worked example / walkthrough

### Example A: Read from a producer

The method needs only to readNumber values, so an extends bound accepts both integer and double lists without permitting unsafe insertion.

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

A Number list can safely receiveInteger values. Reading through thesuper-bounded reference offers less precise type information because the actual list may contain other supertypes.

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

**Expected:** listcontains1,2.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Read from a producer.** Sum `List.of(1, 2, 3)` and `List.of(1.5, 2.5)` through List<?extends Number>.
   **Expected:** sums 6.0 and 4.0.
   **Verify:** Compare your assertion values or captured diagnostic with sums 6.0 and 4.0.

2. **Write to a consumer.** Append integers1,2 to a List<Number> through List<?superInteger>.
   **Expected:** listcontains1,2.
   **Verify:** Compare your assertion values or captured diagnostic with listcontains1,2.

3. **Connect source and destination types.** CopyList<Integer> intoList<Number> with a bounded generic method.
   **Expected:** destinationcontains3,4.
   **Verify:** Compare your assertion values or captured diagnostic with destinationcontains3,4.

4. **Preserve generic return type.** Callfirst on a String list and assign directly toString.
   **Expected:** result alpha.
   **Verify:** Compare your assertion values or captured diagnostic with result alpha.

5. **Handle an empty input contract.** Callfirst on an empty list and require a named failure.
   **Expected:** NoSuchElementException.
   **Verify:** Compare your assertion values or captured diagnostic with NoSuchElementException.

6. **Observe erasure carefully.** Compare runtime classes of ArrayList<String> and ArrayList<Integer>;explain why this does not permit unsafe assignments.
   **Expected:** runtime classes equal; compile-time contracts remain distinct.
   **Verify:** Compare your assertion values or captured diagnostic with runtime classes equal; compile-time contracts remain distinct.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Type parameter, Invariance, Wildcard bound in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-012: Generics and variance.
Read courses/java/guides/java-012.md and courses/java/lessons/java-012.java. Direct prerequisites: `java-011`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
