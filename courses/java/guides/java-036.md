# java-036: Package, diagnose and maintain a release

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-035`

## Learning objectives

Package, self-test and verify a release artifact, rejecting tampering before execution and recording its runtime scope.

The six exercises practice these steps:

- Verify the compiler target.
- Inspect packaged launch metadata.
- Run a fresh-process self-test.
- Verify an invalid launch fails clearly.
- Reject artifact tampering before execution.
- Record runtime-image scope and rollback identity.

## Purpose and mental model

A release is a reproducible artifact plus evidence about how it starts, what contracts it accepts and how failures are diagnosed. Source compilation alone does not prove that packaging preserved the entrypoint or that the target runtime supports the class version. Hashes identify artifact bytes, but a valid hash does not establish correct behavior. A deliberate failing integrity check proves that the gate is connected to the decision rather than merely printing a success label.

This capstone builds a small Java 21 JAR with a fixed timestamp, checks class-file version 65, executes a self-test in a fresh JVM and rejects both an invalid launch argument and tampered artifact bytes. It retains a previous-artifact identity in the release record. jlink is explained as a separate custom-runtime packaging step; the default reference only probes tool availability and does not build a large runtime image inside the bounded browser job. Production deployment and operational acceptance remain separate from this local artifact check.

## Vocabulary and concepts

**Release artifact:** The packaged program and metadata intended for distribution.

**Class-file version:** The bytecode format level required by a JVM.

**Integrity gate:** A check that artifact bytes match the expected identity.

**Custom runtime image:** A platform-specificJava runtime assembled from selected modules.

## How to run this lesson

`ReleaseFixture` writes `App.java` into an owned temporary directory, compiles it with `--release 21`, packages a JAR with a fixed timestamp, launches it in a child JVM with a five-second limit, and deletes everything in `close`.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).

## Packaging scope

The default reference creates only small owned source, class and JAR fixtures. It does not build a custom runtime image or deploy a service. The separate [manual release fixture](../fixtures/java-036/README.md) explains a deliberate jlink workflow and the additional disk/platform checks needed. Keep generated images under an ignored learner-owned directory, not in course source or an ephemeral pad.


## Syntax anatomy and execution trace

Use the prepared compiler with --release 21, then inspect the class magic and major version through DataInputStream. Package with the JDK jar tool and an explicit Main-Class. Launch the artifact using a fixed local java executable with bounded wait and captured output. SHA256 verification occurs before execution. A manual jlink recipe must name required modules, an owned output directory and actual platform; it cannot create one universal runtime for everyOS/architecture. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Worked example / walkthrough

### Example A: Verify the compiler target

The header is direct evidence of the target bytecode level. A filename or README claim cannot replace it.

```java
import java.util.*;

public class Main {

  record Run(int code, String output, String error) {}

  static byte[] sha256(byte[] bytes) throws Exception {
    return java.security.MessageDigest.getInstance("SHA-256").digest(bytes);
  }

  static void verify(java.nio.file.Path artifact, byte[] expected) throws Exception {
    if (
      !Arrays.equals(sha256(java.nio.file.Files.readAllBytes(artifact)), expected)
    ) throw new SecurityException("artifact hash mismatch");
  }

  static final class ReleaseFixture implements AutoCloseable {

    final java.nio.file.Path root, source, classes, jar;

    ReleaseFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-release-");
      source = root.resolve("App.java");
      classes = root.resolve("classes");
      jar = root.resolve("app.jar");
      java.nio.file.Files.createDirectories(classes);
      java.nio.file.Files.writeString(
        source,
        "public class App { public static void main(String[] args){if(args.length==1 && args[0].equals(\"--self-test\")){System.out.println(\"release-ok\");}else{System.err.println(\"unknown argument\");System.exit(2);}} }"
      );
    }

    void build() throws Exception {
      var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
      if (
        compiler == null ||
        compiler.run(
          null,
          null,
          null,
          "--release",
          "21",
          "-d",
          classes.toString(),
          source.toString()
        ) !=
        0
      ) throw new AssertionError("compile failed");
      var tool = java.util.spi.ToolProvider.findFirst("jar").orElseThrow();
      var messages = new java.io.StringWriter();
      int code = tool.run(
        new java.io.PrintWriter(messages),
        new java.io.PrintWriter(messages),
        "--create",
        "--file",
        jar.toString(),
        "--main-class",
        "App",
        "--date=2020-01-01T00:00:02Z",
        "-C",
        classes.toString(),
        "."
      );
      if (code != 0) throw new AssertionError(messages.toString());
    }

