# java-033: Secure application boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-032`

## Learning objectives

Explain allowlist, path containment, resource bound, safe diagnostic using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Create `input.txt` inside an owned root and read at most 10 bytes. The final exercise transfers the mechanism to build a restricted diagnostic record.

## Purpose and mental model

An application boundary converts untrusted input into a limited set of permitted operations. Type and syntax checks are necessary but not sufficient:an identifier can be avalidString while naming an unauthorized file,and an accepted operation can still consume unbounded resources. Prefer explicit operation and identifier allowlists when the task is small. Keep validation close to the resource use and report a named failure instead of silently choosing a broader fallback.

Filesystem containment has both lexical andreal-path concerns. Normalizing awaydot segments can detect a simple parent traversal,but a symbolic link can redirect a seemingly contained path. This lesson uses an owned temporary directory and known fixtures,checks both forms of containment,and bounds reads with limit+1 bytes. It does not claim to be a race-proof sandbox against a concurrent adversary changing the filesystem. Logs retain selected metadata rather than copying secrets orrawsource bodies.

## Vocabulary and concepts

**Allowlist:** An explicit set of admitted operations or identifiers.

**Path containment:** A check that a resource remains within its declared owned root.

**Resource bound:** A limit enforced before unbounded allocation or work.

**Safe diagnostic:** A useful failure record that excludes unnecessary sensitive content.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-033/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Resolve a relative path under a real root,normalize it,and reject absolute orescaping paths. Reject symbolic-linkcomponents under this simple policy,then check the existing realpath remains inside the root. Read atmostlimit+1bytes and reject an oversized payload. A fixed dispatcher maps admitted operation names to known functions;it never passes input to a shell or reflection loader. Build logs from allowlisted metadata schema.

## Worked example / walkthrough

### Example A: Read an admitted owned file

The helper reads actual local bytes under a bounded contract. The fixture root is owned by the lesson and contains no user data.

```java
import java.util.*;

public class Main {
    @FunctionalInterface interface RootWork {void run(java.nio.file.Path root) throws Exception;}
    static void withRoot(RootWork work) throws Exception {var root=java.nio.file.Files.createTempDirectory("ds60-boundary-").toRealPath();try{work.run(root);}finally{try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}}
    static byte[] readBounded(java.nio.file.Path root,String relative,int limit) throws java.io.IOException {
        if(limit<0||limit>1024)throw new IllegalArgumentException("byte limit0..1024 required");var supplied=java.nio.file.Path.of(relative);if(supplied.isAbsolute())throw new SecurityException("relative path required");var candidate=root.resolve(supplied).normalize();if(!candidate.startsWith(root))throw new SecurityException("path escape");
        var current=root;for(var part:root.relativize(candidate)){current=current.resolve(part);if(java.nio.file.Files.isSymbolicLink(current))throw new SecurityException("symbolic link not allowed");}
        var real=candidate.toRealPath();if(!real.startsWith(root))throw new SecurityException("real path escape");try(var input=java.nio.file.Files.newInputStream(real)){byte[] bytes=input.readNBytes(limit+1);if(bytes.length>limit)throw new java.io.IOException("byte limit exceeded");return bytes;}
    }
    public static void main(String[] args) throws Exception {
        withRoot(root -> {java.nio.file.Files.writeString(root.resolve("input.txt"),"hello");assert new String(readBounded(root,"input.txt",10),java.nio.charset.StandardCharsets.UTF_8).equals("hello");});
    }
}

```

**Expected:** content hello.

### Example B: Reject lexical traversal and absolute paths

A path's string appearance is not a permission decision. Normalization andrelative-path validation make the simple boundary explicit.

```java
import java.util.*;

public class Main {
    @FunctionalInterface interface RootWork {void run(java.nio.file.Path root) throws Exception;}
    static void withRoot(RootWork work) throws Exception {var root=java.nio.file.Files.createTempDirectory("ds60-boundary-").toRealPath();try{work.run(root);}finally{try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}}
    static byte[] readBounded(java.nio.file.Path root,String relative,int limit) throws java.io.IOException {
        if(limit<0||limit>1024)throw new IllegalArgumentException("byte limit0..1024 required");var supplied=java.nio.file.Path.of(relative);if(supplied.isAbsolute())throw new SecurityException("relative path required");var candidate=root.resolve(supplied).normalize();if(!candidate.startsWith(root))throw new SecurityException("path escape");
        var current=root;for(var part:root.relativize(candidate)){current=current.resolve(part);if(java.nio.file.Files.isSymbolicLink(current))throw new SecurityException("symbolic link not allowed");}
        var real=candidate.toRealPath();if(!real.startsWith(root))throw new SecurityException("real path escape");try(var input=java.nio.file.Files.newInputStream(real)){byte[] bytes=input.readNBytes(limit+1);if(bytes.length>limit)throw new java.io.IOException("byte limit exceeded");return bytes;}
    }
    public static void main(String[] args) throws Exception {
        withRoot(root -> {java.nio.file.Files.writeString(root.resolve("input.txt"),"hello");assert new String(readBounded(root,"input.txt",10),java.nio.charset.StandardCharsets.UTF_8).equals("hello");});

        withRoot(root -> {
            for(String name:List.of("../outside.txt",root.resolve("input.txt").toString())){boolean rejected=false;try{readBounded(root,name,10);}catch(SecurityException expected){rejected=true;}assert rejected;}
        });
    }
}

```

**Expected:** SecurityException for both.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Read an admitted owned file.** Create `input.txt` inside an owned root and read at most 10 bytes.
   **Expected:** content hello.
   **Verify:** Compare your assertion values or captured diagnostic with content hello.

2. **Reject lexical traversal and absolute paths.** Attempt../outside.txt andanabsolutechildpath.
   **Expected:** SecurityException for both.
   **Verify:** Compare your assertion values or captured diagnostic with SecurityException for both.

3. **Enforce the byte limit after reading a bounded amount.** Writefivebytes and request a four-byte maximum.
   **Expected:** IOException for oversized content.
   **Verify:** Compare your assertion values or captured diagnostic with IOException for oversized content.

4. **Reject symbolic-link access under the declared policy.** Create a link inside the owned root to another owned file and attempt to read throughit.
   **Expected:** link rejected when platform supports creation;unsupported capability recorded explicitly.
   **Verify:** Compare your assertion values or captured diagnostic with link rejected when platform supports creation;unsupported capability recorded explicitly.

5. **Keep operation names out of code execution.** Admitonlyread_fixture andrejectrun_shell.
   **Expected:** unknownoperationIllegalArgumentException.
   **Verify:** Compare your assertion values or captured diagnostic with unknownoperationIllegalArgumentException.

6. **Build a restricted diagnostic record.** Copy onlyrequest_id,operation and status from a map containing token andsource_text.
   **Expected:** diagnostic excludes both sensitive fields.
   **Verify:** Compare your assertion values or captured diagnostic with diagnostic excludes both sensitive fields.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Allowlist, Path containment, Resource bound in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Path.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-033: Secure application boundaries.
Read courses/java/guides/java-033.md and courses/java/lessons/java-033.java. Direct prerequisites: `java-032`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
