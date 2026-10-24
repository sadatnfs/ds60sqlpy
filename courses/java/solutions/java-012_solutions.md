# java-012: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Generics express type relationships so many errors can be detected before execution. List<Integer> is not a subtype of List<Number>, because a caller holdingList<Number> could insert a Double and violate the original integer list. A producer wildcard?extends Number permits reading numbers but generally forbids adding a specific numeric subtype. A consumer wildcard?superInteger permits adding integers, while reads are only known asObject. A generic method can connect input and output types through a type parameter. Java implements most generics through erasure, so runtime class identity does not distinguish ArrayList<String> from ArrayList<Integer>. Avoid raw types that bypass these checks.

**Type parameter:** A named placeholder relating types in a declaration.

**Invariance:** Different generic arguments do not imply a subtype relationship.

**Wildcard bound:** A restriction describing safe reads or writes through a generic reference.

## Reading the reference

The<T> before a method return type declares a method type parameter. List<?extends Number> can be iterated asNumber for summation. List<?superInteger> can acceptInteger values. Use<T>void copy(List<?extendsT>source,List<?superT>target) to connect a producer and consumer. Wildcards describe allowed operations through a reference; they do not freeze the underlying object or create a runtime conversion.

## Exercise 1: Read from a producer

Task: Sum `List.of(1, 2, 3)` and `List.of(1.5, 2.5)` through List<?extends Number>.

The method needs only to readNumber values, so an extends bound accepts both integer and double lists without permitting unsafe insertion.

```java
assert sum(List.of(1,2,3))==6.0;
assert sum(List.of(1.5,2.5))==4.0;
```

**Expected:** sums 6.0 and 4.0.

**Verify:** Compare the program values or named exception with sums 6.0 and 4.0. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Write to a consumer

Task: Append integers1,2 to a List<Number> through List<?superInteger>.

A Number list can safely receiveInteger values. Reading through thesuper-bounded reference offers less precise type information because the actual list may contain other supertypes.

```java
List<Number> numbers=new ArrayList<>(); addTwo(numbers);
assert numbers.equals(List.of(1,2));
```

**Expected:** listcontains1,2.

**Verify:** Compare the program values or named exception with listcontains1,2. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Connect source and destination types

Task: CopyList<Integer> intoList<Number> with a bounded generic method.

The same type parameter links the producer and consumer. It permits safe widening without an unchecked cast.

```java
List<Number> destination=new ArrayList<>(); copy(List.of(3,4),destination);
assert destination.equals(List.of(3,4));
```

**Expected:** destinationcontains3,4.

**Verify:** Compare the program values or named exception with destinationcontains3,4. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Preserve generic return type

Task: Callfirst on a String list and assign directly toString.

The generic signature carries the element type to the return value. A rawObject return would force callers to cast and shift failures to runtime.

```java
String value=first(List.of("alpha","beta")); assert value.equals("alpha");
```

**Expected:** result alpha.

**Verify:** Compare the program values or named exception with result alpha. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Handle an empty input contract

Task: Callfirst on an empty list and require a named failure.

Type safety does not establish nonemptiness. A separate value-level precondition is still needed for an operation that requires an element.

```java
boolean empty=false;
try { first(List.of()); } catch(NoSuchElementException expected){empty=true;}
assert empty;
```

**Expected:** NoSuchElementException.

**Verify:** Compare the program values or named exception with NoSuchElementException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Observe erasure carefully

Task: Compare runtime classes of ArrayList<String> and ArrayList<Integer>;explain why this does not permit unsafe assignments.

Erasure describes runtime representation. It does not repeal the compiler rule thatList<Integer> cannot be assigned toList<Number>. Do not use raw casts to bypass that rule.

```java
var strings=new ArrayList<String>(); var integers=new ArrayList<Integer>();
assert strings.getClass().equals(integers.getClass());
assert strings.isEmpty() && integers.isEmpty();
```

**Expected:** runtime classes equal; compile-time contracts remain distinct.

**Verify:** Compare the program values or named exception with runtime classes equal; compile-time contracts remain distinct. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
