# java-030: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

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

Task: Close Example A and rebuild it in a fresh `Main.java`, keeping the assertion on `decode(encoded).equals(record)`. Then propose one input change that would make that assertion fail and explain why before trying it.

The comparison includes both domain values and text identity. A successful byte write alone would not show that the reader agrees on encoding and field order.

The unchanged code is the part that Example A adds:

```java
Account record = new Account("a1", 125, "Café");
byte[] encoded = encode(record, 2);
assert decode(encoded).equals(record);
```

**Expected:** Your rebuild reproduces the worked observation (equal domain record and exact Unicode note), and your proposed change makes the assertion on `decode(encoded).equals(record)` fail.

**Verify:** Run the rebuild with `java -ea Main` first, then the changed copy, and keep both results. Name the value that makes `decode(encoded).equals(record)` false in the changed copy.

## Exercise 2: Apply a version 1 default: debug a regression

Task: A regression changed one token in the code that Example B adds after Example A, so one line now reads `Account legacy = decode(encode(new Account("a1", 126, "ignored by v1"), 1));`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.

The default is an explicit compatibility rule. It should not be inferred from an empty String or whatever value happened to initialize a field.

The unchanged code is the part that Example B adds:

```java
Account legacy = decode(encode(new Account("a1", 125, "ignored by v1"), 1));
assert legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled");
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")`; after it the line reads `Account legacy = decode(encode(new Account("a1", 125, "ignored by v1"), 1));` again and decoded note unlabelled.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")` for this input.

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

**Verify:** Keep an assertion equivalent to `rejected`. As a control, change `unknown[5] = 99;` to `unknown[6] = 99;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `truncated`. As a control, change `truncated = true;` to `truncated = false;`: the run must fail with an `AssertionError` from the assertion on `truncated`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `bounded`. As a control, change `bounded = expected.getMessage().contains("length");` to `bounded = expected.getMessage().contains("length!");`: the run must fail with an `AssertionError` from the assertion on `bounded`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `extra && negative`. As a control, change `byte[] trailing = Arrays.copyOf(encoded, encoded.length + 1);` to `byte[] trailing = Arrays.copyOf(encoded, encoded.length - 1);`: the run must fail with an `AssertionError` from the assertion on `extra && negative`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
