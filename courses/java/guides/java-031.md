# java-031: Reflection, annotations and service loading

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-030`

## Learning objectives

Explain reflection, runtime annotation, service provider, binary class name using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Read Version on the known Friendly provider. The final exercise transfers the mechanism to treat provider metadata as a policy input.

## Purpose and mental model

Reflection inspects or invokes program elements through metadata rather than ordinary compile-time calls. It can support frameworks and tooling,but it moves some errors from compilation to runtime and can obscure dependencies. An annotation is metadata;it does not enforce behavior until code reads it and applies a policy. Runtime retention is required when reflection should see an annotation after compilation.

ServiceLoader provides a structured provider-discovery mechanism. A service interface defines the contract,and provider metadata names implementations. The provider still needs a compatible constructor,module/classpath visibility and behavior. This lesson creates an owned temporary service descriptor for a known local nested provider,loads it through a scoped URLClassLoader,and validates its annotation and method behavior. It does not load remote code or accept arbitrary class names from untrusted input.

## Vocabulary and concepts

**Reflection:** Runtime inspection or invocation through class metadata.

**Runtime annotation:** Metadata retained so reflection can inspect it after compilation.

**Service provider:** An implementation discovered through a declared service contract.

**Binary class name:** The runtime name used by class loading,including nested-class dollar separators.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-031/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Use getAnnotation for a runtime-retained annotation andgetMethod for a public method signature. Method.invoke wraps an exception thrown by the target in InvocationTargetException. Class.forName reports missing classes explicitly. Aclasspath service descriptor is namedMETA-INF/services/<service-interface-binary-name> and contains provider binary names. Close the owned URLClassLoader and temporary directory after discovery.

## Worked example / walkthrough

### Example A: Inspect a retained annotation

The annotation's retention policy makes it visible at runtime. Its value is information for a compatibility check,not automatic enforcement.

```java
import java.util.*;

public class Main {
    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.TYPE)
    public @interface Version { int value(); }
    public interface Greeting { String greet(String name); }
    @Version(2) public static final class Friendly implements Greeting {
        public Friendly(){}
        public String greet(String name){if(name==null||name.isBlank())throw new IllegalArgumentException("nonblank name required");return "Hello, "+name;}
    }
    static final class ServiceFixture implements AutoCloseable {
        final java.nio.file.Path root;final java.net.URLClassLoader loader;
        ServiceFixture() throws Exception {root=java.nio.file.Files.createTempDirectory("ds60-service-");var descriptor=root.resolve("META-INF/services").resolve(Greeting.class.getName());java.nio.file.Files.createDirectories(descriptor.getParent());java.nio.file.Files.writeString(descriptor,Friendly.class.getName()+System.lineSeparator());loader=new java.net.URLClassLoader(new java.net.URL[]{root.toUri().toURL()},Main.class.getClassLoader());}
        public void close() throws Exception {loader.close();try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
    }
    public static void main(String[] args) throws Exception {
        Version version=Friendly.class.getAnnotation(Version.class);
        assert version!=null && version.value()==2;
    }
}

```

**Expected:** version 2.

### Example B: Invoke a known public method reflectively

The method name and parameter types form an explicit signature. A wrong signature fails at lookup rather than silently selecting an unrelated overload.

```java
import java.util.*;

public class Main {
    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.TYPE)
    public @interface Version { int value(); }
    public interface Greeting { String greet(String name); }
    @Version(2) public static final class Friendly implements Greeting {
        public Friendly(){}
        public String greet(String name){if(name==null||name.isBlank())throw new IllegalArgumentException("nonblank name required");return "Hello, "+name;}
    }
    static final class ServiceFixture implements AutoCloseable {
        final java.nio.file.Path root;final java.net.URLClassLoader loader;
        ServiceFixture() throws Exception {root=java.nio.file.Files.createTempDirectory("ds60-service-");var descriptor=root.resolve("META-INF/services").resolve(Greeting.class.getName());java.nio.file.Files.createDirectories(descriptor.getParent());java.nio.file.Files.writeString(descriptor,Friendly.class.getName()+System.lineSeparator());loader=new java.net.URLClassLoader(new java.net.URL[]{root.toUri().toURL()},Main.class.getClassLoader());}
        public void close() throws Exception {loader.close();try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
    }
    public static void main(String[] args) throws Exception {
        Version version=Friendly.class.getAnnotation(Version.class);
        assert version!=null && version.value()==2;

        var method=Friendly.class.getMethod("greet",String.class);
        assert method.invoke(new Friendly(),"Ada").equals("Hello, Ada");
    }
}

```

**Expected:** Hello, Ada.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Inspect a retained annotation.** Read Version on the known Friendly provider.
   **Expected:** version 2.
   **Verify:** Compare your assertion values or captured diagnostic with version 2.

2. **Invoke a known public method reflectively.** Findgreet(String) and invoke it with Ada.
   **Expected:** Hello, Ada.
   **Verify:** Compare your assertion values or captured diagnostic with Hello, Ada.

3. **Load a real local service descriptor.** Create the temporaryMETA-INF/services entry and discover Greeting providers.
   **Expected:** oneFriendly provider with version 2 andworkinggreet.
   **Verify:** Compare your assertion values or captured diagnostic with oneFriendly provider with version 2 andworkinggreet.

4. **Preserve a reflected target failure.** Invokegreet with blank text and inspect InvocationTargetException cause.
   **Expected:** causeIllegalArgumentException.
   **Verify:** Compare your assertion values or captured diagnostic with causeIllegalArgumentException.

5. **Reject missing class and method contracts.** Look up an absent class and an unsupportedgreet(int)signature.
   **Expected:** ClassNotFoundException and NoSuchMethodException.
   **Verify:** Compare your assertion values or captured diagnostic with ClassNotFoundException and NoSuchMethodException.

6. **Treat provider metadata as a policy input.** Accept provider versions1..2 and reject a hypotheticalversion3 under the current consumer contract.
   **Expected:** version 2 accepted;version 3 rejected.
   **Verify:** Compare your assertion values or captured diagnostic with version 2 accepted;version 3 rejected.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Reflection, Runtime annotation, Service provider in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ServiceLoader.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-031: Reflection, annotations and service loading.
Read courses/java/guides/java-031.md and courses/java/lessons/java-031.java. Direct prerequisites: `java-030`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
