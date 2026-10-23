# java-003: Decisions, loops and invariants

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-002`

## Learning objectives

Explain short circuit, loop invariant, boundary case using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Use text null and test text!=null before calling isEmpty. The final exercise transfers the mechanism to expose a wrong boundary.

## Purpose and mental model

Control flow chooses which statements run and how often. A boolean expression has a truth value, while short-circuit operators can skip an operand entirely. That behavior lets a null check guard a later method call. A loop invariant is a statement that remains true before and after each iteration; it connects a repeated computation to its intended result. For a prefix sum, the accumulator equals the sum of elements already visited. Boundary cases such as an empty array or a limit of zero test whether the initial state and termination condition are correct. A loop that works for one nonempty example can still have an off-by-one error.

## Vocabulary and concepts

**Short circuit:** Skipping an operand once a boolean result is determined.

**Loop invariant:** A property preserved at every iteration boundary.

**Boundary case:** An input at an edge of the accepted domain.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-003/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

if selects a branch. && evaluates the right operand only when the left is true;|| evaluates it only when needed. A for loop has initialization,condition and update. Use index<length for zero-based arrays. The prefix-sum invariant starts with index0,sum0, then adds exactly the element at the current index before advancing. Break exits the loop;continue skips to the next iteration and can accidentally bypass an update in a while loop.

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

The accumulator begins at the additive identity0. Each iteration adds one new element, so no record is skipped or counted twice.

```java
import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        String text = null;
        boolean nonempty = text != null && !text.isEmpty();
        assert !nonempty;

        int[] values = {2, 4, 6}; int sum = 0;
        List<Integer> prefixes = new ArrayList<>();
        for (int i = 0; i < values.length; i++) { sum += values[i]; prefixes.add(sum); }
        assert prefixes.equals(List.of(2, 6, 12)) && sum == 12;
    }
}

```

**Expected:** prefix sums2,6,12;final12.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Guard a nullable value.** Use text null and test text!=null before calling isEmpty.
   **Expected:** condition false with no NullPointerException.
   **Verify:** Compare your assertion values or captured diagnostic with condition false with no NullPointerException.

2. **Trace a prefix sum.** Sum array2,4,6 while retaining the invariant that sum covers indices belowi.
   **Expected:** prefix sums2,6,12;final12.
   **Verify:** Compare your assertion values or captured diagnostic with prefix sums2,6,12;final12.

3. **Handle an empty loop.** Run the same sum pattern over an emptyint array.
   **Expected:** sum0 and zero iterations.
   **Verify:** Compare your assertion values or captured diagnostic with sum0 and zero iterations.

4. **Count a half-open interval.** Count integers starting0 whilei<5.
   **Expected:** visited0,1,2,3,4;count5.
   **Verify:** Compare your assertion values or captured diagnostic with visited0,1,2,3,4;count5.

5. **Stop at the first match.** Search3,8,8 for the first8 and stop immediately.
   **Expected:** index1.
   **Verify:** Compare your assertion values or captured diagnostic with index1.

6. **Expose a wrong boundary.** Compare a loop usingi<=length with the validi<length contract on a one-element array.
   **Expected:** wrong loop raises ArrayIndexOutOfBoundsException.
   **Verify:** Compare your assertion values or captured diagnostic with wrong loop raises ArrayIndexOutOfBoundsException.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Short circuit, Loop invariant, Boundary case in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-003: Decisions, loops and invariants.
Read courses/java/guides/java-003.md and courses/java/lessons/java-003.java. Direct prerequisites: `java-002`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
