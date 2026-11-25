# java-036: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A release is a reproducible artifact plus evidence about how it starts, what contracts it accepts and how failures are diagnosed. Source compilation alone does not prove that packaging preserved the entrypoint or that the target runtime supports the class version. Hashes identify artifact bytes, but a valid hash does not establish correct behavior. A deliberate failing integrity check proves that the gate is connected to the decision rather than merely printing a success label.

This capstone builds a small Java 21 JAR with a fixed timestamp, checks class-file version 65, executes a self-test in a fresh JVM and rejects both an invalid launch argument and tampered artifact bytes. It retains a previous-artifact identity in the release record. jlink is explained as a separate custom-runtime packaging step; the default reference only probes tool availability and does not build a large runtime image inside the bounded browser job. Production deployment and operational acceptance remain separate from this local artifact check.

**Release artifact:** The packaged program and metadata intended for distribution.

**Class-file version:** The bytecode format level required by a JVM.

**Integrity gate:** A check that artifact bytes match the expected identity.

**Custom runtime image:** A platform-specificJava runtime assembled from selected modules.

## Reading the reference

Use the prepared compiler with --release 21, then inspect the class magic and major version through DataInputStream. Package with the JDK jar tool and an explicit Main-Class. Launch the artifact using a fixed local java executable with bounded wait and captured output. SHA256 verification occurs before execution. A manual jlink recipe must name required modules, an owned output directory and actual platform; it cannot create one universal runtime for everyOS/architecture. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Exercise 1: Verify the compiler target: predict an edited check

Task: Change Example A's assertion to `assert magic == 0xCAFEBABE && major == 66;`, predict whether it holds, then run and restore it.

The header is direct evidence of the target bytecode level. A filename or README claim cannot replace it.

The unchanged code is the part that Example A adds:

```java
try (ReleaseFixture fixture = new ReleaseFixture()) {
  fixture.build();
  try (
    var input = new java.io.DataInputStream(
      java.nio.file.Files.newInputStream(fixture.classes.resolve("App.class"))
    )
  ) {
    int magic = input.readInt();
    input.readUnsignedShort();
    int major = input.readUnsignedShort();
    assert magic == 0xCAFEBABE && major == 65;
  }
}
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `magic == 0xCAFEBABE && major == 65`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `magic == 0xCAFEBABE && major == 65`.

## Exercise 2: Inspect packaged launch metadata: diagnose an edited check

Task: Example B's new assertion was edited to `assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App!") &&`. Explain why it fails for unchanged state and restore it.

Packaging can fail independently of compilation. The archive must contain the intended entrypoint and matching metadata.

The unchanged code is the part that Example B adds:

```java
try (ReleaseFixture fixture = new ReleaseFixture()) {
  fixture.build();
  try (var jar = new java.util.jar.JarFile(fixture.jar.toFile())) {
    assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") &&
    jar.getJarEntry("App.class") != null;
  }
}
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class") != null`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class") != null` accepts.

## Exercise 3: Run a fresh-process self-test

Task: Launch the JAR with --self-test through a bounded child JVM.

The new process cannot reuse classes loaded by the authoring program. This checks the actual packaged launch path.

```java
try (ReleaseFixture fixture = new ReleaseFixture()) {
  fixture.build();
  Run result = fixture.run("--self-test");
  assert result.code() == 0 && result.output().strip().equals("release-ok");
}
```

**Expected:** exit 0 and output release-ok.

**Verify:** Control: changing `Run result = fixture.run("--self-test");` to `Run result = fixture.run("--self-test!");` must fail the assertion on `result.code() == 0 && result.output().strip().equals("release-ok")`.

## Exercise 4: Verify an invalid launch fails clearly

Task: Run the same JAR with an unsupported argument.

An acceptance suite should include a meaningful failure path. Returning exit 0 for every argument would make automation unable to distinguish misuse.

```java
try (ReleaseFixture fixture = new ReleaseFixture()) {
  fixture.build();
  Run result = fixture.run("--unsupported");
  assert result.code() == 2 && result.error().contains("unknown argument");
}
```

**Expected:** exit 2 and unknown argument diagnostic.

**Verify:** Control: changing `assert result.code() == 2 && result.error().contains("unknown argument");` to `assert result.code() == 2 && result.error().contains("unknown argument!");` inside the assertion must make it fail.

## Exercise 5: Reject artifact tampering before execution

Task: Hash the JAR, flip one byte, and call the integrity gate.

The corrupt artifact is never executed. A hash check verifies byte identity, while the self-test separately verifies behavior.

```java
try (ReleaseFixture fixture = new ReleaseFixture()) {
  fixture.build();
  byte[] original = java.nio.file.Files.readAllBytes(fixture.jar);
  byte[] expected = sha256(original);
  byte[] changed = original.clone();
  changed[0] ^= 1;
  java.nio.file.Files.write(fixture.jar, changed);
  boolean rejected = false;
  try {
    verify(fixture.jar, expected);
  } catch (SecurityException failure) {
    rejected = true;
  } finally {
    java.nio.file.Files.write(fixture.jar, original);
  }
  assert rejected;
  verify(fixture.jar, expected);
}
```

**Expected:** SecurityException; original bytes restored for cleanup.

**Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected`.

## Exercise 6: Record runtime-image scope and rollback identity

Task: Inspect whether jlink exists, and write a record distinguishing local JAR acceptance from an unbuilt custom runtime.

Tool presence is not a runtime-image build receipt. A manual jlink build needs its own module closure, platform, launch and failure checks before distribution.

```java
var jlink = java.nio.file.Path.of(System.getProperty("java.home"), "bin", "jlink");
Map<String, Object> receipt = Map.of(
  "jar_contract_checked",
  true,
  "previous_artifact",
  "v1",
  "jlink_tool_present",
  java.nio.file.Files.isExecutable(jlink),
  "custom_runtime_built",
  false,
  "production_deployed",
  false
);
assert receipt.get("previous_artifact").equals("v1") &&
receipt.get("custom_runtime_built").equals(false) &&
receipt.get("production_deployed").equals(false);
```

**Expected:** previous artifact v1 retained; custom_runtime_built False.

**Verify:** Control: changing `"v1",` to `"v2",` must fail the assertion on `receipt.get("previous_artifact").equals("v1") && receipt.get("custom_runtime_built").equals(false) && receipt.get("production_deployed").equals(false)`.

## After comparing the answer

Add a `--version` argument to your copy of `App` that prints 1.0.0 and exits 0, rebuild, and add a fresh-process check for it next to the self-test.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
