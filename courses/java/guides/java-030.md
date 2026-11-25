# java-030: Serialization and schema evolution

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-029`

## Learning objectives

Serialize a versioned binary format and reject unknown versions, truncation, oversized lengths and trailing data.

The six exercises practice these steps:

- Round-trip version 2 data.
- Apply a version 1 default.
- Reject an unknown version.
- Detect truncation.
- Reject an oversized declared text length.
- Reject trailing data and invalid domain state.

## Purpose and mental model

Serialization turns domain values into a representation that another process or version can read. A format needs an explicit schema, version, encoding and size policy. A reader should validate before allocating large buffers or constructing trusted domain objects. Schema evolution is a compatibility decision:an older version may omit a newly added field, which needs a documented default or upgrade rule. Unknown versions should not be guessed at silently.

This lesson defines a small explicit binary format using DataInputStream and DataOutputStream. It deliberately avoids Java object deserialization for untrusted input. The format has a magic number, a version, bounded UTF-8 text, integer cents and an optional version 2 note. A version 1 record receives a declared default note. The decoder rejects invalid lengths, malformed UTF-8, truncation, trailing bytes and domain violations. These checks make the data boundary visible rather than relying on a class name to imply trust.

## Vocabulary and concepts

**Wire schema:** The field order, types, encoding and version of serialized data.

**Schema evolution:** A declared compatibility policy between format versions.

**Length bound:** A maximum accepted size checked before allocation.

**Deserialization boundary:** Validation required before external bytes become trusted objects.

## How to run this lesson

`encode` and `decode` implement a small binary format with `DataOutputStream` and `DataInputStream`: a magic number, a version, length-prefixed UTF-8 text with limits, a long balance and an optional note. Exercise 1 has no recorded edit.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Write a fixed magic int and version number before fields. Text is UTF-8 bytes preceded by a bounded integer length. Read the length, validate it, then read exactly that many bytes. A CharsetDecoder with REPORT rejects malformed sequences instead of replacing them. The domain record validates nonnegative cents and identifier shape. Version 2 adds a note; version 1 decodes with the explicit default unlabelled.

## Worked example / walkthrough

### Example A: Round-trip version 2 data

The comparison includes both domain values and text identity. A successful byte write alone would not show that the reader agrees on encoding and field order.

```java
import java.util.*;

public class Main {

  record Account(String id, long cents, String note) {
    Account {
      if (
        id == null || !id.matches("[A-Za-z0-9_-]{1,32}") || cents < 0 || note == null
      ) throw new IllegalArgumentException("invalid account");
    }
  }

  static byte[] encode(Account value, int version) throws java.io.IOException {
    if (version != 1 && version != 2) throw new java.io.IOException("unsupported version");
    var bytes = new java.io.ByteArrayOutputStream();
    try (var out = new java.io.DataOutputStream(bytes)) {
      out.writeInt(0x44533630);
      out.writeShort(version);
      writeText(out, value.id(), 64);
      out.writeLong(value.cents());
      if (version == 2) writeText(out, value.note(), 128);
    }
    return bytes.toByteArray();
  }

