# java-036: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

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

Task: Copy Example A into a scratch `Main.java` and change `assert magic == 0xCAFEBABE && major == 65;` to `assert magic == 0xCAFEBABE && major == 66;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.

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

**Expected:** The changed run fails with an `AssertionError` from the assertion on `magic == 0xCAFEBABE && major == 65`. Restoring the original line brings back the worked observation: magic CAFEBABE; major version 65.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `magic == 0xCAFEBABE && major == 65`. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Inspect packaged launch metadata: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App!") &&`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

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

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class") != null`; after it the line reads `assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") &&` again and main-Class App; class entry present.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class") != null` accepts.

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

**Verify:** Keep an assertion equivalent to `result.code() == 0 && result.output().strip().equals("release-ok")`. As a control, change `Run result = fixture.run("--self-test");` to `Run result = fixture.run("--self-test!");`: the run must fail with an `AssertionError` from the assertion on `result.code() == 0 && result.output().strip().equals("release-ok")`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `result.code() == 2 && result.error().contains("unknown argument")`. As a control, change `assert result.code() == 2 && result.error().contains("unknown argument");` to `assert result.code() == 2 && result.error().contains("unknown argument!");` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `rejected`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `receipt.get("previous_artifact").equals("v1") && receipt.get("custom_runtime_built").equals(false) && receipt.get("production_deployed").equals(false)`. As a control, change `"v1",` to `"v2",`: the run must fail with an `AssertionError` from the assertion on `receipt.get("previous_artifact").equals("v1") && receipt.get("custom_runtime_built").equals(false) && receipt.get("production_deployed").equals(false)`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
