# c-029: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-029_solution.c`, implements all six cases, from the "copy a representation safely" case to the "transfer a bounded byte copy" case, in one `main.c`.

## Mechanism and assumptions

Undefined behavior is not a special runtime result such as a crash. It removes the language guarantee for the operation and can affect compiler reasoning about surrounding code. Common causes include out-of-bounds access, signed overflow, expired lifetimes and incompatible typed access. The effective-type and aliasing rules allow optimizers to assume certain pointer types do not refer to the same object. Use character access or memcpy for object representation rather than casting arbitrary byte storage to a typed pointer. Alignment and representation validity remain separate requirements. A plausible output from one build does not establish that an invalid operation is safe.

unsigned char can inspect object representation bytes. memcpy copies a specified number of bytes between valid nonoverlapping regions. memmove supports overlapping ranges. _Alignof describes a type alignment requirement. A pointer conversion alone does not create an object lifetime, correct alignment or valid value representation. This lesson deliberately demonstrates defined alternatives and never executes the invalid counterpart.

## Exercise 1: Copy a representation safely: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(restored == original);` to `CHECK(restored != original);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
float original = 1.5f, restored = 0.0f;
unsigned char bytes[sizeof original];
memcpy(bytes, &original, sizeof original);
memcpy(&restored, bytes, sizeof restored);
CHECK(restored == original);
```

**Expected:** With `CHECK(restored != original);` the run stops with `Check failed` at the CHECK on `restored == original`, because the "copy a representation safely" case no longer shows that the restored value is 1.5. Restoring `CHECK(restored == original);` brings that observation back.

The copied bytes originated from a valid object of the same type. This does not claim arbitrary external bytes are a valid float representation.

## Exercise 2: Inspect bytes without type punning: debug a regression

A regression changed one token in worked example 2, the "inspect bytes without type punning" case, so one line now reads `sum -= bytes[i];`. Run the example with that line, use the failing CHECK to find why the bytes sum to 7 whatever the byte order no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int value = 7;
const unsigned char *bytes = (const unsigned char *)&value;
unsigned int sum = 0;
for (size_t i = 0; i < sizeof value; i++)
  sum += bytes[i];
CHECK(sum == 7u);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `sum == 7u`. Once the line reads `sum += bytes[i];` again, the "inspect bytes without type punning" case again shows that the bytes sum to 7 whatever the byte order.

Character access is the appropriate representation-view mechanism. The value 7 occupies one byte and the other bytes are zero in either byte order, so the sum does not depend on endianness. Reading the same storage through an incompatible pointer type would break the aliasing rule instead.

## Exercise 3: Handle overlapping moves

Shift abc right by one within a buffer using memmove.

```c
char text[8] = "abc";
memmove(text + 1, text, 4);
CHECK(strcmp(text, "aabc") == 0);
```

**Expected:** The buffer prefix becomes aabc.

memmove supports overlap. memcpy would not provide the required contract for these overlapping ranges.

## Exercise 4: Keep typed access in a real object

Copy an int value into another int with memcpy.

```c
int source = 9, target = 0;
memcpy(&target, &source, sizeof target);
CHECK(target == 9);
```

**Expected:** The target value becomes 9.

Both source and destination are valid int objects with sufficient storage. No misaligned cast is involved.

## Exercise 5: Inspect an alignment requirement

Read the alignment of int and max_align_t.

```c
CHECK(_Alignof(int) > 0 && _Alignof(max_align_t) > 0);
```

**Expected:** Both requirements are positive.

Alignment is part of a typed access precondition. A byte count alone cannot prove an arbitrary address is aligned.

## Exercise 6: Transfer a bounded byte copy

Copy a four-byte payload into an equally sized destination.

```c
unsigned char source[4] = {0, 1, 2, 255}, target[4] = {0};
memcpy(target, source, sizeof source);
CHECK(memcmp(source, target, sizeof source) == 0);
```

**Expected:** All bytes match exactly.

Here bytewise equality is the semantic contract because the objects are explicitly byte arrays, not structs with unspecified padding.

## After comparison

Add a fresh distinguishing input for the "transfer a bounded byte copy" case to your own c-029 source. Explain why every access in the case code inside `main` stays within a live object and each owned resource is released. An expected effective type failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "inspect bytes without type punning" case apart from ordinary output: the fixture proves its stated effective type, object representation and strict aliasing assumptions, not universal safety.
