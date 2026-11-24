# c-012: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-012_solution.c`, implements all six cases, from the "read through a const view" case to the "transfer snapshot independence" case, in one `main.c`.

## Mechanism and assumptions

const describes permitted access through a type-qualified expression. A pointer to const int prevents modifying the target through that pointer, while a const pointer prevents changing which target the pointer designates. These are different guarantees. A mutable object can be observed through a const view and changed through another valid mutable path. An object originally defined const must not be modified by casting away qualification. Const-correct APIs communicate read-only intent and let callers pass immutable data safely, but they do not automatically provide deep immutability, ownership or synchronization.

const int *p reads as a pointer to a const-qualified int. int *const p is a const pointer to a mutable int. const int *const p combines both restrictions. Function parameters can use const for borrowed read-only arrays. A struct containing a pointer can still reference mutable storage even if the outer struct is accessed through a const pointer; deep ownership requires a broader design.

## Exercise 1: Read through a const view: change one input

Copy worked example 1, the "read through a const view" case, into a scratch pad and change `int value = 4;` to `int value = 5;`. Before running, predict which CHECK fails and which value it sees in place of the worked result (the read yields 4); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int value = 4;
const int *view = &value;
CHECK(*view == 4);
```

**Expected:** With `int value = 5;` the run stops with `Check failed` at the CHECK on `*view == 4`, because the "read through a const view" case no longer shows that the read yields 4. Restoring `int value = 4;` brings that observation back.

The view is read-only, but the underlying object was not defined const.

**Approach.** Follow the pointer to its target: `view` holds the address of `value`, so `*view` reads whatever `value` holds, now 5.

**Why it holds here.** `const int *` limits writes through `view`; it does not copy the integer. Changing the initializer to 5 therefore changes the read, and `*view == 4` fails.

**A plausible wrong approach.** Predicting the CHECK passes because a const view somehow pins the value it first saw. `view` is only an address with a read-only access path, so it observes the new initializer.

**Verify.** Print `*view` and see 5 with the edit and 4 after restoring the line.

## Exercise 2: Observe another valid mutation: debug a regression

A regression changed one token in worked example 2, the "observe another valid mutation" case, so one line now reads `value = 8;`. Run the example with that line, use the failing CHECK to find why the const view now reads 7 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int value = 4;
const int *view = &value;
value = 7;
CHECK(*view == 7);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `*view == 7`. Once the line reads `value = 7;` again, the "observe another valid mutation" case again shows that the const view now reads 7.

Const access does not freeze a shared mutable object or create a snapshot.

**Approach.** Locate the write that feeds the failing read: `value = 8;` replaced the expected `value = 7;`, and the view reads 8.

**Why it holds here.** `value` itself is not const, so the direct assignment is legal and the view sees it immediately; restoring 7 makes `*view == 7` true without touching the CHECK.

**A plausible wrong approach.** Repairing through the view, for example `*(int *)view = 7;` after the bad write. That cast hides a design error and does not remove the regression; the correct edit is the one assignment that changed.

**Verify.** Print `value` and `*view` in separate statements and see 8 and 8 before the repair, 7 and 7 after it.

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

**Approach.** Put `const` after the `*`: `int *const fixed` makes the pointer object read-only while `*fixed` stays a writable `int`.

**Why it holds here.** The assignment `*fixed = 8` writes the target, which is allowed, so `value` becomes 8.

**A plausible wrong approach.** Swapping the qualifier position to `const int *fixed`. Then `*fixed = 8` is the forbidden operation and Clang rejects it with `read-only variable is not assignable`; with the correct declaration, it is `fixed = &other;` that is rejected.

**Verify.** Compile both mistakes to read the two diagnostics, then run the original and print `value` to see 8.

## Exercise 4: Read an immutable object

Declare a const integer and access it through a const pointer.

```c
const int value = 9;
const int *p = &value;
CHECK(*p == 9);
```

**Expected:** The value is 9.

No cast is used to bypass the qualification. Modifying an object originally defined const would be undefined behavior.

**Approach.** Read the const object through a `const int *`, which matches its qualification exactly.

**Why it holds here.** Nothing writes `value`, so `*p` is 9; the compiler may even keep 9 in a register or fold it into code, because it may assume a const object never changes.

**A plausible wrong approach.** Casting the qualifier away to change it, `*(int *)p = 10;`. The object was defined const, so the write is undefined behavior, and Clang accepts it silently under `-Wall -Wextra -Wpedantic`; only `-Wcast-qual` reports `cast ... drops const qualifier`. Describe it rather than run it.

**Verify.** Add `-Wcast-qual` to a compile-only build of the bad line to see the warning; run the original and see 9.

## Exercise 5: Pass a read-only array contract

Sum a const array using a const pointer parameter.

```c
const int values[] = {1, 2, 3};
CHECK(read_sum(values, 3) == 6);
```

**Expected:** The sum is 6.

A read-only parameter accepts both const and mutable inputs while promising not to change elements through that path.

**Approach.** Declare the parameter as `const int *values`, so `read_sum` promises to read elements only.

**Why it holds here.** Both `const int[3]` and plain `int[3]` arrays convert to `const int *` without a cast, and the loop adds 1, 2 and 3 to get 6.

**A plausible wrong approach.** Declaring the parameter as `int *values`. Passing this const array then draws `passing 'const int[3]' to parameter of type 'int *' discards qualifiers`, and any write inside the function would modify a const object.

**Verify.** Compile a variant with `int *values` to see the warning, then print `read_sum(values, 3)` and see 6.

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

**Approach.** Copy the integer: `int snapshot = *view;` stores 2 in a separate object before `value` changes.

**Why it holds here.** Later assignments to `value` cannot reach `snapshot`, while `view` still points at `value`, so the two reads are 2 and 5.

**A plausible wrong approach.** Keeping the snapshot as a pointer, `const int *snapshot = view;`. That copies the address, not the integer, so after `value = 5` both reads return 5 and the CHECK on 2 fails.

**Verify.** Print `snapshot` and `*view` in separate statements and see 2 and 5; the pointer variant prints 5 and 5.

## After comparison

Write `void scale_into(const int *in, int *out, size_t n, int factor)` that writes `in[i] * factor` to `out[i]`. Check that a const input `{1, 2, 3}` scaled by 2 gives `{2, 4, 6}`, that `in` is unchanged, and that `n` 0 writes nothing. Then explain what happens when a caller passes the same array as both `in` and `out`, and why the `const` on `in` does not forbid that aliasing.
