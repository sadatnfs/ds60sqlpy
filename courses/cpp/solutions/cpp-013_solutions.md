# cpp-013: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A warning is compiler feedback about suspicious code even when compilation succeeds. A test is an executable check against a contract. CTest runs registered processes and reports their statuses. The NDEBUG macro disables standard assert expressions, so a Release test that only uses assert can accidentally check nothing.

## Worked example 1

```cpp
if (twice(3)!=6) return 1;
```

Expected: The process returns nonzero if the result is wrong, including Release builds.

## Worked example 2

```cpp
#ifdef NDEBUG
// assert expressions can be removed here.
#endif
```

Expected: NDEBUG changes assertions, not ordinary if-based contract checks.

## Exercise 1: Read flags

Explain -std=c++20, -Wall, -Wextra and -Wpedantic.

**Expected:** Language selection and three diagnostic groups distinguished.

**Reasoning:** Warnings are feedback rather than successful tests.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Run named tests

Use the supplied CMake project and ctest --output-on-failure.

**Expected:** One or more registered tests actually execute; record count and status.

**Reasoning:** Configure/build/test are three phases.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Create a failing check

Change the expected twice(3) result to 7 in a scratch copy.

**Expected:** Executable exit 1 and failing test.

**Reasoning:** A failed assertion needs to be observable outside the process.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair a disabled test

Build a scratch assert-only test with -DNDEBUG.

**Expected:** The wrong assert disappears; an if-based test still fails.

**Reasoning:** Do not use disabled assertions as the only release oracle.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test zero

Keep the always-active twice(0)==0 check.

**Expected:** Exit 0 for the correct function.

**Reasoning:** Boundary behavior is a separate test input.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer a regression

Break twice to x+x+1, run both tests, then restore.

**Expected:** Both normal and zero contracts reject the broken function.

**Reasoning:** A test suite earns confidence by detecting a plausible defect.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
