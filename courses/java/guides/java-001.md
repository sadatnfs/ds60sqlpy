# java-001: From source file to running JVM

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: None. This lesson starts from a plain text source file.

## Learning objectives

Compile and run Main.java with assertions enabled and tell a compiler diagnostic from a runtime failure. Along the way, explain source, bytecode, entry point using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Start count 1, increment it, then multiply it by 3. The final exercise transfers the mechanism to observe a real compiler diagnostic.

## Purpose and mental model

A Java program begins as text. The compiler checks syntax and types, then writes bytecode in a class file. The Java Virtual Machine loads that bytecode and invokes a recognized entry point. Compilation and execution are different stages: a missing semicolon prevents compilation, while division by zero can fail after the program starts. This course uses a public class named Main stored in Main.java. The main method is static so the launcher can call it without first creating an object. Its String array parameter contains command-line arguments. Assertions are optional in ordinary Java launches, so the classroom deliberately enables them with -ea. A printed success message cannot replace a check that would fail on incorrect behavior.

## Vocabulary and concepts

**Source:** Human-readable Java text compiled before execution.

**Bytecode:** Instructions stored in a class file for the JVM.

**Entry point:** The method the launcher invokes to start the program.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-001/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

The class braces enclose methods, and the main-method braces enclose statements. public makes the entry point accessible, static associates it with the class, void means it returns no value, and String[] declares an array of text arguments. System.out.println writes one line. A semicolon ends most statements. javac --release 21 selects the source/API target; java-ea Main loads the compiled class from the classpath. Read the first compiler diagnostic before looking for runtime output.

## Worked example / walkthrough

### Example A: Print a first result

The variable holds a reference to a String value. println adds a line separator, while the assertion checks the content independently of terminal formatting.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    String message = "Hello, Java";
    System.out.println(message);
    assert message.equals("Hello, Java");
  }
}
```

**Expected:** one line Hello, Java.

### Example B: Evaluate before printing

The numeric addition happens before concatenation because it is assigned first. Mixing strings and numbers in one expression can change which plus operators mean concatenation.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    String message = "Hello, Java";
    System.out.println(message);
    assert message.equals("Hello, Java");

    int total = 2 + 3;
    String line = "total=" + total;
    assert total == 5;
    assert line.equals("total=5");
  }
}
```

**Expected:** integer 5 and text total=5.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Print a first result: change one input.** Copy Example A into a scratch `Main.java` and change `String message = "Hello, Java";` to `String message = "Hello, Java!";`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `message.equals("Hello, Java")`. Restoring the original line brings back the worked observation: one line Hello, Java.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `message.equals("Hello, Java")` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Evaluate before printing: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert line.equals("total=6");`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `line.equals("total=5")`; after it the line reads `assert line.equals("total=5");` again and integer 5 and text total=5.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `line.equals("total=5")` accepts.

3. **Trace sequential state.** Start count 1, increment it, then multiply it by 3.
   **Expected:** final count 6.
   **Verify:** Keep an assertion equivalent to `count == 6`. As a control, change `count = count + 1;` to `count = count - 1;`: the run must fail with an `AssertionError` from the assertion on `count == 6`. Restore the line before continuing.

4. **Verify assertion mode.** Use an assertion side effect only to detect whether this teaching launch enabled assertions; fail explicitly otherwise.
   **Expected:** assertion-enabled flag true.
   **Verify:** Keep an assertion equivalent to `enabled = true`. As a control, change `assert enabled = true;` to `assert enabled = false;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

5. **Separate runtime failure.** Divide an integer by a variable containing 0 and catch exactly ArithmeticException.
   **Expected:** ArithmeticException observed; program continues after the catch.
   **Verify:** Keep an assertion equivalent to `dividedByZero`. As a control, change `int zero = 0;` to `int zero = 1;`: the run must fail with an `AssertionError` from the assertion on `dividedByZero`. Restore the line before continuing.

6. **Observe a real compiler diagnostic.** Compile a small in-memory Broken class whose return statement lacks a semicolon; capture diagnostics without executing it.
   **Expected:** compiler result false and at least one ERROR diagnostic.
   **Verify:** Keep an assertion equivalent to `diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR)`. As a control, change `.anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR);` to `.anyMatch(d -> d.getKind() != javax.tools.Diagnostic.Kind.ERROR);` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: one line Hello, Java. Then list the values read by `message.equals("Hello, Java")` and trace each one from its declaration. Finally, compute the asserted value with `String message = "Hello, Java!";` in place before running.
- **Exercise 2:** First restate the expected observation: integer 5 and text total=5. Then list the values read by `line.equals("total=5")` and trace each one from its declaration. Finally, compare `assert line.equals("total=6");` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: final count 6. Then list the values read by `count == 6` and trace each one from its declaration. Finally, predict the effect of changing `count = count + 1;` to `count = count - 1;` before running anything.
- **Exercise 4:** First restate the expected observation: assertion-enabled flag true. Then list the values read by `enabled = true` and trace each one from its declaration. Finally, name one input that would make `enabled = true` false.
- **Exercise 5:** First restate the expected observation: arithmeticException observed; program continues after the catch. Then list the values read by `dividedByZero` and trace each one from its declaration. Finally, predict the effect of changing `int zero = 0;` to `int zero = 1;` before running anything.
- **Exercise 6:** First restate the expected observation: compiler result false and at least one ERROR diagnostic. Then list the values read by `diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR)` and trace each one from its declaration. Finally, name one input that would make `diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR)` false.

## Self-check and retrieval

Close the solution and explain Source, Bytecode, Entry point in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-001: From source file to running JVM.
Read courses/java/guides/java-001.md and courses/java/lessons/java-001.java. Direct prerequisites: None. This lesson starts from a plain text source file..
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
