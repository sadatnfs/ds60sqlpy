# java-027: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A build turns source and declared dependencies into an artifact. Reproducibility requires identifying the compiler, target level, inputs, dependency versions and packaging metadata. A source repository alone is not enough if a build fetches moving dependency versions or embeds timestamps that change every run. Maven and Gradle can manage larger builds, but their configuration still needs explicit versions, verification and offline preparation. This default lesson uses only the JDK'sjavac and jar tools on a literal source fixture.

The example compiles one small application, packages it twice with a fixed archive timestamp, and compares the resulting bytes in the same prepared JDK environment. It then executes the JAR. This establishes a bounded local reproducibility property, not byte-identical builds across every JDK or OS. A dependency lock or checksum is an identity control, not proof that a dependency is safe or appropriate.

**Build input:** Source, toolchain and dependency state used to produce an artifact.

**Reproducible artifact:** An output matching a declared byte-identity contract under fixed inputs.

**Dependency pin:** An exact version or hash identifying a required component.

**JAR:** A Java archive containing classes, resources and optional launch metadata.

## Reading the reference

The JavaCompiler API invokes the prepared compiler with --release 21. The JDK jar tool can be accessed through java.util.spi.ToolProvider and given a fixed--date plusmain-class. Package only the intended classes directory. SHA256 compares artifact bytes; use a fresh child JVM to prove the JAR entrypoint works. A changed source or dependency identity should change the recorded build manifest. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Exercise 1: Compile a literal application: predict an edited check

Task: Copy Example A into a scratch `Main.java` and change `assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));` to `assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class!"));` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.

The compiler target is explicit. A file named.class would not by itself prove that the source compiled successfully.

The unchanged code is the part that Example A adds:

```java
try (BuildFixture fixture = new BuildFixture()) {
  int compiled = fixture.compile();
  assert compiled == 0;
  assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));
}
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`. Restoring the original line brings back the worked observation: compiler exit 0; Hello.class exists.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"))`. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Create a runnable archive: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello!");`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

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

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")`; after it the line reads `assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello");` again and JAR exists and contains Hello.class.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello")` accepts.

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

**Verify:** Keep an assertion equivalent to `compiled == 0`. As a control, change `assert compiled == 0;` to `assert compiled != 0;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `output.strip().equals("build-ok")`. As a control, change `assert output.strip().equals("build-ok");` to `assert output.strip().equals("build-ok!");` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `!Arrays.equals(first, second)`. As a control, change `"class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)` to `"class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8)`: the run must fail with an `AssertionError` from the assertion on `!Arrays.equals(first, second)`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST")`. As a control, change `"2.5.252",` to `"3.5.252",`: the run must fail with an `AssertionError` from the assertion on `dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST")`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
