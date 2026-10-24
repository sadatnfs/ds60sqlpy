# c-013: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

The preprocessor transforms tokens before the compiler performs ordinary type checking. Header inclusion, conditional compilation and macros can be useful, but a macro is not a normal function. Its arguments may be substituted more than once, and missing parentheses can change expression grouping. Side-effecting arguments such as increments are therefore hazardous in many function-like macros. Prefer typed functions or static inline functions for behavior when possible. Use macros for configuration and declarations that need preprocessing, and keep conditional platform code small and documented. The same source should not silently change semantic contracts because a build flag was forgotten.

#define creates a macro replacement. Parenthesize each expression argument and the full result, but understand that this does not prevent repeated evaluation. #if and #ifdef select tokens before compilation. Include guards prevent repeated header definitions. _Static_assert checks a constant expression during compilation. _Generic can select an expression by type in C11 and later without becoming a runtime type system.

## Exercise 1: Use a parenthesized macro safely

Square the side-effect-free expression 2+3.

```c
CHECK(SQUARE(2 + 3) == 25);
```

**Expected:** The result is 25.

Parentheses preserve grouping. This macro still evaluates its argument twice, so side effects remain inappropriate.

## Exercise 2: Prefer a typed helper for mutation

Pass value++ to a normal square function.

```c
int value = 3;
int result = square_int(value++);
CHECK(result == 9 && value == 4);
```

**Expected:** The result is 9 and value increments once to 4.

A function argument expression is evaluated once for this call. SQUARE(value++) would create an unsequenced modification hazard.

## Exercise 3: Require a representation fact

Check the language-required char size at translation time.

```c
_Static_assert(sizeof(char) == 1, "char unit must be one");
CHECK(sizeof(char) == 1);
```

**Expected:** Compilation accepts the true static assertion.

A compile-time invariant fails before execution. It is different from a runtime assertion about input data.

## Exercise 4: Read a configuration constant

Use a fixed capacity macro of 8.

```c
int values[LESSON_CAPACITY] = {0};
CHECK(sizeof values / sizeof values[0] == 8);
```

**Expected:** The declared buffer has eight elements.

Configuration macros can express shared compile-time sizes. Runtime input still needs checking against that fixed capacity.

## Exercise 5: Select by a simple type

Use a generic selection for int and double expressions.

```c
CHECK(strcmp(TYPE_LABEL(3), "integer") == 0);
CHECK(strcmp(TYPE_LABEL(3.0), "floating") == 0);
```

**Expected:** The selected labels are integer and floating.

_Generic chooses from declared compatible types at translation time. It does not inspect arbitrary serialized data at runtime.

## Exercise 6: Transfer an inline-style function contract

Square zero and negative three through the typed helper.

```c
CHECK(square_int(0) == 0 && square_int(-3) == 9);
```

**Expected:** The results are 0 and 9.

The helper has ordinary type checking and one evaluation per argument. Large magnitudes still need an overflow policy.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
