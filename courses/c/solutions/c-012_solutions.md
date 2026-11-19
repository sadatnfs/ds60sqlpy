# c-012: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

const describes permitted access through a type-qualified expression. A pointer to const int prevents modifying the target through that pointer, while a const pointer prevents changing which target the pointer designates. These are different guarantees. A mutable object can be observed through a const view and changed through another valid mutable path. An object originally defined const must not be modified by casting away qualification. Const-correct APIs communicate read-only intent and let callers pass immutable data safely, but they do not automatically provide deep immutability, ownership or synchronization.

const int *p reads as a pointer to a const-qualified int. int *const p is a const pointer to a mutable int. const int *const p combines both restrictions. Function parameters can use const for borrowed read-only arrays. A struct containing a pointer can still reference mutable storage even if the outer struct is accessed through a const pointer; deep ownership requires a broader design.

## Exercise 1: Read through a const view: change one input

Copy worked example 1 into a scratch pad and change `int value = 4;` to `int value = 5;`. Before running, predict which CHECK fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```c
int value = 4;
const int *view = &value;
CHECK(*view == 4);
```

**Expected:** The changed run stops with `Check failed` at the CHECK on `*view == 4`. Restoring the original line brings back the worked observation: the read yields 4.

The view is read-only, but the underlying object was not defined const.

## Exercise 2: Observe another valid mutation: debug a regression

A regression changed one token in worked example 2, so one line now reads `value = 8;`. Run worked example 2 with that line, use the failing CHECK to locate the defect and repair it without changing the CHECK.

The unchanged code is worked example 2:

```c
int value = 4;
const int *view = &value;
value = 7;
CHECK(*view == 7);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `*view == 7`; after it the line reads `value = 7;` again and the const view now reads 7.

Const access does not freeze a shared mutable object or create a snapshot.

## Exercise 3: Use a fixed pointer target

Create an int pointer that cannot be reassigned, then update its target.

```c
int value = 1;
int *const fixed = &value;
*fixed = 8;
CHECK(value == 8);
```

**Expected:** The target becomes 8.

The pointer object is fixed while the designated int remains writable.

## Exercise 4: Read an immutable object

Declare a const integer and access it through a const pointer.

```c
const int value = 9;
const int *p = &value;
CHECK(*p == 9);
```

**Expected:** The value is 9.

No cast is used to bypass the qualification. Modifying an object originally defined const would be undefined behavior.

## Exercise 5: Pass a read-only array contract

Sum a const array using a const pointer parameter.

```c
const int values[] = {1, 2, 3};
CHECK(read_sum(values, 3) == 6);
```

**Expected:** The sum is 6.

A read-only parameter accepts both const and mutable inputs while promising not to change elements through that path.

## Exercise 6: Transfer snapshot independence

Copy the scalar observed through a const view and then mutate the original.

```c
int value = 2;
const int *view = &value;
int snapshot = *view;
value = 5;
CHECK(snapshot == 2 && *view == 5);
```

**Expected:** The snapshot remains 2 while the view reads 5.

A value copy establishes an independent snapshot; qualification alone does not.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
