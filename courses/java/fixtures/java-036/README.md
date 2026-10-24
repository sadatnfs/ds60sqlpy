# Java036: release artifact andoptional custom runtime

The default Java036 reference compiles a tiny Java21 application,packages a JAR,checks class-file version65,executes a fresh-process self-test andproves that an altered artifact fails its hash gate. It creates only owned temporary files andcleans them up. It doesnot build a custom runtime image ordeploy a service.

Use a fresh learner-owned directory for this manual version. The following JDK commands have the same argument form in PowerShell andPOSIX:

```text
javac --release 21 -d .learning/java036-run1/classes courses/java/fixtures/java-036/src/App.java
jar --create --file .learning/java036-run1/app.jar --main-class App --date=2020-01-01T00:00:02Z -C .learning/java036-run1/classes .
java -ea -jar .learning/java036-run1/app.jar --self-test
```

Expected output is `release-ok` with exit0. An unsupported argument should produce `unknown argument` andexit2. Check the exit status through your shell's normal mechanism rather than deciding success from whether any text appeared.

## Optional jlink step

A custom runtime is a platform-specific artifact assembled from modules in the prepared JDK. It can be useful when distributing a controlled application, but the output is not one universal runtime for Windows,macOS,Linux andallCPUarchitectures. It also has a nontrivial disk footprint,so do not create it inside an ephemeral browser pad orunder the course source tree.

This tiny fixture uses only `java.base`. After deliberately choosing an empty output directory andconfirming the prepared JDK includes `jlink` andits module files,you can build an optional runtime:

```text
jlink --add-modules java.base --strip-debug --no-header-files --no-man-pages --output .learning/java036-run1/runtime
```

On POSIX,run the produced runtime with:

```bash
.learning/java036-run1/runtime/bin/java -ea -jar .learning/java036-run1/app.jar --self-test
```

On Windows PowerShell,use:

```powershell
& .\.learning\java036-run1\runtime\bin\java.exe -ea -jar .learning/java036-run1/app.jar --self-test
```

This optional image build was not executed by the default lesson reference. Record the actual OS,architecture,JDKbuild,module list,output size andlaunch result if you perform it. A larger service usingHTTP,JDBC,JFR orothermodules needs its real dependency closure;copying this `java.base` command would omit required capabilities.

## Reviewable release evidence

Retain source identity,compiler target,artifact hash,entrypoint,schema/configuration assumptions,normal andnegative launch checks,andthe previous artifact identity needed forrollback. A checksum match doesnot establish behavior,and a self-test doesnot establish production reliability. The application still needs representative contract tests,operational bounds andan owned deployment process. The course intentionally records those as separate gates.
