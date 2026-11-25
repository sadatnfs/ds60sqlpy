# c-019: explained solutions

`c-019_solution.c` assembles the "encode a known word" case through the "transfer a framed payload" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A portable binary format specifies bytes, widths and byte order rather than dumping an in-memory struct. Host representation can differ in endianness, padding, alignment and type sizes. Explicit encoding makes the wire contract inspectable and avoids leaking padding bytes. A decoder must validate the available length before reading fields and reject unsupported versions or values. Use unsigned types for shifts and masks, with shift counts inside the type width. memcpy can safely copy object representation bytes when the destination object and sizes are valid, but interpreting arbitrary bytes as a typed object still requires a representation contract.

A big-endian 32-bit encoding stores the most significant byte first. Cast each input byte to uint32_t before shifting. Without the cast, integer promotion (introduced in c-003) turns the unsigned char into an int, and shifting a byte value of 128 or more left by 24 overflows int, which is undefined behavior. Read four bytes only after checking length. Bitwise OR combines disjoint fields. The format here assumes eight-bit bytes and requires that with _Static_assert because its external definition uses octets.

## Exercise 1: Encode a known word: predict an edited check

In worked example 1, change `CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` to `CHECK(out[1] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
unsigned char out[4];
encode_u32(UINT32_C(0x12345678), out);
CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);
```

**Expected:** `Check failed`: `CHECK(out[1] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` is false, although the bytes are 12, 34, 56, 78 in hexadecimal.

**Verify:** Explain which claim `CHECK(out[1] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` makes that the state fails; restoring `CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` passes again.

The explicit byte contract does not depend on host endianness.

## Exercise 2: Decode a known word: debug a regression

Worked example 2 now has a line reading `unsigned char data[] = {1, 0, 1, 0};`. Repair it so that the numeric value is 256 again.

The unchanged code is worked example 2:

```c
unsigned char data[] = {0, 0, 1, 0};
uint32_t value = 0;
CHECK(decode_u32(data, 4, &value) && value == 256);
```

**Expected:** `Check failed` at `decode_u32(data, 4, &value) && value == 256` until the line reads `unsigned char data[] = {0, 0, 1, 0};` again.

**Verify:** Explain how `unsigned char data[] = {1, 0, 1, 0};` changes the value `decode_u32(data, 4, &value) && value == 256` tests, using your failing and repaired runs.

Each byte is promoted to the intended unsigned width before shifting.

## Exercise 3: Reject a truncated field

Attempt to decode only three available bytes.

```c
unsigned char data[] = {1, 2, 3};
uint32_t value = 9;
CHECK(!decode_u32(data, 3, &value) && value == 9);
```

**Expected:** The decoder fails and preserves output.

**Verify:** Keep a CHECK equivalent to `!decode_u32(data, 3, &value) && value == 9`. Control edit: changing `uint32_t value = 9;` to `uint32_t value = 10;` must fail it; then restore it.

Length validation occurs before any fourth-byte access. Reading first and diagnosing later would already violate bounds.

## Exercise 4: Round-trip zero

Encode and decode numeric zero.

```c
unsigned char out[4];
encode_u32(0, out);
uint32_t value = 1;
CHECK(decode_u32(out, 4, &value) && value == 0);
```

**Expected:** The result is zero.

**Verify:** Keep a CHECK equivalent to `decode_u32(out, 4, &value) && value == 0`. Control edit: changing `encode_u32(0, out);` to `encode_u32(1, out);` must fail it; then restore it.

Zero is a valid payload, not an absent field or string terminator in this format.

## Exercise 5: Round-trip the maximum

Encode and decode UINT32_MAX.

```c
unsigned char out[4];
encode_u32(UINT32_MAX, out);
uint32_t value = 0;
CHECK(decode_u32(out, 4, &value) && value == UINT32_MAX);
```

**Expected:** All bits survive.

**Verify:** Keep a CHECK equivalent to `decode_u32(out, 4, &value) && value == UINT32_MAX`. Control edit: `CHECK(decode_u32(out, 4, &value) && value != UINT32_MAX);` must fail; then restore it.

The boundary case exercises every high bit and catches signed intermediate mistakes.

## Exercise 6: Transfer a framed payload

Decode the four bytes after a one-byte version field.

```c
unsigned char frame[] = {1, 0, 0, 0, 7};
uint32_t value = 0;
CHECK(frame[0] == 1 && decode_u32(frame + 1, sizeof frame - 1, &value) &&
      value == 7);
```

**Expected:** Version 1 and payload 7 are interpreted separately.

**Verify:** Keep a CHECK equivalent to `frame[0] == 1 && decode_u32(frame + 1, sizeof frame - 1, &value) && value == 7`. Control edit: changing `unsigned char frame[] = {1, 0, 0, 0, 7};` to `unsigned char frame[] = {2, 0, 0, 0, 7};` must fail it; then restore it.

A format should reject unsupported versions before interpreting fields under the wrong schema.

## After comparison

Decode `{0x12, 0x34, 0x56, 0x78}` with `decode_u32` and CHECK that the value is `0x12345678`. Then `memcpy` the same bytes into a `uint32_t` and explain why it holds `0x78563412` on a little-endian host while the shift-based decoder gives the same answer everywhere. Finally CHECK that a 3-byte input is rejected before any fourth byte is read.
