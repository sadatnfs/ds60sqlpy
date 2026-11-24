# c-017: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-017_solution.c`, implements all six cases, from the "create an owned string" case to the "transfer a deliberate move" case, in one `main.c`.

## Mechanism and assumptions

A reusable C component needs an ownership vocabulary. A borrowed pointer grants temporary access without transferring release responsibility. An owned result makes the caller responsible for destruction. A clone creates independent owned storage; a shallow struct copy usually does not. Document whether a function consumes its input on success, on failure, both or neither. Ambiguity produces leaks, double-free and use-after-free defects that can be difficult to diagnose after components are combined. The small text owner here has one destructor and an explicit clone operation. It never represents a shallow copy as a second independent owner.

The owner struct contains a char pointer and length. create allocates length plus one, copies bytes and writes a terminator. clone calls the same creation policy on a borrowed source. destroy releases and resets the owner. Use a const pointer for borrowed read access. Returning a struct by value can transfer ownership, but subsequent copies must obey the documented move-or-clone policy because C does not enforce it automatically.

## Exercise 1: Create an owned string: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(text_create(&t, "alpha"));` to `CHECK(text_create(&t, "alpha!"));` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
struct Text t = {0};
CHECK(text_create(&t, "alpha"));
CHECK(t.len == 5 && strcmp(t.data, "alpha") == 0);
text_destroy(&t);
```

**Expected:** With `CHECK(text_create(&t, "alpha!"));` the run stops with `Check failed` at the CHECK on `t.len == 5 && strcmp(t.data, "alpha") == 0`, because the "create an owned string" case no longer shows that length is 5 and content is alpha. Restoring `CHECK(text_create(&t, "alpha"));` brings that observation back.

The owner contains both storage and logical length. The terminator is additional storage, not part of len.

## Exercise 2: Clone independent storage: debug a regression

A regression changed one token in worked example 2, the "clone independent storage" case, so one line now reads `b.data[1] = 'b';`. Run the example with that line, use the failing CHECK to find why the original remains cat no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
struct Text a = {0}, b = {0};
CHECK(text_create(&a, "cat") && text_create(&b, a.data));
b.data[0] = 'b';
CHECK(strcmp(a.data, "cat") == 0 && strcmp(b.data, "bat") == 0);
text_destroy(&a);
text_destroy(&b);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `strcmp(a.data, "cat") == 0 && strcmp(b.data, "bat") == 0`. Once the line reads `b.data[0] = 'b';` again, the "clone independent storage" case again shows that the original remains cat.

Two independently allocated owners can be destroyed separately. A plain struct assignment would share the pointer and make that unsafe.

## Exercise 3: Borrow without releasing

Read through a const pointer borrowed from an owner.

```c
struct Text t = {0};
CHECK(text_create(&t, "ready"));
const char *view = t.data;
CHECK(strcmp(view, "ready") == 0);
text_destroy(&t);
```

**Expected:** The borrowed content is ready.

The view must not be used after destruction. Only the owning object performs release.

## Exercise 4: Represent an owned empty string

Create an owner for empty text.

```c
struct Text t = {0};
CHECK(text_create(&t, ""));
CHECK(t.len == 0 && t.data != NULL && t.data[0] == '\0');
text_destroy(&t);
```

**Expected:** Length is zero but a valid terminator exists.

An empty string still needs one byte under this contract. It differs from an uninitialized or destroyed owner.

## Exercise 5: Make cleanup idempotent

Destroy the same reset owner twice.

```c
struct Text t = {0};
CHECK(text_create(&t, "x"));
text_destroy(&t);
text_destroy(&t);
CHECK(t.data == NULL && t.len == 0);
```

**Expected:** The owner stays empty.

Resetting the owning fields makes this API safe for repeated cleanup. Other stale aliases are not made safe automatically.

## Exercise 6: Transfer a deliberate move

Move ownership by assigning the struct and clearing the source.

```c
struct Text source = {0};
CHECK(text_create(&source, "move"));
struct Text destination = source;
source = (struct Text){0};
CHECK(source.data == NULL && strcmp(destination.data, "move") == 0);
text_destroy(&destination);
```

**Expected:** Only the destination retains the allocation.

The explicit source reset is the manual move protocol. Leaving two apparent owners would make destruction ambiguous.

## After comparison

Add a fresh distinguishing input for the "transfer a deliberate move" case to your own c-017 source. Explain why every access in `text_create` or `text_destroy` stays within a live object and each owned resource is released. An expected borrow failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "clone independent storage" case apart from ordinary output: the fixture proves its stated borrow, owned result and clone assumptions, not universal safety.
