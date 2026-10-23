# java-004: Methods and explicit contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-003`

## Learning objectives

Explain parameter, return value, pass by value using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Implement doubleValue(int x) and evaluate 7 and 0. The final exercise transfers the mechanism to inspect overload selection.

## Purpose and mental model

A method packages a computation behind a contract: which inputs it accepts, what it returns, what state it changes and how it reports invalid input. Parameters are local variables initialized from argument values. Java always passes values. For an object argument, the copied value is a reference, so both caller and callee can refer to the same mutable object. Reassigning the parameter changes only the local reference; mutating the referenced object can be visible to the caller. Overloading selects among methods by parameter types at compile time, while overriding is a different runtime mechanism introduced later. Small explicit contracts make methods testable without reading every caller.

## Vocabulary and concepts

**Parameter:** A local variable receiving an argument value.

**Return value:** The result passed back when a method completes.

**Pass by value:** Copying argument values into method parameters.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-004/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

A method declaration includes return type,name and parameter list. return sends one value to the caller and ends that invocation. Validate a domain precondition before calculating. Overloaded methods need different parameter signatures, not merely different return types. A defensive copy can prevent a helper from changing caller-owned mutable data. Use named exceptions when an argument violates the contract.

## Worked example / walkthrough

### Example A: Call a pure calculation

The result depends only on the argument and the method changes no external state. That makes normal and boundary cases easy to test independently.

```java
import java.util.*;

public class Main {
    static int doubleValue(int x) { return Math.multiplyExact(x, 2); }
    static int positiveArea(int width, int height) {
        if (width <= 0 || height <= 0) throw new IllegalArgumentException("positive dimensions required");
        return Math.multiplyExact(width, height);
    }
    static void reassignInt(int value) { value = 99; }
    static void append(List<Integer> values) { values.add(2); }
    static void replace(List<Integer> values) { values = new ArrayList<>(); }
    static String describe(int value) { return "int"; }
    static String describe(long value) { return "long"; }
    public static void main(String[] args) throws Exception {
        assert doubleValue(7) == 14;
        assert doubleValue(0) == 0;
    }
}

```

**Expected:** 14 and 0.

### Example B: Validate a precondition

A zero dimension is rejected because this method models a strictly positive rectangle. Another domain could allow zero, but its contract must say so.

```java
import java.util.*;

public class Main {
    static int doubleValue(int x) { return Math.multiplyExact(x, 2); }
    static int positiveArea(int width, int height) {
        if (width <= 0 || height <= 0) throw new IllegalArgumentException("positive dimensions required");
        return Math.multiplyExact(width, height);
    }
    static void reassignInt(int value) { value = 99; }
    static void append(List<Integer> values) { values.add(2); }
    static void replace(List<Integer> values) { values = new ArrayList<>(); }
    static String describe(int value) { return "int"; }
    static String describe(long value) { return "long"; }
    public static void main(String[] args) throws Exception {
        assert doubleValue(7) == 14;
        assert doubleValue(0) == 0;

        assert positiveArea(3, 4) == 12;
        boolean badArea = false;
        try { positiveArea(0, 4); } catch (IllegalArgumentException expected) { badArea = true; }
        assert badArea;
    }
}

```

**Expected:** 3by4 gives12;zero width throwsIllegalArgumentException.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Call a pure calculation.** Implement doubleValue(int x) and evaluate 7 and 0.
   **Expected:** 14 and 0.
   **Verify:** Compare your assertion values or captured diagnostic with 14 and 0.

2. **Validate a precondition.** Implement positiveArea(width,height) rejecting nonpositive dimensions.
   **Expected:** 3by4 gives12;zero width throwsIllegalArgumentException.
   **Verify:** Compare your assertion values or captured diagnostic with 3by4 gives12;zero width throwsIllegalArgumentException.

3. **Observe copied primitive values.** Passint5 to a helper that reassigns its local parameter to99.
   **Expected:** caller value remains5.
   **Verify:** Compare your assertion values or captured diagnostic with caller value remains5.

4. **Observe shared object mutation.** Pass a list containing1 to a helper that appends2.
   **Expected:** caller list becomes1,2.
   **Verify:** Compare your assertion values or captured diagnostic with caller list becomes1,2.

5. **Distinguish reference reassignment.** Pass the list to a helper that replaces only its local parameter with a new list.
   **Expected:** caller list remains1,2.
   **Verify:** Compare your assertion values or captured diagnostic with caller list remains1,2.

6. **Inspect overload selection.** Call describe withint1 andlong1L using two overloads.
   **Expected:** int and long respectively.
   **Verify:** Compare your assertion values or captured diagnostic with int and long respectively.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Parameter, Return value, Pass by value in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-004: Methods and explicit contracts.
Read courses/java/guides/java-004.md and courses/java/lessons/java-004.java. Direct prerequisites: `java-003`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
