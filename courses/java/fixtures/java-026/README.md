# Java026: inspect a real two-module source tree

The classroom pad remains one `Main.java`. Its reference creates andcompiles an equivalent owned temporary fixture so the default run exercises real modules. These files let you study the source layout directly andcompile it manually with an already prepared JDK21. No package download orshared environment change is required.

```text
src/
  course.greeting/
    module-info.java
    edu/example/greeting/Greeter.java
  course.app/
    module-info.java
    edu/example/app/Main.java
```

The directory directly under `src/` names the module. Package directories below it follow the package declaration. `course.greeting` exports `edu.example.greeting`; `course.app` requires `course.greeting`. The application package doesnot need to be exported merely to launch its declared main class. Exporting a package is a publicAPI decision,not a way to fix every class-loading problem.

From the repository root,use a new learner-owned output directory. The example `.learning/java026-run1` must be absent oryou should choose another run name. Do not overwrite a prior experiment merely to make a command pass.

The compiler andlauncher arguments are the same in PowerShell andPOSIX once the prepared JDK is on the selected process path:

```text
javac --release 21 --module-source-path courses/java/fixtures/java-026/src -d .learning/java026-run1/out -m course.greeting,course.app
java -ea --module-path .learning/java026-run1/out -m course.app/edu.example.app.Main
```

Expected output is `Hello, modules!`. The compiler should create separate output directories for both modules,each containing `module-info.class`. If a dependency is missing,read the first compiler diagnostic andcheck the `requires` name against the actual module directory anddescriptor. Changing a classpath doesnot automatically satisfy a named-module dependency.

For a deliberate negative experiment,copy the source tree into your own ignored working directory andchange the application descriptor to require `course.missing`. Compilation should fail. Preserve the failure andthen restore the correct descriptor in your copy. Do not edit the checked-in fixture orrelax the compiler flags to hide the problem.

The automated Java026 reference also inspects descriptors with `ModuleFinder` andlaunches a bounded freshJVM. That is evidence about this tiny prepared-runtime fixture. It doesnot qualify an arbitrary modular application,custom runtime image orcross-platform installer.
