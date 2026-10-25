# Java 026: inspect a real two-module source tree

The classroom pad remains one `Main.java`. Its reference creates and compiles an equivalent owned temporary fixture so the default run exercises real modules. These files let you study the source layout directly and compile it manually with an already prepared JDK 21. No package download or shared environment change is required.

```text
src/
  course.greeting/
    module-info.java
    edu/example/greeting/Greeter.java
  course.app/
    module-info.java
    edu/example/app/Main.java
```

The directory directly under `src/` names the module. Package directories below it follow the package declaration. `course.greeting` exports `edu.example.greeting`; `course.app` requires `course.greeting`. The application package does not need to be exported merely to launch its declared main class. Exporting a package is a public API decision, not a way to fix every class-loading problem.

From the repository root, use a new learner-owned output directory. The example `.learning/java026-run1` must be absent or you should choose another run name. Do not overwrite a prior experiment merely to make a command pass.

The compiler and launcher arguments are the same in PowerShell and POSIX once the prepared JDK is on the selected process path:

```text
javac --release 21 --module-source-path courses/java/fixtures/java-026/src -d .learning/java026-run1/out -m course.greeting,course.app
java -ea --module-path .learning/java026-run1/out -m course.app/edu.example.app.Main
```

Expected output is `Hello, modules!`. The compiler should create separate output directories for both modules, each containing `module-info.class`. If a dependency is missing, read the first compiler diagnostic and check the `requires` name against the actual module directory and descriptor. Changing a classpath does not automatically satisfy a named-module dependency.

For a deliberate negative experiment, copy the source tree into your own ignored working directory and change the application descriptor to require `course.missing`. Compilation should fail. Preserve the failure and then restore the correct descriptor in your copy. Do not edit the checked-in fixture or relax the compiler flags to hide the problem.

The automated Java 026 reference also inspects descriptors with `ModuleFinder` and launches a bounded fresh JVM. That is evidence about this tiny prepared-runtime fixture. It does not qualify an arbitrary modular application, custom runtime image or cross-platform installer.
