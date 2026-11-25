# java-031: Reflection, annotations and service loading

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-030`

## Learning objectives

Inspect annotations, invoke methods reflectively and load services with ServiceLoader while preserving failure causes.

The six exercises practice these steps:

- Inspect a retained annotation.
- Invoke a known public method reflectively.
- Load a real local service descriptor.
- Preserve a reflected target failure.
- Reject missing class and method contracts.
- Treat provider metadata as a policy input.

## Purpose and mental model

Reflection inspects or invokes program elements through metadata rather than ordinary compile-time calls. It can support frameworks and tooling, but it moves some errors from compilation to runtime and can obscure dependencies. An annotation is metadata; it does not enforce behavior until code reads it and applies a policy. Runtime retention is required when reflection should see an annotation after compilation.

ServiceLoader provides a structured provider-discovery mechanism. A service interface defines the contract, and provider metadata names implementations. The provider still needs a compatible constructor, module/classpath visibility and behavior. This lesson creates an owned temporary service descriptor for a known local nested provider, loads it through a scoped URLClassLoader, and validates its annotation and method behavior. It does not load remote code or accept arbitrary class names from untrusted input.

## Vocabulary and concepts

**Reflection:** Runtime inspection or invocation through class metadata.

**Runtime annotation:** Metadata retained so reflection can inspect it after compilation.

**Service provider:** An implementation discovered through a declared service contract.

**Binary class name:** The runtime name used by class loading, including nested-class dollar separators.

## How to run this lesson

`ServiceFixture` writes a `META-INF/services` descriptor naming `Friendly` into an owned temporary directory and opens a `URLClassLoader` on it; `close` closes the loader and deletes the directory, and no remote code is loaded.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Use getAnnotation for a runtime-retained annotation and getMethod for a public method signature. Method.invoke wraps an exception thrown by the target in InvocationTargetException. Class.forName reports missing classes explicitly. A classpath service descriptor is named META-INF/services/<service-interface-binary-name> and contains provider binary names. Close the owned URLClassLoader and temporary directory after discovery.

## Worked example / walkthrough

### Example A: Inspect a retained annotation

The annotation's retention policy makes it visible at runtime. Its value is information for a compatibility check, not automatic enforcement.

```java
import java.util.*;

public class Main {

  @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
  @java.lang.annotation.Target(java.lang.annotation.ElementType.TYPE)
  public @interface Version {
    int value();
  }

  public interface Greeting {
    String greet(String name);
  }

  @Version(2)
  public static final class Friendly implements Greeting {

    public Friendly() {}

    public String greet(String name) {
      if (name == null || name.isBlank()) throw new IllegalArgumentException(
        "nonblank name required"
      );
      return "Hello, " + name;
    }
  }

  static final class ServiceFixture implements AutoCloseable {

    final java.nio.file.Path root;
    final java.net.URLClassLoader loader;

    ServiceFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-service-");
      var descriptor = root.resolve("META-INF/services").resolve(Greeting.class.getName());
      java.nio.file.Files.createDirectories(descriptor.getParent());
      java.nio.file.Files.writeString(
        descriptor,
        Friendly.class.getName() + System.lineSeparator()
      );
      loader = new java.net.URLClassLoader(
        new java.net.URL[] { root.toUri().toURL() },
        Main.class.getClassLoader()
      );
    }

