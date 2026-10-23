# java-010: Interfaces and polymorphism

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-009`

## Learning objectives

Explain interface, dynamic dispatch, composition using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is UsePricing references to identity andhalf-price implementations on100 cents. The final exercise transfers the mechanism to reject an invalid wrapper.

## Purpose and mental model

An interface describes behavior a caller can rely on without depending on one implementation. Polymorphism lets a reference typed as that interface dispatch to the concrete object method at runtime. The caller should depend on the contract rather than inspect implementation class names. Composition builds a new behavior by holding another object and delegating to it, often making policy combinations clearer than a deep inheritance tree. Substitution requires preserving accepted inputs and promised outputs; matching a method signature alone is insufficient. This lesson uses pricing functions over integer cents so rounding and external services do not obscure the design.

## Vocabulary and concepts

**Interface:** A named behavioral contract implemented by different objects.

**Dynamic dispatch:** Selecting an implementation from the runtime receiver object.

**Composition:** Building behavior by delegating to contained collaborators.

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-010/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

An interface declares a method; implementing classes or lambdas supply its body. A variable of interface type can hold different implementations. The receiver object selects the overridden method at runtime. A composed wrapper validates its own policy, delegates to the inner implementation and checks arithmetic withMath.addExact. Keep domain validation consistent across all implementations so callers do not need class-specific exceptions.

## Worked example / walkthrough

### Example A: Call through an interface

The caller invokes the same method name while the concrete behavior differs. The shared nonnegative-input contract keeps both implementations substitutable.

```java
import java.util.*;

public class Main {
    interface Pricing { int price(int amount); }
    static void requireNonnegative(int amount) { if(amount<0) throw new IllegalArgumentException("negative amount"); }
    record Fee(Pricing delegate,int cents) implements Pricing {
        Fee { Objects.requireNonNull(delegate); requireNonnegative(cents); }
        public int price(int amount) { return Math.addExact(delegate.price(amount),cents); }
    }
    public static void main(String[] args) throws Exception {
        Pricing regular = amount -> { requireNonnegative(amount); return amount; };
        Pricing half = amount -> { requireNonnegative(amount); return amount / 2; };
        assert regular.price(100) == 100 && half.price(100) == 50;
    }
}

```

**Expected:** 100 and50.

### Example B: Compose a fee policy

The wrapper delegates first and then adds its policy. It does not duplicate the half-price calculation, so the two concerns can change independently.

```java
import java.util.*;

public class Main {
    interface Pricing { int price(int amount); }
    static void requireNonnegative(int amount) { if(amount<0) throw new IllegalArgumentException("negative amount"); }
    record Fee(Pricing delegate,int cents) implements Pricing {
        Fee { Objects.requireNonNull(delegate); requireNonnegative(cents); }
        public int price(int amount) { return Math.addExact(delegate.price(amount),cents); }
    }
    public static void main(String[] args) throws Exception {
        Pricing regular = amount -> { requireNonnegative(amount); return amount; };
        Pricing half = amount -> { requireNonnegative(amount); return amount / 2; };
        assert regular.price(100) == 100 && half.price(100) == 50;

        Pricing withFee = new Fee(half, 10);
        assert withFee.price(100) == 60;
    }
}

```

**Expected:** price100 becomes60.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Call through an interface.** UsePricing references to identity andhalf-price implementations on100 cents.
   **Expected:** 100 and50.
   **Verify:** Compare your assertion values or captured diagnostic with 100 and50.

2. **Compose a fee policy.** Wrap the half-price policy with a10-cent fee.
   **Expected:** price100 becomes60.
   **Verify:** Compare your assertion values or captured diagnostic with price100 becomes60.

3. **Inspect rounding semantics.** Apply integer half-price to101 cents under truncation-toward-zero.
   **Expected:** 50 cents beforefee.
   **Verify:** Compare your assertion values or captured diagnostic with 50 cents beforefee.

4. **Validate every implementation.** Call regular,half andfee policy with-1.
   **Expected:** all throwIllegalArgumentException.
   **Verify:** Compare your assertion values or captured diagnostic with all throwIllegalArgumentException.

5. **Change a collaborator without changing caller code.** Iterate over the three policies and collect prices for100.
   **Expected:** results100,50,60.
   **Verify:** Compare your assertion values or captured diagnostic with results100,50,60.

6. **Reject an invalid wrapper.** Construct a fee wrapper with a negative fee ornull delegate.
   **Expected:** negative feeIllegalArgumentException;null delegateNullPointerException.
   **Verify:** Compare your assertion values or captured diagnostic with negative feeIllegalArgumentException;null delegateNullPointerException.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Interface, Dynamic dispatch, Composition in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-010: Interfaces and polymorphism.
Read courses/java/guides/java-010.md and courses/java/lessons/java-010.java. Direct prerequisites: `java-009`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
