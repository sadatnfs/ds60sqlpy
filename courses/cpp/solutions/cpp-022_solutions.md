# cpp-022: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Portable serialization converts a value into a documented byte or text format. A filesystem path describes a location in the current platform, not a portable file format. Endianness is byte ordering in multi-byte values. A version marker lets a reader reject incompatible representations instead of silently misinterpreting them.

## Worked example 1

```cpp
assert(encode(7,125)=="v1,7,125");
```

Expected: The exact wire text is independent of struct padding.

## Worked example 2

```cpp
auto p=std::filesystem::path("records")/"batch.csv";
```

Expected: The path joins components using platform rules; filename is batch.csv.

## Exercise 1: Specify the wire format

Document v1,7,125 field order and units.

**Expected:** Version v1, ID 7, cents 125, three fields.

**Reasoning:** Representation should be interpretable without the original struct.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Check zero values

Encode ID 0 and cents 0.

**Expected:** v1,0,0.

**Reasoning:** Zero must survive round-trip as data.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Build a strict decoder

Require v1 and exactly three comma-separated fields.

**Expected:** v2,7,125 and v1,7,125,junk rejected.

**Reasoning:** Version and full-field-count checks prevent ambiguity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Reject raw layout

Explain why writing sizeof(record) is not a portable format.

**Expected:** Padding, type width and byte order named.

**Reasoning:** A memory representation is not a schema.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Resolve a path

Print current_path and records/batch.csv absolute resolution in an owned directory.

**Expected:** Both anchor and resolved file documented.

**Reasoning:** Relative locations depend on the working directory.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer versioning

Design v2 with a fourth status field.

**Expected:** Explicit v2 reader or rejection, never v1 silent truncation.

**Reasoning:** Schema changes need compatibility decisions.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
