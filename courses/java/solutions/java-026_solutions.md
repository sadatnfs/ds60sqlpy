# java-026: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Packages organize class names and access boundaries. Aclasspath tells the runtime where unnamed-module classes can be found;it does not change the package declared in source. Java's module system adds explicit requires and exports relationships. Apublic class in a package is not automatically accessible from another named module unless the package is exported. Module boundaries therefore add a level beyond public/private declarations.

This lesson includes a real two-module source fixture:a greeting library exports its package,and an application requires that module. The defaultMain.java diagnostic writes the same tiny fixture into an owned temporary directory,invokes the prepared JDK compiler,inspects module descriptors and runs the application in a bounded child JVM. No external dependency is downloaded. The separate checked-in fixture and manual commands let a learner inspect the file layout directly.

**Package:** A namespace and access grouping declared by a Java source file.

**Classpath:** Locations used to find classes in the unnamed-module model.

**Named module:** A unit declaring dependencies and exported packages.

**Export:** Permission for other modules to access a package's publicAPI.

## Reading the reference

The source root contains one directory per module,each withmodule-info.java and package directories. javac --module-source-path selects that layout and-m names the modules to compile. java --module-path selects compiled modules and-mmodule/class starts the application. ModuleFinder reads descriptors without treating filenames as module identities. The child process uses a fixed local Java executable and bounded wait. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Exercise 1: Inspect a platform module

Task: Read `String.class` module and package names.

The fully qualified class name,package and module are distinct identities. Apackage name alone does not establish module membership.

```java
assert String.class.getModule().getName().equals("java.base");
assert String.class.getPackageName().equals("java.lang");
```

**Expected:** module `java.base`;package `java.lang`.

**Verify:** Compare the program values or named exception with module `java.base`;package `java.lang`. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Inspect the classroom classpath context

Task: ReadMain.class module metadata.

The classroom compiles a singleMain.java andlaunches it by classpath. The separate fixture demonstrates named-module execution rather than pretending the pad itself is modular.

```java
assert !Main.class.getModule().isNamed();
```

**Expected:** Main belongs to the unnamed module in the standard classpath launch.

**Verify:** Compare the program values or named exception with Main belongs to the unnamed module in the standard classpath launch. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Compile two real modules

Task: Create the owned greeting/application fixture and compile both with--module-source-path.

The compiler verifies actualrequires/exports syntax and package layout. Merely reading a module-info string would not establish a valid build.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  assert fixture.compile() == 0;
  assert java.nio.file.Files.isRegularFile(
    fixture.output.resolve("course.greeting/module-info.class")
  );
  assert java.nio.file.Files.isRegularFile(
    fixture.output.resolve("course.app/module-info.class")
  );
}
```

**Expected:** compiler exit 0 andmodule-info.class files present.

**Verify:** Compare the program values or named exception with compiler exit 0 andmodule-info.class files present. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Inspect declared dependencies and exports

Task: Read the compiled descriptors with ModuleFinder.

Descriptors provide structured evidence of the boundary. Apublic class without an export would not supply the same named-moduleAPI.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  assert fixture.compile() == 0;
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

**Expected:** app requirescourse.greeting;library exportsedu.example.greeting.

**Verify:** Compare the program values or named exception with app requirescourse.greeting;library exportsedu.example.greeting. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Run the modular application

Task: Launch the compiled app in a fresh childJVM with the fixed module path.

The fresh process tests runtime module resolution in addition to compilation. It cannot rely on classes accidentally loaded in the parent process.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  assert fixture.compile() == 0;
  assert fixture.run().strip().equals("Hello, modules!");
}
```

**Expected:** stdoutHello, modules! andexit0.

**Verify:** Compare the program values or named exception with stdoutHello, modules! andexit0. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Reject a missing module dependency

Task: Compile an app requiringcourse.missing instead ofcourse.greeting.

The negative control proves dependency resolution is being checked. The failure is expected and does not get converted into a passing runtime result.

```java
try (ModuleFixture fixture = new ModuleFixture()) {
  java.nio.file.Files.writeString(
    fixture.source.resolve("course.app/module-info.java"),
    "module course.app { requires course.missing; }"
  );
  assert fixture.compile() != 0 && !fixture.diagnostics.isBlank();
}
```

**Expected:** nonzero compiler exit and captured diagnostic.

**Verify:** Compare the program values or named exception with nonzero compiler exit and captured diagnostic. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
