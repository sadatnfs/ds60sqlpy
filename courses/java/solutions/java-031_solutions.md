# java-031: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Reflection inspects or invokes program elements through metadata rather than ordinary compile-time calls. It can support frameworks and tooling, but it moves some errors from compilation to runtime and can obscure dependencies. An annotation is metadata; it does not enforce behavior until code reads it and applies a policy. Runtime retention is required when reflection should see an annotation after compilation.

ServiceLoader provides a structured provider-discovery mechanism. A service interface defines the contract, and provider metadata names implementations. The provider still needs a compatible constructor, module/classpath visibility and behavior. This lesson creates an owned temporary service descriptor for a known local nested provider, loads it through a scoped URLClassLoader, and validates its annotation and method behavior. It does not load remote code or accept arbitrary class names from untrusted input.

**Reflection:** Runtime inspection or invocation through class metadata.

**Runtime annotation:** Metadata retained so reflection can inspect it after compilation.

**Service provider:** An implementation discovered through a declared service contract.

**Binary class name:** The runtime name used by class loading, including nested-class dollar separators.

## Reading the reference

Use getAnnotation for a runtime-retained annotation and getMethod for a public method signature. Method.invoke wraps an exception thrown by the target in InvocationTargetException. Class.forName reports missing classes explicitly. A classpath service descriptor is named META-INF/services/<service-interface-binary-name> and contains provider binary names. Close the owned URLClassLoader and temporary directory after discovery.

## Exercise 1: Inspect a retained annotation: predict an edited check

Task: Change Example A's assertion to `assert version != null && version.value() == 3;`, predict whether it holds, then run and restore it.

The annotation's retention policy makes it visible at runtime. Its value is information for a compatibility check, not automatic enforcement.

The unchanged code is the part that Example A adds:

```java
Version version = Friendly.class.getAnnotation(Version.class);
assert version != null && version.value() == 2;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `version != null && version.value() == 2`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `version != null && version.value() == 2`.

## Exercise 2: Invoke a known public method reflectively: diagnose an edited check

Task: Example B's new assertion was edited to `assert method.invoke(new Friendly(), "Ada!").equals("Hello, Ada");`. Explain why it fails for unchanged state and restore it.

The method name and parameter types form an explicit signature. A wrong signature fails at lookup rather than silently selecting an unrelated overload.

The unchanged code is the part that Example B adds:

```java
var method = Friendly.class.getMethod("greet", String.class);
assert method.invoke(new Friendly(), "Ada").equals("Hello, Ada");
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `method.invoke(new Friendly(), "Ada").equals("Hello, Ada")`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `method.invoke(new Friendly(), "Ada").equals("Hello, Ada")` accepts.

## Exercise 3: Load a real local service descriptor

Task: Create the temporaryMETA-INF/services entry and discover Greeting providers.

This exercises actual ServiceLoader discovery and provider construction. A manually instantiated object alone would not verify the descriptor path or binary names.

```java
try (ServiceFixture fixture = new ServiceFixture()) {
  var providers = java.util.ServiceLoader.load(Greeting.class, fixture.loader)
    .stream()
    .map(java.util.ServiceLoader.Provider::get)
    .toList();
  assert providers.size() == 1 && providers.get(0).getClass() == Friendly.class;
  assert providers.get(0).greet("Lin").equals("Hello, Lin");
}
```

**Expected:** one Friendly provider with version 2 and working greet.

**Verify:** Control: changing `assert providers.get(0).greet("Lin").equals("Hello, Lin");` to `assert providers.get(0).greet("Lin!").equals("Hello, Lin");` inside the assertion must make it fail.

## Exercise 4: Preserve a reflected target failure

Task: Invoke greet with blank text and inspect InvocationTargetException cause.

The wrapper distinguishes invocation machinery from the domain failure thrown by the target. Preserve the cause when reporting it.

```java
boolean targetFailure = false;
try {
  method.invoke(new Friendly(), " ");
} catch (java.lang.reflect.InvocationTargetException expected) {
  targetFailure = expected.getCause() instanceof IllegalArgumentException;
}
assert targetFailure;
```

**Expected:** cause IllegalArgumentException.

**Verify:** Control: changing `method.invoke(new Friendly(), " ");` to `method.invoke(new Friendly(), " !");` must fail the assertion on `targetFailure`.

## Exercise 5: Reject missing class and method contracts

Task: Look up an absent class and an unsupported greet(int) signature.

Reflection does not remove type contracts; it delays some checks. Fixed allowlists and startup validation can keep failures understandable.

```java
boolean missingClass = false,
  missingMethod = false;
try {
  Class.forName("course.missing.NoSuchProvider");
} catch (ClassNotFoundException expected) {
  missingClass = true;
}
try {
  Friendly.class.getMethod("greet", int.class);
} catch (NoSuchMethodException expected) {
  missingMethod = true;
}
assert missingClass && missingMethod;
```

**Expected:** ClassNotFoundException and NoSuchMethodException.

**Verify:** Control: changing `missingClass = true;` to `missingClass = false;` must fail the assertion on `missingClass && missingMethod`.

## Exercise 6: Treat provider metadata as a policy input

Task: Accept provider versions 1..2 and reject a hypothetical version 3 under the current consumer contract.

A version annotation does not make a provider compatible by itself. The consumer must define and apply an admission policy and test actual behavior.

```java
int supportedMaximum = 2;
assert version.value() >= 1 && version.value() <= supportedMaximum;
assert 3 > supportedMaximum;
```

**Expected:** version 2 accepted; version 3 rejected.

**Verify:** Control: changing `int supportedMaximum = 2;` to `int supportedMaximum = 3;` must fail the assertion on `3 > supportedMaximum`.

## After comparing the answer

Add a second provider class with `@Version(3)` to your copy's descriptor and change Exercise 6 so the consumer filters providers by the supported range and keeps only `Friendly`.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
