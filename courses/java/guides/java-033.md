# java-033: Secure application boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-032`

## Learning objectives

Enforce secure file and operation boundaries that reject traversal, symbolic links, oversized input and unknown commands. Along the way, explain allowlist, path containment, resource bound, safe diagnostic using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Write five bytes and request a four-byte maximum. The final exercise transfers the mechanism to build a restricted diagnostic record.

## Purpose and mental model

An application boundary converts untrusted input into a limited set of permitted operations. Type and syntax checks are necessary but not sufficient:an identifier can be a valid String while naming an unauthorized file, and an accepted operation can still consume unbounded resources. Prefer explicit operation and identifier allowlists when the task is small. Keep validation close to the resource use and report a named failure instead of silently choosing a broader fallback.

Filesystem containment has both lexical and real-path concerns. Normalizing away dot segments can detect a simple parent traversal, but a symbolic link can redirect a seemingly contained path. This lesson uses an owned temporary directory and known fixtures, checks both forms of containment, and bounds reads with limit+1 bytes. It does not claim to be a race-proof sandbox against a concurrent adversary changing the filesystem. Logs retain selected metadata rather than copying secrets or raw source bodies.

## Vocabulary and concepts

**Allowlist:** An explicit set of admitted operations or identifiers.

**Path containment:** A check that a resource remains within its declared owned root.

**Resource bound:** A limit enforced before unbounded allocation or work.

**Safe diagnostic:** A useful failure record that excludes unnecessary sensitive content.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-033/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Resolve a relative path under a real root, normalize it, and reject absolute or escaping paths. Reject symbolic-link components under this simple policy, then check the existing real path remains inside the root. Read at most limit+1 bytes and reject an oversized payload. A fixed dispatcher maps admitted operation names to known functions; it never passes input to a shell or reflection loader. Build logs from allowlisted metadata schema.

## Worked example / walkthrough

### Example A: Read an admitted owned file

The helper reads actual local bytes under a bounded contract. The fixture root is owned by the lesson and contains no user data.

```java
import java.util.*;

public class Main {

  @FunctionalInterface
  interface RootWork {
    void run(java.nio.file.Path root) throws Exception;
  }

  static void withRoot(RootWork work) throws Exception {
    var root = java.nio.file.Files.createTempDirectory("ds60-boundary-").toRealPath();
    try {
      work.run(root);
    } finally {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  static byte[] readBounded(java.nio.file.Path root, String relative, int limit)
    throws java.io.IOException {
    if (limit < 0 || limit > 1024) throw new IllegalArgumentException("byte limit0..1024 required");
    var supplied = java.nio.file.Path.of(relative);
    if (supplied.isAbsolute()) throw new SecurityException("relative path required");
    var candidate = root.resolve(supplied).normalize();
    if (!candidate.startsWith(root)) throw new SecurityException("path escape");
    var current = root;
    for (var part : root.relativize(candidate)) {
      current = current.resolve(part);
      if (java.nio.file.Files.isSymbolicLink(current)) throw new SecurityException(
        "symbolic link not allowed"
      );
    }
    var real = candidate.toRealPath();
    if (!real.startsWith(root)) throw new SecurityException("real path escape");
    try (var input = java.nio.file.Files.newInputStream(real)) {
      byte[] bytes = input.readNBytes(limit + 1);
      if (bytes.length > limit) throw new java.io.IOException("byte limit exceeded");
      return bytes;
    }
  }

  public static void main(String[] args) throws Exception {
    withRoot(root -> {
      java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");
      assert new String(
        readBounded(root, "input.txt", 10),
        java.nio.charset.StandardCharsets.UTF_8
      ).equals("hello");
    });
  }
}
```

**Expected:** content hello.

### Example B: Reject lexical traversal and absolute paths

A path's string appearance is not a permission decision. Normalization and relative-path validation make the simple boundary explicit.

```java
import java.util.*;

public class Main {

  @FunctionalInterface
  interface RootWork {
    void run(java.nio.file.Path root) throws Exception;
  }

  static void withRoot(RootWork work) throws Exception {
    var root = java.nio.file.Files.createTempDirectory("ds60-boundary-").toRealPath();
    try {
      work.run(root);
    } finally {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  static byte[] readBounded(java.nio.file.Path root, String relative, int limit)
    throws java.io.IOException {
    if (limit < 0 || limit > 1024) throw new IllegalArgumentException("byte limit0..1024 required");
    var supplied = java.nio.file.Path.of(relative);
    if (supplied.isAbsolute()) throw new SecurityException("relative path required");
    var candidate = root.resolve(supplied).normalize();
    if (!candidate.startsWith(root)) throw new SecurityException("path escape");
    var current = root;
    for (var part : root.relativize(candidate)) {
      current = current.resolve(part);
      if (java.nio.file.Files.isSymbolicLink(current)) throw new SecurityException(
        "symbolic link not allowed"
      );
    }
    var real = candidate.toRealPath();
    if (!real.startsWith(root)) throw new SecurityException("real path escape");
    try (var input = java.nio.file.Files.newInputStream(real)) {
      byte[] bytes = input.readNBytes(limit + 1);
      if (bytes.length > limit) throw new java.io.IOException("byte limit exceeded");
      return bytes;
    }
  }

  public static void main(String[] args) throws Exception {
    withRoot(root -> {
      java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");
      assert new String(
        readBounded(root, "input.txt", 10),
        java.nio.charset.StandardCharsets.UTF_8
      ).equals("hello");
    });

    withRoot(root -> {
      for (String name : List.of("../outside.txt", root.resolve("input.txt").toString())) {
        boolean rejected = false;
        try {
          readBounded(root, name, 10);
        } catch (SecurityException expected) {
          rejected = true;
        }
        assert rejected;
      }
    });
  }
}
```

