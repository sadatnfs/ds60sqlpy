# java-026: Packages, classpaths and modules

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-025`

## Learning objectives

Compile and run a two-module application and read its module descriptors, exports and dependency errors.

The six exercises practice these steps:

- Inspect a platform module.
- Inspect the classroom classpath context.
- Compile two real modules.
- Inspect declared dependencies and exports.
- Run the modular application.
- Reject a missing module dependency.

## Purpose and mental model

Packages organize class names and access boundaries. A classpath tells the runtime where unnamed-module classes can be found; it does not change the package declared in source. Java's module system adds explicit requires and exports relationships. A public class in a package is not automatically accessible from another named module unless the package is exported. Module boundaries therefore add a level beyond public/private declarations.

This lesson includes a real two-module source fixture:a greeting library exports its package, and an application requires that module. The default Main.java diagnostic writes the same tiny fixture into an owned temporary directory, invokes the prepared JDK compiler, inspects module descriptors and runs the application in a bounded child JVM. No external dependency is downloaded. The separate checked-in fixture and manual commands let a learner inspect the file layout directly.

## Vocabulary and concepts

**Package:** A namespace and access grouping declared by a Java source file.

**Classpath:** Locations used to find classes in the unnamed-module model.

**Named module:** A unit declaring dependencies and exported packages.

**Export:** Permission for other modules to access a package's public API.

## How to run this lesson

`ModuleFixture` writes a two-module source tree into an owned temporary directory, compiles it with the in-process `javac` through `ToolProvider`, and runs the app in a child JVM with a five-second limit; `close` deletes everything.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).

## Manual module source tree

The [two-module fixture](../fixtures/java-026/README.md) contains the exact source layout and repository-root compile/run commands. The default pad remains Main.java and creates an equivalent owned temporary fixture. No external dependency is required.

## Syntax anatomy and execution trace

The source root contains one directory per module, each with module-info.java and package directories. javac --module-source-path selects that layout and -m names the modules to compile. java --module-path selects compiled modules and -m module/class starts the application. ModuleFinder reads descriptors without treating filenames as module identities. The child process uses a fixed local Java executable and bounded wait. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Worked example / walkthrough

### Example A: Inspect a platform module

The fully qualified class name, package and module are distinct identities. A package name alone does not establish module membership.

```java
import java.util.*;

public class Main {

  static final class ModuleFixture implements AutoCloseable {

    final java.nio.file.Path root, source, output;
    String diagnostics = "";

    ModuleFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-modules-");
      source = root.resolve("src");
      output = root.resolve("out");
      write(
        "course.greeting/module-info.java",
        "module course.greeting { exports edu.example.greeting; }"
      );
      write(
        "course.greeting/edu/example/greeting/Greeter.java",
        "package edu.example.greeting; public final class Greeter { public static String message(){return \"Hello, modules!\";} }"
      );
      write("course.app/module-info.java", "module course.app { requires course.greeting; }");
      write(
        "course.app/edu/example/app/Main.java",
        "package edu.example.app; public class Main { public static void main(String[] args){System.out.println(edu.example.greeting.Greeter.message());} }"
      );
    }

    void write(String relative, String text) throws Exception {
      var path = source.resolve(relative);
      java.nio.file.Files.createDirectories(path.getParent());
      java.nio.file.Files.writeString(path, text);
    }

    int compile() {
      var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
      if (compiler == null) throw new IllegalStateException("JDK compiler required");
      var errors = new java.io.ByteArrayOutputStream();
      int code = compiler.run(
        null,
        errors,
        errors,
        "--release",
        "21",
        "--module-source-path",
        source.toString(),
        "-d",
        output.toString(),
        "-m",
        "course.greeting,course.app"
      );
      diagnostics = errors.toString(java.nio.charset.StandardCharsets.UTF_8);
      return code;
    }

    String childStderr = "";

