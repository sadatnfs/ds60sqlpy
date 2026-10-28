## A text file is not yet a typed table

CSV represents delimited text. A reader must interpret headers, quoting, missing-value markers and data types. Those choices are part of a schema contract. An identifier that looks numeric may need to remain text, because parsing it as an integer can discard leading zeros that are meaningful to identity.

The classroom prepares CSV 0.10.17 with DataFrames. The examples use that actual version's API, including explicit column types and strict parsing. Newer public documentation can describe different behavior, so the pinned source reference is included. No URL or external file is read during these lessons; literal CSV text is wrapped in `IOBuffer`.

An IO buffer has a current position. After writing, read from the beginning or take its bytes deliberately. Reusing a buffer without resetting its position can produce empty or partial input and be mistaken for a parser defect.

## Worked case A: retain identifiers and missing values

The first table contains IDs with leading zeros, a numeric amount and a date. The schema preserves the IDs as strings, parses the date with a declared format and recognizes a named missing marker in the amount column. The tests inspect values and missingness rather than assuming that every text-looking field has the same in-memory storage implementation.

{{WORKED_A}}

## Worked case B: reject malformed typed input and preserve quoting

Strict parsing rejects a noninteger value in a declared count column. A separate round trip includes a comma and embedded quotation marks inside string fields. The writer handles the CSV quoting rules, and the parsed output reproduces the original values. This is a value-level round trip; the exported text need not have the same formatting bytes as an arbitrary source file.

{{WORKED_B}}

## Inference and validation

Inference is useful for exploration, but a production contract should state important types, units and missingness policies. A successful parse does not establish key uniqueness, valid ranges or the correct data grain. Apply those checks after parsing and preserve rejected-row evidence when a repair policy is used.

Do not use a string path when the intended input is literal data. The API distinguishes a source location from a buffer containing text. Likewise, compression, encoding and locale-specific decimal conventions need explicit handling. A field containing a comma may be a quoted value rather than an extra column.

## Diagnose a parsing surprise

Inspect the raw header, delimiter, quoting and type arguments on a small excerpt. Confirm whether the missing marker is part of the agreed source format. A malformed value should not be silently reclassified as valid zero. If permissive parsing is selected, document and inspect its warnings and rejected values using the versioned API contract.

Retain a source checksum or version when a scientific result depends on a file. Record the parser and schema choices alongside it. A later parser version can change inference or warning behavior even when the source bytes remain the same.

The examples establish deterministic parsing and writing behavior for a small authored fixture in the prepared environment. They do not prove that all external CSV files are trustworthy or that inferred schemas are suitable for every application. Keep syntax, data validity and scientific interpretation as separate checks.
