# java-033: Secure application boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-032`

## Learning objectives

Enforce secure file and operation boundaries that reject traversal, symbolic links, oversized input and unknown commands.

The six exercises practice these steps:

- Read an admitted owned file.
- Reject lexical traversal and absolute paths.
- Enforce the byte limit after reading a bounded amount.
- Reject symbolic-link access under the declared policy.
- Keep operation names out of code execution.
- Build a restricted diagnostic record.

## Purpose and mental model

An application boundary converts untrusted input into a limited set of permitted operations. Type and syntax checks are necessary but not sufficient:an identifier can be a valid String while naming an unauthorized file, and an accepted operation can still consume unbounded resources. Prefer explicit operation and identifier allowlists when the task is small. Keep validation close to the resource use and report a named failure instead of silently choosing a broader fallback.

Filesystem containment has both lexical and real-path concerns. Normalizing away dot segments can detect a simple parent traversal, but a symbolic link can redirect a seemingly contained path. This lesson uses an owned temporary directory and known fixtures, checks both forms of containment, and bounds reads with limit+1 bytes. It does not claim to be a race-proof sandbox against a concurrent adversary changing the filesystem. Logs retain selected metadata rather than copying secrets or raw source bodies.

## Vocabulary and concepts

**Allowlist:** An explicit set of admitted operations or identifiers.

**Path containment:** A check that a resource remains within its declared owned root.

**Resource bound:** A limit enforced before unbounded allocation or work.

**Safe diagnostic:** A useful failure record that excludes unnecessary sensitive content.

## How to run this lesson

`withRoot` creates an owned temporary directory, resolves its real path, and deletes it in `finally`; `readBounded` is the only way the exercises read files, and it enforces relative paths, containment, no symbolic links and a byte limit.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

Before running Example A, decide what `readBounded(root, "input.txt", 10)` returns for a five-byte file. For Example B, predict whether `../outside.txt` and an absolute path inside the root are both rejected, and which check catches each. Before Exercise 3, decide how many bytes `readBounded` reads for a five-byte file with a limit of 4, and why it reads one more than the limit.

## Exercises

1. **Read an admitted owned file: change one input.** Change `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");` to `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello!");` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `new String(readBounded(root, "input.txt", 10), java.nio.charset.StandardCharsets.UTF_8).equals("hello")`.
   **Verify:** Name the value that makes `new String(readBounded(root, "input.txt", 10), java.nio.charset.StandardCharsets.UTF_8).equals("hello")` false, then restore the line.

2. **Reject lexical traversal and absolute paths: debug a regression.** A regression changed `rejected = true;` to `rejected = false;` in Example B's new code. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `rejected`; the repaired line reads `rejected = true;`.
   **Verify:** Explain how the changed token alters the value that `rejected` tests.

3. **Enforce the byte limit after reading a bounded amount.** Write five bytes and request a four-byte maximum.
   **Expected:** IOException for oversized content.
   **Verify:** Control: changing `readBounded(root, "large.txt", 4);` to `readBounded(root, "large.txt", 5);` must fail the assertion on `rejected`.

4. **Reject symbolic-link access under the declared policy.** Create a link inside the owned root to another owned file and attempt to read through it.
   **Expected:** link rejected when platform supports creation; unsupported capability recorded explicitly.
   **Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected`.

5. **Keep operation names out of code execution.** Admit only read_fixture and reject run_shell.
   **Expected:** unknown operation IllegalArgumentException.
   **Verify:** Control: changing `if (!operations.containsKey("run_shell")) throw new IllegalArgumentException(` to `if (operations.containsKey("run_shell")) throw new IllegalArgumentException(` must fail the assertion on `rejected`.

6. **Build a restricted diagnostic record.** Copy only request_id, operation and status from a map containing token and source_text.
   **Expected:** diagnostic excludes both sensitive fields.
   **Verify:** Name an input that would make `!safe.containsKey("token") && !safe.containsKey("source_text") && safe.size() == 3` false and the value that changes.

## Common pitfalls and diagnosis

Checking `startsWith` on an unnormalized path lets `..` escape the root. Normalizing is not enough either, because a symbolic link inside the root can point anywhere, which is why `readBounded` rejects links and compares real paths. Checking `Files.size` before reading races with a growing file; reading at most `limit + 1` bytes is safe. Mapping user text to an executable command opens injection, so map names to fixed operations. And logging raw requests copies tokens into log storage.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit writes "hello!", six bytes, which is still under the limit of 10. Then decode the bytes that `readBounded` returns. Finally, compare "hello!" with "hello" and explain why every boundary check passed.
- **Exercise 2:** First note that the `catch` block now stores false, so `rejected` stays false whether or not `readBounded` throws. Then run it: `../outside.txt` is still refused with `SecurityException`, yet `assert rejected` fails on that first name. Finally, restore `rejected = true;` and name the check that stops each input: `startsWith(root)` after normalizing for the traversal, and `isAbsolute` for the absolute path.
- **Exercise 3:** First write five bytes to `large.txt`. Then call `readBounded` with a limit of 4 inside a `try` block. Finally, assert the `IOException` and explain why the method reads five bytes, one past the limit, before deciding.
- **Exercise 4:** First create `target.txt` and try to create the symbolic link `link.txt` pointing to it, recording if the platform refuses. Then read through the link when it exists and catch `SecurityException`. Finally, assert the rejection even though the target is inside the root.
- **Exercise 5:** First map the single allowed name `read_fixture` to a fixed description. Then look up `run_shell` and throw `IllegalArgumentException` when it is absent. Finally, assert the rejection and explain why the input never becomes code or a command line.
- **Exercise 6:** First build a raw map that contains a token and source text alongside the request metadata. Then copy only `request_id`, `operation` and `status` into a new map. Finally, assert three entries and no sensitive keys.

## Self-check and retrieval

Without notes, list the checks `readBounded` performs in order and the attack each one stops. Explain why reading `limit + 1` bytes detects oversized files without a size preflight, why an operation allowlist beats escaping, and which fields the diagnostic record keeps.

## Next step

Continue with `java-034`: Application design and dependency boundaries. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Path.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

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