  static void writeText(java.io.DataOutputStream out, String value, int limit)
    throws java.io.IOException {
    if (value.length() > limit) throw new java.io.IOException("text length limit");
    var encoded = java.nio.charset.StandardCharsets.UTF_8.newEncoder()
      .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
      .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT)
      .encode(java.nio.CharBuffer.wrap(value));
    byte[] bytes = new byte[encoded.remaining()];
    encoded.get(bytes);
    if (bytes.length > limit) throw new java.io.IOException("text length limit");
    out.writeInt(bytes.length);
    out.write(bytes);
  }

  static String readText(java.io.DataInputStream input, int limit) throws java.io.IOException {
    int length = input.readInt();
    if (length < 0 || length > limit) throw new java.io.IOException("text length limit");
    byte[] bytes = input.readNBytes(length);
    if (bytes.length != length) throw new java.io.EOFException("truncated text");
    return java.nio.charset.StandardCharsets.UTF_8.newDecoder()
      .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
      .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT)
      .decode(java.nio.ByteBuffer.wrap(bytes))
      .toString();
  }

  static Account decode(byte[] bytes) throws java.io.IOException {
    try (var input = new java.io.DataInputStream(new java.io.ByteArrayInputStream(bytes))) {
      if (input.readInt() != 0x44533630) throw new java.io.IOException("magic mismatch");
      int version = input.readUnsignedShort();
      if (version != 1 && version != 2) throw new java.io.IOException("unsupported version");
      String id = readText(input, 64);
      long cents = input.readLong();
      String note = version == 2 ? readText(input, 128) : "unlabelled";
      if (input.read() != -1) throw new java.io.IOException("trailing bytes");
      try {
        return new Account(id, cents, note);
      } catch (IllegalArgumentException error) {
        throw new java.io.IOException("invalid domain record", error);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Account record = new Account("a1", 125, "Café");
    byte[] encoded = encode(record, 2);
    assert decode(encoded).equals(record);
  }
}
```

**Expected:** equal domain record and exact Unicode note.

### Example B: Apply a version 1 default

The default is an explicit compatibility rule. It should not be inferred from an empty String or whatever value happened to initialize a field.

```java
import java.util.*;

public class Main {

  record Account(String id, long cents, String note) {
    Account {
      if (
        id == null || !id.matches("[A-Za-z0-9_-]{1,32}") || cents < 0 || note == null
      ) throw new IllegalArgumentException("invalid account");
    }
  }

  static byte[] encode(Account value, int version) throws java.io.IOException {
    if (version != 1 && version != 2) throw new java.io.IOException("unsupported version");
    var bytes = new java.io.ByteArrayOutputStream();
    try (var out = new java.io.DataOutputStream(bytes)) {
      out.writeInt(0x44533630);
      out.writeShort(version);
      writeText(out, value.id(), 64);
      out.writeLong(value.cents());
      if (version == 2) writeText(out, value.note(), 128);
    }
    return bytes.toByteArray();
  }

  static void writeText(java.io.DataOutputStream out, String value, int limit)
    throws java.io.IOException {
    if (value.length() > limit) throw new java.io.IOException("text length limit");
    var encoded = java.nio.charset.StandardCharsets.UTF_8.newEncoder()
      .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
      .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT)
      .encode(java.nio.CharBuffer.wrap(value));
    byte[] bytes = new byte[encoded.remaining()];
    encoded.get(bytes);
    if (bytes.length > limit) throw new java.io.IOException("text length limit");
    out.writeInt(bytes.length);
    out.write(bytes);
  }

  static String readText(java.io.DataInputStream input, int limit) throws java.io.IOException {
    int length = input.readInt();
    if (length < 0 || length > limit) throw new java.io.IOException("text length limit");
    byte[] bytes = input.readNBytes(length);
    if (bytes.length != length) throw new java.io.EOFException("truncated text");
    return java.nio.charset.StandardCharsets.UTF_8.newDecoder()
      .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
      .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT)
      .decode(java.nio.ByteBuffer.wrap(bytes))
      .toString();
  }

  static Account decode(byte[] bytes) throws java.io.IOException {
    try (var input = new java.io.DataInputStream(new java.io.ByteArrayInputStream(bytes))) {
      if (input.readInt() != 0x44533630) throw new java.io.IOException("magic mismatch");
      int version = input.readUnsignedShort();
      if (version != 1 && version != 2) throw new java.io.IOException("unsupported version");
      String id = readText(input, 64);
      long cents = input.readLong();
      String note = version == 2 ? readText(input, 128) : "unlabelled";
      if (input.read() != -1) throw new java.io.IOException("trailing bytes");
      try {
        return new Account(id, cents, note);
      } catch (IllegalArgumentException error) {
        throw new java.io.IOException("invalid domain record", error);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Account record = new Account("a1", 125, "Café");
    byte[] encoded = encode(record, 2);
    assert decode(encoded).equals(record);

    Account legacy = decode(encode(new Account("a1", 125, "ignored by v1"), 1));
    assert legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled");
  }
}
```

**Expected:** decoded note unlabelled.

## Prediction before your attempt

Before running Example A, list the fields in the order `encode` writes them for version 2, and decide whether "Café" survives the round trip unchanged. For Example B, predict what note a version 1 record receives when decoded, given that version 1 never writes one. Before Exercise 5, decide whether the decoder should allocate a buffer before or after it checks a declared length of `Integer.MAX_VALUE`.

## Exercises

1. **Round-trip version 2 data: change one input.** Rebuild Example A from memory and propose one input change that makes the assertion on `decode(encoded).equals(record)` fail.
   **Expected:** The rebuild passes and the changed copy fails as predicted.
   **Verify:** Name the value that differs between your rebuild and the changed copy.

2. **Apply a version 1 default: debug a regression.** A regression in Example B's new code makes one line read `Account legacy = decode(encode(new Account("a1", 126, "ignored by v1"), 1));`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")`; the repaired line reads `Account legacy = decode(encode(new Account("a1", 125, "ignored by v1"), 1));`.
   **Verify:** Explain how the changed token alters the value that `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")` tests.

3. **Reject an unknown version.** Change the version bytes to 99 and decode.
   **Expected:** IOException naming version.
   **Verify:** Control: changing `unknown[5] = 99;` to `unknown[6] = 99;` must fail the assertion on `rejected`.

4. **Detect truncation.** Remove the final byte from a valid version 2 payload.
   **Expected:** IOException or EOFException before returning a record.
   **Verify:** Control: changing `truncated = true;` to `truncated = false;` must fail the assertion on `truncated`.

5. **Reject an oversized declared text length.** Replace the first text length with Integer.MAX_VALUE.
   **Expected:** IOException for length before allocating that size.
   **Verify:** Control: changing `bounded = expected.getMessage().contains("length");` to `bounded = expected.getMessage().contains("length!");` must fail the assertion on `bounded`.

6. **Reject trailing data and invalid domain state.** Append an extra byte, then try constructing a negative-balance account.
   **Expected:** trailing payload IOException; negative balance IllegalArgumentException.
   **Verify:** Control: changing `byte[] trailing = Arrays.copyOf(encoded, encoded.length + 1);` to `byte[] trailing = Arrays.copyOf(encoded, encoded.length - 1);` must fail the assertion on `extra && negative`.

## Common pitfalls and diagnosis

Java's built-in `ObjectInputStream` will construct arbitrary classes from untrusted bytes, a long-running source of remote code execution bugs, so prefer an explicit format like this one. Trusting a length prefix before checking it lets a 4-byte header request gigabytes of memory. Guessing at an unknown version reads bytes with the wrong layout. Ignoring trailing bytes hides corruption. And `String.length()` counts UTF-16 units, not encoded bytes, so limit the byte array too.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First encode an `Account` with id "a1", 125 cents and the note "Café" using version 2. Then decode the bytes. Finally, assert that the decoded record `equals` the original and explain why record equality covers all three fields.
- **Exercise 2:** First note that the edit encodes 126 cents instead of 125. Then decode the version 1 bytes and read the cents field. Finally, explain why the id and default note still match and only the balance comparison fails.
- **Exercise 3:** First copy a valid encoding and overwrite the two version bytes at offsets 4 and 5 with 0 and 99. Then decode it inside a `try` block. Finally, assert that the `IOException` message mentions the version, not some later field.
- **Exercise 4:** First drop the last byte with `Arrays.copyOf(encoded, encoded.length - 1)`. Then decode the shorter array and catch `IOException`, which also covers `EOFException`. Finally, assert that no record was returned and say which field was incomplete.
- **Exercise 5:** First overwrite the four bytes of the id length with the value of `Integer.MAX_VALUE`. Then decode and catch the `IOException`. Finally, assert that its message mentions the length limit and explain why the check runs before `readNBytes`.
- **Exercise 6:** First append one extra byte to a valid encoding and confirm that `decode` rejects the trailing data. Then construct an `Account` with a negative balance and catch `IllegalArgumentException`. Finally, assert both failures and explain why they are separate gates.

## Self-check and retrieval

From memory, describe the byte layout of a version 2 record and the default that version 1 needs. Explain why the decoder rejects an unknown version instead of guessing, why it checks lengths before allocating, and why format errors and domain errors are separate checks.

## Next step

Continue with `java-031`: Reflection, annotations and service loading. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/DataInputStream.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-030: Serialization and schema evolution.
Read courses/java/guides/java-030.md and courses/java/lessons/java-030.java. Direct prerequisites: `java-029`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
