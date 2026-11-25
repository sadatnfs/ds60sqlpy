# c-029: explained solutions

`c-029_solution.c` assembles the "copy a representation safely" case through the "transfer a bounded byte copy" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

Undefined behavior is not a special runtime result such as a crash. It removes the language guarantee for the operation and can affect compiler reasoning about surrounding code. Common causes include out-of-bounds access, signed overflow, expired lifetimes and incompatible typed access. The effective-type and aliasing rules allow optimizers to assume certain pointer types do not refer to the same object. Use character access or memcpy for object representation rather than casting arbitrary byte storage to a typed pointer. Alignment and representation validity remain separate requirements. A plausible output from one build does not establish that an invalid operation is safe.

unsigned char can inspect object representation bytes. memcpy copies a specified number of bytes between valid nonoverlapping regions. memmove supports overlapping ranges. _Alignof describes a type alignment requirement. A pointer conversion alone does not create an object lifetime, correct alignment or valid value representation. This lesson deliberately demonstrates defined alternatives and never executes the invalid counterpart.

## Exercise 1: Copy a representation safely: predict an edited check

In worked example 1, change `CHECK(restored == original);` to `CHECK(restored != original);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
float original = 1.5f, restored = 0.0f;
unsigned char bytes[sizeof original];
memcpy(bytes, &original, sizeof original);
memcpy(&restored, bytes, sizeof restored);
CHECK(restored == original);
```

**Expected:** `Check failed`: `CHECK(restored != original);` is false, although the restored value is 1.5.

**Verify:** Explain which claim `CHECK(restored != original);` makes that the state fails; restoring `CHECK(restored == original);` passes again.

The copied bytes originated from a valid object of the same type. This does not claim arbitrary external bytes are a valid float representation.

## Exercise 2: Inspect bytes without type punning: debug a regression

Worked example 2 now has a line reading `sum -= bytes[i];`. Repair it so that the bytes sum to 7 whatever the byte order again.

The unchanged code is worked example 2:

```c
int value = 7;
const unsigned char *bytes = (const unsigned char *)&value;
unsigned int sum = 0;
for (size_t i = 0; i < sizeof value; i++)
  sum += bytes[i];
CHECK(sum == 7u);
```

**Expected:** `Check failed` at `sum == 7u` until the line reads `sum += bytes[i];` again.

**Verify:** Explain how `sum -= bytes[i];` changes the value `sum == 7u` tests, using your failing and repaired runs.

Character access is the appropriate representation-view mechanism. The value 7 occupies one byte and the other bytes are zero in either byte order, so the sum does not depend on endianness. Reading the same storage through an incompatible pointer type would break the aliasing rule instead.

## Exercise 3: Handle overlapping moves

Shift abc right by one within a buffer using memmove.

```c
char text[8] = "abc";
memmove(text + 1, text, 4);
CHECK(strcmp(text, "aabc") == 0);
```

**Expected:** The buffer prefix becomes aabc.

**Verify:** Keep a CHECK equivalent to `strcmp(text, "aabc") == 0`. Control edit: changing `memmove(text + 1, text, 4);` to `memmove(text + 2, text, 4);` must fail it; then restore it.

memmove supports overlap. memcpy would not provide the required contract for these overlapping ranges.

## Exercise 4: Keep typed access in a real object

Copy an int value into another int with memcpy.

```c
int source = 9, target = 0;
memcpy(&target, &source, sizeof target);
CHECK(target == 9);
```

**Expected:** The target value becomes 9.

**Verify:** Keep a CHECK equivalent to `target == 9`. Control edit: changing `int source = 9, target = 0;` to `int source = 10, target = 0;` must fail it; then restore it.

Both source and destination are valid int objects with sufficient storage. No misaligned cast is involved.

## Exercise 5: Inspect an alignment requirement

Read the alignment of int and max_align_t.

```c
CHECK(_Alignof(int) > 0 && _Alignof(max_align_t) > 0);
```

**Expected:** Both requirements are positive.

**Verify:** Keep a CHECK equivalent to `_Alignof(int) > 0 && _Alignof(max_align_t) > 0` and name a defined input that would make it fail.

Alignment is part of a typed access precondition. A byte count alone cannot prove an arbitrary address is aligned.

## Exercise 6: Transfer a bounded byte copy

Copy a four-byte payload into an equally sized destination.

```c
unsigned char source[4] = {0, 1, 2, 255}, target[4] = {0};
memcpy(target, source, sizeof source);
CHECK(memcmp(source, target, sizeof source) == 0);
```

**Expected:** All bytes match exactly.

**Verify:** Keep a CHECK equivalent to `memcmp(source, target, sizeof source) == 0`. Control edit: `CHECK(memcmp(source, target, sizeof source) != 0);` must fail; then restore it.

Here bytewise equality is the semantic contract because the objects are explicitly byte arrays, not structs with unspecified padding.

## After comparison

Check that `sizeof(float) == sizeof(uint32_t)`, then `memcpy` the `float` value 1.0f into a `uint32_t` and CHECK that the bits are `0x3F800000` on an IEEE 754 target. Explain as text why `*(uint32_t *)&f` breaks the effective-type rule even though it often prints the same number, and why `memcpy` does not.
