# java-016: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A path names a location; it is not the file contents or a guarantee that the location exists. Filesystem operations can fail because of permissions, missing parents, encoding errors or concurrent changes. Choose an explicit character encoding so text has the same meaning across machines. Temporary directories provide owned scratch space, while try-with-resources closes streams that otherwise retain file handles. Replacing a file atomically is a filesystem capability, not a universal property of every move. If atomic replacement is required, fail clearly when unsupported instead of silently claiming the same guarantee from a non-atomic fallback.

**Path:** A typed representation of a filesystem location.

**Encoding:** A rule translating text characters to bytes and back.

**Atomic move:** A replacement operation observed as one filesystem action when supported.

## Reading the reference

Path.resolve appends a child path, normalize removes lexical dot segments, and toRealPath consults the filesystem. Files.writeString/readString accept StandardCharsets.UTF_8. Files.list and Files.walk return streams that must close. Files.move with ATOMIC_MOVE requests atomicity and may throw AtomicMoveNotSupportedException. The helper creates one owned temporary directory and deletes only its contents in a finally block.

## Exercise 1: Round-trip explicit UTF-8: change one input

Task: Close Example A and rebuild it in a fresh `Main.java`, keeping the assertion on `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)`. Then propose one input change that would make that assertion fail and explain why before trying it.

Explicit encoding avoids dependence on platform defaults. The round trip tests both byte writing and reading, not just a String kept in memory.

The unchanged code is the part that Example A adds:

```java
withTemp(root -> {
  var path = root.resolve("text.txt");
  String text = "Café 🙂";
  java.nio.file.Files.writeString(path, text, java.nio.charset.StandardCharsets.UTF_8);
  assert java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(
    text
  );
});
```

**Expected:** Your rebuild reproduces the worked observation (exact text equality), and your proposed change makes the assertion on `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` fail.

**Verify:** Run the rebuild with `java -ea Main` first, then the changed copy, and keep both results. Name the value that makes `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` false in the changed copy.

## Exercise 2: Distinguish a path from existence: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `var missing = root.resolve("missing.txt!");`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

Constructing a Path does not create a file. Keeping those actions separate prevents accidental assumptions about setup state.

The unchanged code is the part that Example B adds:

```java
withTemp(root -> {
  var missing = root.resolve("missing.txt");
  assert missing.getFileName().toString().equals("missing.txt") &&
  !java.nio.file.Files.exists(missing);
});
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)`; after it the line reads `var missing = root.resolve("missing.txt");` again and path object exists; filesystem entry absent.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)` for this input.

## Exercise 3: Close a directory stream

Task: Create two files and count them through a try-with-resources Files.list stream.

The stream can hold a directory resource until closed. A terminal operation alone is not the ownership policy for an I/O-backed stream.

```java
withTemp(root -> {
  java.nio.file.Files.writeString(root.resolve("a.txt"), "a");
  java.nio.file.Files.writeString(root.resolve("b.txt"), "b");
  try (var entries = java.nio.file.Files.list(root)) {
    assert entries.count() == 2;
  }
});
```

**Expected:** count 2.

**Verify:** Keep an assertion equivalent to `entries.count() == 2`. As a control, change `assert entries.count() == 2;` to `assert entries.count() != 2;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 4: Request atomic replacement honestly

Task: Write old and staged files, request ATOMIC_MOVE, then verify the selected outcome without claiming a fallback is atomic.

The branch reports a capability limit rather than silently weakening the contract. Atomic replacement also does not by itself prove durable persistence after a power loss.

```java
withTemp(root -> {
  var target = root.resolve("target.txt");
  var staged = root.resolve("staged.txt");
  java.nio.file.Files.writeString(target, "old");
  java.nio.file.Files.writeString(staged, "new");
  try {
    java.nio.file.Files.move(
      staged,
      target,
      java.nio.file.StandardCopyOption.ATOMIC_MOVE,
      java.nio.file.StandardCopyOption.REPLACE_EXISTING
    );
    assert java.nio.file.Files.readString(target).equals("new") &&
    !java.nio.file.Files.exists(staged);
  } catch (java.nio.file.AtomicMoveNotSupportedException expected) {
    assert java.nio.file.Files.readString(target).equals("old");
  }
});
```

**Expected:** either target new with staged absent, or explicit unsupported result retaining old.

**Verify:** Keep an assertion equivalent to `java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged)`. As a control, change `java.nio.file.Files.writeString(staged, "new");` to `java.nio.file.Files.writeString(staged, "new!");`: the run must fail with an `AssertionError` from the assertion on `java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged)`. Restore the line before continuing.

## Exercise 5: Expose a lexical path escape

Task: Resolve../outside under an owned root and normalize it before checking containment.

Lexical containment is useful but does not resolve symlinks. A security-sensitive file boundary needs real-path and ownership checks as discussed later.

```java
withTemp(root -> {
  var candidate = root.resolve("../outside").normalize();
  assert !candidate.startsWith(root.normalize());
});
```

**Expected:** normalized path is outside the root.

**Verify:** Keep an assertion equivalent to `!candidate.startsWith(root.normalize())`. As a control, change `assert !candidate.startsWith(root.normalize());` to `assert candidate.startsWith(root.normalize());` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 6: Verify cleanup after failure

Task: Throw inside the owned temporary scope and confirm the directory is removed by the helper.

Cleanup should run on both paths while preserving the primary failure. It must remain confined to the directory this exercise created.

```java
final java.nio.file.Path[] created = { null };
boolean propagated = false;
try {
  withTemp(root -> {
    created[0] = root;
    throw new java.io.IOException("fixture failure");
  });
} catch (java.io.IOException expected) {
  propagated = expected.getMessage().equals("fixture failure");
}
assert propagated && created[0] != null && !java.nio.file.Files.exists(created[0]);
```

**Expected:** original exception propagated; owned directory absent.

**Verify:** Keep an assertion equivalent to `propagated && created[0] != null && !java.nio.file.Files.exists(created[0])`. As a control, change `throw new java.io.IOException("fixture failure");` to `throw new java.io.IOException("fixture failure!");`: the run must fail with an `AssertionError` from the assertion on `propagated && created[0] != null && !java.nio.file.Files.exists(created[0])`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