**Expected:** SecurityException for both.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Read an admitted owned file: change one input.** Copy Example A into a scratch `Main.java` and change `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");` to `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello!");`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `new String(readBounded(root, "input.txt", 10), java.nio.charset.StandardCharsets.UTF_8).equals("hello")`. Restoring the original line brings back the worked observation: content hello.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `new String(readBounded(root, "input.txt", 10), java.nio.charset.StandardCharsets.UTF_8).equals("hello")` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Reject lexical traversal and absolute paths: debug a regression.** A regression changed `rejected = true;` to `rejected = false;` in the code that Example B adds after Example A. Run Example B with that change, use the failing assertion to explain the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `rejected`; after it the line reads `rejected = true;` again and securityException for both.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `rejected` for this input.

3. **Enforce the byte limit after reading a bounded amount.** Write five bytes and request a four-byte maximum.
   **Expected:** IOException for oversized content.
   **Verify:** Keep an assertion equivalent to `rejected`. As a control, change `readBounded(root, "large.txt", 4);` to `readBounded(root, "large.txt", 5);`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

4. **Reject symbolic-link access under the declared policy.** Create a link inside the owned root to another owned file and attempt to read through it.
   **Expected:** link rejected when platform supports creation; unsupported capability recorded explicitly.
   **Verify:** Keep an assertion equivalent to `rejected`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

5. **Keep operation names out of code execution.** Admit only read_fixture and reject run_shell.
   **Expected:** unknown operation IllegalArgumentException.
   **Verify:** Keep an assertion equivalent to `rejected`. As a control, change `if (!operations.containsKey("run_shell")) throw new IllegalArgumentException(` to `if (operations.containsKey("run_shell")) throw new IllegalArgumentException(`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

6. **Build a restricted diagnostic record.** Copy only request_id, operation and status from a map containing token and source_text.
   **Expected:** diagnostic excludes both sensitive fields.
   **Verify:** Keep an assertion equivalent to `!safe.containsKey("token") && !safe.containsKey("source_text") && safe.size() == 3` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: content hello. Then list the values read by `new String(readBounded(root, "input.txt", 10), java.nio.charset.StandardCharsets.UTF_8).equals("hello")` and trace each one from its declaration. Finally, compute the asserted value with `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello!");` in place before running.
- **Exercise 2:** First restate the expected observation: securityException for both. Then list the values read by `rejected` and trace each one from its declaration. Finally, compare `rejected = false;` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: IOException for oversized content. Then list the values read by `rejected` and trace each one from its declaration. Finally, predict the effect of changing `readBounded(root, "large.txt", 4);` to `readBounded(root, "large.txt", 5);` before running anything.
- **Exercise 4:** First restate the expected observation: link rejected when platform supports creation; unsupported capability recorded explicitly. Then list the values read by `rejected` and trace each one from its declaration. Finally, predict the effect of changing `rejected = true;` to `rejected = false;` before running anything.
- **Exercise 5:** First restate the expected observation: unknown operation IllegalArgumentException. Then list the values read by `rejected` and trace each one from its declaration. Finally, predict the effect of changing `if (!operations.containsKey("run_shell")) throw new IllegalArgumentException(` to `if (operations.containsKey("run_shell")) throw new IllegalArgumentException(` before running anything.
- **Exercise 6:** First restate the expected observation: diagnostic excludes both sensitive fields. Then list the values read by `!safe.containsKey("token") && !safe.containsKey("source_text") && safe.size() == 3` and trace each one from its declaration. Finally, name one input that would make `!safe.containsKey("token") && !safe.containsKey("source_text") && safe.size() == 3` false.

## Self-check and retrieval

Close the solution and explain Allowlist, Path containment, Resource bound in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Path.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-033: Secure application boundaries.
Read courses/java/guides/java-033.md and courses/java/lessons/java-033.java. Direct prerequisites: `java-032`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
