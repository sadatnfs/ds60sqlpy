# c-029: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Undefined behavior is not a special runtime result such as a crash. It removes the language guarantee for the operation and can affect compiler reasoning about surrounding code. Common causes include out-of-bounds access, signed overflow, expired lifetimes and incompatible typed access. The effective-type and aliasing rules allow optimizers to assume certain pointer types do not refer to the same object. Use character access or memcpy for object representation rather than casting arbitrary byte storage to a typed pointer. Alignment and representation validity remain separate requirements. A plausible output from one build does not establish that an invalid operation is safe.

unsigned char can inspect object representation bytes. memcpy copies a specified number of bytes between valid nonoverlapping regions. memmove supports overlapping ranges. _Alignof describes a type alignment requirement. A pointer conversion alone does not create an object lifetime, correct alignment or valid value representation. This lesson deliberately demonstrates defined alternatives and never executes the invalid counterpart.

## Exercise 1: Copy a representation safely

Copy a float into bytes and back into a float object.

```c
float original = 1.5f, restored = 0.0f;
unsigned char bytes[sizeof original];
memcpy(bytes, &original, sizeof original);
memcpy(&restored, bytes, sizeof restored);
CHECK(restored == original);
```

**Expected:** The restored value is 1.5.

The copied bytes originated from a valid object of the same type. This does not claim arbitrary external bytes are a valid float representation.

## Exercise 2: Inspect bytes without type punning

Read an integer representation through unsigned char.

```c
int value = 7;
const unsigned char *bytes = (const unsigned char *)&value;
unsigned int sum = 0;
for (size_t i = 0; i < sizeof value; i++)
  sum += bytes[i];
CHECK(sizeof value >= 1);
(void)sum;
```

**Expected:** The byte view has exactly sizeof(int) bytes.

Character access is the appropriate representation-view mechanism. The test deliberately avoids assuming a particular byte order.

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

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
