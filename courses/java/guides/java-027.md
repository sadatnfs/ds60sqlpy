# java-027: Builds and dependency reproducibility

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-026`

## Learning objectives

Build a runnable JAR reproducibly and detect when a changed source produces a different artifact.

The six exercises practice these steps:

- Compile a literal application.
- Create a runnable archive.
- Compare two builds with fixed metadata.
- Execute the packaged entrypoint.
- Detect a changed source identity.
- Record an explicit dependency contract.

## Purpose and mental model

A build turns source and declared dependencies into an artifact. Reproducibility requires identifying the compiler, target level, inputs, dependency versions and packaging metadata. A source repository alone is not enough if a build fetches moving dependency versions or embeds timestamps that change every run. Maven and Gradle can manage larger builds, but their configuration still needs explicit versions, verification and offline preparation. This default lesson uses only the JDK'sjavac and jar tools on a literal source fixture.

The example compiles one small application, packages it twice with a fixed archive timestamp, and compares the resulting bytes in the same prepared JDK environment. It then executes the JAR. This establishes a bounded local reproducibility property, not byte-identical builds across every JDK or OS. A dependency lock or checksum is an identity control, not proof that a dependency is safe or appropriate.

## Vocabulary and concepts

**Build input:** Source, toolchain and dependency state used to produce an artifact.

**Reproducible artifact:** An output matching a declared byte-identity contract under fixed inputs.

**Dependency pin:** An exact version or hash identifying a required component.

**JAR:** A Java archive containing classes, resources and optional launch metadata.

## How to run this lesson

`BuildFixture` writes `Hello.java` into an owned temporary directory, compiles it with the JDK's in-process compiler, packages it with the `jar` tool and a fixed `--date`, and runs the archive in a child JVM with a five-second limit.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).

## Manual build fixture

The [JAR fixture](../fixtures/java-027/README.md) provides the matching source and explicit javac/jar commands for a fresh learner-owned output directory. The reference's fixed-timestamp byte comparison applies only to its prepared JDK environment.

## Syntax anatomy and execution trace

The JavaCompiler API invokes the prepared compiler with --release 21. The JDK jar tool can be accessed through java.util.spi.ToolProvider and given a fixed --date plus --main-class. Package only the intended classes directory. SHA256 compares artifact bytes; use a fresh child JVM to prove the JAR entrypoint works. A changed source or dependency identity should change the recorded build manifest. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Worked example / walkthrough

### Example A: Compile a literal application

The compiler target is explicit. A file named.class would not by itself prove that the source compiled successfully.

```java
import java.util.*;

public class Main {

  static final class BuildFixture implements AutoCloseable {

    final java.nio.file.Path root, source, classes;

    BuildFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-build-");
      source = root.resolve("Hello.java");
      classes = root.resolve("classes");
      java.nio.file.Files.createDirectories(classes);
      java.nio.file.Files.writeString(
        source,
        "public class Hello { public static void main(String[] args){System.out.println(\"build-ok\");} }"
      );
    }

    int compile() {
      var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
      if (compiler == null) throw new IllegalStateException("JDK required");
      return compiler.run(
        null,
        null,
        null,
        "--release",
        "21",
        "-d",
        classes.toString(),
        source.toString()
      );
    }

    java.nio.file.Path pack(String name) throws Exception {
      var target = root.resolve(name);
      var jar = java.util.spi.ToolProvider.findFirst("jar").orElseThrow();
      var output = new java.io.StringWriter();
      int result = jar.run(
        new java.io.PrintWriter(output),
        new java.io.PrintWriter(output),
        "--create",
        "--file",
        target.toString(),
        "--main-class",
        "Hello",
        "--date=2020-01-01T00:00:02Z",
        "-C",
        classes.toString(),
        "."
      );
      if (result != 0) throw new AssertionError(output.toString());
      return target;
    }

    String childStderr = "";

