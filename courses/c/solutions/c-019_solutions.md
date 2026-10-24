# c-019: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A portable binary format specifies bytes, widths and byte order rather than dumping an in-memory struct. Host representation can differ in endianness, padding, alignment and type sizes. Explicit encoding makes the wire contract inspectable and avoids leaking padding bytes. A decoder must validate the available length before reading fields and reject unsupported versions or values. Use unsigned types for shifts and masks, with shift counts inside the type width. memcpy can safely copy object representation bytes when the destination object and sizes are valid, but interpreting arbitrary bytes as a typed object still requires a representation contract.

A big-endian 32-bit encoding stores the most significant byte first. Cast each input byte to uint32_t before shifting so integer promotion does not produce a problematic signed operation. Read four bytes only after checking length. Bitwise OR combines disjoint fields. The format here assumes eight-bit bytes and requires that with _Static_assert because its external definition uses octets.

## Exercise 1: Encode a known word

Encode 0x12345678 in big-endian order.

```c
unsigned char out[4];
encode_u32(UINT32_C(0x12345678), out);
CHECK(out[0] == 0x12 && out[1] == 0x34 && out[2] == 0x56 && out[3] == 0x78);
```

**Expected:** The bytes are 12, 34, 56, 78 in hexadecimal.

The explicit byte contract does not depend on host endianness.

## Exercise 2: Decode a known word

Decode bytes 00, 00, 01, 00.

```c
unsigned char data[] = {0, 0, 1, 0};
uint32_t value = 0;
CHECK(decode_u32(data, 4, &value) && value == 256);
```

**Expected:** The numeric value is 256.

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

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