    String run() throws Exception {
      String executable = java.nio.file.Path.of(
        System.getProperty("java.home"),
        "bin",
        "java"
      ).toString();
      var stdout = root.resolve("child.stdout");
      var stderr = root.resolve("child.stderr");
      var process = new ProcessBuilder(
        executable,
        "-ea",
        "--module-path",
        output.toString(),
        "-m",
        "course.app/edu.example.app.Main"
      )
        .redirectOutput(stdout.toFile())
        .redirectError(stderr.toFile())
        .start();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError("child JVM timeout");
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
    assert String.class.getModule().getName().equals("java.base");
    assert String.class.getPackageName().equals("java.lang");
  }
}
```

**Expected:** module `java.base`; package `java.lang`.

### Example B: Inspect the classroom classpath context

The classroom compiles a single Main.java and launches it by classpath. The separate fixture demonstrates named-module execution rather than pretending the pad itself is modular.

```java
import java.util.*;

public class Main {

  static final class ModuleFixture implements AutoCloseable {

    final java.nio.file.Path root, source, output;
    String diagnostics = "";

    ModuleFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-modules-");
      source = root.resolve("src");
      output = root.resolve("out");
      write(
        "course.greeting/module-info.java",
        "module course.greeting { exports edu.example.greeting; }"
      );
      write(
        "course.greeting/edu/example/greeting/Greeter.java",
        "package edu.example.greeting; public final class Greeter { public static String message(){return \"Hello, modules!\";} }"
      );
      write("course.app/module-info.java", "module course.app { requires course.greeting; }");
      write(
        "course.app/edu/example/app/Main.java",
        "package edu.example.app; public class Main { public static void main(String[] args){System.out.println(edu.example.greeting.Greeter.message());} }"
      );
    }

    void write(String relative, String text) throws Exception {
      var path = source.resolve(relative);
      java.nio.file.Files.createDirectories(path.getParent());
      java.nio.file.Files.writeString(path, text);
    }

    int compile() {
      var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
      if (compiler == null) throw new IllegalStateException("JDK compiler required");
      var errors = new java.io.ByteArrayOutputStream();
      int code = compiler.run(
        null,
        errors,
        errors,
        "--release",
        "21",
        "--module-source-path",
        source.toString(),
        "-d",
        output.toString(),
        "-m",
        "course.greeting,course.app"
      );
      diagnostics = errors.toString(java.nio.charset.StandardCharsets.UTF_8);
      return code;
    }

    String childStderr = "";

