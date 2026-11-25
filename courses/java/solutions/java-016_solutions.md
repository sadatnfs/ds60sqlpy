# java-016: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A path names a location; it is not the file contents or a guarantee that the location exists. Filesystem operations can fail because of permissions, missing parents, encoding errors or concurrent changes. Choose an explicit character encoding so text has the same meaning across machines. Temporary directories provide owned scratch space, while try-with-resources closes streams that otherwise retain file handles. Replacing a file atomically is a filesystem capability, not a universal property of every move. If atomic replacement is required, fail clearly when unsupported instead of silently claiming the same guarantee from a non-atomic fallback.

**Path:** A typed representation of a filesystem location.

**Encoding:** A rule translating text characters to bytes and back.

**Atomic move:** A replacement operation observed as one filesystem action when supported.

## Reading the reference

Path.resolve appends a child path, normalize removes lexical dot segments, and toRealPath consults the filesystem. Files.writeString/readString accept StandardCharsets.UTF_8. Files.list and Files.walk return streams that must close. Files.move with ATOMIC_MOVE requests atomicity and may throw AtomicMoveNotSupportedException. The helper creates one owned temporary directory and deletes only its contents in a finally block.

## Exercise 1: Round-trip explicit UTF-8: change one input

Task: Rebuild Example A from memory and propose one input change that makes the assertion on `java.nio.file.Files.readString(path, java.nio.charset.StandardCharsets.UTF_8).equals(text)` fail.

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

**Expected:** The rebuild passes and the changed copy fails as predicted.

**Verify:** Name the value that differs between your rebuild and the changed copy.

## Exercise 2: Distinguish a path from existence: debug a regression

Task: A regression in Example B's new code makes one line read `var missing = root.resolve("missing.txt!");`. Repair it using the failing assertion.

Constructing a Path does not create a file. Keeping those actions separate prevents accidental assumptions about setup state.

The unchanged code is the part that Example B adds:

```java
withTemp(root -> {
  var missing = root.resolve("missing.txt");
  assert missing.getFileName().toString().equals("missing.txt") &&
  !java.nio.file.Files.exists(missing);
});
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)`; the repaired line reads `var missing = root.resolve("missing.txt");`.

**Verify:** Explain how the changed token alters the value that `missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing)` tests.

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

**Verify:** Control: changing `assert entries.count() == 2;` to `assert entries.count() != 2;` inside the assertion must make it fail.

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

**Verify:** Control: changing `java.nio.file.Files.writeString(staged, "new");` to `java.nio.file.Files.writeString(staged, "new!");` must fail the assertion on `java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged)`.

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

**Verify:** Control: changing `assert !candidate.startsWith(root.normalize());` to `assert candidate.startsWith(root.normalize());` inside the assertion must make it fail.

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

**Verify:** Control: changing `throw new java.io.IOException("fixture failure");` to `throw new java.io.IOException("fixture failure!");` must fail the assertion on `propagated && created[0] != null && !java.nio.file.Files.exists(created[0])`.

## After comparing the answer

In your copy, read the UTF-8 file from Example A with `StandardCharsets.ISO_8859_1` and inspect the garbled result, which shows the bytes were fine and only the decoding changed.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
