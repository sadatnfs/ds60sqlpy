# c-004: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Control flow chooses which operations execute. A loop invariant describes what remains true before and after each iteration, connecting repeated steps to the intended result. For summation, the accumulator equals the sum of elements already visited. Empty input is then handled by the initial state rather than a special fabricated element. Index-based loops should use a half-open range from zero to length. An off-by-one error in C can access memory outside the array without a guaranteed runtime exception. Prove the bound before access rather than relying on a crash to identify mistakes.

if treats zero as false and nonzero as true. for combines initialization, condition and update. while checks before the body; do-while checks afterward. break exits the nearest loop or switch, while continue skips to the next iteration. switch cases fall through unless control exits explicitly. Use size_t for lengths and indices, and avoid decrement loops that accidentally wrap an unsigned counter below zero.

## Exercise 1: Trace a prefix sum

Sum 2, 4 and 6 with a length-bounded loop.

```c
int values[] = {2, 4, 6};
int sum = 0;
for (size_t i = 0; i < 3; i++) {
  sum += values[i];
}
CHECK(sum == 12);
```

**Expected:** The result is 12.

Each iteration adds exactly one valid element. The index is proven less than the declared length before access.

## Exercise 2: Handle zero iterations

Sum zero elements from a valid storage object.

```c
int values[1] = {9};
size_t length = 0;
int sum = 0;
for (size_t i = 0; i < length; i++) {
  sum += values[i];
}
CHECK(sum == 0);
```

**Expected:** The accumulator remains zero.

The example uses a real array because zero-length arrays are not standard C17. The logical length may still be zero.

## Exercise 3: Find the first match

Search 3, 8, 8 and stop on the first 8.

```c
int values[] = {3, 8, 8};
size_t found = 3;
for (size_t i = 0; i < 3; i++) {
  if (values[i] == 8) {
    found = i;
    break;
  }
}
CHECK(found == 1);
```

**Expected:** The index is 1.

The sentinel equals length and is never dereferenced. break preserves the first-match contract.

## Exercise 4: Include an exact threshold

Classify score 60 with passing threshold 60.

```c
int score = 60;
bool passed = score >= 60;
CHECK(passed);
```

**Expected:** The boundary passes.

This distinguishes an inclusive threshold from a strict comparison. The policy should be stated before choosing the operator.

## Exercise 5: Terminate a switch case

Map code 2 to value 20 with explicit breaks.

```c
int code = 2, result = 0;
switch (code) {
case 1:
  result = 10;
  break;
case 2:
  result = 20;
  break;
default:
  result = -1;
  break;
}
CHECK(result == 20);
```

**Expected:** The result is 20.

An omitted break can execute later case statements. Deliberate fallthrough needs a clear explanation and compiler-supported annotation policy.

## Exercise 6: Transfer reverse traversal safely

Visit indices 2, 1 and 0 using a positive-count loop.

```c
int values[] = {1, 2, 3};
int out = 0;
for (size_t remaining = 3; remaining > 0; remaining--) {
  size_t i = remaining - 1;
  out = out * 10 + values[i];
}
CHECK(out == 321);
```

**Expected:** The reversed number is 321.

The subtraction occurs only while remaining is positive. A condition i>=0 on size_t would never become false after wraparound.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