    String run(java.nio.file.Path jar) throws Exception {
      String executable = java.nio.file.Path.of(
        System.getProperty("java.home"),
        "bin",
        "java"
      ).toString();
      var stdout = root.resolve("child.stdout");
      var stderr = root.resolve("child.stderr");
      var process = new ProcessBuilder(executable, "-ea", "-jar", jar.toString())
        .redirectOutput(stdout.toFile())
        .redirectError(stderr.toFile())
        .start();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError("JAR timeout");
      }
      String text = java.nio.file.Files.readString(stdout);
      childStderr = java.nio.file.Files.readString(stderr);
      if (process.exitValue() != 0) throw new AssertionError(
        "child exit " + process.exitValue() + ": " + childStderr
      );
      return text;
    }

    public void close() throws java.io.IOException {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    try (BuildFixture fixture = new BuildFixture()) {
      int compiled = fixture.compile();
      assert compiled == 0;
      assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));
    }
  }
}
```

**Expected:** compiler exit 0; Hello.class exists.

### Example B: Create a runnable archive

The archive contains both bytecode and entrypoint metadata. These are separate checks from its filename extension.

```java
import java.util.*;

public class Main {

  static final class BuildFixture implements AutoCloseable {

    final java.nio.file.Path root, source, classes;

    BuildFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-build-");
      source = root.resolve("Hello.java");
      classes = root.resolve("classes");
      java.nio.file.Files.createDirectories(classes);
      java.nio.file.Files.writeString(
        source,
        "public class Hello { public static void main(String[] args){System.out.println(\"build-ok\");} }"
      );
    }

    int compile() {
      var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
      if (compiler == null) throw new IllegalStateException("JDK required");
      return compiler.run(
        null,
        null,
        null,
        "--release",
        "21",
        "-d",
        classes.toString(),
        source.toString()
      );
    }

    java.nio.file.Path pack(String name) throws Exception {
      var target = root.resolve(name);
      var jar = java.util.spi.ToolProvider.findFirst("jar").orElseThrow();
      var output = new java.io.StringWriter();
      int result = jar.run(
        new java.io.PrintWriter(output),
        new java.io.PrintWriter(output),
        "--create",
        "--file",
        target.toString(),
        "--main-class",
        "Hello",
        "--date=2020-01-01T00:00:02Z",
        "-C",
        classes.toString(),
        "."
      );
      if (result != 0) throw new AssertionError(output.toString());
      return target;
    }

    String childStderr = "";

    String run(java.nio.file.Path jar) throws Exception {
      String executable = java.nio.file.Path.of(
        System.getProperty("java.home"),
        "bin",
        "java"
      ).toString();
      var stdout = root.resolve("child.stdout");
      var stderr = root.resolve("child.stderr");
      var process = new ProcessBuilder(executable, "-ea", "-jar", jar.toString())
        .redirectOutput(stdout.toFile())
        .redirectError(stderr.toFile())
        .start();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError("JAR timeout");
      }
      String text = java.nio.file.Files.readString(stdout);
      childStderr = java.nio.file.Files.readString(stderr);
      if (process.exitValue() != 0) throw new AssertionError(
        "child exit " + process.exitValue() + ": " + childStderr
      );
      return text;
    }

    public void close() throws java.io.IOException {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    try (BuildFixture fixture = new BuildFixture()) {
      int compiled = fixture.compile();
      assert compiled == 0;
      assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));
    }

    try (BuildFixture fixture = new BuildFixture()) {
      int compiled = fixture.compile();
      assert compiled == 0;
      var jar = fixture.pack("one.jar");
      try (var archive = new java.util.jar.JarFile(jar.toFile())) {
        assert archive.getJarEntry("Hello.class") != null;
        assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello");
      }
    }
  }
}
```

**Expected:** JAR exists and contains Hello.class.

## Prediction before your attempt

Before running Example A, decide what proves that `Hello.java` compiled: the compiler exit code, the `.class` file, or both. For Example B, predict what `Main-Class` value the manifest holds after `jar --main-class Hello`. Before Exercise 3, decide whether two archives packed from the same class files with the same `--date` will have equal SHA-256 digests, and what would differ if each used the current time.

## Exercises

1. **Compile a literal application: predict an edited check.** Change Example A's assertion to `assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class!"));`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`.

