# java-030: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Serialization turns domain values into a representation that another process or version can read. A format needs an explicit schema, version, encoding and size policy. A reader should validate before allocating large buffers or constructing trusted domain objects. Schema evolution is a compatibility decision:an older version may omit a newly added field, which needs a documented default or upgrade rule. Unknown versions should not be guessed at silently.

This lesson defines a small explicit binary format using DataInputStream and DataOutputStream. It deliberately avoids Java object deserialization for untrusted input. The format has a magic number, a version, bounded UTF-8 text, integer cents and an optional version 2 note. A version 1 record receives a declared default note. The decoder rejects invalid lengths, malformed UTF-8, truncation, trailing bytes and domain violations. These checks make the data boundary visible rather than relying on a class name to imply trust.

**Wire schema:** The field order, types, encoding and version of serialized data.

**Schema evolution:** A declared compatibility policy between format versions.

**Length bound:** A maximum accepted size checked before allocation.

**Deserialization boundary:** Validation required before external bytes become trusted objects.

## Reading the reference

Write a fixed magic int and version number before fields. Text is UTF-8 bytes preceded by a bounded integer length. Read the length, validate it, then read exactly that many bytes. A CharsetDecoder with REPORT rejects malformed sequences instead of replacing them. The domain record validates nonnegative cents and identifier shape. Version 2 adds a note; version 1 decodes with the explicit default unlabelled.

## Exercise 1: Round-trip version 2 data: change one input

Task: Rebuild Example A from memory and propose one input change that makes the assertion on `decode(encoded).equals(record)` fail.

The comparison includes both domain values and text identity. A successful byte write alone would not show that the reader agrees on encoding and field order.

The unchanged code is the part that Example A adds:

```java
Account record = new Account("a1", 125, "Café");
byte[] encoded = encode(record, 2);
assert decode(encoded).equals(record);
```

**Expected:** The rebuild passes and the changed copy fails as predicted.

**Verify:** Name the value that differs between your rebuild and the changed copy.

## Exercise 2: Apply a version 1 default: debug a regression

Task: A regression in Example B's new code makes one line read `Account legacy = decode(encode(new Account("a1", 126, "ignored by v1"), 1));`. Repair it using the failing assertion.

The default is an explicit compatibility rule. It should not be inferred from an empty String or whatever value happened to initialize a field.

The unchanged code is the part that Example B adds:

```java
Account legacy = decode(encode(new Account("a1", 125, "ignored by v1"), 1));
assert legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled");
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")`; the repaired line reads `Account legacy = decode(encode(new Account("a1", 125, "ignored by v1"), 1));`.

**Verify:** Explain how the changed token alters the value that `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")` tests.

## Exercise 3: Reject an unknown version

Task: Change the version bytes to 99 and decode.

A reader that guesses the layout of an unknown version can reinterpret bytes incorrectly while appearing to succeed.

```java
byte[] unknown = encoded.clone();
unknown[4] = 0;
unknown[5] = 99;
boolean rejected = false;
try {
  decode(unknown);
} catch (java.io.IOException expected) {
  rejected = expected.getMessage().contains("version");
}
assert rejected;
```

**Expected:** IOException naming version.

**Verify:** Control: changing `unknown[5] = 99;` to `unknown[6] = 99;` must fail the assertion on `rejected`.

## Exercise 4: Detect truncation

Task: Remove the final byte from a valid version 2 payload.

The reader must obtain exactly the declared field length. A partial field is not a valid shorter value.

```java
boolean truncated = false;
try {
  decode(Arrays.copyOf(encoded, encoded.length - 1));
} catch (java.io.IOException expected) {
  truncated = true;
}
assert truncated;
```

**Expected:** IOException or EOFException before returning a record.

**Verify:** Control: changing `truncated = true;` to `truncated = false;` must fail the assertion on `truncated`.

## Exercise 5: Reject an oversized declared text length

Task: Replace the first text length with Integer.MAX_VALUE.

Length-prefix validation is a resource boundary. Reading or allocating first and checking afterward defeats that protection.

```java
byte[] huge = encoded.clone();
java.nio.ByteBuffer.wrap(huge, 6, 4).putInt(Integer.MAX_VALUE);
boolean bounded = false;
try {
  decode(huge);
} catch (java.io.IOException expected) {
  bounded = expected.getMessage().contains("length");
}
assert bounded;
```

**Expected:** IOException for length before allocating that size.

**Verify:** Control: changing `bounded = expected.getMessage().contains("length");` to `bounded = expected.getMessage().contains("length!");` must fail the assertion on `bounded`.

## Exercise 6: Reject trailing data and invalid domain state

Task: Append an extra byte, then try constructing a negative-balance account.

Format validity and domain validity are separate gates. The fixture chooses strict trailing-byte rejection rather than an undocumented forward-compatibility policy.

```java
byte[] trailing = Arrays.copyOf(encoded, encoded.length + 1);
boolean extra = false,
  negative = false;
try {
  decode(trailing);
} catch (java.io.IOException expected) {
  extra = expected.getMessage().contains("trailing");
}
try {
  new Account("a1", -1, "x");
} catch (IllegalArgumentException expected) {
  negative = true;
}
assert extra && negative;
```

**Expected:** trailing payload IOException; negative balance IllegalArgumentException.

**Verify:** Control: changing `byte[] trailing = Arrays.copyOf(encoded, encoded.length + 1);` to `byte[] trailing = Arrays.copyOf(encoded, encoded.length - 1);` must fail the assertion on `extra && negative`.

## After comparing the answer

Add a version 3 to your copy that appends an `int` priority with a default of 0 for older versions; update both directions and keep the trailing-byte check.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