    Run run(String argument) throws Exception {
      String executable = java.nio.file.Path.of(
        System.getProperty("java.home"),
        "bin",
        "java"
      ).toString();
      var stdout = root.resolve("child.stdout");
      var stderr = root.resolve("child.stderr");
      var process = new ProcessBuilder(executable, "-ea", "-jar", jar.toString(), argument)
        .redirectOutput(stdout.toFile())
        .redirectError(stderr.toFile())
        .start();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError("release child timeout");
      }
      return new Run(
        process.exitValue(),
        java.nio.file.Files.readString(stdout),
        java.nio.file.Files.readString(stderr)
      );
    }

    public void close() throws java.io.IOException {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
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
  }
}
```

**Expected:** magic CAFEBABE; major version 65.

### Example B: Inspect packaged launch metadata

Packaging can fail independently of compilation. The archive must contain the intended entrypoint and matching metadata.

```java
import java.util.*;

public class Main {

  record Run(int code, String output, String error) {}

  static byte[] sha256(byte[] bytes) throws Exception {
    return java.security.MessageDigest.getInstance("SHA-256").digest(bytes);
  }

  static void verify(java.nio.file.Path artifact, byte[] expected) throws Exception {
    if (
      !Arrays.equals(sha256(java.nio.file.Files.readAllBytes(artifact)), expected)
    ) throw new SecurityException("artifact hash mismatch");
  }

  static final class ReleaseFixture implements AutoCloseable {

    final java.nio.file.Path root, source, classes, jar;

    ReleaseFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-release-");
      source = root.resolve("App.java");
      classes = root.resolve("classes");
      jar = root.resolve("app.jar");
      java.nio.file.Files.createDirectories(classes);
      java.nio.file.Files.writeString(
        source,
        "public class App { public static void main(String[] args){if(args.length==1 && args[0].equals(\"--self-test\")){System.out.println(\"release-ok\");}else{System.err.println(\"unknown argument\");System.exit(2);}} }"
      );
    }

    void build() throws Exception {
      var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
      if (
        compiler == null ||
        compiler.run(
          null,
          null,
          null,
          "--release",
          "21",
          "-d",
          classes.toString(),
          source.toString()
        ) !=
        0
      ) throw new AssertionError("compile failed");
      var tool = java.util.spi.ToolProvider.findFirst("jar").orElseThrow();
      var messages = new java.io.StringWriter();
      int code = tool.run(
        new java.io.PrintWriter(messages),
        new java.io.PrintWriter(messages),
        "--create",
        "--file",
        jar.toString(),
        "--main-class",
        "App",
        "--date=2020-01-01T00:00:02Z",
        "-C",
        classes.toString(),
        "."
      );
      if (code != 0) throw new AssertionError(messages.toString());
    }

    Run run(String argument) throws Exception {
      String executable = java.nio.file.Path.of(
        System.getProperty("java.home"),
        "bin",
        "java"
      ).toString();
      var stdout = root.resolve("child.stdout");
      var stderr = root.resolve("child.stderr");
      var process = new ProcessBuilder(executable, "-ea", "-jar", jar.toString(), argument)
        .redirectOutput(stdout.toFile())
        .redirectError(stderr.toFile())
        .start();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError("release child timeout");
      }
      return new Run(
        process.exitValue(),
        java.nio.file.Files.readString(stdout),
        java.nio.file.Files.readString(stderr)
      );
    }

    public void close() throws java.io.IOException {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
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

    try (ReleaseFixture fixture = new ReleaseFixture()) {
      fixture.build();
      try (var jar = new java.util.jar.JarFile(fixture.jar.toFile())) {
        assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") &&
        jar.getJarEntry("App.class") != null;
      }
    }
  }
}
```

**Expected:** Main-Class App; class entry present.

## Prediction before your attempt

Before running Example A, decide which bytes start every class file and which major version `--release 21` produces. For Example B, predict the `Main-Class` value in the manifest and whether `App.class` is a JAR entry. Before Exercise 3, decide the exit code and output when the child JVM runs the JAR with `--self-test`, and what changes for any other argument.

## Exercises

1. **Verify the compiler target: predict an edited check.** Change Example A's assertion to `assert magic == 0xCAFEBABE && major == 66;`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `magic == 0xCAFEBABE && major == 65`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `magic == 0xCAFEBABE && major == 65`.

2. **Inspect packaged launch metadata: diagnose an edited check.** Example B's new assertion was edited to `assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App!") &&`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class") != null`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class") != null` accepts.

