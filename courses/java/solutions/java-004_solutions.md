# java-004: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A method packages a computation behind a contract: which inputs it accepts, what it returns, what state it changes and how it reports invalid input. Parameters are local variables initialized from argument values. Java always passes values. For an object argument, the copied value is a reference, so both caller and callee can refer to the same mutable object. Reassigning the parameter changes only the local reference; mutating the referenced object can be visible to the caller. Overloading selects among methods by parameter types at compile time, while overriding is a different runtime mechanism introduced later. Small explicit contracts make methods testable without reading every caller.

**Parameter:** A local variable receiving an argument value.

**Return value:** The result passed back when a method completes.

**Pass by value:** Copying argument values into method parameters.

## Reading the reference

A method declaration includes return type,name and parameter list. return sends one value to the caller and ends that invocation. Validate a domain precondition before calculating. Overloaded methods need different parameter signatures, not merely different return types. A defensive copy can prevent a helper from changing caller-owned mutable data. Use named exceptions when an argument violates the contract.

## Exercise 1: Call a pure calculation

Task: Implement doubleValue(int x) and evaluate 7 and 0.

The result depends only on the argument and the method changes no external state. That makes normal and boundary cases easy to test independently.

```java
assert doubleValue(7) == 14;
assert doubleValue(0) == 0;
```

**Expected:** 14 and 0.

**Verify:** Compare the program values or named exception with 14 and 0. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Validate a precondition

Task: Implement positiveArea(width,height) rejecting nonpositive dimensions.

A zero dimension is rejected because this method models a strictly positive rectangle. Another domain could allow zero, but its contract must say so.

```java
assert positiveArea(3, 4) == 12;
boolean badArea = false;
try {
  positiveArea(0, 4);
} catch (IllegalArgumentException expected) {
  badArea = true;
}
assert badArea;
```

**Expected:** 3by4 gives12;zero width throwsIllegalArgumentException.

**Verify:** Compare the program values or named exception with 3by4 gives12;zero width throwsIllegalArgumentException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Observe copied primitive values

Task: Passint5 to a helper that reassigns its local parameter to99.

The callee receives a copy of the integer. Reassigning its parameter does not create a link back to the caller variable.

```java
int original = 5;
reassignInt(original);
assert original == 5;
```

**Expected:** caller value remains5.

**Verify:** Compare the program values or named exception with caller value remains5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Observe shared object mutation

Task: Pass a list containing1 to a helper that appends2.

The reference value is copied, and both references identify the same list. Mutating that object is visible through either reference.

```java
List<Integer> list = new ArrayList<>(List.of(1));
append(list);
assert list.equals(List.of(1, 2));
```

**Expected:** caller list becomes1,2.

**Verify:** Compare the program values or named exception with caller list becomes1,2. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Distinguish reference reassignment

Task: Pass the list to a helper that replaces only its local parameter with a new list.

Reassigning a local reference does not mutate the original object and does not reassign the caller variable. This is still pass by value.

```java
replace(list);
assert list.equals(List.of(1, 2));
```

**Expected:** caller list remains1,2.

**Verify:** Compare the program values or named exception with caller list remains1,2. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Inspect overload selection

Task: Call describe withint1 andlong1L using two overloads.

The literal type selects the overload. This compile-time selection is distinct from polymorphic dispatch on an object receiver.

```java
assert describe(1).equals("int");
assert describe(1L).equals("long");
```

**Expected:** int and long respectively.

**Verify:** Compare the program values or named exception with int and long respectively. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