    String run() throws Exception {
      String executable = java.nio.file.Path.of(
        System.getProperty("java.home"),
        "bin",
        "java"
      ).toString();
      var stdout = root.resolve("child.stdout");
      var stderr = root.resolve("child.stderr");
      var process = new ProcessBuilder(
        executable,
        "-ea",
        "--module-path",
        output.toString(),
        "-m",
        "course.app/edu.example.app.Main"
      )
        .redirectOutput(stdout.toFile())
        .redirectError(stderr.toFile())
        .start();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError("child JVM timeout");
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
    assert String.class.getModule().getName().equals("java.base");
    assert String.class.getPackageName().equals("java.lang");

    assert !Main.class.getModule().isNamed();
  }
}
```

**Expected:** Main belongs to the unnamed module in the standard classpath launch.

## Prediction before your attempt

Before running Example A, decide which module and package `String.class` belongs to. For Example B, predict whether `Main.class.getModule().isNamed()` is true when the classroom launches `Main.java` from the classpath. Before Exercise 6, predict whether compiling an app whose `module-info.java` requires `course.missing` fails at compile time or only later when the app runs.

## Exercises

1. **Inspect a platform module: predict an edited check.** Change Example A's assertion to `assert String.class.getPackageName().equals("java.lang!");`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `String.class.getPackageName().equals("java.lang")`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `String.class.getPackageName().equals("java.lang")`.

2. **Inspect the classroom classpath context: diagnose an edited check.** Example B's new assertion was edited to `assert Main.class.getModule().isNamed();`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `!Main.class.getModule().isNamed()`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `!Main.class.getModule().isNamed()` accepts.

3. **Compile two real modules.** Create the owned greeting/application fixture and compile both with --module-source-path.
   **Expected:** compiler exit 0 and module-info.class files present.
   **Verify:** Control: changing `fixture.output.resolve("course.app/module-info.class")` to `fixture.output.resolve("course.app/module-info.class!")` inside the assertion must make it fail.

4. **Inspect declared dependencies and exports.** Read the compiled descriptors with ModuleFinder.
   **Expected:** app requires course.greeting; library exports edu.example.greeting.
   **Verify:** Control: changing `.anyMatch(item -> item.source().equals("edu.example.greeting"));` to `.anyMatch(item -> item.source().equals("edu.example.greeting!"));` inside the assertion must make it fail.

5. **Run the modular application.** Launch the compiled app in a fresh child JVM with the fixed module path.
   **Expected:** stdout Hello, modules! and exit 0.
   **Verify:** Control: changing `assert output.strip().equals("Hello, modules!");` to `assert output.strip().equals("Hello, modules!!");` inside the assertion must make it fail.

6. **Reject a missing module dependency.** Compile an app requiring course.missing instead of course.greeting.
   **Expected:** nonzero compiler exit and captured diagnostic.
   **Verify:** Control: changing `fixture.source.resolve("course.app/module-info.java"),` to `fixture.source.resolve("course.app/module-info.java!"),` must fail the assertion on `compiled != 0 && !fixture.diagnostics.isBlank()`.

## Common pitfalls and diagnosis

`public` is not enough across named modules: a public class in a package that is not exported cannot be used from another module, which surprises developers coming from the classpath. Package names must match directory layout under `--module-source-path`, or `javac` rejects the tree. Mixing classpath and module path means classpath code lands in the unnamed module, which can read everything but cannot be required by name. And a missing `requires` fails at compile time, so read the diagnostic.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the in-check edit compares the package with "java.lang!". Then read `String.class.getPackageName()`, which returns "java.lang". Finally, explain why the module check on the first line passed and only the package comparison fails.
- **Exercise 2:** First note that the edit asserts `isNamed()` instead of its negation. Then recall that `Main.java` is compiled and launched from the classpath. Finally, explain why classpath classes belong to the unnamed module, which makes the edited assertion false.
- **Exercise 3:** First create a `ModuleFixture`, which writes both module descriptors and their packages. Then call `compile()` and assert exit code 0. Finally, check that `course.app/module-info.class` exists in the output directory, and say why reading a source string would prove nothing.
- **Exercise 4:** First compile the fixture and open the output with `ModuleFinder.of`. Then find `course.app` and `course.greeting` and read their descriptors. Finally, assert that the app requires the library and that the library exports `edu.example.greeting`.
- **Exercise 5:** First compile the fixture and call `run()`, which starts a child JVM with `--module-path` and `-m course.app/edu.example.app.Main`. Then read its captured standard output. Finally, assert "Hello, modules!" and explain why a fresh process rules out classes already loaded in the parent.
- **Exercise 6:** First overwrite the app descriptor with `requires course.missing`. Then call `compile()` and keep the exit code and the captured diagnostics. Finally, assert a nonzero exit code and nonblank diagnostics, and name the module the compiler could not find.

## Self-check and retrieval

From memory, explain the difference between a package, a classpath entry and a named module. State what `requires` and `exports` each declare, why the classroom `Main` lives in the unnamed module, and what the child JVM in Exercise 5 proves that compiling alone does not.

## Next step

Continue with `java-027`: Builds and dependency reproducibility. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/module/ModuleFinder.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-026: Packages, classpaths and modules.
Read courses/java/guides/java-026.md and courses/java/lessons/java-026.java. Direct prerequisites: `java-025`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
