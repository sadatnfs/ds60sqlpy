# java-001: From source file to running JVM

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: None. This lesson starts from a plain text source file.

## Learning objectives

Compile and run Main.java with assertions enabled and tell a compiler diagnostic from a runtime failure.

The six exercises practice these steps:

- Print a first result.
- Evaluate before printing.
- Trace sequential state.
- Verify assertion mode.
- Separate runtime failure.
- Observe a real compiler diagnostic.

## Purpose and mental model

A Java program begins as text. The compiler checks syntax and types, then writes bytecode in a class file. The Java Virtual Machine loads that bytecode and invokes a recognized entry point. Compilation and execution are different stages: a missing semicolon prevents compilation, while division by zero can fail after the program starts. This course uses a public class named Main stored in Main.java. The main method is static so the launcher can call it without first creating an object. Its String array parameter contains command-line arguments. Assertions are optional in ordinary Java launches, so the classroom deliberately enables them with -ea. A printed success message cannot replace a check that would fail on incorrect behavior.

## Vocabulary and concepts

**Source:** Human-readable Java text compiled before execution.

**Bytecode:** Instructions stored in a class file for the JVM.

**Entry point:** The method the launcher invokes to start the program.

## How to run this lesson

Exercise 6 asks the system Java compiler for diagnostics at run time, so this lesson needs a full JDK rather than a bare runtime; every other check works on literals only.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

Before running Example A, say exactly which line it prints and whether the assertion on `message` could fail even when the text appears on screen. For Example B, decide whether `total` holds the number 5 or the text "5" when `line` is built, and what `"total=" + 2 + 3` would produce instead (it is `total=23`, because the left operand is already a `String`). For Exercise 5, predict whether `javac` or the running JVM rejects a division by a variable that holds 0.

## Exercises

1. **Print a first result: change one input.** Change `String message = "Hello, Java";` to `String message = "Hello, Java!";` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `message.equals("Hello, Java")`.
   **Verify:** Name the value that makes `message.equals("Hello, Java")` false, then restore the line.

2. **Evaluate before printing: diagnose an edited check.** Example B's new assertion was edited to `assert line.equals("total=6");`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `line.equals("total=5")`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `line.equals("total=5")` accepts.

3. **Trace sequential state.** Start count 1, increment it, then multiply it by 3.
   **Expected:** final count 6.
   **Verify:** Control: changing `count = count + 1;` to `count = count - 1;` must fail the assertion on `count == 6`.

4. **Verify assertion mode.** Use an assertion side effect only to detect whether this teaching launch enabled assertions; fail explicitly otherwise.
   **Expected:** assertion-enabled flag true.
   **Verify:** Control: changing `assert enabled = true;` to `assert enabled = false;` inside the assertion must make it fail.

5. **Separate runtime failure.** Divide an integer by a variable containing 0 and catch exactly ArithmeticException.
   **Expected:** ArithmeticException observed; program continues after the catch.
   **Verify:** Control: changing `int zero = 0;` to `int zero = 1;` must fail the assertion on `dividedByZero`.

6. **Observe a real compiler diagnostic.** Compile a small in-memory Broken class whose return statement lacks a semicolon; capture diagnostics without executing it.
   **Expected:** compiler result false and at least one ERROR diagnostic.
   **Verify:** Control: changing `.anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR);` to `.anyMatch(d -> d.getKind() != javax.tools.Diagnostic.Kind.ERROR);` inside the assertion must make it fail.

## Common pitfalls and diagnosis

The classic first mistake is treating a compiler error and a runtime exception as the same event. A missing semicolon stops `javac`, so no class file is written and nothing prints; a division by zero compiles cleanly and then throws `ArithmeticException` while `main` runs. A second trap is launching with plain `java Main`: every `assert` is skipped silently and the run looks green, which is exactly what Exercise 4 is built to detect. Finally, a public class named `Main` in a file with any other name is a compile error, not a runtime one.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit changes the value stored in `message`, not the assertion. Then compare the new text with the literal inside `equals` character by character; `equals` compares the whole content, so one extra `!` is enough. Finally, decide whether `println` still runs before the assertion and what it shows.
- **Exercise 2:** First compute `total` and then `line` by hand from the two statements above the assertion. Then compare that text with the literal in the edited assertion. Finally, decide which side is wrong here: the program state, or the claim the assertion makes about it.
- **Exercise 3:** First write the value of `count` after each of the three statements. Then check that your table reaches 6 only because the increment runs before the multiplication. Finally, predict what swapping the last two statements would produce and why order matters even in a single thread.
- **Exercise 4:** First recall that the expression inside `assert` is evaluated only when assertions are enabled. Then use that fact: an assignment inside the assertion changes a flag only under `-ea`. Finally, throw an explicit error when the flag is still false, so a plain `java Main` launch cannot pass quietly.
- **Exercise 5:** First keep the divisor 0 in a variable and divide by it inside a `try` block. Then catch exactly `ArithmeticException` and set a flag in the handler; a broad `catch (Exception e)` would also swallow unrelated bugs. Finally, assert on the flag after the `catch`, which proves the program continued past the failure.
- **Exercise 6:** First obtain the compiler with `ToolProvider.getSystemJavaCompiler()` and give it source text for a class whose `return` statement lacks a semicolon. Then collect diagnostics with a `DiagnosticCollector` and keep the boolean the compilation task returns. Finally, assert that the task returned false and that at least one diagnostic has kind `ERROR`.

## Self-check and retrieval

Without the guide, name the stage, `javac` or the JVM, that reports a missing semicolon and the stage that reports a division by zero, and explain why `main` must be `static`. Then describe what a launch without `-ea` would do to the six checks and how Exercise 4 turns that silent mistake into a visible failure.

## Next step

Continue with `java-002`: Values, numeric types and conversion. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

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
