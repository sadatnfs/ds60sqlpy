# cpp-022: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Portable serialization converts a value into a documented byte or text format. A filesystem path describes a location in the current platform, not a portable file format. Endianness is byte ordering in multi-byte values. A version marker lets a reader reject incompatible representations instead of silently misinterpreting them.

## Detailed reasoning

A serializer chooses a representation that survives a different compiler or machine. The text v1, 7, 125 has a version, field order and unit interpretation; a raw struct dump has unspecified padding and platform-specific layout. A decoder must validate the version, exact field count, complete integer syntax and value ranges separately. The executable reference separates a shape-only illustration from decode, which also checks both integer conversions, full consumption and nonnegative ranges. The malformed suffix case must fail the full decoder even though its field count looks correct.

<!-- depth:start -->
## Paths, serialized bytes and versioned records

A filesystem path describes a location; a serialized record describes data. Joining records and batch.csv with filesystem::path uses platform-aware path composition. It does not open the file, create directories or validate the record bytes. A .csv suffix is a naming convention, not a parser implementation or a guarantee about quoting and delimiters.

The record format in this lesson is intentionally narrow: v1, id, cents with exactly three fields, decimal integer values and nonnegative domain constraints. The version tag is part of the data contract. A decoder should reject an unsupported version rather than guessing that a future format has the same meaning. A writer and reader can round-trip a value only when they agree on those details.

Shape validation checks delimiters and field count; value validation checks each field's full conversion and range. The reference contains both an introductory shape illustration and a strict decoder. A string such as v1, 7, 125x has the right number of fields but fails full numeric consumption. A negative amount can parse as an integer while failing the domain rule. Keep those reasons distinct when debugging.

Text serialization avoids some machine-layout hazards but still needs explicit rules for encoding, line endings, whitespace and maximum size. Writing the raw bytes of a C++ struct is not a portable substitute: padding, endianness, integer width and ABI layout can differ. Even on the same machine, uninitialized padding is not a stable public format.

Path safety is also separate from grammar. A correctly parsed record can be written to the wrong location if the working directory or user-controlled path is misunderstood. The examples only construct a relative path and inspect filename/parent components. Actual file creation belongs to an owned host directory with explicit failure handling. Later lessons restrict identifiers before mapping them into filenames.

## Debugging the contract

If a round-trip passes only because both writer and reader share the same bug, add independent known-byte fixtures. If a suffix slips through, inspect conversion end pointers. If a file appears in an unexpected folder, record the process working directory and resolved input/output paths. If a version mismatch is silently accepted, restore an explicit version gate rather than treating every three-field string as v1.
<!-- depth:end -->

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

Document v1, 7, 125 field order and units.

**Expected:** Version v1, ID 7, cents 125, three fields.

**Reasoning:** Representation should be interpretable without the original struct.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Check zero values

Encode ID 0 and cents 0.

**Expected:** v1, 0, 0.

**Reasoning:** Zero must survive round-trip as data.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Build a strict decoder

Require v1 and exactly three comma-separated fields.

**Expected:** v2, 7, 125 and v1, 7, 125, junk rejected.

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
