# c-019: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-019_solution.c`, implements all six cases, from the "encode a known word" case to the "transfer a framed payload" case, in one `main.c`.

## Mechanism and assumptions

A portable binary format specifies bytes, widths and byte order rather than dumping an in-memory struct. Host representation can differ in endianness, padding, alignment and type sizes. Explicit encoding makes the wire contract inspectable and avoids leaking padding bytes. A decoder must validate the available length before reading fields and reject unsupported versions or values. Use unsigned types for shifts and masks, with shift counts inside the type width. memcpy can safely copy object representation bytes when the destination object and sizes are valid, but interpreting arbitrary bytes as a typed object still requires a representation contract.

A big-endian 32-bit encoding stores the most significant byte first. Cast each input byte to uint32_t before shifting. Without the cast, integer promotion (introduced in c-003) turns the unsigned char into an int, and shifting a byte value of 128 or more left by 24 overflows int, which is undefined behavior. Read four bytes only after checking length. Bitwise OR combines disjoint fields. The format here assumes eight-bit bytes and requires that with _Static_assert because its external definition uses octets.

## Exercise 1: Encode a known word: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` to `CHECK(out[1] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
unsigned char out[4];
encode_u32(UINT32_C(0x12345678), out);
CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);
```

**Expected:** With `CHECK(out[1] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` the run stops with `Check failed` at the CHECK on `out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78`, because the "encode a known word" case no longer shows that the bytes are 12, 34, 56, 78 in hexadecimal. Restoring `CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);` brings that observation back.

The explicit byte contract does not depend on host endianness.

## Exercise 2: Decode a known word: debug a regression

A regression changed one token in worked example 2, the "decode a known word" case, so one line now reads `unsigned char data[] = {1, 0, 1, 0};`. Run the example with that line, use the failing CHECK to find why the numeric value is 256 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
unsigned char data[] = {0, 0, 1, 0};
uint32_t value = 0;
CHECK(decode_u32(data, 4, &value) && value == 256);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `decode_u32(data, 4, &value) && value == 256`. Once the line reads `unsigned char data[] = {0, 0, 1, 0};` again, the "decode a known word" case again shows that the numeric value is 256.

Each byte is promoted to the intended unsigned width before shifting.

## Exercise 3: Reject a truncated field

Attempt to decode only three available bytes.

```c
unsigned char data[] = {1, 2, 3};
uint32_t value = 9;
CHECK(!decode_u32(data, 3, &value) && value == 9);
```

**Expected:** The decoder fails and preserves output.

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

A format should reject unsupported versions before interpreting fields under the wrong schema.

## After comparison

Add a fresh distinguishing input for the "transfer a framed payload" case to your own c-019 source. Explain why every access in `encode_u32` or `decode_u32` stays within a live object and each owned resource is released. An expected endianness failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "decode a known word" case apart from ordinary output: the fixture proves its stated endianness, wire format and alignment assumptions, not universal safety.
