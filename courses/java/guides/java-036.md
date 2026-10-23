# java-036: Package, diagnose and maintain a release

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-035`

## Learning objectives

Explain release artifact, class-file version, integrity gate, custom runtime image using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Compile the fixture with --release 21 and inspect its class header. The final exercise transfers the mechanism to record runtime-image scope and rollback identity.

## Purpose and mental model

A release is a reproducible artifact plus evidence about how it starts,what contracts it accepts and how failures are diagnosed. Source compilation alone does not prove that packaging preserved the entrypoint or that the target runtime supports the class version. Hashes identify artifact bytes,but avalidhash does not establish correct behavior. A deliberate failing integrity check proves that the gate is connected to the decision rather than merely printing a success label.

This capstone builds a smallJava21JAR witha fixed timestamp,checks class-file version65,executes a self-test in a freshJVM and rejects both an invalid launch argument and tampered artifact bytes. It retains a previous-artifact identity in the release record. jlink is explained as a separate custom-runtime packaging step;the default reference only probes tool availability and does not build a large runtime image inside the bounded browser job. Production deployment and operational acceptance remain separate from this local artifact check.

## Vocabulary and concepts

**Release artifact:** The packaged program and metadata intended for distribution.

**Class-file version:** The bytecode format level required by a JVM.

**Integrity gate:** A check that artifact bytes match the expected identity.

**Custom runtime image:** A platform-specificJava runtime assembled from selected modules.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-036/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.

## Packaging scope

The default reference creates only small owned source,class and JAR fixtures. It does not build a custom runtime image or deploy a service. The separate [manual release fixture](../fixtures/java-036/README.md) explains a deliberate jlink workflow and the additional disk/platform checks needed. Keep generated images under an ignored learner-owned directory,not in course source or an ephemeral pad.


## Syntax anatomy and execution trace

Use the prepared compiler with --release 21,then inspect the class magic and major version throughDataInputStream. Package withtheJDKjar tool andanexplicitMain-Class. Launch the artifact using a fixed local java executable with bounded wait and captured output. SHA256 verification occurs before execution. A manualjlink recipe must name required modules,an owned output directory and actual platform;itcannot create one universal runtime for everyOS/architecture. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Worked example / walkthrough

### Example A: Verify the compiler target

The header is direct evidence of the target bytecode level. Afilename or README claim cannot replace it.

```java
import java.util.*;

public class Main {
    record Run(int code,String output,String error){}
    static byte[] sha256(byte[] bytes) throws Exception{return java.security.MessageDigest.getInstance("SHA-256").digest(bytes);}
    static void verify(java.nio.file.Path artifact,byte[] expected) throws Exception {if(!Arrays.equals(sha256(java.nio.file.Files.readAllBytes(artifact)),expected))throw new SecurityException("artifact hash mismatch");}
    static final class ReleaseFixture implements AutoCloseable {
        final java.nio.file.Path root,source,classes,jar;
        ReleaseFixture() throws Exception {root=java.nio.file.Files.createTempDirectory("ds60-release-");source=root.resolve("App.java");classes=root.resolve("classes");jar=root.resolve("app.jar");java.nio.file.Files.createDirectories(classes);java.nio.file.Files.writeString(source,"public class App { public static void main(String[] args){if(args.length==1 && args[0].equals(\"--self-test\")){System.out.println(\"release-ok\");}else{System.err.println(\"unknown argument\");System.exit(2);}} }");}
        void build() throws Exception {var compiler=javax.tools.ToolProvider.getSystemJavaCompiler();if(compiler==null||compiler.run(null,null,null,"--release","21","-d",classes.toString(),source.toString())!=0)throw new AssertionError("compile failed");var tool=java.util.spi.ToolProvider.findFirst("jar").orElseThrow();var messages=new java.io.StringWriter();int code=tool.run(new java.io.PrintWriter(messages),new java.io.PrintWriter(messages),"--create","--file",jar.toString(),"--main-class","App","--date=2020-01-01T00:00:02Z","-C",classes.toString(),".");if(code!=0)throw new AssertionError(messages.toString());}
        Run run(String argument) throws Exception {
            String executable=java.nio.file.Path.of(System.getProperty("java.home"),"bin","java").toString();
            var stdout=root.resolve("child.stdout");var stderr=root.resolve("child.stderr");
            var process=new ProcessBuilder(executable,"-ea","-jar",jar.toString(),argument).redirectOutput(stdout.toFile()).redirectError(stderr.toFile()).start();
            if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)){process.destroyForcibly();throw new AssertionError("release child timeout");}
            return new Run(process.exitValue(),java.nio.file.Files.readString(stdout),java.nio.file.Files.readString(stderr));
        }
        public void close() throws java.io.IOException {try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
    }
    public static void main(String[] args) throws Exception {
        try(ReleaseFixture fixture=new ReleaseFixture()) {
            fixture.build();try(var input=new java.io.DataInputStream(java.nio.file.Files.newInputStream(fixture.classes.resolve("App.class")))){assert input.readInt()==0xCAFEBABE;input.readUnsignedShort();assert input.readUnsignedShort()==65;}
        }
    }
}

