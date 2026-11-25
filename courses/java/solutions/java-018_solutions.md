# java-018: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A useful test distinguishes correct behavior from a plausible mistake. Repeating the implementation formula in the expected value can reproduce the same bug on both sides. Use independent examples, boundary cases and properties that follow from the contract. A mutation test deliberately changes one behavior and checks that the tests detect it. Assertions are convenient in this course because the launcher enables-ea, but production test suites often use a dedicated framework so checks cannot be disabled accidentally. Tests should expose failures rather than catch every exception and print success.

**Test oracle:** An independent basis for deciding the expected result.

**Property:** A relation that should hold across a family of inputs.

**Mutation test:** A check that an intentionally broken variant is detected.

## Reading the reference

A table-driven test stores inputs and expected outputs together, then runs the same checker over all cases. A property test checks a relation over several inputs, such as reversing twice restoring an array. An exception helper should verify the expected type and fail when no exception occurs. Keep test fixtures deterministic and avoid timing assumptions for concurrency. A test passing on one input says nothing about untested boundaries unless a valid general argument supports the claim.

## Exercise 1: Use independent table cases: change one input

Task: Change `int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };` to `int[][] cases = { { -2, 1 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };` in Example A and predict which assertion fails and why.

The expected outputs are literal contract examples. They do not call clamp or duplicate its full branching logic to generate answers.

The unchanged code is the part that Example A adds:

```java
int[][] cases = { { -2, 0 }, { 0, 0 }, { 3, 3 }, { 9, 5 } };
for (int[] row : cases) assert clamp(row[0], 0, 5) == row[1];
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `clamp(row[0], 0, 5) == row[1]`.

**Verify:** Name the value that makes `clamp(row[0], 0, 5) == row[1]` false, then restore the line.

## Exercise 2: Check a boundary failure: debug a regression

Task: Add one defect to Example B's new code that changes its observation, then repair it.

An invalid interval is different from a value outside a valid interval. The test ensures the implementation rejects the contract violation.

The unchanged code is the part that Example B adds:

```java
expect(IllegalArgumentException.class, () -> clamp(3, 5, 2));
```

**Expected:** The defective copy fails its assertion and the repaired copy passes.

**Verify:** Name the first statement whose value differs between the failing and repaired runs.

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

**Verify:** Control: changing `int once = clamp(value, 0, 5);` to `int once = clamp(value, 0, 6);` must fail the assertion on `clamp(once, 0, 5) == once`.

## Exercise 4: Detect a broken implementation

Task: Use a mutant that returns upper for values below lower and show the table rejects it.

A test suite should fail on a meaningful defect. This control demonstrates that the lower-bound example is not merely decorative.

```java
boolean caught = false;
for (int[] row : cases) if (brokenClamp(row[0], 0, 5) != row[1]) caught = true;
assert caught;
```

**Expected:** at least one mismatch.

**Verify:** Control: changing `for (int[] row : cases) if (brokenClamp(row[0], 0, 5) != row[1]) caught = true;` to `for (int[] row : cases) if (brokenClamp(row[1], 0, 5) != row[1]) caught = true;` must fail the assertion on `caught`.

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

**Verify:** Control: changing `checkerFailed = true;` to `checkerFailed = false;` must fail the assertion on `checkerFailed`.

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

**Verify:** Control: changing `if (original.length > 1) assert first[0] == original[original.length - 1];` to `if (original.length > 1) assert first[1] == original[original.length - 1];` inside the assertion must make it fail.

## After comparing the answer

Write one more mutant in your copy, for example a clamp that ignores the upper bound, and confirm that at least one row of the case table fails for it.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
