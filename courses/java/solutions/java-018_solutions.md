# java-018: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A useful test distinguishes correct behavior from a plausible mistake. Repeating the implementation formula in the expected value can reproduce the same bug on both sides. Use independent examples,boundary cases and properties that follow from the contract. A mutation test deliberately changes one behavior and checks that the tests detect it. Assertions are convenient in this course because the launcher enables-ea,but production test suites often use a dedicated framework so checks cannot be disabled accidentally. Tests should expose failures rather than catch every exception and print success.

**Test oracle:** An independent basis for deciding the expected result.

**Property:** A relation that should hold across a family of inputs.

**Mutation test:** A check that an intentionally broken variant is detected.

## Reading the reference

A table-driven test stores inputs and expected outputs together,then runs the same checker over all cases. A property test checks a relation over several inputs,such as reversing twice restoring an array. An exception helper should verify the expected type and fail when no exception occurs. Keep test fixtures deterministic and avoid timing assumptions for concurrency. A test passing on one input says nothing about untested boundaries unless a valid general argument supports the claim.

## Exercise 1: Use independent table cases

Task: Test clamp for values -2,0,3,9 under bounds 0..5.

The expected outputs are literal contract examples. They do not call clamp or duplicate its full branching logic to generate answers.

```java
int[][] cases={{-2,0},{0,0},{3,3},{9,5}};
for(int[] row:cases) assert clamp(row[0],0,5)==row[1];
```

**Expected:** outputs 0,0,3,5.

**Verify:** Compare the program values or named exception with outputs 0,0,3,5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Check a boundary failure

Task: Callclamp withlower5,upper2 and requireIllegalArgumentException.

An invalid interval is different from a value outside a valid interval. The test ensures the implementation rejects the contract violation.

```java
expect(IllegalArgumentException.class,() -> clamp(3,5,2));
```

**Expected:** exception observed.

**Verify:** Compare the program values or named exception with exception observed. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Test an idempotence property

Task: For values-10 through10,clamping an already clamped value leaves it unchanged.

The property follows from the output range contract. It adds coverage,but a constant-returning mutant could also be idempotent,so examples remain necessary.

```java
for(int value=-10;value<=10;value++) {
    int once=clamp(value,0,5); assert clamp(once,0,5)==once;
}
```

**Expected:** all21 cases satisfyidempotence.

**Verify:** Compare the program values or named exception with all21 cases satisfyidempotence. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Detect a broken implementation

Task: Use a mutant that returns upper for values below lower and show the table rejects it.

A test suite should fail on a meaningful defect. This control demonstrates that the lower-bound example is not merely decorative.

```java
boolean caught=false;
for(int[] row:cases) if(brokenClamp(row[0],0,5)!=row[1]) caught=true;
assert caught;
```

**Expected:** at least one mismatch.

**Verify:** Compare the program values or named exception with at least one mismatch. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Verify the exception checker itself

Task: Ask the helper to expect an exception from a successful action and catch itsAssertionError.

A broken helper that silently accepts success would make every negative test pass. Testing the test utility is justified because it is a shared correctness boundary.

```java
boolean checkerFailed=false;
try { expect(IllegalArgumentException.class,() -> { }); }
catch(AssertionError expected){checkerFailed=true;}
assert checkerFailed;
```

**Expected:** checker fails when no exception is thrown.

**Verify:** Compare the program values or named exception with checker fails when no exception is thrown. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Test a fresh transfer property

Task: Reverse arrays oflength0,1,3 twice using a separate copy and compare with originals.

The round-trip property and a directional example complement each other. A function returning its input unchanged would pass only the round trip,so the second assertion matters.

```java
for(int[] original:List.of(new int[0],new int[]{4},new int[]{1,2,3})) {
    int[] first=reverse(original); int[] second=reverse(first);
    assert Arrays.equals(second,original);
    if(original.length>1) assert first[0]==original[original.length-1];
}
```

**Expected:** all originals restored; input arrays unchanged.

**Verify:** Compare the program values or named exception with all originals restored; input arrays unchanged. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
