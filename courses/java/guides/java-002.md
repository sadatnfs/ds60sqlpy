# java-002: Values, numeric types and conversion

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-001`

## Learning objectives

Explain primitive, overflow, narrowing conversion using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Calculate7/2 and7/2.0. The final exercise transfers the mechanism to reject an unsupported exact division.

## Purpose and mental model

A numeric type defines both a range and a set of operations. Java int arithmetic uses fixed-width signed integers and can wrap on overflow. Integer division discards the fractional part toward zero, while a floating-point operand changes the operation to approximate real-number arithmetic. A cast can narrow a value and lose information; it does not prove the value fits. BigDecimal represents decimal arithmetic with explicit precision and rounding choices, useful when exact decimal meaning matters. Construct it from text when the source is decimal text, because constructing from a binary floating-point value preserves that prior approximation. Choose types from the domain contract rather than from the apparent size of one example.

## Vocabulary and concepts

**Primitive:** A built-in value type such asint orboolean.

**Overflow:** A result outside the range of its chosen representation.

**Narrowing conversion:** A conversion that can lose range or precision.

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-002/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

L suffix creates a long literal. A widening conversion fromint tolong preserves the integer value, but the multiplication must occur after widening if it would overflowint. Math.addExact throws on overflow rather than wrapping. BigDecimal.add returns a new value because BigDecimal is immutable. compareTo compares numeric value, while equals also considers scale, so1.0 and1.00 need a declared equality policy.

## Worked example / walkthrough

### Example A: Compare integer and decimal division

The operand types select the operation. Assigning7/2 to a double afterward would preserve the already-truncated value3.0.

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

**Expected:** integer3 and double3.5.

### Example B: Widen before multiplication

The cast affects the multiplication itself. Casting the wrappedint result tolong afterward cannot recover lost information.

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

**Expected:** 2500000000L;int product differs.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Compare integer and decimal division.** Calculate7/2 and7/2.0.
   **Expected:** integer3 and double3.5.
   **Verify:** Compare your assertion values or captured diagnostic with integer3 and double3.5.

2. **Widen before multiplication.** Compute50000 squared with an explicitly widened left operand.
   **Expected:** 2500000000L;int product differs.
   **Verify:** Compare your assertion values or captured diagnostic with 2500000000L;int product differs.

3. **Detect overflow explicitly.** Add1 to Integer.MAX_VALUE withMath.addExact.
   **Expected:** ArithmeticException.
   **Verify:** Compare your assertion values or captured diagnostic with ArithmeticException.

4. **Preserve decimal source meaning.** Add BigDecimal values constructed from strings0.10 and0.20.
   **Expected:** exact decimal0.30.
   **Verify:** Compare your assertion values or captured diagnostic with exact decimal0.30.

5. **Distinguish value from scale.** Compare BigDecimal1.0 and1.00 withcompareTo andequals.
   **Expected:** compareTo0;equalsfalse.
   **Verify:** Compare your assertion values or captured diagnostic with compareTo0;equalsfalse.

6. **Reject an unsupported exact division.** Divide decimal1 by3 without a rounding policy, then supply scale2 andHALF_UP.
   **Expected:** exact division throws;rounded result0.33.
   **Verify:** Compare your assertion values or captured diagnostic with exact division throws;rounded result0.33.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Primitive, Overflow, Narrowing conversion in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-002: Values, numeric types and conversion.
Read courses/java/guides/java-002.md and courses/java/lessons/java-002.java. Direct prerequisites: `java-001`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
