# java-027: Builds and dependency reproducibility

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-026`

## Learning objectives

Build a runnable JAR reproducibly and detect when a changed source produces a different artifact. Along the way, explain build input, reproducible artifact, dependency pin, jar using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Package the same classes twice with the same timestamp. The final exercise transfers the mechanism to record an explicit dependency contract.

## Purpose and mental model

A build turns source and declared dependencies into an artifact. Reproducibility requires identifying the compiler, target level, inputs, dependency versions and packaging metadata. A source repository alone is not enough if a build fetches moving dependency versions or embeds timestamps that change every run. Maven and Gradle can manage larger builds, but their configuration still needs explicit versions, verification and offline preparation. This default lesson uses only the JDK'sjavac and jar tools on a literal source fixture.

The example compiles one small application, packages it twice with a fixed archive timestamp, and compares the resulting bytes in the same prepared JDK environment. It then executes the JAR. This establishes a bounded local reproducibility property, not byte-identical builds across every JDK or OS. A dependency lock or checksum is an identity control, not proof that a dependency is safe or appropriate.

## Vocabulary and concepts

**Build input:** Source, toolchain and dependency state used to produce an artifact.

**Reproducible artifact:** An output matching a declared byte-identity contract under fixed inputs.

**Dependency pin:** An exact version or hash identifying a required component.

**JAR:** A Java archive containing classes, resources and optional launch metadata.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-027/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.

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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Compile a literal application: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));` to `assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class!"));` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`. Restoring the original line brings back the worked observation: compiler exit 0; Hello.class exists.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`. After restoring the line, the program completes without an `AssertionError` again.

2. **Create a runnable archive: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello!");`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")`; after it the line reads `assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello");` again and JAR exists and contains Hello.class.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")` accepts.

3. **Compare two builds with fixed metadata.** Package the same classes twice with the same timestamp.
   **Expected:** archive byte hashes equal in this prepared JDK.
   **Verify:** Keep an assertion equivalent to `compiled == 0`. As a control, change `assert compiled == 0;` to `assert compiled != 0;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

4. **Execute the packaged entrypoint.** Run the JAR in a bounded child JVM.
   **Expected:** stdout build-ok; exit 0.
   **Verify:** Keep an assertion equivalent to `output.strip().equals("build-ok")`. As a control, change `assert output.strip().equals("build-ok");` to `assert output.strip().equals("build-ok!");` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

5. **Detect a changed source identity.** Hash two source strings differing in their printed message.
   **Expected:** different SHA-256 digests.
   **Verify:** Keep an assertion equivalent to `!Arrays.equals(first, second)`. As a control, change `"class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` to `"class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)`: the run must fail with an `AssertionError` from the assertion on `!Arrays.equals(first, second)`. Restore the line before continuing.

6. **Record an explicit dependency contract.** Represent H2 as version 2.5.252 with a required verified hash field and reject a moving LATEST label.
   **Expected:** exact version accepted; LATEST not treated as a pin.
   **Verify:** Keep an assertion equivalent to `dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST")`. As a control, change `"2.5.252",` to `"3.5.252",`: the run must fail with an `AssertionError` from the assertion on `dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST")`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: compiler exit 0; Hello.class exists. Then list the values read by `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))` and trace each one from its declaration. Finally, compute the asserted value with `assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class!"));` in place before running.
- **Exercise 2:** First restate the expected observation: JAR exists and contains Hello.class. Then list the values read by `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")` and trace each one from its declaration. Finally, compare `assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello!");` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: archive byte hashes equal in this prepared JDK. Then list the values read by `compiled == 0` and trace each one from its declaration. Finally, name one input that would make `compiled == 0` false.
- **Exercise 4:** First restate the expected observation: stdout build-ok; exit 0. Then list the values read by `output.strip().equals("build-ok")` and trace each one from its declaration. Finally, name one input that would make `output.strip().equals("build-ok")` false.
- **Exercise 5:** First restate the expected observation: different SHA-256 digests. Then list the values read by `!Arrays.equals(first, second)` and trace each one from its declaration. Finally, predict the effect of changing `"class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` to `"class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` before running anything.
- **Exercise 6:** First restate the expected observation: exact version accepted; LATEST not treated as a pin. Then list the values read by `dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST")` and trace each one from its declaration. Finally, predict the effect of changing `"2.5.252",` to `"3.5.252",` before running anything.

## Self-check and retrieval

Close the solution and explain Build input, Reproducible artifact, Dependency pin in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jar.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
