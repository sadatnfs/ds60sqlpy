# julia-017: Typed CSV input and round-trip data contracts

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-015`, `julia-016`.

Parse and export bounded CSV data using explicit types and missingness rules rather than accidental inference.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A text file is not yet a typed table

CSV represents delimited text. A reader must interpret headers, quoting, missing-value markers and data types. Those choices are part of a schema contract. An identifier that looks numeric may need to remain text, because parsing it as an integer can discard leading zeros that are meaningful to identity.

The classroom prepares CSV 0.10.17 with DataFrames. The examples use that actual version's API, including explicit column types and strict parsing. Newer public documentation can describe different behavior, so the pinned source reference is included. No URL or external file is read during these lessons; literal CSV text is wrapped in `IOBuffer`.

An IO buffer has a current position. After writing, read from the beginning or take its bytes deliberately. Reusing a buffer without resetting its position can produce empty or partial input and be mistaken for a parser defect.

## Worked case A: retain identifiers and missing values

The first table contains IDs with leading zeros, a numeric amount and a date. The schema preserves the IDs as strings, parses the date with a declared format and recognizes a named missing marker in the amount column. The tests inspect values and missingness rather than assuming that every text-looking field has the same in-memory storage implementation.

```julia
using Test
using CSV
using DataFrames
using Dates

function worked_a()
    text = "id,amount,date
001,2.5,2024-02-29
002,NA,2024-03-01
"
    table = CSV.read(
        IOBuffer(text),
        DataFrame;
        types = Dict(:id => String, :amount => Float64, :date => Date),
        missingstring = "NA",
        dateformat = "yyyy-mm-dd",
        strict = true,
    )
    @test String.(table.id) == ["001", "002"]
    @test table.amount[1] == 2.5
    @test ismissing(table.amount[2])
    @test table.date == [Date(2024, 2, 29), Date(2024, 3, 1)]
    println("Typed CSV table: ", table)
end

worked_a()
```

## Worked case B: reject malformed typed input and preserve quoting

Strict parsing rejects a noninteger value in a declared count column. A separate round trip includes a comma and embedded quotation marks inside string fields. The writer handles the CSV quoting rules, and the parsed output reproduces the original values. This is a value-level round trip; the exported text need not have the same formatting bytes as an arbitrary source file.

```julia
using Test
using CSV
using DataFrames
using Dates

function worked_b()
    @test_throws CSV.Error CSV.read(IOBuffer("count
wrong
"), DataFrame; types = Int, strict = true)
    original = DataFrame(id = ["001", "002"], note = ["contains,comma", "quoted \"value\""])
    output = IOBuffer()
    CSV.write(output, original)
    encoded = String(take!(output))
    restored = CSV.read(IOBuffer(encoded), DataFrame; types = String, strict = true)
    @test String.(restored.id) == original.id
    @test String.(restored.note) == original.note
    println("CSV round-trip preserved 2 authored records")
end

worked_b()
```

## Inference and validation

Inference is useful for exploration, but a production contract should state important types, units and missingness policies. A successful parse does not establish key uniqueness, valid ranges or the correct data grain. Apply those checks after parsing and preserve rejected-row evidence when a repair policy is used.

Do not use a string path when the intended input is literal data. The API distinguishes a source location from a buffer containing text. Likewise, compression, encoding and locale-specific decimal conventions need explicit handling. A field containing a comma may be a quoted value rather than an extra column.

## Diagnose a parsing surprise

Inspect the raw header, delimiter, quoting and type arguments on a small excerpt. Confirm whether the missing marker is part of the agreed source format. A malformed value should not be silently reclassified as valid zero. If permissive parsing is selected, document and inspect its warnings and rejected values using the versioned API contract.

Retain a source checksum or version when a scientific result depends on a file. Record the parser and schema choices alongside it. A later parser version can change inference or warning behavior even when the source bytes remain the same.

The examples establish deterministic parsing and writing behavior for a small authored fixture in the prepared environment. They do not prove that all external CSV files are trustworthy or that inferred schemas are suitable for every application. Keep syntax, data validity and scientific interpretation as separate checks.


## Six investigations

### 1. Preserve a textual ID

Read 001 as a declared string.

**Expected:** Its leading zeros remain.

**Hint:** Identity is not necessarily a measurement.

### 2. Declare missingness

Parse the authored NA amount marker.

**Expected:** The second amount is missing.

**Hint:** Use the agreed source-format policy.

### 3. Reject a wrong type

Parse 1.5 as a strict integer field.

**Expected:** The parser raises its typed-input error.

**Hint:** A decimal value violates this declared schema.

### 4. Retain quoted content

Round-trip a string containing a comma or quotation marks.

**Expected:** The restored field values agree.

**Hint:** Use the CSV writer instead of hand-concatenating fields.

### 5. Handle buffer position

Write to an IOBuffer and then read its contents.

**Expected:** Reset or take the bytes explicitly.

**Hint:** The buffer has state.

### 6. Separate parsing and meaning

A file parses successfully but has duplicate entity IDs.

**Expected:** The relational data contract still needs validation.

**Hint:** Parsing proves only part of the input boundary.

## Primary references

- [CSV 0.10.17 reading source](https://github.com/JuliaData/CSV.jl/blob/v0.10.17/docs/src/reading.md)
- [DataFrames IO](https://dataframes.juliadata.org/stable/man/importing_and_exporting/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
