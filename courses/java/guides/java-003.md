# java-003: Decisions, loops and invariants

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-002`

## Learning objectives

Write guarded conditions, loops with explicit invariants and an exhaustive switch expression, and expose an off-by-one boundary. Along the way, explain short circuit, loop invariant, boundary case, switch expression using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Run the same sum pattern over an empty int array. The final exercise transfers the mechanism to expose a wrong boundary.

## Purpose and mental model

Control flow chooses which statements run and how often. A boolean expression has a truth value, while short-circuit operators can skip an operand entirely. That behavior lets a null check guard a later method call. A loop invariant is a statement that remains true before and after each iteration; it connects a repeated computation to its intended result. For a prefix sum, the accumulator equals the sum of elements already visited. Boundary cases such as an empty array or a limit of zero test whether the initial state and termination condition are correct. A loop that works for one nonempty example can still have an off-by-one error. A switch expression chooses one value from several labeled cases, and the compiler can check that every possible input has a case.

## Vocabulary and concepts

**Short circuit:** Skipping an operand once a boolean result is determined.

**Loop invariant:** A property preserved at every iteration boundary.

**Boundary case:** An input at an edge of the accepted domain.

**Switch expression:** A switch that evaluates to one value and must cover every possible input.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-003/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

if selects a branch. && evaluates the right operand only when the left is true; || evaluates it only when needed. A for loop has initialization, condition and update. Use index < length for zero-based arrays. The prefix-sum invariant starts with index 0, sum 0, then adds exactly the element at the current index before advancing. Break exits the loop; continue skips to the next iteration and can accidentally bypass an update in a while loop. In a switch expression, each case label is followed by -> and one result; labels never fall through, and an expression switch must cover every value of its input type.

## Worked example / walkthrough

### Example A: Guard a nullable value

The right operand is not evaluated when the left is false. Reversing the operands would attempt the method call before the guard.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    String text = null;
    boolean nonempty = text != null && !text.isEmpty();
    assert !nonempty;
  }
}
```

**Expected:** condition false with no NullPointerException.

### Example B: Trace a prefix sum

The accumulator begins at the additive identity 0. Each iteration adds one new element, so no record is skipped or counted twice.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    String text = null;
    boolean nonempty = text != null && !text.isEmpty();
    assert !nonempty;

    int[] values = { 2, 4, 6 };
    int sum = 0;
    List<Integer> prefixes = new ArrayList<>();
    for (int i = 0; i < values.length; i++) {
      sum += values[i];
      prefixes.add(sum);
    }
    assert prefixes.equals(List.of(2, 6, 12)) && sum == 12;
  }
}
```

**Expected:** prefix sums 2, 6, 12; final 12.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Guard a nullable value: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert !nonempty;` to `assert nonempty;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `!nonempty`. Restoring the original line brings back the worked observation: condition false with no NullPointerException.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `!nonempty`. After restoring the line, the program completes without an `AssertionError` again.

2. **Trace a prefix sum: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `sum -= values[i];`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `prefixes.equals(List.of(2, 6, 12)) && sum == 12`; after it the line reads `sum += values[i];` again and prefix sums 2, 6, 12; final 12.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `prefixes.equals(List.of(2, 6, 12)) && sum == 12` for this input.

3. **Handle an empty loop.** Run the same sum pattern over an empty int array.
   **Expected:** sum 0 and zero iterations.
   **Verify:** Keep an assertion equivalent to `emptySum == 0 && iterations == 0`. As a control, change `int emptySum = 0;` to `int emptySum = 1;`: the run must fail with an `AssertionError` from the assertion on `emptySum == 0 && iterations == 0`. Restore the line before continuing.

4. **Choose a value with a switch expression.** Classify Saturday and Wednesday with one exhaustive switch expression over java.time.DayOfWeek.
   **Expected:** weekend, then weekday.
   **Verify:** Keep an assertion equivalent to `kinds.equals(List.of("weekend", "weekday"))`. As a control, change `case SATURDAY, SUNDAY -> "weekend";` to `case SATURDAY, SUNDAY -> "weekend!";`: the run must fail with an `AssertionError` from the assertion on `kinds.equals(List.of("weekend", "weekday"))`. Restore the line before continuing.

5. **Stop at the first match.** Search 3, 8, 8 for the first 8 and stop immediately.
   **Expected:** index 1.
   **Verify:** Keep an assertion equivalent to `found == 1`. As a control, change `if (items[i] == 8) {` to `if (items[i] != 8) {`: the run must fail with an `AssertionError` from the assertion on `found == 1`. Restore the line before continuing.

6. **Expose a wrong boundary.** Compare a loop using i <= length with the valid i < length contract on a one-element array.
   **Expected:** wrong loop raises ArrayIndexOutOfBoundsException.
   **Verify:** Keep an assertion equivalent to `failed`. As a control, change `for (int i = 0; i <= single.length; i++) {` to `for (int i = 0; i < single.length; i++) {`: the run must fail with an `AssertionError` from the assertion on `failed`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: condition false with no NullPointerException. Then list the values read by `!nonempty` and trace each one from its declaration. Finally, compute the asserted value with `assert nonempty;` in place before running.
- **Exercise 2:** First restate the expected observation: prefix sums 2, 6, 12; final 12. Then list the values read by `prefixes.equals(List.of(2, 6, 12)) && sum == 12` and trace each one from its declaration. Finally, compare `sum -= values[i];` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: sum 0 and zero iterations. Then list the values read by `emptySum == 0 && iterations == 0` and trace each one from its declaration. Finally, predict the effect of changing `int emptySum = 0;` to `int emptySum = 1;` before running anything.
- **Exercise 4:** First restate the expected observation: weekend, then weekday. Then list the values read by `kinds.equals(List.of("weekend", "weekday"))` and trace each one from its declaration. Finally, predict the effect of changing `case SATURDAY, SUNDAY -> "weekend";` to `case SATURDAY, SUNDAY -> "weekend!";` before running anything.
- **Exercise 5:** First restate the expected observation: index 1. Then list the values read by `found == 1` and trace each one from its declaration. Finally, predict the effect of changing `if (items[i] == 8) {` to `if (items[i] != 8) {` before running anything.
- **Exercise 6:** First restate the expected observation: wrong loop raises ArrayIndexOutOfBoundsException. Then list the values read by `failed` and trace each one from its declaration. Finally, predict the effect of changing `for (int i = 0; i <= single.length; i++) {` to `for (int i = 0; i < single.length; i++) {` before running anything.

## Self-check and retrieval

Close the solution and explain Short circuit, Loop invariant, Boundary case in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-003: Decisions, loops and invariants.
Read courses/java/guides/java-003.md and courses/java/lessons/java-003.java. Direct prerequisites: `java-002`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
