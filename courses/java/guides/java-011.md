# java-011: Equality, hashing and ordering

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-010`

## Learning objectives

Implement consistent equals, hashCode and Comparator ordering and show the failures that inconsistent keys cause. Along the way, explain equality contract, hash code, comparator using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Insert two different people of age 20 into a TreeSet comparing age only. The final exercise transfers the mechanism to keep identity and display separate.

## Purpose and mental model

Equality, hashing and ordering are related contracts with different roles. equals determines logical sameness; equal objects must have equal hashCode values so hash collections can find them. Unequal objects may share a hash, and the collection resolves collisions through equality. A comparator defines order and can consider two unequal objects tied. Tree-based sets use comparison equality for uniqueness, so a comparator that ignores an identity field can collapse distinct records. Mutable map keys are dangerous because changing a field used in hashing can make the entry unreachable through normal lookup. Prefer immutable value keys and deterministic tie-breakers.

## Vocabulary and concepts

**Equality contract:** Rules defining when two values represent the same logical identity.

**Hash code:** A bucket-selection value consistent with equality.

**Comparator:** A rule ordering two values and identifying ties.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-011/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Records generate component-based equals and hashCode. Comparator.comparing selects a primary sort key; thenComparing supplies a tie-breaker. HashMap lookup uses hashing and equality, not toString. A key should remain stable while stored. For numeric ordering use Integer.compare rather than subtraction, because subtracting extreme values can overflow and reverse the intended sign.

## Worked example / walkthrough

### Example A: Use immutable value keys

The lookup uses logical equality rather than reference identity. A record supplies a useful default for immutable coordinate values.

```java
import java.util.*;

public class Main {

  record Point(int x, int y) {}

  record Person(String id, int age) {}

  static final class MutableKey {

    int value;

    MutableKey(int value) {
      this.value = value;
    }

    public int hashCode() {
      return value;
    }

    public boolean equals(Object other) {
      return other instanceof MutableKey key && key.value == value;
    }
  }

  public static void main(String[] args) throws Exception {
    Point a = new Point(0, 0),
      b = new Point(0, 0);
    Map<Point, String> map = new HashMap<>();
    map.put(a, "origin");
    assert a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin");
  }
}
```

**Expected:** lookup with the other returns origin; hashes equal.

### Example B: Sort with a tie-breaker

The secondary key makes equal-age ordering explicit. Without it, a presentation may depend on input order rather than the intended identity ordering.

```java
import java.util.*;

public class Main {

  record Point(int x, int y) {}

  record Person(String id, int age) {}

  static final class MutableKey {

    int value;

    MutableKey(int value) {
      this.value = value;
    }

    public int hashCode() {
      return value;
    }

    public boolean equals(Object other) {
      return other instanceof MutableKey key && key.value == value;
    }
  }

  public static void main(String[] args) throws Exception {
    Point a = new Point(0, 0),
      b = new Point(0, 0);
    Map<Point, String> map = new HashMap<>();
    map.put(a, "origin");
    assert a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin");

    List<Person> people = new ArrayList<>(
      List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))
    );
    people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::id));
    assert people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"));
  }
}
```

**Expected:** IDs c, a, b.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Use immutable value keys: change one input.** Copy Example A into a scratch `Main.java` and change `Point a = new Point(0, 0),` to `Point a = new Point(1, 0),`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")`. Restoring the original line brings back the worked observation: lookup with the other returns origin; hashes equal.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Sort with a tie-breaker: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `List.of(new Person("b", 20), new Person("a", 21), new Person("c", 18))`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))`; after it the line reads `List.of(new Person("b", 20), new Person("a", 20), new Person("c", 18))` again and IDs c, a, b.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))` for this input.

3. **Expose comparator uniqueness.** Insert two different people of age 20 into a TreeSet comparing age only.
   **Expected:** set size 1 despite unequal records.
   **Verify:** Keep an assertion equivalent to `byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20))`. As a control, change `byAge.add(new Person("a", 20));` to `byAge.add(new Person("a", 21));`: the run must fail with an `AssertionError` from the assertion on `byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20))`. Restore the line before continuing.

4. **Demonstrate mutable-key failure.** Insert a key with hash 1, mutate its hash field to 2, and attempt lookup with the same object.
   **Expected:** lookup fails in this fixture while map size remains 1.
   **Verify:** Keep an assertion equivalent to `mutable.get(key) == null && mutable.size() == 1`. As a control, change `MutableKey key = new MutableKey(1);` to `MutableKey key = new MutableKey(2);`: the run must fail with an `AssertionError` from the assertion on `mutable.get(key) == null && mutable.size() == 1`. Restore the line before continuing.

5. **Avoid comparator subtraction.** Compare Integer.MIN_VALUE and 1 using Integer.compare.
   **Expected:** negative result; subtraction overflows positive.
   **Verify:** Keep an assertion equivalent to `Integer.MIN_VALUE - 1 > 0`. As a control, change `assert Integer.MIN_VALUE - 1 > 0;` to `assert Integer.MIN_VALUE + 1 > 0;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

6. **Keep identity and display separate.** Give two Points the same formatted label but different coordinates; compare values.
   **Expected:** display labels equal; points unequal.
   **Verify:** Keep an assertion equivalent to `labelLeft.equals(labelRight) && !left.equals(right)`. As a control, change `String labelLeft = "point",` to `String labelLeft = "point!",`: the run must fail with an `AssertionError` from the assertion on `labelLeft.equals(labelRight) && !left.equals(right)`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: lookup with the other returns origin; hashes equal. Then list the values read by `a.equals(b) && a.hashCode() == b.hashCode() && map.get(b).equals("origin")` and trace each one from its declaration. Finally, compute the asserted value with `Point a = new Point(1, 0),` in place before running.
- **Exercise 2:** First restate the expected observation: IDs c, a, b. Then list the values read by `people.stream().map(Person::id).toList().equals(List.of("c", "a", "b"))` and trace each one from its declaration. Finally, compare `List.of(new Person("b", 20), new Person("a", 21), new Person("c", 18))` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: set size 1 despite unequal records. Then list the values read by `byAge.size() == 1 && !new Person("a", 20).equals(new Person("b", 20))` and trace each one from its declaration. Finally, predict the effect of changing `byAge.add(new Person("a", 20));` to `byAge.add(new Person("a", 21));` before running anything.
- **Exercise 4:** First restate the expected observation: lookup fails in this fixture while map size remains 1. Then list the values read by `mutable.get(key) == null && mutable.size() == 1` and trace each one from its declaration. Finally, predict the effect of changing `MutableKey key = new MutableKey(1);` to `MutableKey key = new MutableKey(2);` before running anything.
- **Exercise 5:** First restate the expected observation: negative result; subtraction overflows positive. Then list the values read by `Integer.MIN_VALUE - 1 > 0` and trace each one from its declaration. Finally, name one input that would make `Integer.MIN_VALUE - 1 > 0` false.
- **Exercise 6:** First restate the expected observation: display labels equal; points unequal. Then list the values read by `labelLeft.equals(labelRight) && !left.equals(right)` and trace each one from its declaration. Finally, predict the effect of changing `String labelLeft = "point",` to `String labelLeft = "point!",` before running anything.

## Self-check and retrieval

Close the solution and explain Equality contract, Hash code, Comparator in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-011: Equality, hashing and ordering.
Read courses/java/guides/java-011.md and courses/java/lessons/java-011.java. Direct prerequisites: `java-010`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