2. **Create a runnable archive: diagnose an edited check.** Example B's new assertion was edited to `assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello!");`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")` accepts.

3. **Compare two builds with fixed metadata.** Package the same classes twice with the same timestamp.
   **Expected:** archive byte hashes equal in this prepared JDK.
   **Verify:** Control: changing `assert compiled == 0;` to `assert compiled != 0;` inside the assertion must make it fail.

4. **Execute the packaged entrypoint.** Run the JAR in a bounded child JVM.
   **Expected:** stdout build-ok; exit 0.
   **Verify:** Control: changing `assert output.strip().equals("build-ok");` to `assert output.strip().equals("build-ok!");` inside the assertion must make it fail.

5. **Detect a changed source identity.** Hash two source strings differing in their printed message.
   **Expected:** different SHA-256 digests.
   **Verify:** Control: changing `"class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` to `"class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` must fail the assertion on `!Arrays.equals(first, second)`.

6. **Record an explicit dependency contract.** Represent H2 as version 2.5.252 with a required verified hash field and reject a moving LATEST label.
   **Expected:** exact version accepted; LATEST not treated as a pin.
   **Verify:** Control: changing `"2.5.252",` to `"3.5.252",` must fail the assertion on `dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST")`.

## Common pitfalls and diagnosis

Floating versions such as `LATEST` or open ranges make two builds of the same commit pull different code, so a pin names one exact version and a checksum confirms the bytes. Archive timestamps differ on every build unless they are fixed, so identical code yields different hashes. Matching hashes prove identity, not safety or correctness. And a JAR with the right classes but a missing `Main-Class` entry fails at startup, which is why Exercise 4 runs the artifact.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the in-check edit looks for "Hello.class!" in the classes directory. Then recall that the compiler writes `Hello.class` for the public class `Hello`. Finally, explain why the exit code check passed but the file lookup fails.
- **Exercise 2:** First note that the in-check edit expects the manifest `Main-Class` to equal "Hello!". Then read what `pack` passed with `--main-class Hello`. Finally, explain why the `Hello.class` entry check passed and only the manifest comparison fails.
- **Exercise 3:** First compile the fixture once and pack it twice with the same `--date`. Then hash both archives with `MessageDigest.getInstance("SHA-256")`. Finally, assert that the digests are equal with `Arrays.equals` and name the input you fixed to make that possible.
- **Exercise 4:** First compile and pack the fixture. Then call `run(jar)`, which starts `java -jar` in a child process with a bound. Finally, assert that the trimmed standard output is "build-ok" and explain what a missing manifest entry would cause.
- **Exercise 5:** First hash the source text `class A { int x=1; }` with SHA-256. Then hash the version where `x` is 2. Finally, assert that the two digests differ and explain why one changed character must produce a new artifact identity.
- **Exercise 6:** First record the H2 coordinate, the exact version 2.5.252 and a hash policy in a map. Then assert that the version equals 2.5.252 and is not "LATEST". Finally, explain why the policy must point to a verified checksum rather than an invented one.

## Self-check and retrieval

Without the guide, list the build inputs that must be fixed for two archives to match byte for byte. Explain what the `--date` option controls, why Exercise 4 runs the JAR after hashing it, and why a version pin plus a verified hash is stronger than a version name alone.

## Next step

Continue with `java-028`: HTTP services and clients. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jar.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-027: Builds and dependency reproducibility.
Read courses/java/guides/java-027.md and courses/java/lessons/java-027.java. Direct prerequisites: `java-026`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
