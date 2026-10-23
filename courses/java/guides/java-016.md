# java-016: Files, paths and character encoding

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-015`

## Learning objectives

Explain path, encoding, atomic move using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is WriteCafé and an emoji to an owned temporary file,then read it withUTF-8. The final exercise transfers the mechanism to verify cleanup after failure.

## Purpose and mental model

A path names a location; it is not the file contents or a guarantee that the location exists. Filesystem operations can fail because of permissions,missing parents,encoding errors or concurrent changes. Choose an explicit character encoding so text has the same meaning across machines. Temporary directories provide owned scratch space,while try-with-resources closes streams that otherwise retain file handles. Replacing a file atomically is a filesystem capability,not a universal property of every move. If atomic replacement is required,fail clearly when unsupported instead of silently claiming the same guarantee from a non-atomic fallback.

## Vocabulary and concepts

**Path:** A typed representation of a filesystem location.

**Encoding:** A rule translating text characters to bytes and back.

**Atomic move:** A replacement operation observed as one filesystem action when supported.

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-016/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Path.resolve appends a child path,normalize removes lexicaldot segments,andtoRealPath consults the filesystem. Files.writeString/readString acceptStandardCharsets.UTF_8. Files.list andFiles.walk return streams that must close. Files.move withATOMIC_MOVE requests atomicity and may throwAtomicMoveNotSupportedException. The helper creates one owned temporary directory and deletes only its contents in a finally block.

## Worked example / walkthrough

### Example A: Round-trip explicit UTF-8

Explicit encoding avoids dependence on platform defaults. The round trip tests both byte writing and reading,not just aString kept in memory.

```java
import java.util.*;

public class Main {
    @FunctionalInterface interface FileWork { void run(java.nio.file.Path root) throws Exception; }
    static void withTemp(FileWork work) throws Exception {
        var root=java.nio.file.Files.createTempDirectory("ds60-java-");
        try { work.run(root); }
        finally {
            try(var paths=java.nio.file.Files.walk(root)) {
                for(var path:paths.sorted(Comparator.reverseOrder()).toList()) java.nio.file.Files.deleteIfExists(path);
            }
        }
    }
    public static void main(String[] args) throws Exception {
        withTemp(root -> {
            var path = root.resolve("text.txt"); String text = "Café 🙂";
            java.nio.file.Files.writeString(path,text,java.nio.charset.StandardCharsets.UTF_8);
            assert java.nio.file.Files.readString(path,java.nio.charset.StandardCharsets.UTF_8).equals(text);
        });
    }
}

```

**Expected:** exact text equality.

### Example B: Distinguish a path from existence

Constructing aPath does not create a file. Keeping those actions separate prevents accidental assumptions about setup state.

```java
import java.util.*;

public class Main {
    @FunctionalInterface interface FileWork { void run(java.nio.file.Path root) throws Exception; }
    static void withTemp(FileWork work) throws Exception {
        var root=java.nio.file.Files.createTempDirectory("ds60-java-");
        try { work.run(root); }
        finally {
            try(var paths=java.nio.file.Files.walk(root)) {
                for(var path:paths.sorted(Comparator.reverseOrder()).toList()) java.nio.file.Files.deleteIfExists(path);
            }
        }
    }
    public static void main(String[] args) throws Exception {
        withTemp(root -> {
            var path = root.resolve("text.txt"); String text = "Café 🙂";
            java.nio.file.Files.writeString(path,text,java.nio.charset.StandardCharsets.UTF_8);
            assert java.nio.file.Files.readString(path,java.nio.charset.StandardCharsets.UTF_8).equals(text);
        });

        withTemp(root -> {
            var missing = root.resolve("missing.txt");
            assert missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing);
        });
    }
}

```

**Expected:** path object exists;filesystem entry absent.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Round-trip explicit UTF-8.** WriteCafé and an emoji to an owned temporary file,then read it withUTF-8.
   **Expected:** exact text equality.
   **Verify:** Compare your assertion values or captured diagnostic with exact text equality.

2. **Distinguish a path from existence.** Resolve a missing child inside the temporary directory and inspect existence before creating it.
   **Expected:** path object exists;filesystem entry absent.
   **Verify:** Compare your assertion values or captured diagnostic with path object exists;filesystem entry absent.

3. **Close a directory stream.** Create two files and count them through atry-with-resourcesFiles.list stream.
   **Expected:** count2.
   **Verify:** Compare your assertion values or captured diagnostic with count2.

4. **Request atomic replacement honestly.** Write old and staged files,requestATOMIC_MOVE,then verify the selected outcome without claiming a fallback is atomic.
   **Expected:** either targetnew withstagedabsent,or explicit unsupported result retainingold.
   **Verify:** Compare your assertion values or captured diagnostic with either targetnew withstagedabsent,or explicit unsupported result retainingold.

5. **Expose a lexical path escape.** Resolve../outside under an owned root and normalize it before checking containment.
   **Expected:** normalized path is outside the root.
   **Verify:** Compare your assertion values or captured diagnostic with normalized path is outside the root.

6. **Verify cleanup after failure.** Throw inside the owned temporary scope and confirm the directory is removed by the helper.
   **Expected:** original exception propagated;owned directory absent.
   **Verify:** Compare your assertion values or captured diagnostic with original exception propagated;owned directory absent.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Path, Encoding, Atomic move in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-016: Files, paths and character encoding.
Read courses/java/guides/java-016.md and courses/java/lessons/java-016.java. Direct prerequisites: `java-015`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
