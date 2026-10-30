# java-026: Packages, classpaths and modules

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-025`

## Learning objectives

Explain package, classpath, named module, export using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Read `String.class` module and package names. The final exercise transfers the mechanism to reject a missing module dependency.

## Purpose and mental model

Packages organize class names and access boundaries. Aclasspath tells the runtime where unnamed-module classes can be found;it does not change the package declared in source. Java's module system adds explicit requires and exports relationships. Apublic class in a package is not automatically accessible from another named module unless the package is exported. Module boundaries therefore add a level beyond public/private declarations.

This lesson includes a real two-module source fixture:a greeting library exports its package,and an application requires that module. The defaultMain.java diagnostic writes the same tiny fixture into an owned temporary directory,invokes the prepared JDK compiler,inspects module descriptors and runs the application in a bounded child JVM. No external dependency is downloaded. The separate checked-in fixture and manual commands let a learner inspect the file layout directly.

## Vocabulary and concepts

**Package:** A namespace and access grouping declared by a Java source file.

**Classpath:** Locations used to find classes in the unnamed-module model.

**Named module:** A unit declaring dependencies and exported packages.

**Export:** Permission for other modules to access a package's publicAPI.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-026/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.

## Manual module source tree

The [two-module fixture](../fixtures/java-026/README.md) contains the exact source layout and repository-root compile/run commands. The default pad remains Main.java and creates an equivalent owned temporary fixture. No external dependency is required.

## Syntax anatomy and execution trace

The source root contains one directory per module,each withmodule-info.java and package directories. javac --module-source-path selects that layout and-m names the modules to compile. java --module-path selects compiled modules and-mmodule/class starts the application. ModuleFinder reads descriptors without treating filenames as module identities. The child process uses a fixed local Java executable and bounded wait. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Worked example / walkthrough

### Example A: Inspect a platform module

The fully qualified class name,package and module are distinct identities. Apackage name alone does not establish module membership.

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

**Expected:** module `java.base`;package `java.lang`.

### Example B: Inspect the classroom classpath context

The classroom compiles a singleMain.java andlaunches it by classpath. The separate fixture demonstrates named-module execution rather than pretending the pad itself is modular.

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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Inspect a platform module.** Read `String.class` module and package names.
   **Expected:** module `java.base`;package `java.lang`.
   **Verify:** Compare your assertion values or captured diagnostic with module `java.base`;package `java.lang`.

2. **Inspect the classroom classpath context.** ReadMain.class module metadata.
   **Expected:** Main belongs to the unnamed module in the standard classpath launch.
   **Verify:** Compare your assertion values or captured diagnostic with Main belongs to the unnamed module in the standard classpath launch.

3. **Compile two real modules.** Create the owned greeting/application fixture and compile both with--module-source-path.
   **Expected:** compiler exit 0 andmodule-info.class files present.
   **Verify:** Compare your assertion values or captured diagnostic with compiler exit 0 andmodule-info.class files present.

4. **Inspect declared dependencies and exports.** Read the compiled descriptors with ModuleFinder.
   **Expected:** app requirescourse.greeting;library exportsedu.example.greeting.
   **Verify:** Compare your assertion values or captured diagnostic with app requirescourse.greeting;library exportsedu.example.greeting.

5. **Run the modular application.** Launch the compiled app in a fresh childJVM with the fixed module path.
   **Expected:** stdoutHello, modules! andexit0.
   **Verify:** Compare your assertion values or captured diagnostic with stdoutHello, modules! andexit0.

6. **Reject a missing module dependency.** Compile an app requiringcourse.missing instead ofcourse.greeting.
   **Expected:** nonzero compiler exit and captured diagnostic.
   **Verify:** Compare your assertion values or captured diagnostic with nonzero compiler exit and captured diagnostic.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Package, Classpath, Named module in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/module/ModuleFinder.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-026: Packages, classpaths and modules.
Read courses/java/guides/java-026.md and courses/java/lessons/java-026.java. Direct prerequisites: `java-025`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
