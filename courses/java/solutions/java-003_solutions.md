# java-003: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Control flow chooses which statements run and how often. A boolean expression has a truth value, while short-circuit operators can skip an operand entirely. That behavior lets a null check guard a later method call. A loop invariant is a statement that remains true before and after each iteration; it connects a repeated computation to its intended result. For a prefix sum, the accumulator equals the sum of elements already visited. Boundary cases such as an empty array or a limit of zero test whether the initial state and termination condition are correct. A loop that works for one nonempty example can still have an off-by-one error.

**Short circuit:** Skipping an operand once a boolean result is determined.

**Loop invariant:** A property preserved at every iteration boundary.

**Boundary case:** An input at an edge of the accepted domain.

## Reading the reference

if selects a branch. && evaluates the right operand only when the left istrue;|| evaluates it only when needed. A for loop has initialization,condition andupdate. Use index<length for zero-based arrays. The prefix-sum invariant starts with index0,sum0, then adds exactly the element at the current index before advancing. Break exits the loop;continue skips to the next iteration and can accidentally bypass an update in a while loop.

## Exercise 1: Guard a nullable value

Task: Use textnull and testtext!=null before callingisEmpty.

The right operand is not evaluated when the left isfalse. Reversing the operands would attempt the method call before the guard.

```java
String text = null;
boolean nonempty = text != null && !text.isEmpty();
assert !nonempty;
```

**Expected:** conditionfalse with noNullPointerException.

**Verify:** Compare the program values or named exception with conditionfalse with noNullPointerException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Trace a prefix sum

Task: Sum array2,4,6 while retaining the invariant thatsum covers indices belowi.

The accumulator begins at the additive identity0. Each iteration adds one new element, so no record is skipped or counted twice.

```java
int[] values = {2, 4, 6}; int sum = 0;
List<Integer> prefixes = new ArrayList<>();
for (int i = 0; i < values.length; i++) { sum += values[i]; prefixes.add(sum); }
assert prefixes.equals(List.of(2, 6, 12)) && sum == 12;
```

**Expected:** prefix sums2,6,12;final12.

**Verify:** Compare the program values or named exception with prefix sums2,6,12;final12. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Handle an empty loop

Task: Run the same sum pattern over an emptyint array.

An empty collection is a valid case for this sum contract. The initial value already represents the result, so no special fabricated element is needed.

```java
int emptySum = 0; int iterations = 0;
for (int value : new int[0]) { emptySum += value; iterations++; }
assert emptySum == 0 && iterations == 0;
```

**Expected:** sum0 and zero iterations.

**Verify:** Compare the program values or named exception with sum0 and zero iterations. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Count a half-open interval

Task: Count integers starting0 whilei<5.

Half-open bounds align naturally with array indices. Using<= would include5 and create six iterations.

```java
List<Integer> visited = new ArrayList<>();
for (int i = 0; i < 5; i++) visited.add(i);
assert visited.equals(List.of(0, 1, 2, 3, 4));
```

**Expected:** visited0,1,2,3,4;count5.

**Verify:** Compare the program values or named exception with visited0,1,2,3,4;count5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Stop at the first match

Task: Search3,8,8 for the first8 and stop immediately.

Without thebreak, later matches would overwrite the first index. The sentinel-1 represents absence and cannot be mistaken for index0.

```java
int[] items = {3, 8, 8}; int found = -1;
for (int i = 0; i < items.length; i++) { if (items[i] == 8) { found = i; break; } }
assert found == 1;
```

**Expected:** index1.

**Verify:** Compare the program values or named exception with index1. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Expose a wrong boundary

Task: Compare a loop usingi<=length with the validi<length contract on a one-element array.

The invalid condition reachesindex1 whenlength1. This tiny counterexample localizes the off-by-one error more clearly than a large dataset.

```java
boolean failed = false; int[] single = {7};
try { for (int i = 0; i <= single.length; i++) { int ignored = single[i]; } }
catch (ArrayIndexOutOfBoundsException expected) { failed = true; }
assert failed;
```

**Expected:** wrong loop raisesArrayIndexOutOfBoundsException.

**Verify:** Compare the program values or named exception with wrong loop raisesArrayIndexOutOfBoundsException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
