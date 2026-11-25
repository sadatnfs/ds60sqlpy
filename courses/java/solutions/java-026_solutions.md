# java-026: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

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

Task: Change Example A's assertion to `assert String.class.getPackageName().equals("java.lang!");`, predict whether it holds, then run and restore it.

The fully qualified class name, package and module are distinct identities. A package name alone does not establish module membership.

The unchanged code is the part that Example A adds:

```java
assert String.class.getModule().getName().equals("java.base");
assert String.class.getPackageName().equals("java.lang");
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `String.class.getPackageName().equals("java.lang")`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `String.class.getPackageName().equals("java.lang")`.

## Exercise 2: Inspect the classroom classpath context: diagnose an edited check

Task: Example B's new assertion was edited to `assert Main.class.getModule().isNamed();`. Explain why it fails for unchanged state and restore it.

The classroom compiles a single Main.java and launches it by classpath. The separate fixture demonstrates named-module execution rather than pretending the pad itself is modular.

The unchanged code is the part that Example B adds:

```java
assert !Main.class.getModule().isNamed();
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `!Main.class.getModule().isNamed()`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `!Main.class.getModule().isNamed()` accepts.

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

**Verify:** Control: changing `fixture.output.resolve("course.app/module-info.class")` to `fixture.output.resolve("course.app/module-info.class!")` inside the assertion must make it fail.

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

**Verify:** Control: changing `.anyMatch(item -> item.source().equals("edu.example.greeting"));` to `.anyMatch(item -> item.source().equals("edu.example.greeting!"));` inside the assertion must make it fail.

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

**Verify:** Control: changing `assert output.strip().equals("Hello, modules!");` to `assert output.strip().equals("Hello, modules!!");` inside the assertion must make it fail.

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

**Verify:** Control: changing `fixture.source.resolve("course.app/module-info.java"),` to `fixture.source.resolve("course.app/module-info.java!"),` must fail the assertion on `compiled != 0 && !fixture.diagnostics.isBlank()`.

## After comparing the answer

Remove the `exports` line from the library descriptor in your copy of the fixture and recompile; read the diagnostic and identify the sentence that names the package that is no longer visible.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