```

**Expected:** magic CAFEBABE; major version 65.

### Example B: Inspect packaged launch metadata

Packaging can fail independently of compilation. The archive must contain the intended entrypoint and matching metadata.

```java
import java.util.*;

public class Main {
    record Run(int code,String output,String error){}
    static byte[] sha256(byte[] bytes) throws Exception{return java.security.MessageDigest.getInstance("SHA-256").digest(bytes);}
    static void verify(java.nio.file.Path artifact,byte[] expected) throws Exception {if(!Arrays.equals(sha256(java.nio.file.Files.readAllBytes(artifact)),expected))throw new SecurityException("artifact hash mismatch");}
    static final class ReleaseFixture implements AutoCloseable {
        final java.nio.file.Path root,source,classes,jar;
        ReleaseFixture() throws Exception {root=java.nio.file.Files.createTempDirectory("ds60-release-");source=root.resolve("App.java");classes=root.resolve("classes");jar=root.resolve("app.jar");java.nio.file.Files.createDirectories(classes);java.nio.file.Files.writeString(source,"public class App { public static void main(String[] args){if(args.length==1 && args[0].equals(\"--self-test\")){System.out.println(\"release-ok\");}else{System.err.println(\"unknown argument\");System.exit(2);}} }");}
        void build() throws Exception {var compiler=javax.tools.ToolProvider.getSystemJavaCompiler();if(compiler==null||compiler.run(null,null,null,"--release","21","-d",classes.toString(),source.toString())!=0)throw new AssertionError("compile failed");var tool=java.util.spi.ToolProvider.findFirst("jar").orElseThrow();var messages=new java.io.StringWriter();int code=tool.run(new java.io.PrintWriter(messages),new java.io.PrintWriter(messages),"--create","--file",jar.toString(),"--main-class","App","--date=2020-01-01T00:00:02Z","-C",classes.toString(),".");if(code!=0)throw new AssertionError(messages.toString());}
        Run run(String argument) throws Exception {
            String executable=java.nio.file.Path.of(System.getProperty("java.home"),"bin","java").toString();
            var stdout=root.resolve("child.stdout");var stderr=root.resolve("child.stderr");
            var process=new ProcessBuilder(executable,"-ea","-jar",jar.toString(),argument).redirectOutput(stdout.toFile()).redirectError(stderr.toFile()).start();
            if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)){process.destroyForcibly();throw new AssertionError("release child timeout");}
            return new Run(process.exitValue(),java.nio.file.Files.readString(stdout),java.nio.file.Files.readString(stderr));
        }
        public void close() throws java.io.IOException {try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
    }
    public static void main(String[] args) throws Exception {
        try(ReleaseFixture fixture=new ReleaseFixture()) {
            fixture.build();try(var input=new java.io.DataInputStream(java.nio.file.Files.newInputStream(fixture.classes.resolve("App.class")))){assert input.readInt()==0xCAFEBABE;input.readUnsignedShort();assert input.readUnsignedShort()==65;}
        }

        try(ReleaseFixture fixture=new ReleaseFixture()) {
            fixture.build();try(var jar=new java.util.jar.JarFile(fixture.jar.toFile())){assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class")!=null;}
        }
    }
}

```

**Expected:** Main-ClassApp;class entry present.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Verify the compiler target.** Compile the fixture with --release 21 and inspect its class header.
   **Expected:** magic CAFEBABE; major version 65.
   **Verify:** Compare your assertion values or captured diagnostic with magic CAFEBABE; major version 65.

2. **Inspect packaged launch metadata.** Open thebuiltJAR andcheckMain-Class andApp.class.
   **Expected:** Main-ClassApp;class entry present.
   **Verify:** Compare your assertion values or captured diagnostic with Main-ClassApp;class entry present.

3. **Run a fresh-process self-test.** Launch the JAR with--self-test through a bounded childJVM.
   **Expected:** exit 0 andoutputrelease-ok.
   **Verify:** Compare your assertion values or captured diagnostic with exit 0 andoutputrelease-ok.

4. **Verify an invalid launch fails clearly.** Run thesameJAR with an unsupported argument.
   **Expected:** exit2 and unknown argument diagnostic.
   **Verify:** Compare your assertion values or captured diagnostic with exit2 and unknown argument diagnostic.

5. **Reject artifact tampering before execution.** Hash the JAR,fliponebyte,and call the integrity gate.
   **Expected:** SecurityException;original bytes restored for cleanup.
   **Verify:** Compare your assertion values or captured diagnostic with SecurityException;original bytes restored for cleanup.

6. **Record runtime-image scope and rollback identity.** Inspect whether jlink exists,and write a record distinguishing local JAR acceptance fromanunbuiltcustomruntime.
   **Expected:** previous artifact v1 retained; custom_runtime_built False.
   **Verify:** Compare your assertion values or captured diagnostic with previous artifact v1 retained; custom_runtime_built False.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Release artifact, Class-file version, Integrity gate in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jlink.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-036: Package, diagnose and maintain a release.
Read courses/java/guides/java-036.md and courses/java/lessons/java-036.java. Direct prerequisites: `java-035`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