    public void close() throws Exception {
      loader.close();
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Version version = Friendly.class.getAnnotation(Version.class);
    assert version != null && version.value() == 2;
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
  public @interface Version {
    int value();
  }

  public interface Greeting {
    String greet(String name);
  }

  @Version(2)
  public static final class Friendly implements Greeting {

    public Friendly() {}

    public String greet(String name) {
      if (name == null || name.isBlank()) throw new IllegalArgumentException(
        "nonblank name required"
      );
      return "Hello, " + name;
    }
  }

  static final class ServiceFixture implements AutoCloseable {

    final java.nio.file.Path root;
    final java.net.URLClassLoader loader;

    ServiceFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-service-");
      var descriptor = root.resolve("META-INF/services").resolve(Greeting.class.getName());
      java.nio.file.Files.createDirectories(descriptor.getParent());
      java.nio.file.Files.writeString(
        descriptor,
        Friendly.class.getName() + System.lineSeparator()
      );
      loader = new java.net.URLClassLoader(
        new java.net.URL[] { root.toUri().toURL() },
        Main.class.getClassLoader()
      );
    }

    public void close() throws Exception {
      loader.close();
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Version version = Friendly.class.getAnnotation(Version.class);
    assert version != null && version.value() == 2;

    var method = Friendly.class.getMethod("greet", String.class);
    assert method.invoke(new Friendly(), "Ada").equals("Hello, Ada");
  }
}
```

**Expected:** Hello, Ada.

## Prediction before your attempt

Before running Example A, decide whether `Friendly.class.getAnnotation(Version.class)` returns the annotation, and what it would return if `Version` had the default class retention. For Example B, predict the string `greet` returns when invoked reflectively with "Ada". Before Exercise 4, decide what exception reaches the caller when the reflected method itself throws `IllegalArgumentException`.

## Exercises

1. **Inspect a retained annotation: predict an edited check.** Change Example A's assertion to `assert version != null && version.value() == 3;`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `version != null && version.value() == 2`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `version != null && version.value() == 2`.

2. **Invoke a known public method reflectively: diagnose an edited check.** Example B's new assertion was edited to `assert method.invoke(new Friendly(), "Ada!").equals("Hello, Ada");`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `method.invoke(new Friendly(), "Ada").equals("Hello, Ada")`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `method.invoke(new Friendly(), "Ada").equals("Hello, Ada")` accepts.

3. **Load a real local service descriptor.** Create the temporaryMETA-INF/services entry and discover Greeting providers.
   **Expected:** one Friendly provider with version 2 and working greet.
   **Verify:** Control: changing `assert providers.get(0).greet("Lin").equals("Hello, Lin");` to `assert providers.get(0).greet("Lin!").equals("Hello, Lin");` inside the assertion must make it fail.

4. **Preserve a reflected target failure.** Invoke greet with blank text and inspect InvocationTargetException cause.
   **Expected:** cause IllegalArgumentException.
   **Verify:** Control: changing `method.invoke(new Friendly(), " ");` to `method.invoke(new Friendly(), " !");` must fail the assertion on `targetFailure`.

5. **Reject missing class and method contracts.** Look up an absent class and an unsupported greet(int) signature.
   **Expected:** ClassNotFoundException and NoSuchMethodException.
   **Verify:** Control: changing `missingClass = true;` to `missingClass = false;` must fail the assertion on `missingClass && missingMethod`.

6. **Treat provider metadata as a policy input.** Accept provider versions 1..2 and reject a hypothetical version 3 under the current consumer contract.
   **Expected:** version 2 accepted; version 3 rejected.
   **Verify:** Control: changing `int supportedMaximum = 2;` to `int supportedMaximum = 3;` must fail the assertion on `3 > supportedMaximum`.

## Common pitfalls and diagnosis

Reflection moves errors from compile time to run time: a renamed method or wrong parameter type fails only when the code runs, so validate reflective lookups at startup. An annotation without `RetentionPolicy.RUNTIME` is invisible to `getAnnotation`. `Method.invoke` wraps target exceptions in `InvocationTargetException`, and reporting the wrapper hides the real cause. `ServiceLoader` needs a public no-argument constructor. And loading a class name taken from user input is a code execution risk, so use a fixed allowlist.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the in-check edit expects `version.value()` to be 3. Then read the annotation on `Friendly`, which declares 2. Finally, explain why the annotation was found and only the value comparison fails.
- **Exercise 2:** First note that the in-check edit invokes `greet` with "Ada!". Then compute the returned string, "Hello, Ada!". Finally, compare it with "Hello, Ada" and explain why the reflective lookup and invocation both worked.
- **Exercise 3:** First create a `ServiceFixture`, which writes the descriptor and opens its class loader. Then call `ServiceLoader.load(Greeting.class, fixture.loader)` and collect the providers. Finally, assert one `Friendly` provider whose `greet("Lin")` returns "Hello, Lin".
- **Exercise 4:** First look up `greet(String)` with `getMethod`. Then invoke it with a single space inside a `try` block and catch `InvocationTargetException`. Finally, assert that `getCause()` is an `IllegalArgumentException` from the target method.
- **Exercise 5:** First call `Class.forName` with a name that does not exist and catch `ClassNotFoundException`. Then ask `Friendly.class` for `greet(int)` and catch `NoSuchMethodException`. Finally, assert both flags and explain why reflection delays these checks.
- **Exercise 6:** First set the supported maximum to 2 and assert that `Friendly`'s version lies between 1 and that maximum. Then assert that a provider declaring version 3 falls outside the range. Finally, explain why the consumer, not the annotation, owns this policy.

## Self-check and retrieval

Without the guide, explain what runtime retention means and why an annotation by itself enforces nothing. Describe how `getMethod` selects an overload, what `InvocationTargetException.getCause()` returns, and the three things `ServiceLoader` needs to construct a provider.

## Next step

Continue with `java-032`: Profiling and benchmark reasoning. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ServiceLoader.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-031: Reflection, annotations and service loading.
Read courses/java/guides/java-031.md and courses/java/lessons/java-031.java. Direct prerequisites: `java-030`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
