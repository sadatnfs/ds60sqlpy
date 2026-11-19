# java-006: Lists, sets and maps

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-005`

## Learning objectives

Choose a List, Set or Map for a counting task and produce deterministic output from unordered collections. Along the way, explain list, set, map using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Insert red twice into a HashSet and inspect return values. The final exercise transfers the mechanism to respect unmodifiable fixtures.

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

List.of creates a fixed unmodifiable list; new ArrayList<>(...) creates a mutable copy. Map.merge combines an existing value with a new contribution and is convenient for counting. getOrDefault supplies a fallback without inserting it. Set.add returns whether membership changed. When comparing collection results, use equals for logical contents and sort keys explicitly before claiming a deterministic presentation order.

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

The merge function defines how repeated keys combine. Replacing put on every iteration would retain only the final contribution 1.

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

**Expected:** red 2, blue 1, green 1.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Retain sequence multiplicity: change one input.** Copy Example A into a scratch `Main.java` and change `List<String> colors = new ArrayList<>(List.of("red", "blue", "red"));` to `List<String> colors = new ArrayList<>(List.of("red!", "blue", "red"));`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `colors.size() == 4 && Collections.frequency(colors, "red") == 2`. Restoring the original line brings back the worked observation: size 4; red appears twice.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `colors.size() == 4 && Collections.frequency(colors, "red") == 2` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Count with a map: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `for (String color : colors) counts.merge(color, 2, Integer::sum);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))`; after it the line reads `for (String color : colors) counts.merge(color, 1, Integer::sum);` again and red 2, blue 1, green 1.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))` for this input.

3. **Inspect set insertion.** Insert red twice into a HashSet and inspect return values.
   **Expected:** first true, second false, size 1.
   **Verify:** Keep an assertion equivalent to `firstAdded && !secondAdded && unique.size() == 1`. As a control, change `boolean firstAdded = unique.add("red");` to `boolean firstAdded = unique.add("red!");`: the run must fail with an `AssertionError` from the assertion on `firstAdded && !secondAdded && unique.size() == 1`. Restore the line before continuing.

4. **Create deterministic output order.** Sort the count-map keys before presenting them.
   **Expected:** blue, green, red.
   **Verify:** Keep an assertion equivalent to `keys.equals(List.of("blue", "green", "red"))`. As a control, change `assert keys.equals(List.of("blue", "green", "red"));` to `assert keys.equals(List.of("blue!", "green", "red"));` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

5. **Distinguish lookup from insertion.** Read missing with getOrDefault 0 and compare map size.
   **Expected:** value 0; map still size 3.
   **Verify:** Keep an assertion equivalent to `absent == 0 && counts.size() == before && !counts.containsKey("missing")`. As a control, change `int absent = counts.getOrDefault("missing", 0);` to `int absent = counts.getOrDefault("missing", 1);`: the run must fail with an `AssertionError` from the assertion on `absent == 0 && counts.size() == before && !counts.containsKey("missing")`. Restore the line before continuing.

6. **Respect unmodifiable fixtures.** Try adding to List.of(1, 2) and catch the specific exception.
   **Expected:** UnsupportedOperationException.
   **Verify:** Keep an assertion equivalent to `fixed`. As a control, change `fixed = true;` to `fixed = false;`: the run must fail with an `AssertionError` from the assertion on `fixed`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: size 4; red appears twice. Then list the values read by `colors.size() == 4 && Collections.frequency(colors, "red") == 2` and trace each one from its declaration. Finally, compute the asserted value with `List<String> colors = new ArrayList<>(List.of("red!", "blue", "red"));` in place before running.
- **Exercise 2:** First restate the expected observation: red 2, blue 1, green 1. Then list the values read by `counts.equals(Map.of("red", 2, "blue", 1, "green", 1))` and trace each one from its declaration. Finally, compare `for (String color : colors) counts.merge(color, 2, Integer::sum);` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: first true, second false, size 1. Then list the values read by `firstAdded && !secondAdded && unique.size() == 1` and trace each one from its declaration. Finally, predict the effect of changing `boolean firstAdded = unique.add("red");` to `boolean firstAdded = unique.add("red!");` before running anything.
- **Exercise 4:** First restate the expected observation: blue, green, red. Then list the values read by `keys.equals(List.of("blue", "green", "red"))` and trace each one from its declaration. Finally, name one input that would make `keys.equals(List.of("blue", "green", "red"))` false.
- **Exercise 5:** First restate the expected observation: value 0; map still size 3. Then list the values read by `absent == 0 && counts.size() == before && !counts.containsKey("missing")` and trace each one from its declaration. Finally, predict the effect of changing `int absent = counts.getOrDefault("missing", 0);` to `int absent = counts.getOrDefault("missing", 1);` before running anything.
- **Exercise 6:** First restate the expected observation: unsupportedOperationException. Then list the values read by `fixed` and trace each one from its declaration. Finally, predict the effect of changing `fixed = true;` to `fixed = false;` before running anything.

## Self-check and retrieval

Close the solution and explain List, Set, Map in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-006: Lists, sets and maps.
Read courses/java/guides/java-006.md and courses/java/lessons/java-006.java. Direct prerequisites: `java-005`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
