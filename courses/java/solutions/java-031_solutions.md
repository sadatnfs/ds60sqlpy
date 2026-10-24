# java-031: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Reflection inspects or invokes program elements through metadata rather than ordinary compile-time calls. It can support frameworks and tooling,but it moves some errors from compilation to runtime and can obscure dependencies. An annotation is metadata;it does not enforce behavior until code reads it and applies a policy. Runtime retention is required when reflection should see an annotation after compilation.

ServiceLoader provides a structured provider-discovery mechanism. A service interface defines the contract,and provider metadata names implementations. The provider still needs a compatible constructor,module/classpath visibility and behavior. This lesson creates an owned temporary service descriptor for a known local nested provider,loads it through a scoped URLClassLoader,and validates its annotation and method behavior. It does not load remote code or accept arbitrary class names from untrusted input.

**Reflection:** Runtime inspection or invocation through class metadata.

**Runtime annotation:** Metadata retained so reflection can inspect it after compilation.

**Service provider:** An implementation discovered through a declared service contract.

**Binary class name:** The runtime name used by class loading,including nested-class dollar separators.

## Reading the reference

Use getAnnotation for a runtime-retained annotation andgetMethod for a public method signature. Method.invoke wraps an exception thrown by the target in InvocationTargetException. Class.forName reports missing classes explicitly. Aclasspath service descriptor is namedMETA-INF/services/<service-interface-binary-name> and contains provider binary names. Close the owned URLClassLoader and temporary directory after discovery.

## Exercise 1: Inspect a retained annotation

Task: Read Version on the known Friendly provider.

The annotation's retention policy makes it visible at runtime. Its value is information for a compatibility check,not automatic enforcement.

```java
Version version=Friendly.class.getAnnotation(Version.class);
assert version!=null && version.value()==2;
```

**Expected:** version 2.

**Verify:** Compare the program values or named exception with version 2. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Invoke a known public method reflectively

Task: Findgreet(String) and invoke it with Ada.

The method name and parameter types form an explicit signature. A wrong signature fails at lookup rather than silently selecting an unrelated overload.

```java
var method=Friendly.class.getMethod("greet",String.class);
assert method.invoke(new Friendly(),"Ada").equals("Hello, Ada");
```

**Expected:** Hello, Ada.

**Verify:** Compare the program values or named exception with Hello, Ada. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Load a real local service descriptor

Task: Create the temporaryMETA-INF/services entry and discover Greeting providers.

This exercises actual ServiceLoader discovery and provider construction. A manually instantiated object alone would not verify the descriptor path or binary names.

```java
try(ServiceFixture fixture=new ServiceFixture()) {
    var providers=java.util.ServiceLoader.load(Greeting.class,fixture.loader).stream().map(java.util.ServiceLoader.Provider::get).toList();
    assert providers.size()==1 && providers.get(0).getClass()==Friendly.class;
    assert providers.get(0).greet("Lin").equals("Hello, Lin");
}
```

**Expected:** oneFriendly provider with version 2 andworkinggreet.

**Verify:** Compare the program values or named exception with oneFriendly provider with version 2 andworkinggreet. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Preserve a reflected target failure

Task: Invokegreet with blank text and inspect InvocationTargetException cause.

The wrapper distinguishes invocation machinery from the domain failure thrown by the target. Preserve the cause when reporting it.

```java
boolean targetFailure=false;
try{method.invoke(new Friendly()," ");}catch(java.lang.reflect.InvocationTargetException expected){targetFailure=expected.getCause() instanceof IllegalArgumentException;}
assert targetFailure;
```

**Expected:** causeIllegalArgumentException.

**Verify:** Compare the program values or named exception with causeIllegalArgumentException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reject missing class and method contracts

Task: Look up an absent class and an unsupportedgreet(int)signature.

Reflection does not remove type contracts;it delays some checks. Fixed allowlists and startup validation can keep failures understandable.

```java
boolean missingClass=false,missingMethod=false;
try{Class.forName("course.missing.NoSuchProvider");}catch(ClassNotFoundException expected){missingClass=true;}
try{Friendly.class.getMethod("greet",int.class);}catch(NoSuchMethodException expected){missingMethod=true;}
assert missingClass && missingMethod;
```

**Expected:** ClassNotFoundException and NoSuchMethodException.

**Verify:** Compare the program values or named exception with ClassNotFoundException and NoSuchMethodException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Treat provider metadata as a policy input

Task: Accept provider versions1..2 and reject a hypotheticalversion3 under the current consumer contract.

A version annotation does not make a provider compatible by itself. The consumer must define and apply an admission policy and test actual behavior.

```java
int supportedMaximum=2;assert version.value()>=1 && version.value()<=supportedMaximum;
assert 3>supportedMaximum;
```

**Expected:** version 2 accepted;version 3 rejected.

**Verify:** Compare the program values or named exception with version 2 accepted;version 3 rejected. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
