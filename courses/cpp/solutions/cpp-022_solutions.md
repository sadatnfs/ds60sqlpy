# cpp-022: explanations and reference observations

The [executable reference](cpp-022_solution.cpp) decodes `"v1,7,125"` back to the same record and rejects both a v2 prefix and an extra `junk` field. The explanations cover versioned formats and why path arithmetic needs no file. How to compare: [study guide](../STUDY-GUIDE.md#compare-with-the-solutions).

## Mechanism

Portable serialization converts a value into a documented byte or text format. A filesystem path describes a location in the current platform, not a portable file format. Endianness is byte ordering in multi-byte values. A version marker lets a reader reject incompatible representations instead of silently misinterpreting them.

## Detailed reasoning

A serializer chooses a representation that survives a different compiler or machine. The text `v1,7,125` has a version, field order and unit interpretation; a raw struct dump has unspecified padding and platform-specific layout. A decoder must validate the version, exact field count, complete integer syntax and value ranges separately. The executable reference separates a shape-only illustration from decode, which also checks both integer conversions, full consumption and nonnegative ranges. The malformed suffix case must fail the full decoder even though its field count looks correct.

<!-- depth:start -->
## Paths, serialized bytes and versioned records

A filesystem path describes a location; a serialized record describes data. Joining records and batch.csv with filesystem::path uses platform-aware path composition. It does not open the file, create directories or validate the record bytes. A .csv suffix is a naming convention, not a parser implementation or a guarantee about quoting and delimiters.

The record format in this lesson is intentionally narrow: `v1,<id>,<cents>` with exactly three fields, decimal integer values and nonnegative domain constraints. The version tag is part of the data contract. A decoder should reject an unsupported version rather than guessing that a future format has the same meaning. A writer and reader can round-trip a value only when they agree on those details.

Shape validation checks delimiters and field count; value validation checks each field's full conversion and range. The reference contains both an introductory shape illustration and a strict decoder. A string such as `v1,7,125x` has the right number of fields but fails full numeric consumption. A negative amount can parse as an integer while failing the domain rule. Keep those reasons distinct when debugging.

Text serialization avoids some machine-layout hazards but still needs explicit rules for encoding, line endings, whitespace and maximum size. Writing the raw bytes of a C++ struct is not a portable substitute: padding, endianness, integer width and ABI layout can differ. Even on the same machine, uninitialized padding is not a stable public format.

Path safety is also separate from grammar. A correctly parsed record can be written to the wrong location if the working directory or user-controlled path is misunderstood. The examples only construct a relative path and inspect filename/parent components. Actual file creation belongs to an owned host directory with explicit failure handling. Later lessons restrict identifiers before mapping them into filenames.

## Debugging the contract

If a round-trip passes only because both writer and reader share the same bug, add independent known-byte fixtures. If a suffix slips through, inspect conversion end pointers. If a file appears in an unexpected folder, record the process working directory and resolved input/output paths. If a version mismatch is silently accepted, restore an explicit version gate rather than treating every three-field string as v1.
<!-- depth:end -->

## Worked example 1

```cpp
assert(encode(7, 125) == "v1,7,125");
```

Expected: The exact wire text is independent of struct padding.

## Worked example 2

```cpp
auto p = std::filesystem::path("records") / "batch.csv";
```

Expected: The path joins components using platform rules; filename is batch.csv.

## Exercise 1: Specify the wire format

Document the field order and units of `v1,7,125`.

**Expected:** Version v1, ID 7, cents 125, three fields.

**Reasoning:** A reader on another machine only has the bytes, so the document must fix the field order (version, ID, cents) and the unit (integer cents) that `decode` relies on; without it, `7` and `125` could be swapped or read as dollars.

**Verify:** Check your document against `encode(7, 125) == "v1,7,125"`: the version comes first, the ID second and the cents third, and the unit is named.

## Exercise 2: Check zero values

Encode ID 0 and cents 0.

**Expected:** `v1,0,0`.

**Reasoning:** `std::to_string(0)` yields `"0"`, so the record is `v1,0,0` with all three fields present. A writer that skipped zero or empty values would change the field count and the strict decoder would reject its own output.

**Verify:** Assert `encode(0, 0) == "v1,0,0"`; zero values must still produce all three fields.

## Exercise 3: Build a strict decoder

Require v1 and exactly three comma-separated fields.

**Expected:** `v2,7,125` and `v1,7,125,junk` rejected; `v1,7,125` accepted.

**Reasoning:** `v2,7,125` has the right shape but an unknown version, so only the version gate rejects it; `v1,7,125,junk` has a known version but four fields, so only the exact field count rejects it. Each check catches a case the other misses.

**Verify:** Assert your decoder rejects `"v2,7,125"` and `"v1,7,125,junk"` but accepts `"v1,7,125"` as ID 7 and 125 cents.

## Exercise 4: Reject raw layout

Explain why writing sizeof(record) is not a portable format.

**Expected:** Padding, type width and byte order named.

**Reasoning:** A struct's bytes include compiler-chosen padding, platform-dependent integer widths such as `long`, and the host byte order. None of these is written down for the reader, so the same `sizeof(record)` bytes can decode to different values on another compiler or machine.

**Verify:** Check that your explanation ties each hazard to a concrete case, for example `sizeof(long)` being 4 on 64-bit Windows but 8 on 64-bit Linux.

## Exercise 5: Resolve a path

Print current_path and records/batch.csv absolute resolution in an owned directory.

**Expected:** Both anchor and resolved file documented.

**Reasoning:** `records/batch.csv` is resolved against `std::filesystem::current_path()` at run time, so the same program writes to different folders when launched from different directories; printing both paths shows which anchor was used.

**Verify:** Print `std::filesystem::current_path()` and `std::filesystem::absolute("records/batch.csv")`, and confirm the second path starts with the first.

## Exercise 6: Transfer versioning

Design v2 with a fourth status field.

**Expected:** Explicit v2 reader or rejection, never v1 silent truncation.

**Reasoning:** A v1 reader that ignored extra fields would decode `v2,7,125,paid` as ID 7 and 125 cents and silently drop the status. Rejecting unknown versions, or adding an explicit v2 reader, makes the compatibility decision visible instead of losing data.

**Verify:** Feed `"v2,7,125,paid"` to the v1 reader and confirm it is rejected rather than decoded as ID 7 and 125 cents; only the v2 reader may accept it.
