# cpp-013: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A warning is compiler feedback about suspicious code even when compilation succeeds. A test is an executable check against a contract. CTest runs registered processes and reports their statuses. The NDEBUG macro disables standard assert expressions, so a Release test that only uses assert can accidentally check nothing.

## Detailed reasoning

A test has two jobs: perform a check and make failure observable. With NDEBUG, assert(expression) can remove expression entirely, including side effects accidentally placed inside it. An ordinary if condition and nonzero return stay active in Release. CTest adds process orchestration but cannot invent checks inside a program. Inspect the executed test count as well as the pass label, because a project with zero registered tests has not validated the intended behavior.

<!-- depth:start -->
## Build configuration and always-active checks

A build configuration selects compiler options and dependency relationships. CMake describes targets and their requirements; it does not replace the compiler or infer a correct source contract. A clean configure/build sequence should identify the source directory, build directory, selected generator, compiler and target. Keeping generated build files outside the source tree makes it easier to distinguish authored inputs from tool output.

Debug and Release commonly differ in optimization and assertion configuration, but those names alone are not a universal specification. Inspect the actual flags. The standard assert macro can be removed when NDEBUG is defined. Any expression inside assert can then disappear, including side effects. A validation step that must happen in every build should use an ordinary condition and explicit failure result rather than relying on assert.

The first complete example uses if to return failure when twice(3) is wrong. It remains active under NDEBUG. The second deliberately increments a counter inside assert to expose the macro behavior: without NDEBUG the counter reaches1; with NDEBUG it stays0. This is a teaching negative pattern, not a recommendation. It explains why tests should not initialize data or perform required work solely inside assert.

CMake target properties express requirements for one executable or library. A language standard requirement belongs to the target, and include/link dependencies should be scoped according to whether consumers need them. Global flags copied into every directory can accidentally couple unrelated targets and hide missing public dependencies. The real multifile fixture is the appropriate place to inspect this behavior.

A successful configuration only generates a build system. A successful build produces an artifact. Running the artifact and checking its output is another step. If the generator supports multiple configurations, the build/run path must select the intended configuration explicitly. The course host instructions distinguish those operations; the browser profile invokes its own fixed compiler pipeline and does not run arbitrary CMake projects.

## Debugging the contract

If Release passes instantly while Debug catches a failure, inspect NDEBUG and any side effects inside assert. If CMake configures but linking fails, read the target's actual source/link inputs rather than assuming configuration validated them. If the wrong executable runs, inspect the selected build directory and configuration path. Record an always-active checksum before interpreting an optimized timing result, because a faster program that skipped required work is not an improvement.
<!-- depth:end -->

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
