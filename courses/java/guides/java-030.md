# java-030: Serialization and schema evolution

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-029`

## Learning objectives

Serialize a versioned binary format and reject unknown versions, truncation, oversized lengths and trailing data. Along the way, explain wire schema, schema evolution, length bound, deserialization boundary using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Change the version bytes to 99 and decode. The final exercise transfers the mechanism to reject trailing data and invalid domain state.

## Purpose and mental model

Serialization turns domain values into a representation that another process or version can read. A format needs an explicit schema, version, encoding and size policy. A reader should validate before allocating large buffers or constructing trusted domain objects. Schema evolution is a compatibility decision:an older version may omit a newly added field, which needs a documented default or upgrade rule. Unknown versions should not be guessed at silently.

This lesson defines a small explicit binary format using DataInputStream and DataOutputStream. It deliberately avoids Java object deserialization for untrusted input. The format has a magic number, a version, bounded UTF-8 text, integer cents and an optional version 2 note. A version 1 record receives a declared default note. The decoder rejects invalid lengths, malformed UTF-8, truncation, trailing bytes and domain violations. These checks make the data boundary visible rather than relying on a class name to imply trust.

## Vocabulary and concepts

**Wire schema:** The field order, types, encoding and version of serialized data.

**Schema evolution:** A declared compatibility policy between format versions.

**Length bound:** A maximum accepted size checked before allocation.

**Deserialization boundary:** Validation required before external bytes become trusted objects.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-030/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Round-trip version 2 data: change one input.** Close Example A and rebuild it in a fresh `Main.java`, keeping the assertion on `decode(encoded).equals(record)`. Then propose one input change that would make that assertion fail and explain why before trying it.
   **Expected:** Your rebuild reproduces the worked observation (equal domain record and exact Unicode note), and your proposed change makes the assertion on `decode(encoded).equals(record)` fail.
   **Verify:** Run the rebuild with `java -ea Main` first, then the changed copy, and keep both results. Name the value that makes `decode(encoded).equals(record)` false in the changed copy.

2. **Apply a version 1 default: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `Account legacy = decode(encode(new Account("a1", 126, "ignored by v1"), 1));`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")`; after it the line reads `Account legacy = decode(encode(new Account("a1", 125, "ignored by v1"), 1));` again and decoded note unlabelled.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")` for this input.

3. **Reject an unknown version.** Change the version bytes to 99 and decode.
   **Expected:** IOException naming version.
   **Verify:** Keep an assertion equivalent to `rejected`. As a control, change `unknown[5] = 99;` to `unknown[6] = 99;`: the run must fail with an `AssertionError` from the assertion on `rejected`. Restore the line before continuing.

4. **Detect truncation.** Remove the final byte from a valid version 2 payload.
   **Expected:** IOException or EOFException before returning a record.
   **Verify:** Keep an assertion equivalent to `truncated`. As a control, change `truncated = true;` to `truncated = false;`: the run must fail with an `AssertionError` from the assertion on `truncated`. Restore the line before continuing.

5. **Reject an oversized declared text length.** Replace the first text length with Integer.MAX_VALUE.
   **Expected:** IOException for length before allocating that size.
   **Verify:** Keep an assertion equivalent to `bounded`. As a control, change `bounded = expected.getMessage().contains("length");` to `bounded = expected.getMessage().contains("length!");`: the run must fail with an `AssertionError` from the assertion on `bounded`. Restore the line before continuing.

6. **Reject trailing data and invalid domain state.** Append an extra byte, then try constructing a negative-balance account.
   **Expected:** trailing payload IOException; negative balance IllegalArgumentException.
   **Verify:** Keep an assertion equivalent to `extra && negative`. As a control, change `byte[] trailing = Arrays.copyOf(encoded, encoded.length + 1);` to `byte[] trailing = Arrays.copyOf(encoded, encoded.length - 1);`: the run must fail with an `AssertionError` from the assertion on `extra && negative`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: equal domain record and exact Unicode note. Then list the values read by `decode(encoded).equals(record)` and trace each one from its declaration. Finally, name one input that would make `decode(encoded).equals(record)` false.
- **Exercise 2:** First restate the expected observation: decoded note unlabelled. Then list the values read by `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")` and trace each one from its declaration. Finally, compare `Account legacy = decode(encode(new Account("a1", 126, "ignored by v1"), 1));` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: IOException naming version. Then list the values read by `rejected` and trace each one from its declaration. Finally, predict the effect of changing `unknown[5] = 99;` to `unknown[6] = 99;` before running anything.
- **Exercise 4:** First restate the expected observation: IOException or EOFException before returning a record. Then list the values read by `truncated` and trace each one from its declaration. Finally, predict the effect of changing `truncated = true;` to `truncated = false;` before running anything.
- **Exercise 5:** First restate the expected observation: IOException for length before allocating that size. Then list the values read by `bounded` and trace each one from its declaration. Finally, predict the effect of changing `bounded = expected.getMessage().contains("length");` to `bounded = expected.getMessage().contains("length!");` before running anything.
- **Exercise 6:** First restate the expected observation: trailing payload IOException; negative balance IllegalArgumentException. Then list the values read by `extra && negative` and trace each one from its declaration. Finally, predict the effect of changing `byte[] trailing = Arrays.copyOf(encoded, encoded.length + 1);` to `byte[] trailing = Arrays.copyOf(encoded, encoded.length - 1);` before running anything.

## Self-check and retrieval

Close the solution and explain Wire schema, Schema evolution, Length bound in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/DataInputStream.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
