# java-016: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A path names a location; it is not the file contents or a guarantee that the location exists. Filesystem operations can fail because of permissions,missing parents,encoding errors or concurrent changes. Choose an explicit character encoding so text has the same meaning across machines. Temporary directories provide owned scratch space,while try-with-resources closes streams that otherwise retain file handles. Replacing a file atomically is a filesystem capability,not a universal property of every move. If atomic replacement is required,fail clearly when unsupported instead of silently claiming the same guarantee from a non-atomic fallback.

**Path:** A typed representation of a filesystem location.

**Encoding:** A rule translating text characters to bytes and back.

**Atomic move:** A replacement operation observed as one filesystem action when supported.

## Reading the reference

Path.resolve appends a child path,normalize removes lexicaldot segments,andtoRealPath consults the filesystem. Files.writeString/readString acceptStandardCharsets.UTF_8. Files.list andFiles.walk return streams that must close. Files.move withATOMIC_MOVE requests atomicity and may throwAtomicMoveNotSupportedException. The helper creates one owned temporary directory and deletes only its contents in a finally block.

## Exercise 1: Round-trip explicit UTF-8

Task: WriteCafé and an emoji to an owned temporary file,then read it withUTF-8.

Explicit encoding avoids dependence on platform defaults. The round trip tests both byte writing and reading,not just aString kept in memory.

```java
withTemp(root -> {
    var path = root.resolve("text.txt"); String text = "Café 🙂";
    java.nio.file.Files.writeString(path,text,java.nio.charset.StandardCharsets.UTF_8);
    assert java.nio.file.Files.readString(path,java.nio.charset.StandardCharsets.UTF_8).equals(text);
});
```

**Expected:** exact text equality.

**Verify:** Compare the program values or named exception with exact text equality. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Distinguish a path from existence

Task: Resolve a missing child inside the temporary directory and inspect existence before creating it.

Constructing aPath does not create a file. Keeping those actions separate prevents accidental assumptions about setup state.

```java
withTemp(root -> {
    var missing = root.resolve("missing.txt");
    assert missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing);
});
```

**Expected:** path object exists;filesystem entry absent.

**Verify:** Compare the program values or named exception with path object exists;filesystem entry absent. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Close a directory stream

Task: Create two files and count them through atry-with-resourcesFiles.list stream.

The stream can hold a directory resource until closed. A terminal operation alone is not the ownership policy for anI/O-backed stream.

```java
withTemp(root -> {
    java.nio.file.Files.writeString(root.resolve("a.txt"),"a"); java.nio.file.Files.writeString(root.resolve("b.txt"),"b");
    try(var entries = java.nio.file.Files.list(root)) { assert entries.count() == 2; }
});
```

**Expected:** count2.

**Verify:** Compare the program values or named exception with count2. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Request atomic replacement honestly

Task: Write old and staged files,requestATOMIC_MOVE,then verify the selected outcome without claiming a fallback is atomic.

The branch reports a capability limit rather than silently weakening the contract. Atomic replacement also does not by itself prove durable persistence after a power loss.

```java
withTemp(root -> {
    var target=root.resolve("target.txt"); var staged=root.resolve("staged.txt");
    java.nio.file.Files.writeString(target,"old"); java.nio.file.Files.writeString(staged,"new");
    try {
        java.nio.file.Files.move(staged,target,java.nio.file.StandardCopyOption.ATOMIC_MOVE,java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        assert java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged);
    } catch(java.nio.file.AtomicMoveNotSupportedException expected) {
        assert java.nio.file.Files.readString(target).equals("old");
    }
});
```

**Expected:** either targetnew withstagedabsent,or explicit unsupported result retainingold.

**Verify:** Compare the program values or named exception with either targetnew withstagedabsent,or explicit unsupported result retainingold. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Expose a lexical path escape

Task: Resolve../outside under an owned root and normalize it before checking containment.

Lexical containment is useful but does not resolve symlinks. A security-sensitive file boundary needs real-path and ownership checks as discussed later.

```java
withTemp(root -> {
    var candidate=root.resolve("../outside").normalize();
    assert !candidate.startsWith(root.normalize());
});
```

**Expected:** normalized path is outside the root.

**Verify:** Compare the program values or named exception with normalized path is outside the root. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Verify cleanup after failure

Task: Throw inside the owned temporary scope and confirm the directory is removed by the helper.

Cleanup should run on both paths while preserving the primary failure. It must remain confined to the directory this exercise created.

```java
final java.nio.file.Path[] created={null}; boolean propagated=false;
try { withTemp(root -> { created[0]=root; throw new java.io.IOException("fixture failure"); }); }
catch(java.io.IOException expected) { propagated=expected.getMessage().equals("fixture failure"); }
assert propagated && created[0]!=null && !java.nio.file.Files.exists(created[0]);
```

**Expected:** original exception propagated;owned directory absent.

**Verify:** Compare the program values or named exception with original exception propagated;owned directory absent. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
