# java-033: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An application boundary converts untrusted input into a limited set of permitted operations. Type and syntax checks are necessary but not sufficient:an identifier can be a valid String while naming an unauthorized file, and an accepted operation can still consume unbounded resources. Prefer explicit operation and identifier allowlists when the task is small. Keep validation close to the resource use and report a named failure instead of silently choosing a broader fallback.

Filesystem containment has both lexical and real-path concerns. Normalizing away dot segments can detect a simple parent traversal, but a symbolic link can redirect a seemingly contained path. This lesson uses an owned temporary directory and known fixtures, checks both forms of containment, and bounds reads with limit+1 bytes. It does not claim to be a race-proof sandbox against a concurrent adversary changing the filesystem. Logs retain selected metadata rather than copying secrets or raw source bodies.

**Allowlist:** An explicit set of admitted operations or identifiers.

**Path containment:** A check that a resource remains within its declared owned root.

**Resource bound:** A limit enforced before unbounded allocation or work.

**Safe diagnostic:** A useful failure record that excludes unnecessary sensitive content.

## Reading the reference

Resolve a relative path under a real root, normalize it, and reject absolute or escaping paths. Reject symbolic-link components under this simple policy, then check the existing real path remains inside the root. Read at most limit+1 bytes and reject an oversized payload. A fixed dispatcher maps admitted operation names to known functions; it never passes input to a shell or reflection loader. Build logs from allowlisted metadata schema.

## Exercise 1: Read an admitted owned file: change one input

Task: Copy Example A into a scratch `Main.java` and change `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");` to `java.nio.file.Files.writeString(root.resolve("input.txt"), "hello!");`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The helper reads actual local bytes under a bounded contract. The fixture root is owned by the lesson and contains no user data.

The unchanged code is the part that Example A adds:

```java
withRoot(root -> {
  java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");
  assert new String(
    readBounded(root, "input.txt", 10),
    java.nio.charset.StandardCharsets.UTF_8
  ).equals("hello");
});
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `new String(readBounded(root, "input.txt", 10), java.nio.charset.StandardCharsets.UTF_8).equals("hello")`. Restoring the original line brings back the worked observation: content hello.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `new String(readBounded(root, "input.txt", 10), java.nio.charset.StandardCharsets.UTF_8).equals("hello")` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Reject lexical traversal and absolute paths: debug a regression

Task: A regression changed `rejected = true;` to `rejected = false;` in the code that Example B adds after Example A. Run Example B with that change, use the failing assertion to explain the defect and repair it without changing the assertion.

A path's string appearance is not a permission decision. Normalization and relative-path validation make the simple boundary explicit.

The unchanged code is the part that Example B adds:

```java
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
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `rejected`; after it the line reads `rejected = true;` again and securityException for both.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `rejected` for this input.

## Exercise 3: Enforce the byte limit after reading a bounded amount

Task: Write five bytes and request a four-byte maximum.

A preflight Files.size check alone can race with file growth. Reading only limit+1 bytes keeps allocation bounded and detects an oversized result.

```java
withRoot(root -> {
  java.nio.file.Files.writeString(root.resolve("large.txt"), "abcde");
  boolean rejected = false;
  try {
    readBounded(root, "large.txt", 4);
  } catch (java.io.IOException expected) {
    rejected = expected.getMessage().contains("limit");
  }
  assert rejected;
});
```

**Expected:** IOException for oversized content.

**Verify:** Keep an assertion equivalent to `rejected`. As a control, change `readBounded(root, "large.txt", 4);` to `readBounded(root, "large.txt", 5);`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

## Exercise 4: Reject symbolic-link access under the declared policy

Task: Create a link inside the owned root to another owned file and attempt to read through it.

The default policy rejects all symlink components, even an in-root target. A more permissive policy needs additional ownership and race analysis rather than simply skipping the check.

```java
withRoot(root -> {
  java.nio.file.Files.writeString(root.resolve("target.txt"), "fixture");
  boolean created = false;
  try {
    java.nio.file.Files.createSymbolicLink(
      root.resolve("link.txt"),
      java.nio.file.Path.of("target.txt")
    );
    created = true;
  } catch (UnsupportedOperationException | java.io.IOException unavailable) {
    System.out.println("symbolic-link fixture unavailable on this platform");
  }
  if (created) {
    boolean rejected = false;
    try {
      readBounded(root, "link.txt", 20);
    } catch (SecurityException expected) {
      rejected = true;
    }
    assert rejected;
  }
});
```

**Expected:** link rejected when platform supports creation; unsupported capability recorded explicitly.

**Verify:** Keep an assertion equivalent to `rejected`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

## Exercise 5: Keep operation names out of code execution

Task: Admit only read_fixture and reject run_shell.

The input selects among fixed behavior; it does not become executable text. A model proposal or retrieved instruction cannot expand this catalog.

```java
Map<String, String> operations = Map.of("read_fixture", "fixed local reader");
assert operations.containsKey("read_fixture");
boolean rejected = false;
try {
  if (!operations.containsKey("run_shell")) throw new IllegalArgumentException(
    "operation not allowed"
  );
} catch (IllegalArgumentException expected) {
  rejected = true;
}
assert rejected;
```

**Expected:** unknown operation IllegalArgumentException.

**Verify:** Keep an assertion equivalent to `rejected`. As a control, change `if (!operations.containsKey("run_shell")) throw new IllegalArgumentException(` to `if (operations.containsKey("run_shell")) throw new IllegalArgumentException(`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

## Exercise 6: Build a restricted diagnostic record

Task: Copy only request_id, operation and status from a map containing token and source_text.

Logs are another data surface. Selecting metadata deliberately is more reliable than assuming every raw input is safe to print.

```java
Map<String, String> raw = Map.of(
  "request_id",
  "r1",
  "operation",
  "read_fixture",
  "status",
  "rejected",
  "token",
  "do-not-log",
  "source_text",
  "private fixture"
);
Map<String, String> safe = Map.of(
  "request_id",
  raw.get("request_id"),
  "operation",
  raw.get("operation"),
  "status",
  raw.get("status")
);
assert !safe.containsKey("token") && !safe.containsKey("source_text") && safe.size() == 3;
```

**Expected:** diagnostic excludes both sensitive fields.

**Verify:** Keep an assertion equivalent to `!safe.containsKey("token") && !safe.containsKey("source_text") && safe.size() == 3` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
