# java-017: Optional values and validation boundaries

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-016`

## Learning objectives

Model optional results with Optional, choose eager or lazy fallbacks, and validate input at the boundary. Along the way, explain optional, domain error, lazy fallback using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Use a counter-producing fallback with orElse and orElseGet on a present value. The final exercise transfers the mechanism to expose unsafe get.

## Purpose and mental model

Optional represents the presence or absence of a value in a return contract. It can make a missing lookup explicit, but it does not replace every null or every domain error. An absent record is different from a malformed identifier, an unavailable service or a zero numeric value. Use Optional for an expected missing result and exceptions or a richer result type for invalid inputs and operational failures. A method returning Optional should not return null. Optional itself is a value container; calling get without checking simply moves an unchecked absence failure to a later line.

## Vocabulary and concepts

**Optional:** A container explicitly representing presence or absence.

**Domain error:** An input or operation violating the accepted business contract.

**Lazy fallback:** A fallback computation invoked only when the value is absent.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-017/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Optional.of rejects null, ofNullable maps null to empty, and map transforms only a present value. orElse evaluates its fallback argument eagerly, while orElseGet invokes a supplier only when needed. flatMap avoids nested Optional when the mapper already returns one. A boundary parser can validate text before performing a lookup so malformed input does not masquerade as an ordinary miss.

## Worked example / walkthrough

### Example A: Represent a missing lookup

The absence ofb is an expected lookup outcome. It is not represented as zero because zero could be a valid stored value.

```java
import java.util.*;

public class Main {

  static Optional<Integer> lookup(Map<String, Integer> data, String id) {
    if (id == null || id.isBlank()) throw new IllegalArgumentException("nonblank id required");
    return Optional.ofNullable(data.get(id));
  }

  static Optional<Integer> tryParse(String text) {
    try {
      return Optional.of(Integer.parseInt(text));
    } catch (NumberFormatException error) {
      return Optional.empty();
    }
  }

  public static void main(String[] args) throws Exception {
    Map<String, Integer> data = Map.of("a", 7);
    Optional<Integer> known = Optional.ofNullable(data.get("a"));
    Optional<Integer> missing = Optional.ofNullable(data.get("b"));
    assert known.orElseThrow() == 7 && missing.isEmpty();
  }
}
```

**Expected:** a present with 7; b empty.

### Example B: Transform only present values

The mapping function is not called for an empty Optional. This keeps the absence policy visible without repeated null conditionals.

```java
import java.util.*;

public class Main {

  static Optional<Integer> lookup(Map<String, Integer> data, String id) {
    if (id == null || id.isBlank()) throw new IllegalArgumentException("nonblank id required");
    return Optional.ofNullable(data.get(id));
  }

  static Optional<Integer> tryParse(String text) {
    try {
      return Optional.of(Integer.parseInt(text));
    } catch (NumberFormatException error) {
      return Optional.empty();
    }
  }

  public static void main(String[] args) throws Exception {
    Map<String, Integer> data = Map.of("a", 7);
    Optional<Integer> known = Optional.ofNullable(data.get("a"));
    Optional<Integer> missing = Optional.ofNullable(data.get("b"));
    assert known.orElseThrow() == 7 && missing.isEmpty();

    assert known.map(value -> value * 2).orElseThrow() == 14;
    assert missing.map(value -> value * 2).isEmpty();
  }
}
```

**Expected:** 14 and empty.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Represent a missing lookup: change one input.** Copy Example A into a scratch `Main.java` and change `Map<String, Integer> data = Map.of("a", 7);` to `Map<String, Integer> data = Map.of("a", 8);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `known.orElseThrow() == 7 && missing.isEmpty()`. Restoring the original line brings back the worked observation: a present with 7; b empty.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `known.orElseThrow() == 7 && missing.isEmpty()` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Transform only present values: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert known.map(value -> value + 2).orElseThrow() == 14;`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `known.map(value -> value * 2).orElseThrow() == 14`; after it the line reads `assert known.map(value -> value * 2).orElseThrow() == 14;` again and 14 and empty.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `known.map(value -> value * 2).orElseThrow() == 14` accepts.

3. **Compare eager and lazy fallback.** Use a counter-producing fallback with orElse and orElseGet on a present value.
   **Expected:** orElse increments; orElseGet does not.
   **Verify:** Keep an assertion equivalent to `lazy == 7 && calls.get() == 1`. As a control, change `assert lazy == 7 && calls.get() == 1;` to `assert lazy != 7 && calls.get() == 1;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

4. **Reject malformed lookup input.** Validate an empty identifier before consulting the map.
   **Expected:** IllegalArgumentException rather than empty.
   **Verify:** Keep an assertion equivalent to `invalid && lookup(data, "b").isEmpty()`. As a control, change `invalid = true;` to `invalid = false;`: the run must fail with an `AssertionError` from the assertion on `invalid && lookup(data, "b").isEmpty()`. Restore the line before continuing.

5. **Flatten a nullable transformation.** Parse an optional numeric string through a helper returning Optional<Integer>.
   **Expected:** valid 12 present; bad text empty under this declared parser policy.
   **Verify:** Keep an assertion equivalent to `Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12`. As a control, change `assert Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12;` to `assert Optional.of("13").flatMap(Main::tryParse).orElseThrow() == 12;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

6. **Expose unsafe get.** Call get on empty and catchNoSuchElementException.
   **Expected:** specific absence failure.
   **Verify:** Keep an assertion equivalent to `absent`. As a control, change `absent = true;` to `absent = false;`: the run must fail with an `AssertionError` from the assertion on `absent`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: a present with 7; b empty. Then list the values read by `known.orElseThrow() == 7 && missing.isEmpty()` and trace each one from its declaration. Finally, compute the asserted value with `Map<String, Integer> data = Map.of("a", 8);` in place before running.
- **Exercise 2:** First restate the expected observation: 14 and empty. Then list the values read by `known.map(value -> value * 2).orElseThrow() == 14` and trace each one from its declaration. Finally, compare `assert known.map(value -> value + 2).orElseThrow() == 14;` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: orElse increments; orElseGet does not. Then list the values read by `lazy == 7 && calls.get() == 1` and trace each one from its declaration. Finally, name one input that would make `lazy == 7 && calls.get() == 1` false.
- **Exercise 4:** First restate the expected observation: illegalArgumentException rather than empty. Then list the values read by `invalid && lookup(data, "b").isEmpty()` and trace each one from its declaration. Finally, predict the effect of changing `invalid = true;` to `invalid = false;` before running anything.
- **Exercise 5:** First restate the expected observation: valid 12 present; bad text empty under this declared parser policy. Then list the values read by `Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12` and trace each one from its declaration. Finally, name one input that would make `Optional.of("12").flatMap(Main::tryParse).orElseThrow() == 12` false.
- **Exercise 6:** First restate the expected observation: specific absence failure. Then list the values read by `absent` and trace each one from its declaration. Finally, predict the effect of changing `absent = true;` to `absent = false;` before running anything.

## Self-check and retrieval

Close the solution and explain Optional, Domain error, Lazy fallback in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-017: Optional values and validation boundaries.
Read courses/java/guides/java-017.md and courses/java/lessons/java-017.java. Direct prerequisites: `java-016`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