3. **Run a fresh-process self-test.** Launch the JAR with --self-test through a bounded child JVM.
   **Expected:** exit 0 and output release-ok.
   **Verify:** Control: changing `Run result = fixture.run("--self-test");` to `Run result = fixture.run("--self-test!");` must fail the assertion on `result.code() == 0 && result.output().strip().equals("release-ok")`.

4. **Verify an invalid launch fails clearly.** Run the same JAR with an unsupported argument.
   **Expected:** exit 2 and unknown argument diagnostic.
   **Verify:** Control: changing `assert result.code() == 2 && result.error().contains("unknown argument");` to `assert result.code() == 2 && result.error().contains("unknown argument!");` inside the assertion must make it fail.

5. **Reject artifact tampering before execution.** Hash the JAR, flip one byte, and call the integrity gate.
   **Expected:** SecurityException; original bytes restored for cleanup.
   **Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected`.

6. **Record runtime-image scope and rollback identity.** Inspect whether jlink exists, and write a record distinguishing local JAR acceptance from an unbuilt custom runtime.
   **Expected:** previous artifact v1 retained; custom_runtime_built False.
   **Verify:** Control: changing `"v1",` to `"v2",` must fail the assertion on `receipt.get("previous_artifact").equals("v1") && receipt.get("custom_runtime_built").equals(false) && receipt.get("production_deployed").equals(false)`.

## Common pitfalls and diagnosis

A successful `javac` does not prove that the JAR has the right entrypoint, so inspect the manifest. Compiling with a newer JDK without `--release` produces class files an older runtime refuses with `UnsupportedClassVersionError`. Running the self-test in the same JVM can reuse already loaded classes, so launch a fresh process. A matching hash proves the bytes, not the behavior. And a tool being present is not proof that a `jlink` image was built.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the in-check edit expects major version 66. Then recall that `--release 21` writes major version 65, and 66 belongs to Java 22. Finally, explain why the magic number matched and only the version comparison fails.
- **Exercise 2:** First note that the in-check edit expects the `Main-Class` attribute to be "App!". Then read the value the `jar --main-class App` option wrote. Finally, explain why the JAR and its `App.class` entry are fine and only the expected text is wrong.
- **Exercise 3:** First build the fixture and call `fixture.run("--self-test")`, which starts a separate `java -jar` process. Then read its exit code and standard output. Finally, assert 0 and `release-ok` after stripping the trailing newline.
- **Exercise 4:** First run the same JAR with an argument that `App` does not recognize. Then read the exit code and standard error from the `Run` record. Finally, assert exit code 2 and the `unknown argument` message, and say why misuse must not exit 0.
- **Exercise 5:** First hash the JAR, flip one bit of the first byte and write it back. Then call `verify` and catch `SecurityException`, restoring the original bytes in `finally`. Finally, assert the rejection and confirm that the restored JAR passes `verify`.
- **Exercise 6:** First check whether `jlink` is executable under `java.home`. Then write a receipt that keeps `v1` as the previous artifact and records the custom runtime and production deployment as false. Finally, assert those three values and explain what tool presence does not prove.

## Self-check and retrieval

From memory, explain what class-file major version 65 means, why the self-test runs in a child JVM with a timeout, why the hash check runs before execution, and why the release record keeps the previous artifact and marks the custom runtime as not built.

## Next step

This is the last Java lesson; revisit any lesson whose contracts you cannot yet explain. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jlink.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-036: Package, diagnose and maintain a release.
Read courses/java/guides/java-036.md and courses/java/lessons/java-036.java. Direct prerequisites: `java-035`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
