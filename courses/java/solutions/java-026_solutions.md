# java-026: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Packages organize class names and access boundaries. A classpath tells the runtime where unnamed-module classes can be found; it does not change the package declared in source. Java's module system adds explicit requires and exports relationships. A public class in a package is not automatically accessible from another named module unless the package is exported. Module boundaries therefore add a level beyond public/private declarations.

This lesson includes a real two-module source fixture:a greeting library exports its package, and an application requires that module. The default Main.java diagnostic writes the same tiny fixture into an owned temporary directory, invokes the prepared JDK compiler, inspects module descriptors and runs the application in a bounded child JVM. No external dependency is downloaded. The separate checked-in fixture and manual commands let a learner inspect the file layout directly.

**Package:** A namespace and access grouping declared by a Java source file.

**Classpath:** Locations used to find classes in the unnamed-module model.

**Named module:** A unit declaring dependencies and exported packages.

**Export:** Permission for other modules to access a package's public API.

## Reading the reference

The source root contains one directory per module, each with module-info.java and package directories. javac --module-source-path selects that layout and -m names the modules to compile. java --module-path selects compiled modules and -m module/class starts the application. ModuleFinder reads descriptors without treating filenames as module identities. The child process uses a fixed local Java executable and bounded wait. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Exercise 1: Inspect a platform module: predict an edited check

Task: Copy Example A into a scratch `Main.java` and change `assert String.class.getPackageName().equals("java.lang");` to `assert String.class.getPackageName().equals("java.lang!");` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.

The fully qualified class name, package and module are distinct identities. A package name alone does not establish module membership.

The unchanged code is the part that Example A adds:

```java
assert String.class.getModule().getName().equals("java.base");
assert String.class.getPackageName().equals("java.lang");
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `String.class.getPackageName().equals("java.lang")`. Restoring the original line brings back the worked observation: module `java.base`; package `java.lang`.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `String.class.getPackageName().equals("java.lang")`. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Inspect the classroom classpath context: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `assert Main.class.getModule().isNamed();`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

The classroom compiles a single Main.java and launches it by classpath. The separate fixture demonstrates named-module execution rather than pretending the pad itself is modular.

The unchanged code is the part that Example B adds:

```java
assert !Main.class.getModule().isNamed();
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `!Main.class.getModule().isNamed()`; after it the line reads `assert !Main.class.getModule().isNamed();` again and main belongs to the unnamed module in the standard classpath launch.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `!Main.class.getModule().isNamed()` accepts.

## Exercise 3: Compile two real modules

Task: Create the owned greeting/application fixture and compile both with --module-source-path.

The compiler verifies actual requires/exports syntax and package layout. Merely reading a module-info string would not establish a valid build.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  assert java.nio.file.Files.isRegularFile(
    fixture.output.resolve("course.greeting/module-info.class")
  );
  assert java.nio.file.Files.isRegularFile(
    fixture.output.resolve("course.app/module-info.class")
  );
}
```

**Expected:** compiler exit 0 and module-info.class files present.

**Verify:** Keep an assertion equivalent to `java.nio.file.Files.isRegularFile(fixture.output.resolve("course.app/module-info.class"))`. As a control, change `fixture.output.resolve("course.app/module-info.class")` to `fixture.output.resolve("course.app/module-info.class!")` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 4: Inspect declared dependencies and exports

Task: Read the compiled descriptors with ModuleFinder.

Descriptors provide structured evidence of the boundary. A public class without an export would not supply the same named-module API.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  var finder = java.lang.module.ModuleFinder.of(fixture.output);
  var app = finder.find("course.app").orElseThrow().descriptor();
  var library = finder.find("course.greeting").orElseThrow().descriptor();
  assert app
    .requires()
    .stream()
    .anyMatch(item -> item.name().equals("course.greeting"));
  assert library
    .exports()
    .stream()
    .anyMatch(item -> item.source().equals("edu.example.greeting"));
}
```

**Expected:** app requires course.greeting; library exports edu.example.greeting.

**Verify:** Keep an assertion equivalent to `library.exports().stream().anyMatch(item -> item.source().equals("edu.example.greeting"))`. As a control, change `.anyMatch(item -> item.source().equals("edu.example.greeting"));` to `.anyMatch(item -> item.source().equals("edu.example.greeting!"));` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 5: Run the modular application

Task: Launch the compiled app in a fresh child JVM with the fixed module path.

The fresh process tests runtime module resolution in addition to compilation. It cannot rely on classes accidentally loaded in the parent process.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  String output = fixture.run();
  assert output.strip().equals("Hello, modules!");
}
```

**Expected:** stdout Hello, modules! and exit 0.

**Verify:** Keep an assertion equivalent to `output.strip().equals("Hello, modules!")`. As a control, change `assert output.strip().equals("Hello, modules!");` to `assert output.strip().equals("Hello, modules!!");` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 6: Reject a missing module dependency

Task: Compile an app requiring course.missing instead of course.greeting.

The negative control proves dependency resolution is being checked. The failure is expected and does not get converted into a passing runtime result.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  java.nio.file.Files.writeString(
    fixture.source.resolve("course.app/module-info.java"),
    "module course.app { requires course.missing; }"
  );
  int compiled = fixture.compile();
  assert compiled != 0 && !fixture.diagnostics.isBlank();
}
```

**Expected:** nonzero compiler exit and captured diagnostic.

**Verify:** Keep an assertion equivalent to `compiled != 0 && !fixture.diagnostics.isBlank()`. As a control, change `fixture.source.resolve("course.app/module-info.java"),` to `fixture.source.resolve("course.app/module-info.java!"),`: the run must fail with an `AssertionError` from the assertion on `compiled != 0 && !fixture.diagnostics.isBlank()`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
