# java-005: Arrays, strings and Unicode

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-004`

## Learning objectives

Copy arrays safely and count, slice and normalize strings by code point instead of by UTF-16 unit. Along the way, explain array index, utf-16 code unit, code point using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Convert lowercase red to uppercase and retain both references. The final exercise transfers the mechanism to reject an invalid array index.

## Purpose and mental model

An array is a fixed-length indexed container. A String is immutable text represented in UTF-16 code units. Those code units are not always complete Unicode characters: an emoji outside the basic multilingual plane uses a surrogate pair. String.length counts code units, while codePointCount counts Unicode code points. Even code points do not always equal user-perceived characters, because combining marks can join a base letter. Indexing and slicing therefore need a declared unit. Immutability means a transformation returns a new String rather than editing the original; it does not mean every object containing a String is immutable.

## Vocabulary and concepts

**Array index:** A zero-based position in a fixed-length container.

**UTF-16 code unit:** A16-bit storage unit used by Java String indexing.

**Code point:** A Unicode scalar identity represented by one or two UTF-16 units.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-005/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Array indices start at 0 and stop before length. Arrays.copyOf creates a separate array, while assigning another variable shares the original array reference. String.codePoints produces integer Unicode values. substring uses UTF-16 offsets and can split a surrogate pair if given an arbitrary index. Normalizer.normalize with NFC is an explicit identity policy, not an automatic rule for every text field.

## Worked example / walkthrough

### Example A: Copy array storage

The new array owns its storage. A simple assignment copy=original would alias the same array and make the mutation visible through both variables.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int[] original = { 1, 2, 3 };
    int[] copy = Arrays.copyOf(original, original.length);
    copy[0] = 9;
    assert original[0] == 1 && copy[0] == 9;
  }
}
```

**Expected:** original starts 1; copy starts 9.

### Example B: Count text units

The emoji occupies a surrogate pair. Treating length as a visible-character count would overcount this simple example.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int[] original = { 1, 2, 3 };
    int[] copy = Arrays.copyOf(original, original.length);
    copy[0] = 9;
    assert original[0] == 1 && copy[0] == 9;

    String text = "A\ud83d\ude42";
    assert text.length() == 3;
    assert text.codePointCount(0, text.length()) == 2;
  }
}
```

**Expected:** length 3 code units; 2 code points.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Copy array storage: change one input.** Copy Example A into a scratch `Main.java` and change `int[] original = { 1, 2, 3 };` to `int[] original = { 2, 2, 3 };`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `original[0] == 1 && copy[0] == 9`. Restoring the original line brings back the worked observation: original starts 1; copy starts 9.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `original[0] == 1 && copy[0] == 9` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Count text units: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert text.codePointCount(1, text.length()) == 2;`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `text.codePointCount(0, text.length()) == 2`; after it the line reads `assert text.codePointCount(0, text.length()) == 2;` again and length 3 code units; 2 code points.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `text.codePointCount(0, text.length()) == 2` accepts.

3. **Observe String immutability.** Convert lowercase red to uppercase and retain both references.
   **Expected:** original red; new RED.
   **Verify:** Keep an assertion equivalent to `lower.equals("red") && upper.equals("RED")`. As a control, change `String lower = "red";` to `String lower = "red!";`: the run must fail with an `AssertionError` from the assertion on `lower.equals("red") && upper.equals("RED")`. Restore the line before continuing.

4. **Select by code-point offset.** Find the UTF-16 offset of the second code point and take the remaining substring.
   **Expected:** substring is the intact emoji with length 2.
   **Verify:** Keep an assertion equivalent to `emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1`. As a control, change `int offset = text.offsetByCodePoints(0, 1);` to `int offset = text.offsetByCodePoints(1, 1);`: the run must fail with an `AssertionError` from the assertion on `emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1`. Restore the line before continuing.

5. **Normalize deliberately.** Compare composedé ande plus combining acute before and after NFC.
   **Expected:** raw strings differ; normalized strings equal.
   **Verify:** Keep an assertion equivalent to `java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(composed)`. As a control, change `String composed = "é";` to `String composed = "é!";`: the run must fail with an `AssertionError` from the assertion on `java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(composed)`. Restore the line before continuing.

6. **Reject an invalid array index.** Read index 3 from a length 3 array and catch the boundary failure.
   **Expected:** ArrayIndexOutOfBoundsException.
   **Verify:** Keep an assertion equivalent to `invalid`. As a control, change `invalid = true;` to `invalid = false;`: the run must fail with an `AssertionError` from the assertion on `invalid`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: original starts 1; copy starts 9. Then list the values read by `original[0] == 1 && copy[0] == 9` and trace each one from its declaration. Finally, compute the asserted value with `int[] original = { 2, 2, 3 };` in place before running.
- **Exercise 2:** First restate the expected observation: length 3 code units; 2 code points. Then list the values read by `text.codePointCount(0, text.length()) == 2` and trace each one from its declaration. Finally, compare `assert text.codePointCount(1, text.length()) == 2;` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: original red; new RED. Then list the values read by `lower.equals("red") && upper.equals("RED")` and trace each one from its declaration. Finally, predict the effect of changing `String lower = "red";` to `String lower = "red!";` before running anything.
- **Exercise 4:** First restate the expected observation: substring is the intact emoji with length 2. Then list the values read by `emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1` and trace each one from its declaration. Finally, predict the effect of changing `int offset = text.offsetByCodePoints(0, 1);` to `int offset = text.offsetByCodePoints(1, 1);` before running anything.
- **Exercise 5:** First restate the expected observation: raw strings differ; normalized strings equal. Then list the values read by `java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(composed)` and trace each one from its declaration. Finally, predict the effect of changing `String composed = "é";` to `String composed = "é!";` before running anything.
- **Exercise 6:** First restate the expected observation: arrayIndexOutOfBoundsException. Then list the values read by `invalid` and trace each one from its declaration. Finally, predict the effect of changing `invalid = true;` to `invalid = false;` before running anything.

## Self-check and retrieval

Close the solution and explain Array index, UTF-16 code unit, Code point in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-005: Arrays, strings and Unicode.
Read courses/java/guides/java-005.md and courses/java/lessons/java-005.java. Direct prerequisites: `java-004`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
