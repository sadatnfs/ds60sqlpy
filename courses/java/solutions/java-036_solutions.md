# java-036: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A release is a reproducible artifact plus evidence about how it starts,what contracts it accepts and how failures are diagnosed. Source compilation alone does not prove that packaging preserved the entrypoint or that the target runtime supports the class version. Hashes identify artifact bytes,but avalidhash does not establish correct behavior. A deliberate failing integrity check proves that the gate is connected to the decision rather than merely printing a success label.

This capstone builds a smallJava21JAR witha fixed timestamp,checks class-file version65,executes a self-test in a freshJVM and rejects both an invalid launch argument and tampered artifact bytes. It retains a previous-artifact identity in the release record. jlink is explained as a separate custom-runtime packaging step;the default reference only probes tool availability and does not build a large runtime image inside the bounded browser job. Production deployment and operational acceptance remain separate from this local artifact check.

**Release artifact:** The packaged program and metadata intended for distribution.

**Class-file version:** The bytecode format level required by a JVM.

**Integrity gate:** A check that artifact bytes match the expected identity.

**Custom runtime image:** A platform-specificJava runtime assembled from selected modules.

## Reading the reference

Use the prepared compiler with --release 21,then inspect the class magic and major version throughDataInputStream. Package withtheJDKjar tool andanexplicitMain-Class. Launch the artifact using a fixed local java executable with bounded wait and captured output. SHA256 verification occurs before execution. A manualjlink recipe must name required modules,an owned output directory and actual platform;itcannot create one universal runtime for everyOS/architecture. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Exercise 1: Verify the compiler target

Task: Compile the fixture with --release 21 and inspect its class header.

The header is direct evidence of the target bytecode level. Afilename or README claim cannot replace it.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {
    fixture.build();try(var input=new java.io.DataInputStream(java.nio.file.Files.newInputStream(fixture.classes.resolve("App.class")))){assert input.readInt()==0xCAFEBABE;input.readUnsignedShort();assert input.readUnsignedShort()==65;}
}
```

**Expected:** magic CAFEBABE; major version 65.

**Verify:** Compare the program values or named exception with magic CAFEBABE; major version 65. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Inspect packaged launch metadata

Task: Open thebuiltJAR andcheckMain-Class andApp.class.

Packaging can fail independently of compilation. The archive must contain the intended entrypoint and matching metadata.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {
    fixture.build();try(var jar=new java.util.jar.JarFile(fixture.jar.toFile())){assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class")!=null;}
}
```

**Expected:** Main-ClassApp;class entry present.

**Verify:** Compare the program values or named exception with Main-ClassApp;class entry present. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Run a fresh-process self-test

Task: Launch the JAR with--self-test through a bounded childJVM.

The newprocess cannot reuse classes loaded by the authoring program. Thischecks the actual packaged launch path.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {fixture.build();Run result=fixture.run("--self-test");assert result.code()==0 && result.output().strip().equals("release-ok");}
```

**Expected:** exit 0 andoutputrelease-ok.

**Verify:** Compare the program values or named exception with exit 0 andoutputrelease-ok. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Verify an invalid launch fails clearly

Task: Run thesameJAR with an unsupported argument.

An acceptance suite should include a meaningful failure path. Returningexit0 for every argument would make automation unable to distinguish misuse.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {fixture.build();Run result=fixture.run("--unsupported");assert result.code()==2 && result.error().contains("unknown argument");}
```

**Expected:** exit2 and unknown argument diagnostic.

**Verify:** Compare the program values or named exception with exit2 and unknown argument diagnostic. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reject artifact tampering before execution

Task: Hash the JAR,fliponebyte,and call the integrity gate.

The corrupt artifact is never executed. Ahashcheck verifies byte identity,while theself-test separately verifies behavior.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {
    fixture.build();byte[] original=java.nio.file.Files.readAllBytes(fixture.jar);byte[] expected=sha256(original);byte[] changed=original.clone();changed[0]^=1;java.nio.file.Files.write(fixture.jar,changed);boolean rejected=false;
    try{verify(fixture.jar,expected);}catch(SecurityException failure){rejected=true;}finally{java.nio.file.Files.write(fixture.jar,original);}
    assert rejected;verify(fixture.jar,expected);
}
```

**Expected:** SecurityException;original bytes restored for cleanup.

**Verify:** Compare the program values or named exception with SecurityException;original bytes restored for cleanup. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Record runtime-image scope and rollback identity

Task: Inspect whether jlink exists,and write a record distinguishing local JAR acceptance fromanunbuiltcustomruntime.

Toolpresence is not a runtime-image build receipt. Amanualjlink build needs its own module closure,platform,launch and failure checks before distribution.

```java
var jlink=java.nio.file.Path.of(System.getProperty("java.home"),"bin","jlink");
Map<String,Object> receipt=Map.of("jar_contract_checked",true,"previous_artifact","v1","jlink_tool_present",java.nio.file.Files.isExecutable(jlink),"custom_runtime_built",false,"production_deployed",false);
assert receipt.get("previous_artifact").equals("v1") && receipt.get("custom_runtime_built").equals(false) && receipt.get("production_deployed").equals(false);
```

**Expected:** previous artifact v1 retained; custom_runtime_built False.

**Verify:** Compare the program values or named exception with previous artifact v1 retained; custom_runtime_built False. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
