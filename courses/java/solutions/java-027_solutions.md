# java-027: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A build turns source and declared dependencies into an artifact. Reproducibility requires identifying the compiler, target level, inputs, dependency versions and packaging metadata. A source repository alone is not enough if a build fetches moving dependency versions or embeds timestamps that change every run. Maven and Gradle can manage larger builds, but their configuration still needs explicit versions, verification and offline preparation. This default lesson uses only the JDK'sjavac and jar tools on a literal source fixture.

The example compiles one small application, packages it twice with a fixed archive timestamp, and compares the resulting bytes in the same prepared JDK environment. It then executes the JAR. This establishes a bounded local reproducibility property, not byte-identical builds across every JDK or OS. A dependency lock or checksum is an identity control, not proof that a dependency is safe or appropriate.

**Build input:** Source, toolchain and dependency state used to produce an artifact.

**Reproducible artifact:** An output matching a declared byte-identity contract under fixed inputs.

**Dependency pin:** An exact version or hash identifying a required component.

**JAR:** A Java archive containing classes, resources and optional launch metadata.

## Reading the reference

The JavaCompiler API invokes the prepared compiler with --release 21. The JDK jar tool can be accessed through java.util.spi.ToolProvider and given a fixed --date plus --main-class. Package only the intended classes directory. SHA256 compares artifact bytes; use a fresh child JVM to prove the JAR entrypoint works. A changed source or dependency identity should change the recorded build manifest. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Exercise 1: Compile a literal application: predict an edited check

Task: Change Example A's assertion to `assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class!"));`, predict whether it holds, then run and restore it.

The compiler target is explicit. A file named.class would not by itself prove that the source compiled successfully.

The unchanged code is the part that Example A adds:

```java
try (BuildFixture fixture = new BuildFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));
}
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`.

## Exercise 2: Create a runnable archive: diagnose an edited check

Task: Example B's new assertion was edited to `assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello!");`. Explain why it fails for unchanged state and restore it.

The archive contains both bytecode and entrypoint metadata. These are separate checks from its filename extension.

The unchanged code is the part that Example B adds:

```java
try (BuildFixture fixture = new BuildFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  var jar = fixture.pack("one.jar");
  try (var archive = new java.util.jar.JarFile(jar.toFile())) {
    assert archive.getJarEntry("Hello.class") != null;
    assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello");
  }
}
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")` accepts.

## Exercise 3: Compare two builds with fixed metadata

Task: Package the same classes twice with the same timestamp.

The test controls timestamp and input class bytes. It does not claim that different compiler releases generate identical bytecode.

```java
try (BuildFixture fixture = new BuildFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  var a = fixture.pack("a.jar");
  var b = fixture.pack("b.jar");
  assert Arrays.equals(
    java.security.MessageDigest.getInstance("SHA-256").digest(
      java.nio.file.Files.readAllBytes(a)
    ),
    java.security.MessageDigest.getInstance("SHA-256").digest(
      java.nio.file.Files.readAllBytes(b)
    )
  );
}
```

**Expected:** archive byte hashes equal in this prepared JDK.

**Verify:** Control: changing `assert compiled == 0;` to `assert compiled != 0;` inside the assertion must make it fail.

## Exercise 4: Execute the packaged entrypoint

Task: Run the JAR in a bounded child JVM.

Execution verifies that packaging and entrypoint metadata agree. A hash match alone would not show that the artifact can start.

```java
try (BuildFixture fixture = new BuildFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  String output = fixture.run(fixture.pack("run.jar"));
  assert output.strip().equals("build-ok");
}
```

**Expected:** stdout build-ok; exit 0.

**Verify:** Control: changing `assert output.strip().equals("build-ok");` to `assert output.strip().equals("build-ok!");` inside the assertion must make it fail.

## Exercise 5: Detect a changed source identity

Task: Hash two source strings differing in their printed message.

The manifest should bind the exact inputs, not only a repository name. A changed input needs a new artifact identity and validation.

```java
var digest = java.security.MessageDigest.getInstance("SHA-256");
byte[] first = digest.digest(
  "class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)
);
byte[] second = digest.digest(
  "class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)
);
assert !Arrays.equals(first, second);
```

**Expected:** different SHA-256 digests.

**Verify:** Control: changing `"class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` to `"class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` must fail the assertion on `!Arrays.equals(first, second)`.

## Exercise 6: Record an explicit dependency contract

Task: Represent H2 as version 2.5.252 with a required verified hash field and reject a moving LATEST label.

This record states the required identity policy rather than inventing a hash. The actual prepared JAR receipt must supply the verified bytes before a release claim.

```java
Map<String, String> dependency = Map.of(
  "coordinate",
  "com.h2database:h2",
  "version",
  "2.5.252",
  "hash_policy",
  "verify prepared artifact SHA256"
);
assert dependency.get("version").equals("2.5.252") &&
!dependency.get("version").equals("LATEST");
```

**Expected:** exact version accepted; LATEST not treated as a pin.

**Verify:** Control: changing `"2.5.252",` to `"3.5.252",` must fail the assertion on `dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST")`.

## After comparing the answer

Remove the `--date` argument from `pack` in your copy, pack twice a few seconds apart, and compare the digests; then explain which bytes changed.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
