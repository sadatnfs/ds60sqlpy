# c-003: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

An expression can compute a value and sometimes change state. C does not guarantee one universal evaluation order for every operator or function argument. Modifying one scalar more than once without the required sequencing can be undefined behavior. Keep complex updates in separate statements until the ordering is clear. Before any arithmetic, operands narrower than int, such as char, unsigned char and short, are converted to int when int can represent all their values (the integer promotions); the usual arithmetic conversions then bring both operands to a common type. Those conversions also affect comparisons: mixing a negative signed integer with an unsigned value can convert the negative operand into a large unsigned value. Parentheses clarify grouping but do not create sequencing where the language supplies none. Distinguish precedence, associativity and evaluation order.

&& and || short-circuit and sequence their left operand before a needed right operand. The conditional operator evaluates only its selected second or third operand. Assignment returns the assigned value, so accidental assignment inside a condition can be legal but wrong. ++ changes a value; using it in a larger expression requires careful reasoning. Prefer explicit temporary variables for updates with several observable effects.

## Exercise 1: Group before calculating: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK((2 + 3) * 4 == 20);` to `CHECK((3 + 3) * 4 == 20);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
CHECK(2 + 3 * 4 == 14);
CHECK((2 + 3) * 4 == 20);
```

**Expected:** The changed run stops with `Check failed` at the CHECK on `(2 + 3) * 4 == 20`. Restoring the original line brings back the worked observation: the values are 14 and 20.

Parentheses alter grouping. This example has no side effects, so it does not depend on evaluation order.

## Exercise 2: Use a short-circuit guard: debug a regression

A regression changed one token in worked example 2, so one line now reads `bool found = length >= 0 && values[0] == 7;`. Run worked example 2 with that line, use the failing CHECK to locate the defect and repair it without changing the CHECK.

The unchanged code is worked example 2:

```c
int values[1] = {7};
size_t length = 0;
bool found = length > 0 && values[0] == 7;
CHECK(!found);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `!found`; after it the line reads `bool found = length > 0 && values[0] == 7;` again and the access is skipped and the condition is false.

The right operand is evaluated only when the left is true. A guard must precede the operation it protects.

## Exercise 3: Sequence updates explicitly

Increment x and then calculate twice its updated value.

```c
int x = 1;
x += 1;
int result = x * 2;
CHECK(x == 2 && result == 4);
```

**Expected:** x is 2 and the result is 4.

Separate statements avoid unsequenced read/write hazards and make the intended state transition visible.

## Exercise 4: Expose signed-unsigned conversion

Compare -1 with 1U under the usual conversion rules.

```c
int negative = -1;
unsigned int positive = 1U;
CHECK(!((unsigned int)negative < positive));
```

**Expected:** The comparison -1 < 1U is false on this int/unsigned-int pair.

The explicit cast displays the same unsigned conversion that the mixed comparison would perform implicitly. The negative value becomes large rather than remaining mathematically negative; the cast also keeps this reference warning-clean.

## Exercise 5: Choose one conditional branch

Select a valid value while the other branch would divide by zero.

```c
int zero = 0;
int value = true ? 7 : 10 / zero;
CHECK(value == 7);
```

**Expected:** Only the chosen branch is evaluated and result is 7.

The unchosen operand of ?: is not evaluated. This safe fixture demonstrates the rule without executing the invalid division.

## Exercise 6: Transfer integer promotion

Add two unsigned char values 200 and 100, then store the sum back into an unsigned char.

```c
unsigned char a = 200, b = 100;
int sum = a + b;
unsigned char stored = (unsigned char)(a + b);
CHECK(sum == 300 && stored == 44);
```

**Expected:** The promoted int sum is 300; the stored unsigned char is 44.

Operands narrower than int, such as unsigned char, are promoted to int before arithmetic, so a + b is the int 300 rather than a value that wraps at 256. Converting the result back to unsigned char reduces it modulo 256, giving 44. The same rule turns a uint16_t product such as 65535 * 65535 into a signed int multiplication that overflows on common 32-bit int targets; widen first with (uint32_t)x * x.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
