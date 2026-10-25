# Java 027: compile and package a reproducible tiny JAR

This manual fixture matches the literal source used by the executable reference. Use an already prepared JDK 21 and an empty learner-owned run directory under `.learning/`. The commands create generated classes and archives only in that run directory.

```text
javac --release 21 -d .learning/java027-run1/classes courses/java/fixtures/java-027/src/Hello.java
jar --create --file .learning/java027-run1/hello.jar --main-class Hello --date=2020-01-01T00:00:02Z -C .learning/java027-run1/classes .
java -ea -jar .learning/java027-run1/hello.jar
```

The argument forms work in PowerShell and POSIX with the selected JDK tools. Choose a new run name if the directory already contains learner work. Expected output is `build-ok`.

The fixed archive timestamp removes one source of byte variation. The prepared compiler version, target release, source bytes, manifest fields and input class ordering still belong to the reproducibility contract. The automated reference packages the same class directory twice and compares SHA256 digests in one prepared JDK environment. It does not promise byte-identical output across all JDK builds or operating systems.

For a larger Maven or Gradle project, pin plugin and dependency versions, record repositories, verify dependency checksums and prepare an offline cache deliberately. A moving `LATEST` coordinate or unspecified plugin version can change the build even when your source files are unchanged. A dependency hash identifies bytes; it does not establish that the dependency is safe, licensed for every use or compatible with the application.

Inspect the JAR with `jar --list --file .learning/java027-run1/hello.jar`. The archive should contain `Hello.class` and a manifest naming `Hello` as `Main-Class`. A package that exists but cannot launch has failed a different gate from source compilation. Keep both the compiler result and fresh-process launch result in a release receipt.
