# java-002: Values, numeric types and conversion

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-001`

## Learning objectives

Predict integer and decimal arithmetic, widen before overflow, and use BigDecimal value and scale deliberately. Along the way, explain primitive, overflow, narrowing conversion using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Add 1 to Integer.MAX_VALUE with Math.addExact. The final exercise transfers the mechanism to reject an unsupported exact division.

## Purpose and mental model

A numeric type defines both a range and a set of operations. Java int arithmetic uses fixed-width signed integers and can wrap on overflow. Integer division discards the fractional part toward zero, while a floating-point operand changes the operation to approximate real-number arithmetic. A cast can narrow a value and lose information; it does not prove the value fits. BigDecimal represents decimal arithmetic with explicit precision and rounding choices, useful when exact decimal meaning matters. Construct it from text when the source is decimal text, because constructing from a binary floating-point value preserves that prior approximation. Choose types from the domain contract rather than from the apparent size of one example.

## Vocabulary and concepts

**Primitive:** A built-in value type such as int or boolean.

**Overflow:** A result outside the range of its chosen representation.

**Narrowing conversion:** A conversion that can lose range or precision.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-002/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

L suffix creates a long literal. A widening conversion from int to long preserves the integer value, but the multiplication must occur after widening if it would overflow int. Math.addExact throws on overflow rather than wrapping. BigDecimal.add returns a new value because BigDecimal is immutable. compareTo compares numeric value, while equals also considers scale, so 1.0 and 1.00 need a declared equality policy.

## Worked example / walkthrough

### Example A: Compare integer and decimal division

The operand types select the operation. Assigning 7/2 to a double afterward would preserve the already-truncated value 3.0.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int whole = 7 / 2;
    double fractional = 7 / 2.0;
    assert whole == 3 && fractional == 3.5;
  }
}
```

**Expected:** integer 3 and double 3.5.

### Example B: Widen before multiplication

The cast affects the multiplication itself. Casting the wrapped int result to long afterward cannot recover lost information.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int whole = 7 / 2;
    double fractional = 7 / 2.0;
    assert whole == 3 && fractional == 3.5;

    long safe = (long) 50_000 * 50_000;
    int wrapped = 50_000 * 50_000;
    assert safe == 2_500_000_000L;
    assert wrapped != safe;
  }
}
```

**Expected:** 2500000000L; int product differs.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Compare integer and decimal division: change one input.** Copy Example A into a scratch `Main.java` and change `int whole = 7 / 2;` to `int whole = 8 / 2;`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `whole == 3 && fractional == 3.5`. Restoring the original line brings back the worked observation: integer 3 and double 3.5.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `whole == 3 && fractional == 3.5` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Widen before multiplication: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `long safe = (long) 50_000 + 50_000;`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `safe == 2_500_000_000L`; after it the line reads `long safe = (long) 50_000 * 50_000;` again and 2500000000L; int product differs.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `safe == 2_500_000_000L` for this input.

3. **Detect overflow explicitly.** Add 1 to Integer.MAX_VALUE with Math.addExact.
   **Expected:** ArithmeticException.
   **Verify:** Keep an assertion equivalent to `rejected`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

4. **Preserve decimal source meaning.** Add BigDecimal values constructed from strings 0.10 and 0.20.
   **Expected:** exact decimal 0.30.
   **Verify:** Keep an assertion equivalent to `amount.equals(new java.math.BigDecimal("0.30"))`. As a control, change `var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));` to `var amount = new java.math.BigDecimal("1.10").add(new java.math.BigDecimal("0.20"));`: the run must fail with an `AssertionError` from the assertion on `amount.equals(new java.math.BigDecimal("0.30"))`. Restore the line before continuing.

5. **Distinguish value from scale.** Compare BigDecimal 1.0 and 1.00 with compareTo and equals.
   **Expected:** compareTo 0; equals false.
   **Verify:** Keep an assertion equivalent to `one.compareTo(scaled) == 0 && !one.equals(scaled)`. As a control, change `var one = new java.math.BigDecimal("1.0");` to `var one = new java.math.BigDecimal("2.0");`: the run must fail with an `AssertionError` from the assertion on `one.compareTo(scaled) == 0 && !one.equals(scaled)`. Restore the line before continuing.

6. **Reject an unsupported exact division.** Divide decimal 1 by 3 without a rounding policy, then supply scale 2 and HALF_UP.
   **Expected:** exact division throws; rounded result 0.33.
   **Verify:** Keep an assertion equivalent to `java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"), 2, java.math.RoundingMode.HALF_UP).toPlainString().equals("0.33")`. As a control, change `2,` to `3,` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: integer 3 and double 3.5. Then list the values read by `whole == 3 && fractional == 3.5` and trace each one from its declaration. Finally, compute the asserted value with `int whole = 8 / 2;` in place before running.
- **Exercise 2:** First restate the expected observation: 2500000000L; int product differs. Then list the values read by `safe == 2_500_000_000L` and trace each one from its declaration. Finally, compare `long safe = (long) 50_000 + 50_000;` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: arithmeticException. Then list the values read by `rejected` and trace each one from its declaration. Finally, predict the effect of changing `rejected = true;` to `rejected = false;` before running anything.
- **Exercise 4:** First restate the expected observation: exact decimal 0.30. Then list the values read by `amount.equals(new java.math.BigDecimal("0.30"))` and trace each one from its declaration. Finally, predict the effect of changing `var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));` to `var amount = new java.math.BigDecimal("1.10").add(new java.math.BigDecimal("0.20"));` before running anything.
- **Exercise 5:** First restate the expected observation: compareTo 0; equals false. Then list the values read by `one.compareTo(scaled) == 0 && !one.equals(scaled)` and trace each one from its declaration. Finally, predict the effect of changing `var one = new java.math.BigDecimal("1.0");` to `var one = new java.math.BigDecimal("2.0");` before running anything.
- **Exercise 6:** First restate the expected observation: exact division throws; rounded result 0.33. Then list the values read by `java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"), 2, java.math.RoundingMode.HALF_UP).toPlainString().equals("0.33")` and trace each one from its declaration. Finally, name one input that would make `java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"), 2, java.math.RoundingMode.HALF_UP).toPlainString().equals("0.33")` false.

## Self-check and retrieval

Close the solution and explain Primitive, Overflow, Narrowing conversion in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-002: Values, numeric types and conversion.
Read courses/java/guides/java-002.md and courses/java/lessons/java-002.java. Direct prerequisites: `java-001`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
