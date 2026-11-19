# java-018: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A useful test distinguishes correct behavior from a plausible mistake. Repeating the implementation formula in the expected value can reproduce the same bug on both sides. Use independent examples, boundary cases and properties that follow from the contract. A mutation test deliberately changes one behavior and checks that the tests detect it. Assertions are convenient in this course because the launcher enables-ea, but production test suites often use a dedicated framework so checks cannot be disabled accidentally. Tests should expose failures rather than catch every exception and print success.

**Test oracle:** An independent basis for deciding the expected result.

**Property:** A relation that should hold across a family of inputs.

**Mutation test:** A check that an intentionally broken variant is detected.

## Reading the reference

A table-driven test stores inputs and expected outputs together, then runs the same checker over all cases. A property test checks a relation over several inputs, such as reversing twice restoring an array. An exception helper should verify the expected type and fail when no exception occurs. Keep test fixtures deterministic and avoid timing assumptions for concurrency. A test passing on one input says nothing about untested boundaries unless a valid general argument supports the claim.

## Exercise 1: Use independent table cases: change one input

Task: Copy Example A into a scratch `Main.java` and change `int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };` to `int[][] cases = { { -2, 1 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The expected outputs are literal contract examples. They do not call clamp or duplicate its full branching logic to generate answers.

The unchanged code is the part that Example A adds:

```java
int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };
for (int[] row : cases) assert clamp(row[0], 0, 5) == row[1];
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `clamp(row[0], 0, 5) == row[1]`. Restoring the original line brings back the worked observation: outputs 0, 0, 3, 5.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `clamp(row[0], 0, 5) == row[1]` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Check a boundary failure: debug a regression

Task: Introduce one deliberate defect into the code that Example B adds after Example A and explain which observation exposes it, then repair it.

An invalid interval is different from a value outside a valid interval. The test ensures the implementation rejects the contract violation.

The unchanged code is the part that Example B adds:

```java
expect(IllegalArgumentException.class, () -> clamp(3, 5, 2));
```

**Expected:** The defective copy changes the observation; the repaired copy reproduces the worked observation: exception observed.

**Verify:** Keep the failing and the repaired runs and name the first statement whose value differs between them.

## Exercise 3: Test an idempotence property

Task: For values -10 through 10, clamping an already clamped value leaves it unchanged.

The property follows from the output range contract. It adds coverage, but a constant-returning mutant could also be idempotent, so examples remain necessary.

```java
for (int value = -10; value <= 10; value++) {
  int once = clamp(value, 0, 5);
  assert clamp(once, 0, 5) == once;
}
```

**Expected:** all 21 cases satisfy idempotence.

**Verify:** Keep an assertion equivalent to `clamp(once, 0, 5) == once`. As a control, change `int once = clamp(value, 0, 5);` to `int once = clamp(value, 0, 6);`: the run must fail with an `AssertionError` from the assertion on `clamp(once, 0, 5) == once`. Restore the line before continuing.

## Exercise 4: Detect a broken implementation

Task: Use a mutant that returns upper for values below lower and show the table rejects it.

A test suite should fail on a meaningful defect. This control demonstrates that the lower-bound example is not merely decorative.

```java
boolean caught = false;
for (int[] row : cases) if (brokenClamp(row[0], 0, 5) != row[1]) caught = true;
assert caught;
```

**Expected:** at least one mismatch.

**Verify:** Keep an assertion equivalent to `caught`. As a control, change `for (int[] row : cases) if (brokenClamp(row[0], 0, 5) != row[1]) caught = true;` to `for (int[] row : cases) if (brokenClamp(row[1], 0, 5) != row[1]) caught = true;`: the run must fail with an `AssertionError` from the assertion on `caught`. Restore the line before continuing.

## Exercise 5: Verify the exception checker itself

Task: Ask the helper to expect an exception from a successful action and catch its AssertionError.

A broken helper that silently accepts success would make every negative test pass. Testing the test utility is justified because it is a shared correctness boundary.

```java
boolean checkerFailed = false;
try {
  expect(IllegalArgumentException.class, () -> {});
} catch (AssertionError expected) {
  checkerFailed = true;
}
assert checkerFailed;
```

**Expected:** checker fails when no exception is thrown.

**Verify:** Keep an assertion equivalent to `checkerFailed`. As a control, change `checkerFailed = true;` to `checkerFailed = false;`: the run must fail with an `AssertionError` from the assertion on `checkerFailed`. Restore the line before continuing.

## Exercise 6: Test a fresh transfer property

Task: Reverse arrays of length 0, 1, 3 twice using a separate copy and compare with originals.

The round-trip property and a directional example complement each other. A function returning its input unchanged would pass only the round trip, so the second assertion matters.

```java
for (int[] original : List.of(new int[0], new int[] { 4 }, new int[] { 1, 2, 3 })) {
  int[] first = reverse(original);
  int[] second = reverse(first);
  assert Arrays.equals(second, original);
  if (original.length > 1) assert first[0] == original[original.length - 1];
}
```

**Expected:** all originals restored; input arrays unchanged.

**Verify:** Keep an assertion equivalent to `first[0] == original[original.length - 1]`. As a control, change `if (original.length > 1) assert first[0] == original[original.length - 1];` to `if (original.length > 1) assert first[1] == original[original.length - 1];` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
