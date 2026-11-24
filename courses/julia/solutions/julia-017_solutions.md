# julia-017: explained reference

The executable reference is `julia-017_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Write the schema before reading. Worked example A passes `types` for `id`, `amount` and `date`, `missingstring = "NA"`, a date format and `strict = true` to `CSV.read`, so every column has a declared meaning. Round trips use `CSV.write` into an `IOBuffer` and `take!` to collect the bytes, and relational checks come after parsing.

## 1. Preserve a textual ID

Numeric-looking keys can lose meaning when inference converts them to integers.

**Expected observation:** Its leading zeros remain.

**Why it holds here:** Declaring `:id => String` keeps the text `001` exactly, so `String.(table.id)` equals `["001", "002"]`.

**Plausible wrong approach:** Letting CSV.jl infer the column type reads `001` as the integer 1, and a later join against string keys then matches nothing.

**How to verify:** Example A asserts the restored ids; print `eltype(table.id)` to see a string type rather than `Int`.

## 2. Declare missingness

A missing marker should not silently become a valid numeric zero.

**Expected observation:** The second amount is missing.

**Why it holds here:** `missingstring = "NA"` tells the parser that `NA` means unknown, so the second amount is `missing` and the column stays `Float64` otherwise.

**Plausible wrong approach:** Replacing NA with 0 in a text editor before reading turns an absent amount into a recorded zero dollars.

**How to verify:** Example A asserts `ismissing(table.amount[2])` and `table.amount[1] == 2.5`.

## 3. Reject a wrong type

Changing the schema or using a repair policy requires an explicit decision.

**Expected observation:** The parser raises its typed-input error.

**Why it holds here:** With `types = Int` and `strict = true`, the value `1.5` cannot be parsed as an integer, so `CSV.read` raises `CSV.Error`.

**Plausible wrong approach:** Dropping `strict = true` lets the parser substitute `missing` for the bad cell, so the schema violation becomes an apparently ordinary gap.

**How to verify:** The reference asserts `@test_throws CSV.Error` for this input and a passing strict read of `1` and `2` that sums to 3.

## 4. Retain quoted content

Correct quoting preserves structure without promising byte-identical formatting to every original file.

**Expected observation:** The restored field values agree.

**Why it holds here:** `CSV.write` quotes fields that contain the delimiter or quotation marks, so `contains,comma` and `quoted "value"` return intact.

**Plausible wrong approach:** Building lines with `join(fields, ",")` splits `contains,comma` into two columns on reread.

**How to verify:** Example B asserts `String.(restored.note) == original.note` after the round trip.

## 5. Handle buffer position

An empty read after a write can reflect the current position rather than missing source data.

**Expected observation:** Reset or take the bytes explicitly.

**Why it holds here:** After `CSV.write(output, ...)` the buffer position sits at the end, so `take!(output)` is the call that returns all written bytes.

**Plausible wrong approach:** Calling `read(output, String)` right after writing returns an empty string, which looks like a failed export.

**How to verify:** Compare `String(take!(output))` with a fresh `read` at the end position and note which one is empty.

## 6. Separate parsing and meaning

Types and delimiters do not establish grain, units or scientific validity.

**Expected observation:** The relational data contract still needs validation.

**Why it holds here:** A file can parse cleanly yet contain the id `001` twice, which breaks a one-row-per-entity assumption that types cannot express.

**Plausible wrong approach:** Treating a successful `CSV.read` as full validation lets duplicate keys fan out later joins.

**How to verify:** Check `length(unique(table.id)) == nrow(table)` after parsing and report any duplicated ids.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-017: all reference checks passed`:

Parsing with `types = Int` and `strict = true` reads the two integer rows and sums them to 3, and the same settings turn `1.5` into a `CSV.Error` instead of a silent conversion. The date lines show that 2024-02-29 is a valid leap day while 2023-02-29 raises `ArgumentError`, so a declared format catches impossible dates at the boundary.

```julia
function exercise_checks()
    table = CSV.read(IOBuffer("value
1
2
"), DataFrame; types = Int, strict = true)
    @test sum(table.value) == 3
    @test nrow(table) == 2
    @test names(table) == ["value"]
    @test_throws CSV.Error CSV.read(IOBuffer("value
1.5
"), DataFrame; types = Int, strict = true)
    @test Date("2024-02-29", dateformat"yyyy-mm-dd") == Date(2024, 2, 29)
    @test_throws ArgumentError Date("2023-02-29", dateformat"yyyy-mm-dd")
end
```
