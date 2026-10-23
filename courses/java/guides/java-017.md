# java-017: Optional values and validation boundaries

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-016`

## Learning objectives

Explain optional, domain error, lazy fallback using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Look up known a and unknown b in a fixed map through Optional. The final exercise transfers the mechanism to expose unsafeget.

## Purpose and mental model

Optional represents the presence or absence of a value in a return contract. It can make a missing lookup explicit,but it does not replace every null or every domain error. An absent record is different from a malformed identifier,an unavailable service or a zero numeric value. UseOptional for an expected missing result and exceptions or a richer result type for invalid inputs and operational failures. A method returningOptional should not return null. Optional itself is a value container; callingget without checking simply moves an unchecked absence failure to a later line.

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

Optional.of rejects null,ofNullable maps null to empty,and map transforms only a present value. orElse evaluates its fallback argument eagerly,whileorElseGet invokes a supplier only when needed. flatMap avoids nestedOptional when the mapper already returns one. A boundary parser can validate text before performing a lookup so malformed input does not masquerade as an ordinary miss.

## Worked example / walkthrough

### Example A: Represent a missing lookup

The absence ofb is an expected lookup outcome. It is not represented as zero because zero could be a valid stored value.

```java
import java.util.*;

public class Main {
    static Optional<Integer> lookup(Map<String,Integer> data,String id){if(id==null||id.isBlank())throw new IllegalArgumentException("nonblank id required");return Optional.ofNullable(data.get(id));}
    static Optional<Integer> tryParse(String text){try{return Optional.of(Integer.parseInt(text));}catch(NumberFormatException error){return Optional.empty();}}
    public static void main(String[] args) throws Exception {
        Map<String,Integer> data=Map.of("a",7);
        Optional<Integer> known=Optional.ofNullable(data.get("a")); Optional<Integer> missing=Optional.ofNullable(data.get("b"));
        assert known.orElseThrow()==7 && missing.isEmpty();
    }
}

```

**Expected:** a present with 7; b empty.

### Example B: Transform only present values

The mapping function is not called for an emptyOptional. This keeps the absence policy visible without repeated null conditionals.

```java
import java.util.*;

public class Main {
    static Optional<Integer> lookup(Map<String,Integer> data,String id){if(id==null||id.isBlank())throw new IllegalArgumentException("nonblank id required");return Optional.ofNullable(data.get(id));}
    static Optional<Integer> tryParse(String text){try{return Optional.of(Integer.parseInt(text));}catch(NumberFormatException error){return Optional.empty();}}
    public static void main(String[] args) throws Exception {
        Map<String,Integer> data=Map.of("a",7);
        Optional<Integer> known=Optional.ofNullable(data.get("a")); Optional<Integer> missing=Optional.ofNullable(data.get("b"));
        assert known.orElseThrow()==7 && missing.isEmpty();

        assert known.map(value -> value*2).orElseThrow()==14;
        assert missing.map(value -> value*2).isEmpty();
    }
}

```

**Expected:** 14 and empty.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Represent a missing lookup.** Look up known a and unknown b in a fixed map through Optional.
   **Expected:** a present with 7; b empty.
   **Verify:** Compare your assertion values or captured diagnostic with a present with 7; b empty.

2. **Transform only present values.** Map the known value to double and apply the same mapping to empty.
   **Expected:** 14 and empty.
   **Verify:** Compare your assertion values or captured diagnostic with 14 and empty.

3. **Compare eager and lazy fallback.** Use a counter-producing fallback withorElse andorElseGet on a present value.
   **Expected:** orElse increments;orElseGet does not.
   **Verify:** Compare your assertion values or captured diagnostic with orElse increments;orElseGet does not.

4. **Reject malformed lookup input.** Validate an empty identifier before consulting the map.
   **Expected:** IllegalArgumentException rather than empty.
   **Verify:** Compare your assertion values or captured diagnostic with IllegalArgumentException rather than empty.

5. **Flatten a nullable transformation.** Parse an optional numeric string through a helper returningOptional<Integer>.
   **Expected:** valid12 present;badtext empty under this declared parser policy.
   **Verify:** Compare your assertion values or captured diagnostic with valid12 present;badtext empty under this declared parser policy.

6. **Expose unsafeget.** Callget on empty and catchNoSuchElementException.
   **Expected:** specific absence failure.
   **Verify:** Compare your assertion values or captured diagnostic with specific absence failure.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Optional, Domain error, Lazy fallback in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-017: Optional values and validation boundaries.
Read courses/java/guides/java-017.md and courses/java/lessons/java-017.java. Direct prerequisites: `java-016`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
