# java-008: Constructors, records and invariants

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-007`

## Learning objectives

Explain record, compact constructor, defensive copy using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Create an Order with ID " A " and item x. The final exercise transfers the mechanism to reject null collection members.

## Purpose and mental model

A record is a concise carrier for a fixed set of components, with generated accessors, equality, hashing and a descriptive string. It is shallowly immutable: the component references cannot be reassigned, but a mutable object referenced by a component can still change. A compact constructor can validate and normalize incoming component values before the record is created. Defensive copying is necessary when the record owns a collection. Constructor validation should reject invalid domain state consistently, so every successfully created value can be trusted to satisfy its invariant. Records are appropriate for value-like data, not a substitute for every stateful object.

## Vocabulary and concepts

**Record:** A value-oriented class with declared components and generated methods.

**Compact constructor:** Validation and normalization code for record components.

**Defensive copy:** An owned copy preventing external mutation through shared storage.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-008/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

record Order(String id,List<String>items) declares component accessorsid() and items(). In a compact constructor, assign a normalized parameter such asid=id.strip(); implicit field assignment occurs afterward. List.copyOf makes an unmodifiable shallow copy, preventing later structural changes through the caller list. It also rejects null elements, which becomes part of the chosen contract.

## Worked example / walkthrough

### Example A: Normalize at construction

Normalization occurs once at the boundary. Every later accessor sees the canonical ID, rather than requiring callers to remember to trim it.

```java
import java.util.*;

public class Main {
    record Order(String id, List<String> items) {
        Order {
            Objects.requireNonNull(id, "id"); id = id.strip();
            if (id.isEmpty()) throw new IllegalArgumentException("blank id");
            items = List.copyOf(items);
        }
    }
    public static void main(String[] args) throws Exception {
        Order order = new Order(" A ", List.of("x"));
        assert order.id().equals("A") && order.items().equals(List.of("x"));
    }
}

```

**Expected:** ID A and items[x].

### Example B: Copy caller-owned collections

Without the copy, a caller could change the record observed value after construction. Final component references alone would not prevent that mutation.

```java
import java.util.*;

public class Main {
    record Order(String id, List<String> items) {
        Order {
            Objects.requireNonNull(id, "id"); id = id.strip();
            if (id.isEmpty()) throw new IllegalArgumentException("blank id");
            items = List.copyOf(items);
        }
    }
    public static void main(String[] args) throws Exception {
        Order order = new Order(" A ", List.of("x"));
        assert order.id().equals("A") && order.items().equals(List.of("x"));

        List<String> supplied = new ArrayList<>(List.of("x")); Order copied = new Order("B", supplied); supplied.add("y");
        assert copied.items().equals(List.of("x"));
    }
}

```

**Expected:** record retains its original single item.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Normalize at construction.** Create an Order with ID " A " and item x.
   **Expected:** ID A and items[x].
   **Verify:** Compare your assertion values or captured diagnostic with ID A and items[x].

2. **Copy caller-owned collections.** Create an Order from a mutable list,then append to the original list.
   **Expected:** record retains its original single item.
   **Verify:** Compare your assertion values or captured diagnostic with record retains its original single item.

3. **Use value equality.** Construct another Order with normalizedA and item x.
   **Expected:** equals true and equalhashCode.
   **Verify:** Compare your assertion values or captured diagnostic with equals true and equalhashCode.

4. **Reject blank identity.** Construct an Order with an all-space ID.
   **Expected:** IllegalArgumentException.
   **Verify:** Compare your assertion values or captured diagnostic with IllegalArgumentException.

5. **Protect the exposed collection.** Attempt to add toorder.items().
   **Expected:** UnsupportedOperationException.
   **Verify:** Compare your assertion values or captured diagnostic with UnsupportedOperationException.

6. **Reject null collection members.** Try creating an Order whose items contains null.
   **Expected:** NullPointerException from the declared copy policy.
   **Verify:** Compare your assertion values or captured diagnostic with NullPointerException from the declared copy policy.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Record, Compact constructor, Defensive copy in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-008: Constructors, records and invariants.
Read courses/java/guides/java-008.md and courses/java/lessons/java-008.java. Direct prerequisites: `java-007`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
