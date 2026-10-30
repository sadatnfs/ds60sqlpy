# java-006: Lists, sets and maps

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-005`

## Learning objectives

Explain list, set, map using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Create a mutable list red,blue,red and append green. The final exercise transfers the mechanism to respect unmodifiable fixtures.

## Purpose and mental model

Lists preserve an ordered sequence and may contain duplicates. Sets represent membership without duplicate equal elements. Maps associate keys with values. Choosing among them changes what information is retained: converting a list to a set loses multiplicity, while a map keeps only one current value per equal key. ArrayList supports indexed access and resizing, while HashMap and HashSet use hashing and equality. Their iteration order is not a sorting contract. Use an explicitly ordered collection or sort a derived list when the output order matters. Immutable factory collections reject mutation; they are useful for fixed fixtures but should not be confused with mutable working state.

## Vocabulary and concepts

**List:** An ordered collection retaining duplicates.

**Set:** A collection of unique equal elements.

**Map:** A mapping from unique keys to associated values.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-006/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

List.of creates a fixed unmodifiable list; newArrayList<>(...) creates a mutable copy. Map.merge combines an existing value with a new contribution and is convenient for counting. getOrDefault supplies a fallback without inserting it. Set.add returns whether membership changed. When comparing collection results, use equals for logical contents and sort keys explicitly before claiming a deterministic presentation order.

## Worked example / walkthrough

### Example A: Retain sequence multiplicity

A list records positions and repeated observations. Removing duplicates would change the meaning if each entry represents an event.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));
    colors.add("green");
    assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;
  }
}
```

**Expected:** size 4; red appears twice.

### Example B: Count with a map

The merge function defines how repeated keys combine. Replacingput on every iteration would retain only the final contribution1.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));
    colors.add("green");
    assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;

    Map<String, Integer> counts = new HashMap<>();
    for (String color : colors) counts.merge(color, 1, Integer::sum);
    assert counts.equals(Map.of("red", 2, "blue", 1, "green", 1));
  }
}
```

**Expected:** red2,blue1,green1.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Retain sequence multiplicity.** Create a mutable list red,blue,red and append green.
   **Expected:** size 4; red appears twice.
   **Verify:** Compare your assertion values or captured diagnostic with size 4; red appears twice.

2. **Count with a map.** Count each color withMap.merge.
   **Expected:** red2,blue1,green1.
   **Verify:** Compare your assertion values or captured diagnostic with red2,blue1,green1.

3. **Inspect set insertion.** Insertred twice into a HashSet and inspect return values.
   **Expected:** first true,second false,size1.
   **Verify:** Compare your assertion values or captured diagnostic with first true,second false,size1.

4. **Create deterministic output order.** Sort the count-map keys before presenting them.
   **Expected:** blue,green,red.
   **Verify:** Compare your assertion values or captured diagnostic with blue,green,red.

5. **Distinguish lookup from insertion.** Readmissing withgetOrDefault0 and compare map size.
   **Expected:** value0;map stillsize3.
   **Verify:** Compare your assertion values or captured diagnostic with value0;map stillsize3.

6. **Respect unmodifiable fixtures.** Try adding toList.of(1,2) and catch the specific exception.
   **Expected:** UnsupportedOperationException.
   **Verify:** Compare your assertion values or captured diagnostic with UnsupportedOperationException.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain List, Set, Map in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-006: Lists, sets and maps.
Read courses/java/guides/java-006.md and courses/java/lessons/java-006.java. Direct prerequisites: `java-005`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
