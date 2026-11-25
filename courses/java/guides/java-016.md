# java-016: Files, paths and character encoding

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-015`

## Learning objectives

Read and write files with explicit encodings, close directory streams and keep path checks honest.

The six exercises practice these steps:

- Round-trip explicit UTF-8.
- Distinguish a path from existence.
- Close a directory stream.
- Request atomic replacement honestly.
- Expose a lexical path escape.
- Verify cleanup after failure.

## Purpose and mental model

A path names a location; it is not the file contents or a guarantee that the location exists. Filesystem operations can fail because of permissions, missing parents, encoding errors or concurrent changes. Choose an explicit character encoding so text has the same meaning across machines. Temporary directories provide owned scratch space, while try-with-resources closes streams that otherwise retain file handles. Replacing a file atomically is a filesystem capability, not a universal property of every move. If atomic replacement is required, fail clearly when unsupported instead of silently claiming the same guarantee from a non-atomic fallback.

## Vocabulary and concepts

**Path:** A typed representation of a filesystem location.

**Encoding:** A rule translating text characters to bytes and back.

**Atomic move:** A replacement operation observed as one filesystem action when supported.

## How to run this lesson

Every file operation happens inside a directory that `withTemp` creates with `Files.createTempDirectory` and deletes in a `finally` block; Exercise 4 accepts either outcome because some filesystems cannot move atomically.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

Before running Example A, decide what bytes UTF-8 uses for é and the emoji, and whether reading the file back with UTF-8 returns a string that `equals` the original. For Example B, predict whether `root.resolve("missing.txt")` creates anything on disk and what `Files.exists` reports for it. Before Exercise 5, normalize `root.resolve("../outside")` in your head and decide whether the result still starts with `root`.

## Exercises

1. **Round-trip explicit UTF-8: change one input.** Rebuild Example A from memory and propose one input change that makes the assertion on `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` fail.
   **Expected:** The rebuild passes and the changed copy fails as predicted.
   **Verify:** Name the value that differs between your rebuild and the changed copy.

2. **Distinguish a path from existence: debug a regression.** A regression in Example B's new code makes one line read `var missing = root.resolve("missing.txt!");`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)`; the repaired line reads `var missing = root.resolve("missing.txt");`.
   **Verify:** Explain how the changed token alters the value that `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)` tests.

3. **Close a directory stream.** Create two files and count them through a try-with-resources Files.list stream.
   **Expected:** count 2.
   **Verify:** Control: changing `assert entries.count() == 2;` to `assert entries.count() != 2;` inside the assertion must make it fail.

4. **Request atomic replacement honestly.** Write old and staged files, request ATOMIC_MOVE, then verify the selected outcome without claiming a fallback is atomic.
   **Expected:** either target new with staged absent, or explicit unsupported result retaining old.
   **Verify:** Control: changing `java.nio.file.Files.writeString(staged, "new");` to `java.nio.file.Files.writeString(staged, "new!");` must fail the assertion on `java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged)`.

5. **Expose a lexical path escape.** Resolve../outside under an owned root and normalize it before checking containment.
   **Expected:** normalized path is outside the root.
   **Verify:** Control: changing `assert !candidate.startsWith(root.normalize());` to `assert candidate.startsWith(root.normalize());` inside the assertion must make it fail.

6. **Verify cleanup after failure.** Throw inside the owned temporary scope and confirm the directory is removed by the helper.
   **Expected:** original exception propagated; owned directory absent.
   **Verify:** Control: changing `throw new java.io.IOException("fixture failure");` to `throw new java.io.IOException("fixture failure!");` must fail the assertion on `propagated && created[0] != null && !java.nio.file.Files.exists(created[0])`.

## Common pitfalls and diagnosis

Relying on the platform default charset is the classic encoding bug: the same file reads correctly on one machine and as mojibake on another, so pass `StandardCharsets.UTF_8` or use the `Files` methods that default to it explicitly. `Files.list` and `Files.walk` hold an open directory handle until the stream is closed, so wrap them in try-with-resources. Checking containment with `startsWith` before `normalize()` lets `..` escape the root, and even a normalized check does not follow symbolic links.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First write the text with `Files.writeString(path, text, StandardCharsets.UTF_8)` inside the owned temporary directory. Then read it back with `Files.readString` and the same charset. Finally, compare the two strings with `equals` and say what a different decoder would do to é.
- **Exercise 2:** First note that the edit adds `!` to the resolved file name. Then compare `missing.getFileName().toString()` with "missing.txt". Finally, notice that the existence half of the condition was never reached because `&&` stopped at the name.
- **Exercise 3:** First create two files in the temporary directory. Then open `Files.list(root)` in a try-with-resources statement and count the entries. Finally, assert the count is 2 and explain what stays open if the stream is never closed.
- **Exercise 4:** First write "old" to the target and "new" to the staged file. Then call `Files.move` with `ATOMIC_MOVE` and `REPLACE_EXISTING`, and catch `AtomicMoveNotSupportedException` separately. Finally, assert the new content in the success branch and the untouched old content in the unsupported branch.
- **Exercise 5:** First resolve "../outside" against the owned root. Then call `normalize()` on the result and on the root. Finally, check that the candidate does not start with the root, and explain why symbolic links would need `toRealPath` as well.
- **Exercise 6:** First keep the temporary root in an array element so the lambda can record it. Then throw an `IOException` inside `withTemp` and catch it outside, comparing its message. Finally, assert that the recorded directory no longer exists, which proves the `finally` cleanup ran on the failure path.

## Self-check and retrieval

From memory, explain the difference between a `Path` and the file it names, why an explicit charset matters for a round trip, why a stream from `Files.list` needs closing, and what you should report when `ATOMIC_MOVE` is not supported instead of quietly copying.

## Next step

Continue with `java-017`: Optional values and validation boundaries. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

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
