# Java 036: release artifact and optional custom runtime

The default Java 036 reference compiles a tiny Java 21 application, packages a JAR, checks class-file version 65, executes a fresh-process self-test and proves that an altered artifact fails its hash gate. It creates only owned temporary files and cleans them up. It does not build a custom runtime image or deploy a service.

This manual fixture is an optional external JDK project, separate from the
browser's single-source pad and saved progress. The maintained contributor
route is a prepared POSIX or WSL 2 environment with JDK 21. Use a fresh,
learner-owned directory. The following JDK commands have the same argument form
in POSIX shells and a separately prepared native PowerShell environment:

```text
javac --release 21 -d .learning/java036-run1/classes courses/java/fixtures/java-036/src/App.java
jar --create --file .learning/java036-run1/app.jar --main-class App --date=2020-01-01T00:00:02Z -C .learning/java036-run1/classes .
java -ea -jar .learning/java036-run1/app.jar --self-test
```

Expected output is `release-ok` with exit 0. An unsupported argument should produce `unknown argument` and exit 2. Check the exit status through your shell's normal mechanism rather than deciding success from whether any text appeared.

## Optional jlink step

A custom runtime is a platform-specific artifact assembled from modules in the prepared JDK. It can be useful when distributing a controlled application, but the output is not one universal runtime for Windows, macOS, Linux and all CPU architectures. It also has a nontrivial disk footprint, so do not create it inside an ephemeral browser pad or checked-in source. Use only an ignored, learner-owned output directory such as the one below.

This tiny fixture uses only `java.base`. After deliberately choosing an empty output directory and confirming the prepared JDK includes `jlink` and its module files, you can build an optional runtime:

```text
jlink --add-modules java.base --strip-debug --no-header-files --no-man-pages --output .learning/java036-run1/runtime
```

On Linux, macOS or Windows through WSL 2, run the produced runtime with:

```bash
.learning/java036-run1/runtime/bin/java -ea -jar .learning/java036-run1/app.jar --self-test
```

For comparison, an already prepared native Windows JDK produces `java.exe`.
That separate host workflow is outside classroom release qualification:


```powershell
& .\.learning\java036-run1\runtime\bin\java.exe -ea -jar .learning/java036-run1/app.jar --self-test
```

This optional image build was not executed by the default lesson reference. Record the actual OS, architecture, JDK build, module list, output size and launch result if you perform it. A larger service using HTTP, JDBC, JFR or other modules needs its real dependency closure; copying this `java.base` command would omit required capabilities.

## Reviewable release evidence

Retain source identity, compiler target, artifact hash, entrypoint, schema/configuration assumptions, normal and negative launch checks, and the previous artifact identity needed for rollback. A checksum match does not establish behavior, and a self-test does not establish production reliability. The application still needs representative contract tests, operational bounds and an owned deployment process. The course intentionally records those as separate gates.
