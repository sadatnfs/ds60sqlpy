# java-018: Tests that detect broken behavior

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-017`

## Learning objectives

Explain test oracle, property, mutation test using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Test clamp for values -2,0,3,9 under bounds 0..5. The final exercise transfers the mechanism to test a fresh transfer property.

## Purpose and mental model

A useful test distinguishes correct behavior from a plausible mistake. Repeating the implementation formula in the expected value can reproduce the same bug on both sides. Use independent examples,boundary cases and properties that follow from the contract. A mutation test deliberately changes one behavior and checks that the tests detect it. Assertions are convenient in this course because the launcher enables-ea,but production test suites often use a dedicated framework so checks cannot be disabled accidentally. Tests should expose failures rather than catch every exception and print success.

## Vocabulary and concepts

**Test oracle:** An independent basis for deciding the expected result.

**Property:** A relation that should hold across a family of inputs.

**Mutation test:** A check that an intentionally broken variant is detected.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-018/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

A table-driven test stores inputs and expected outputs together,then runs the same checker over all cases. A property test checks a relation over several inputs,such as reversing twice restoring an array. An exception helper should verify the expected type and fail when no exception occurs. Keep test fixtures deterministic and avoid timing assumptions for concurrency. A test passing on one input says nothing about untested boundaries unless a valid general argument supports the claim.

## Worked example / walkthrough

### Example A: Use independent table cases

The expected outputs are literal contract examples. They do not call clamp or duplicate its full branching logic to generate answers.

```java
import java.util.*;

public class Main {
    static int clamp(int value,int lower,int upper){if(lower>upper)throw new IllegalArgumentException("invalid bounds");return Math.max(lower,Math.min(value,upper));}
    static int brokenClamp(int value,int lower,int upper){return value<lower?upper:Math.min(value,upper);}
    @FunctionalInterface interface Action{void run() throws Exception;}
    static void expect(Class<? extends Throwable> type,Action action){
        try{action.run();}catch(Throwable error){if(type.isInstance(error))return;throw new AssertionError("wrong exception",error);}
        throw new AssertionError("expected "+type.getSimpleName());
    }
    static int[] reverse(int[] values){int[] result=values.clone();for(int i=0,j=result.length-1;i<j;i++,j--){int temporary=result[i];result[i]=result[j];result[j]=temporary;}return result;}
    public static void main(String[] args) throws Exception {
        int[][] cases={{-2,0},{0,0},{3,3},{9,5}};
        for(int[] row:cases) assert clamp(row[0],0,5)==row[1];
    }
}

```

**Expected:** outputs 0,0,3,5.

### Example B: Check a boundary failure

An invalid interval is different from a value outside a valid interval. The test ensures the implementation rejects the contract violation.

```java
import java.util.*;

public class Main {
    static int clamp(int value,int lower,int upper){if(lower>upper)throw new IllegalArgumentException("invalid bounds");return Math.max(lower,Math.min(value,upper));}
    static int brokenClamp(int value,int lower,int upper){return value<lower?upper:Math.min(value,upper);}
    @FunctionalInterface interface Action{void run() throws Exception;}
    static void expect(Class<? extends Throwable> type,Action action){
        try{action.run();}catch(Throwable error){if(type.isInstance(error))return;throw new AssertionError("wrong exception",error);}
        throw new AssertionError("expected "+type.getSimpleName());
    }
    static int[] reverse(int[] values){int[] result=values.clone();for(int i=0,j=result.length-1;i<j;i++,j--){int temporary=result[i];result[i]=result[j];result[j]=temporary;}return result;}
    public static void main(String[] args) throws Exception {
        int[][] cases={{-2,0},{0,0},{3,3},{9,5}};
        for(int[] row:cases) assert clamp(row[0],0,5)==row[1];

        expect(IllegalArgumentException.class,() -> clamp(3,5,2));
    }
}

```

**Expected:** exception observed.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Use independent table cases.** Test clamp for values -2,0,3,9 under bounds 0..5.
   **Expected:** outputs 0,0,3,5.
   **Verify:** Compare your assertion values or captured diagnostic with outputs 0,0,3,5.

2. **Check a boundary failure.** Callclamp withlower5,upper2 and requireIllegalArgumentException.
   **Expected:** exception observed.
   **Verify:** Compare your assertion values or captured diagnostic with exception observed.

3. **Test an idempotence property.** For values-10 through10,clamping an already clamped value leaves it unchanged.
   **Expected:** all21 cases satisfyidempotence.
   **Verify:** Compare your assertion values or captured diagnostic with all21 cases satisfyidempotence.

4. **Detect a broken implementation.** Use a mutant that returns upper for values below lower and show the table rejects it.
   **Expected:** at least one mismatch.
   **Verify:** Compare your assertion values or captured diagnostic with at least one mismatch.

5. **Verify the exception checker itself.** Ask the helper to expect an exception from a successful action and catch itsAssertionError.
   **Expected:** checker fails when no exception is thrown.
   **Verify:** Compare your assertion values or captured diagnostic with checker fails when no exception is thrown.

6. **Test a fresh transfer property.** Reverse arrays oflength0,1,3 twice using a separate copy and compare with originals.
   **Expected:** all originals restored; input arrays unchanged.
   **Verify:** Compare your assertion values or captured diagnostic with all originals restored; input arrays unchanged.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Test oracle, Property, Mutation test in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-018: Tests that detect broken behavior.
Read courses/java/guides/java-018.md and courses/java/lessons/java-018.java. Direct prerequisites: `java-017`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
