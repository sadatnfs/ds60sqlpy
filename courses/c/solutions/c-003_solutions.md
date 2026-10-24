# c-003: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

An expression can compute a value and sometimes change state. C does not guarantee one universal evaluation order for every operator or function argument. Modifying one scalar more than once without the required sequencing can be undefined behavior. Keep complex updates in separate statements until the ordering is clear. The usual arithmetic conversions also affect comparisons: mixing a negative signed integer with an unsigned value can convert the negative operand into a large unsigned value. Parentheses clarify grouping but do not create sequencing where the language supplies none. Distinguish precedence, associativity and evaluation order.

&& and || short-circuit and sequence their left operand before a needed right operand. The conditional operator evaluates only its selected second or third operand. Assignment returns the assigned value, so accidental assignment inside a condition can be legal but wrong. ++ changes a value; using it in a larger expression requires careful reasoning. Prefer explicit temporary variables for updates with several observable effects.

## Exercise 1: Group before calculating

Compare 2+3*4 with (2+3)*4.

```c
CHECK(2 + 3 * 4 == 14);
CHECK((2 + 3) * 4 == 20);
```

**Expected:** The values are 14 and 20.

Parentheses alter grouping. This example has no side effects, so it does not depend on evaluation order.

## Exercise 2: Use a short-circuit guard

Guard an array access with a false length test.

```c
int values[1] = {7};
size_t length = 0;
bool found = length > 0 && values[0] == 7;
CHECK(!found);
```

**Expected:** The access is skipped and the condition is false.

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

## Exercise 6: Transfer assignment diagnosis

Assign 3 to a variable, then separately compare it with 3.

```c
int x = 0;
x = 3;
bool same = (x == 3);
CHECK(same &&x == 3);
```

**Expected:** The assignment changes the variable and equality tests it.

Using = where == was intended may compile because assignment is an expression. Warnings and clear statement boundaries help expose that defect.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
