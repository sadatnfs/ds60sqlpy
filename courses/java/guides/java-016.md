# java-016: Files, paths and character encoding

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-015`

## Learning objectives

Read and write files with explicit encodings, close directory streams and keep path checks honest. Along the way, explain path, encoding, atomic move using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Create two files and count them through a try-with-resources Files.list stream. The final exercise transfers the mechanism to verify cleanup after failure.

## Purpose and mental model

A path names a location; it is not the file contents or a guarantee that the location exists. Filesystem operations can fail because of permissions, missing parents, encoding errors or concurrent changes. Choose an explicit character encoding so text has the same meaning across machines. Temporary directories provide owned scratch space, while try-with-resources closes streams that otherwise retain file handles. Replacing a file atomically is a filesystem capability, not a universal property of every move. If atomic replacement is required, fail clearly when unsupported instead of silently claiming the same guarantee from a non-atomic fallback.

## Vocabulary and concepts

**Path:** A typed representation of a filesystem location.

**Encoding:** A rule translating text characters to bytes and back.

**Atomic move:** A replacement operation observed as one filesystem action when supported.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-016/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Path.resolve appends a child path, normalize removes lexical dot segments, and toRealPath consults the filesystem. Files.writeString/readString accept StandardCharsets.UTF_8. Files.list and Files.walk return streams that must close. Files.move with ATOMIC_MOVE requests atomicity and may throw AtomicMoveNotSupportedException. The helper creates one owned temporary directory and deletes only its contents in a finally block.

## Worked example / walkthrough

### Example A: Round-trip explicit UTF-8

Explicit encoding avoids dependence on platform defaults. The round trip tests both byte writing and reading, not just a String kept in memory.

```java
import java.util.*;

public class Main {

  @FunctionalInterface
  interface FileWork {
    void run(java.nio.file.Path root) throws Exception;
  }

  static void withTemp(FileWork work) throws Exception {
    var root = java.nio.file.Files.createTempDirectory("ds60-java-");
    try {
      work.run(root);
    } finally {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    withTemp(root -> {
      var path = root.resolve("text.txt");
      String text = "Café 🙂";
      java.nio.file.Files.writeString(path, text, java.nio.charset.StandardCharsets.UTF_8);
      assert java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(
        text
      );
    });
  }
}
```

**Expected:** exact text equality.

### Example B: Distinguish a path from existence

Constructing a Path does not create a file. Keeping those actions separate prevents accidental assumptions about setup state.

```java
import java.util.*;

public class Main {

  @FunctionalInterface
  interface FileWork {
    void run(java.nio.file.Path root) throws Exception;
  }

  static void withTemp(FileWork work) throws Exception {
    var root = java.nio.file.Files.createTempDirectory("ds60-java-");
    try {
      work.run(root);
    } finally {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    withTemp(root -> {
      var path = root.resolve("text.txt");
      String text = "Café 🙂";
      java.nio.file.Files.writeString(path, text, java.nio.charset.StandardCharsets.UTF_8);
      assert java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(
        text
      );
    });

    withTemp(root -> {
      var missing = root.resolve("missing.txt");
      assert missing.getFileName().toString().equals("missing.txt") &&
      !java.nio.file.Files.exists(missing);
    });
  }
}
```

**Expected:** path object exists; filesystem entry absent.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Round-trip explicit UTF-8: change one input.** Close Example A and rebuild it in a fresh `Main.java`, keeping the assertion on `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)`. Then propose one input change that would make that assertion fail and explain why before trying it.
   **Expected:** Your rebuild reproduces the worked observation (exact text equality), and your proposed change makes the assertion on `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` fail.
   **Verify:** Run the rebuild with `java -ea Main` first, then the changed copy, and keep both results. Name the value that makes `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` false in the changed copy.

2. **Distinguish a path from existence: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `var missing = root.resolve("missing.txt!");`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)`; after it the line reads `var missing = root.resolve("missing.txt");` again and path object exists; filesystem entry absent.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)` for this input.

3. **Close a directory stream.** Create two files and count them through a try-with-resources Files.list stream.
   **Expected:** count 2.
   **Verify:** Keep an assertion equivalent to `entries.count() == 2`. As a control, change `assert entries.count() == 2;` to `assert entries.count() != 2;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

4. **Request atomic replacement honestly.** Write old and staged files, request ATOMIC_MOVE, then verify the selected outcome without claiming a fallback is atomic.
   **Expected:** either target new with staged absent, or explicit unsupported result retaining old.
   **Verify:** Keep an assertion equivalent to `java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged)`. As a control, change `java.nio.file.Files.writeString(staged, "new");` to `java.nio.file.Files.writeString(staged, "new!");`: the run must fail with an `AssertionError` from the assertion on `java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged)`. Restore the line before continuing.

5. **Expose a lexical path escape.** Resolve../outside under an owned root and normalize it before checking containment.
   **Expected:** normalized path is outside the root.
   **Verify:** Keep an assertion equivalent to `!candidate.startsWith(root.normalize())`. As a control, change `assert !candidate.startsWith(root.normalize());` to `assert candidate.startsWith(root.normalize());` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

6. **Verify cleanup after failure.** Throw inside the owned temporary scope and confirm the directory is removed by the helper.
   **Expected:** original exception propagated; owned directory absent.
   **Verify:** Keep an assertion equivalent to `propagated && created[0] != null && !java.nio.file.Files.exists(created[0])`. As a control, change `throw new java.io.IOException("fixture failure");` to `throw new java.io.IOException("fixture failure!");`: the run must fail with an `AssertionError` from the assertion on `propagated && created[0] != null && !java.nio.file.Files.exists(created[0])`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: exact text equality. Then list the values read by `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` and trace each one from its declaration. Finally, name one input that would make `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` false.
- **Exercise 2:** First restate the expected observation: path object exists; filesystem entry absent. Then list the values read by `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)` and trace each one from its declaration. Finally, compare `var missing = root.resolve("missing.txt!");` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: count 2. Then list the values read by `entries.count() == 2` and trace each one from its declaration. Finally, name one input that would make `entries.count() == 2` false.
- **Exercise 4:** First restate the expected observation: either target new with staged absent, or explicit unsupported result retaining old. Then list the values read by `java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged)` and trace each one from its declaration. Finally, predict the effect of changing `java.nio.file.Files.writeString(staged, "new");` to `java.nio.file.Files.writeString(staged, "new!");` before running anything.
- **Exercise 5:** First restate the expected observation: normalized path is outside the root. Then list the values read by `!candidate.startsWith(root.normalize())` and trace each one from its declaration. Finally, name one input that would make `!candidate.startsWith(root.normalize())` false.
- **Exercise 6:** First restate the expected observation: original exception propagated; owned directory absent. Then list the values read by `propagated && created[0] != null && !java.nio.file.Files.exists(created[0])` and trace each one from its declaration. Finally, predict the effect of changing `throw new java.io.IOException("fixture failure");` to `throw new java.io.IOException("fixture failure!");` before running anything.

## Self-check and retrieval

Close the solution and explain Path, Encoding, Atomic move in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-016: Files, paths and character encoding.
Read courses/java/guides/java-016.md and courses/java/lessons/java-016.java. Direct prerequisites: `java-015`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
