# c-013: explained solutions

`c-013_solution.c` assembles the "use a parenthesized macro safely" case through the "transfer an inline-style function contract" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

The preprocessor transforms tokens before the compiler performs ordinary type checking. Header inclusion, conditional compilation and macros can be useful, but a macro is not a normal function. Its arguments may be substituted more than once, and missing parentheses can change expression grouping. Side-effecting arguments such as increments are therefore hazardous in many function-like macros. Prefer typed functions or static inline functions for behavior when possible. Use macros for configuration and declarations that need preprocessing, and keep conditional platform code small and documented. The same source should not silently change semantic contracts because a build flag was forgotten.

#define creates a macro replacement. Parenthesize each expression argument and the full result, but understand that this does not prevent repeated evaluation. #if and #ifdef select tokens before compilation. Include guards prevent repeated header definitions. _Static_assert checks a constant expression during compilation. _Generic can select an expression by type in C11 and later without becoming a runtime type system.

## Exercise 1: Use a parenthesized macro safely: predict an edited check

In worked example 1, change `CHECK(SQUARE(2 + 3) == 25);` to `CHECK(SQUARE(3 + 3) == 25);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
CHECK(SQUARE(2 + 3) == 25);
```

**Expected:** `Check failed`: `CHECK(SQUARE(3 + 3) == 25);` is false, although the result is 25.

Parentheses preserve grouping. This macro still evaluates its argument twice, so side effects remain inappropriate.

**Approach.** Expand the macro by hand: `SQUARE(3 + 3)` becomes `((3 + 3)*(3 + 3))`, which is 36.

**Why it holds here.** The parentheses around each `x` and the whole body keep the argument grouped, so the edit gives a true square, and 36 is not 25.

**A plausible wrong approach.** Expanding without the parentheses, `3 + 3*3 + 3`, and predicting 15. That is what an unparenthesized `#define SQUARE(x) x*x` would produce, and it still fails, for the wrong reason.

**Verify.** Run `cc -E` on the file and read the expanded line, then print `SQUARE(3 + 3)` and see 36.

## Exercise 2: Prefer a typed helper for mutation: debug a regression

Worked example 2 now has a line reading `int value = 4;`. Repair it so that the result is 9 and value increments once to 4 again.

The unchanged code is worked example 2:

```c
int value = 3;
int result = square_int(value++);
CHECK(result == 9 && value == 4);
```

**Expected:** `Check failed` at `result == 9 && value == 4` until the line reads `int value = 3;` again.

A function argument expression is evaluated once for this call. SQUARE(value++) would create an unsequenced modification hazard.

**Approach.** Find the changed initializer: with `int value = 4;` the call passes 4, the helper returns 16, and `value` ends at 5.

**Why it holds here.** `&&` evaluates the left side first and `result == 9` is already false, so the CHECK fails without ever comparing 5 to 4; restoring 3 makes both sides true.

**A plausible wrong approach.** Repairing by switching the call to `SQUARE(value++)`. The macro expands the argument twice, so `value` is modified twice without sequencing, which is undefined behavior; Clang warns `multiple unsequenced modifications to 'value'`. Describe it rather than run it.

**Verify.** Print `result` and `value` in separate statements and see 16 and 5 before the repair, 9 and 4 after it.

## Exercise 3: Require a representation fact

Check the language-required char size at translation time.

```c
_Static_assert(sizeof(char) == 1, "char unit must be one");
CHECK(sizeof(char) == 1);
```

**Expected:** Compilation accepts the true static assertion.

A compile-time invariant fails before execution. It is different from a runtime assertion about input data.

**Approach.** Assert a fact the compiler can evaluate: `sizeof(char) == 1` is an integer constant expression the standard guarantees.

**Why it holds here.** `_Static_assert` evaluates the expression during translation, so a true fact produces no code and no runtime cost, and the runtime CHECK repeats the same truth.

**A plausible wrong approach.** Using it for a runtime value, `int n = 2; _Static_assert(n > 0, "positive");`. Clang rejects it with `static assertion expression is not an integral constant expression`; data that arrives at run time needs an ordinary check.

**Verify.** Compile `_Static_assert(sizeof(int) == 2, ...)` and read `expression evaluates to '4 == 2'`, which proves a false assertion stops the build before the program exists.

## Exercise 4: Read a configuration constant

Use a fixed capacity macro of 8.

```c
int values[LESSON_CAPACITY] = {0};
CHECK(sizeof values / sizeof values[0] == 8);
```

**Expected:** The declared buffer has eight elements.

Configuration macros can express shared compile-time sizes. Runtime input still needs checking against that fixed capacity.

**Approach.** Size the array with `LESSON_CAPACITY` and compute the element count with `sizeof values / sizeof values[0]` in the same scope.

**Why it holds here.** `values` is still an array object here, so `sizeof values` is 32 bytes and each `int` is 4, giving 8.

**A plausible wrong approach.** Moving the count into a helper, `size_t count_of(int values[LESSON_CAPACITY])`. The parameter is really an `int *`, so the division gives 8 / 4 = 2 on the worker, and Clang warns `sizeof on array function parameter will return size of 'int *'`.

**Verify.** Print the count in `main` and from the helper and see 8 and 2; pass the capacity explicitly instead.

## Exercise 5: Select by a simple type

Use a generic selection for int and double expressions.

```c
CHECK(strcmp(TYPE_LABEL(3), "integer") == 0);
CHECK(strcmp(TYPE_LABEL(3.0), "floating") == 0);
```

**Expected:** The selected labels are integer and floating.

_Generic chooses from declared compatible types at translation time. It does not inspect arbitrary serialized data at runtime.

**Approach.** Let `_Generic` select a string literal from the controlling expression's type: `3` is `int` and `3.0` is `double`.

**Why it holds here.** Selection happens at compile time from the type alone, and both types have an association, so `strcmp` returns 0 for both labels.

**A plausible wrong approach.** Expecting `TYPE_LABEL('a')` to be `other` or `TYPE_LABEL(3.0f)` to be `floating`. In C a character constant has type `int`, so it selects `integer`, and `float` has no association here, so it falls to `default` and prints `other`.

**Verify.** Print the labels for `'a'`, `3.0f` and `3L` and see `integer other other`.

## Exercise 6: Transfer an inline-style function contract

Square zero and negative three through the typed helper.

```c
CHECK(square_int(0) == 0 && square_int(-3) == 9);
```

**Expected:** The results are 0 and 9.

The helper has ordinary type checking and one evaluation per argument. Large magnitudes still need an overflow policy.

**Approach.** Call the typed helper with 0 and -3; each argument is evaluated once and converted to `int` at the call.

**Why it holds here.** Zero times zero is 0 and -3 times -3 is 9, both well inside `int`, so the conjunction holds.

**A plausible wrong approach.** Assuming every `int` input is safe. `square_int(46341)` would need 2147488281, which exceeds `INT_MAX` 2147483647, so signed overflow is undefined; 46340 gives 2147395600 and is the largest safe magnitude.

**Verify.** Print `square_int(46340)` and see 2147395600, and compute `46341LL * 46341LL` in `long long` to see the overflow without triggering it.

## After comparison

Write `bool checked_square(int value, int *out)` that returns false when `value` is outside -46340..46340 and otherwise stores the square. Check 0, -3, 46340 and 46341, and confirm that `*out` is unchanged on rejection. Then add `#define MAX_ITEMS 4` with `_Static_assert(MAX_ITEMS <= LESSON_CAPACITY, ...)`, and explain why raising `MAX_ITEMS` to 9 fails the build, not the run.
