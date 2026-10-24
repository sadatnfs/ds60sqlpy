# c-001: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

C source is text describing declarations and operations. The preprocessor handles directives, the compiler translates a translation unit, and the linker combines machine-code objects with required libraries. The executable is a separate artifact from main.c. A syntax error prevents compilation; an unresolved symbol prevents linking; an assertion can fail only after execution begins. These stages require different diagnoses. C does not automatically validate every runtime memory operation, so successful compilation is a starting point rather than a safety proof. Begin with independently checked scalar results before learning pointers and resource ownership.

#include makes header declarations available. int main(void) is an entrypoint with no parameters; returning zero signals successful termination. Braces form a block and semicolons finish most statements. printf formats values, while puts writes a string plus a newline. assert from assert.h checks a condition when NDEBUG is not defined. %d expects an int, and a mismatched format argument can be undefined behavior.

## Exercise 1: Check a first value

Store 2 plus 3 in an int.

```c
int total = 2 + 3;
CHECK(total == 5);
```

**Expected:** The stored value is 5.

The expectation is known independently of the program. A print statement alone would not reject a wrong calculation.

## Exercise 2: Format a checked result

Format total=5 into a bounded character buffer.

```c
char out[16];
int n = snprintf(out, sizeof out, "total=%d", 5);
CHECK(n == 7);
CHECK(strcmp(out, "total=5") == 0);
```

**Expected:** The result length is 7 and text is total=5.

snprintf returns the length that would be required, excluding the terminating null byte. A caller must compare it with capacity before treating output as complete.

## Exercise 3: Trace statement order

Start at 1, increment, then multiply by 3.

```c
int count = 1;
count += 1;
count *= 3;
CHECK(count == 6);
```

**Expected:** The result is 6.

Changing operation order changes the state trajectory. Separate statements make sequencing explicit.

## Exercise 4: Inspect a boolean condition

Compare 4 with 4 and 4 with 5.

```c
bool same = (4 == 4);
bool different = (4 != 5);
CHECK(same &&different);
```

**Expected:** Equality is true and inequality is true.

An equality expression compares values. Assignment uses a different operator and changes state.

## Exercise 5: Use an explicit return contract

Call a helper returning the value 7.

```c
CHECK(seven() == 7);
```

**Expected:** The caller receives 7.

The declaration gives the compiler a return-type contract. A missing or incompatible declaration should be repaired before execution.

## Exercise 6: Transfer a receipt calculation

Multiply 4 items by a unit amount of 6.

```c
int items = 4;
int unit = 6;
int amount = items * unit;
CHECK(amount == 24);
```

**Expected:** The checked amount is 24.

These small values fit int. A reusable arithmetic API later needs a range and overflow policy rather than relying on one benign fixture.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
