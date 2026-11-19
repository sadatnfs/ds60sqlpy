# java-004: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A method packages a computation behind a contract: which inputs it accepts, what it returns, what state it changes and how it reports invalid input. Parameters are local variables initialized from argument values. Java always passes values. For an object argument, the copied value is a reference, so both caller and callee can refer to the same mutable object. Reassigning the parameter changes only the local reference; mutating the referenced object can be visible to the caller. Overloading selects among methods by parameter types at compile time, while overriding is a different runtime mechanism introduced later. Small explicit contracts make methods testable without reading every caller.

**Parameter:** A local variable receiving an argument value.

**Return value:** The result passed back when a method completes.

**Pass by value:** Copying argument values into method parameters.

## Reading the reference

A method declaration includes return type, name and parameter list. return sends one value to the caller and ends that invocation. Validate a domain precondition before calculating. Overloaded methods need different parameter signatures, not merely different return types. A defensive copy can prevent a helper from changing caller-owned mutable data. Use named exceptions when an argument violates the contract.

## Exercise 1: Call a pure calculation: predict an edited check

Task: Copy Example A into a scratch `Main.java` and change `assert doubleValue(0) == 0;` to `assert doubleValue(1) == 0;` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.

The result depends only on the argument and the method changes no external state. That makes normal and boundary cases easy to test independently.

The unchanged code is the part that Example A adds:

```java
assert doubleValue(7) == 14;
assert doubleValue(0) == 0;
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `doubleValue(0) == 0`. Restoring the original line brings back the worked observation: 14 and 0.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `doubleValue(0) == 0`. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Validate a precondition: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `positiveArea(1, 4);`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

A zero dimension is rejected because this method models a strictly positive rectangle. Another domain could allow zero, but its contract must say so.

The unchanged code is the part that Example B adds:

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

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `badArea`; after it the line reads `positiveArea(0, 4);` again and 3 by 4 gives 12; zero width throws IllegalArgumentException.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `badArea` for this input.

## Exercise 3: Observe copied primitive values

Task: Pass int 5 to a helper that reassigns its local parameter to 99.

The callee receives a copy of the integer. Reassigning its parameter does not create a link back to the caller variable.

```java
int original = 5;
reassignInt(original);
assert original == 5;
```

**Expected:** caller value remains 5.

**Verify:** Keep an assertion equivalent to `original == 5`. As a control, change `int original = 5;` to `int original = 6;`: the run must fail with an `AssertionError` from the assertion on `original == 5`. Restore the line before continuing.

## Exercise 4: Observe shared object mutation

Task: Pass a list containing 1 to a helper that appends 2.

The reference value is copied, and both references identify the same list. Mutating that object is visible through either reference.

```java
List<Integer> list = new ArrayList<>(List.of(1));
append(list);
assert list.equals(List.of(1, 2));
```

**Expected:** caller list becomes 1, 2.

**Verify:** Keep an assertion equivalent to `list.equals(List.of(1, 2))`. As a control, change `List<Integer> list = new ArrayList<>(List.of(1));` to `List<Integer> list = new ArrayList<>(List.of(2));`: the run must fail with an `AssertionError` from the assertion on `list.equals(List.of(1, 2))`. Restore the line before continuing.

## Exercise 5: Distinguish reference reassignment

Task: Pass the list to a helper that replaces only its local parameter with a new list.

Reassigning a local reference does not mutate the original object and does not reassign the caller variable. This is still pass by value.

```java
replace(list);
assert list.equals(List.of(1, 2));
```

**Expected:** caller list remains 1, 2.

**Verify:** Keep an assertion equivalent to `list.equals(List.of(1, 2))`. As a control, change `assert list.equals(List.of(1, 2));` to `assert list.equals(List.of(2, 2));` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 6: Inspect overload selection

Task: Call describe with int 1 and long 1L using two overloads.

The literal type selects the overload. This compile-time selection is distinct from polymorphic dispatch on an object receiver.

```java
assert describe(1).equals("int");
assert describe(1L).equals("long");
```

**Expected:** int and long respectively.

**Verify:** Keep an assertion equivalent to `describe(1L).equals("long")`. As a control, change `assert describe(1L).equals("long");` to `assert describe(1L).equals("long!");` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
