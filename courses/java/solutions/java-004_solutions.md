# java-004: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A method packages a computation behind a contract: which inputs it accepts, what it returns, what state it changes and how it reports invalid input. Parameters are local variables initialized from argument values. Java always passes values. For an object argument, the copied value is a reference, so both caller and callee can refer to the same mutable object. Reassigning the parameter changes only the local reference; mutating the referenced object can be visible to the caller. Overloading selects among methods by parameter types at compile time, while overriding is a different runtime mechanism introduced later. Small explicit contracts make methods testable without reading every caller.

**Parameter:** A local variable receiving an argument value.

**Return value:** The result passed back when a method completes.

**Pass by value:** Copying argument values into method parameters.

## Reading the reference

A method declaration includes return type, name and parameter list. return sends one value to the caller and ends that invocation. Validate a domain precondition before calculating. Overloaded methods need different parameter signatures, not merely different return types. A defensive copy can prevent a helper from changing caller-owned mutable data. Use named exceptions when an argument violates the contract.

## Exercise 1: Call a pure calculation: predict an edited check

Task: Change Example A's assertion to `assert doubleValue(1) == 0;`, predict whether it holds, then run and restore it.

The result depends only on the argument and the method changes no external state. That makes normal and boundary cases easy to test independently.

The unchanged code is the part that Example A adds:

```java
assert doubleValue(7) == 14;
assert doubleValue(0) == 0;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `doubleValue(0) == 0`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `doubleValue(0) == 0`.

## Exercise 2: Validate a precondition: debug a regression

Task: A regression in Example B's new code makes one line read `positiveArea(1, 4);`. Repair it using the failing assertion.

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

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `badArea`; the repaired line reads `positiveArea(0, 4);`.

**Verify:** Explain how the changed token alters the value that `badArea` tests.

## Exercise 3: Observe copied primitive values

Task: Pass int 5 to a helper that reassigns its local parameter to 99.

The callee receives a copy of the integer. Reassigning its parameter does not create a link back to the caller variable.

```java
int original = 5;
reassignInt(original);
assert original == 5;
```

**Expected:** caller value remains 5.

**Verify:** Control: changing `int original = 5;` to `int original = 6;` must fail the assertion on `original == 5`.

## Exercise 4: Observe shared object mutation

Task: Pass a list containing 1 to a helper that appends 2.

The reference value is copied, and both references identify the same list. Mutating that object is visible through either reference.

```java
List<Integer> list = new ArrayList<>(List.of(1));
append(list);
assert list.equals(List.of(1, 2));
```

**Expected:** caller list becomes 1, 2.

**Verify:** Control: changing `List<Integer> list = new ArrayList<>(List.of(1));` to `List<Integer> list = new ArrayList<>(List.of(2));` must fail the assertion on `list.equals(List.of(1, 2))`.

## Exercise 5: Distinguish reference reassignment

Task: Pass the list to a helper that replaces only its local parameter with a new list.

Reassigning a local reference does not mutate the original object and does not reassign the caller variable. This is still pass by value.

```java
replace(list);
assert list.equals(List.of(1, 2));
```

**Expected:** caller list remains 1, 2.

**Verify:** Control: changing `assert list.equals(List.of(1, 2));` to `assert list.equals(List.of(2, 2));` inside the assertion must make it fail.

## Exercise 6: Inspect overload selection

Task: Call describe with int 1 and long 1L using two overloads.

The literal type selects the overload. This compile-time selection is distinct from polymorphic dispatch on an object receiver.

```java
assert describe(1).equals("int");
assert describe(1L).equals("long");
```

**Expected:** int and long respectively.

**Verify:** Control: changing `assert describe(1L).equals("long");` to `assert describe(1L).equals("long!");` inside the assertion must make it fail.

## After comparing the answer

Add an overload `describe(Integer)` to your copy, predict which method `describe(1)` selects now, and confirm that an exact primitive match still wins over boxing.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
