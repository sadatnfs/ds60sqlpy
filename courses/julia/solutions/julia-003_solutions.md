# julia-003: explained reference

The executable reference is `julia-003_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Keep three units apart: bytes indexed by `String`, characters returned by iteration, and graphemes a reader sees. Move between positions with `nextind` rather than `+ 1`, count with the function that matches the unit, normalize only by deliberate choice, and handle the empty string before asking for a first character.

## 1. Advance safely

Adding one to a valid byte index can enter a multibyte character.

**Expected observation:** nextind returns 3.

**Why it holds here:** In `"éλ"` the letter é occupies bytes 1 and 2 in UTF-8, so `nextind("éλ", 1)` returns 3, where λ begins.

**Plausible wrong approach:** Using index 2 as the second character lands inside é, and `"éλ"[2]` throws `StringIndexError` instead of returning λ.

**How to verify:** The reference asserts `nextind("éλ", 1) == 3`; also print `ncodeunits("éλ")`, which is 4, beside `length("éλ")`, which is 2.

## 2. Count visible units

A visible text unit can contain multiple code points.

**Expected observation:** Two characters form one grapheme.

**Why it holds here:** `"e\u0301"` stores e followed by a combining acute accent: two characters that render as one visible grapheme.

**Plausible wrong approach:** Reporting `length` as the visible count says 2 for a single displayed letter, which miscounts any text with combining marks.

**How to verify:** Compare `length(s)` with `length(collect(Unicode.graphemes(s)))` after `using Unicode`; expect 2 and 1.

## 3. Normalize deliberately

Canonical equivalence is a specific Unicode relation, not arbitrary semantic equivalence.

**Expected observation:** It matches the precomposed form.

**Why it holds here:** NFC composes e plus U+0301 into the single code point U+00E9, so the normalized string equals the precomposed é.

**Plausible wrong approach:** Comparing the raw strings with `==` reports them unequal and could lead to duplicate keys for what readers consider the same word.

**How to verify:** Assert `Unicode.normalize("e\u0301", :NFC) == "\u00e9"` and keep the original string if provenance must be exact.

## 4. Handle empty text

A parser or display routine needs a documented empty-input policy.

**Expected observation:** The empty case is identified explicitly.

**Why it holds here:** `""` has no characters, so `first("")` fails; testing `isempty` first lets the routine apply its stated empty policy.

**Plausible wrong approach:** Assuming index 1 always exists produces an indexing error deep inside a parser rather than a clear message about empty input.

**How to verify:** The reference checks `isempty("")`; add a branch that returns `nothing` for empty input and test both branches.

## 5. Choose offset units

Offsets are only reproducible against the same representation and indexing contract.

**Expected observation:** Name byte, character or grapheme units and the text version.

**Why it holds here:** Citation offsets depend on the unit, since the same passage starting after é sits at byte 3 but character 2.

**Plausible wrong approach:** Storing bare integers without naming the unit lets a reader slice bytes with character counts and cut a character in half.

**How to verify:** Record each offset with its unit and text version, then reslice with `nextind` or `thisind` and confirm the cited text reappears.

## 6. Add a counterexample

A representative boundary fixture checks a mechanism that ASCII alone cannot exercise.

**Expected observation:** The invalid byte-index assumption becomes visible.

**Why it holds here:** An algorithm that steps by `i + 1` works on `"ASCII"` because there `ncodeunits` equals `length`; multibyte text breaks that equality.

**Plausible wrong approach:** Testing only with ASCII fixtures passes every case while the byte-stepping bug remains, since every character there is one byte.

**How to verify:** Keep `ncodeunits("ASCII") == length("ASCII")` as the reference does, and add `@test_throws StringIndexError "éλ"[2]` as the counterexample.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-003: all reference checks passed`:

These six lines separate characters from bytes. `nextind("éλ", 1) == 3` holds because é occupies two code units, so the next valid index skips index 2. The ASCII comparison then shows the one case where `length` and `ncodeunits` agree. `join` and `string` build text without manual spacing, and `lowercase` normalizes a label without changing its meaning. If an edit makes `nextind` return 2, it is treating byte offsets as character positions.

```julia
function exercise_checks()
    @test isempty("")
    @test nextind("éλ", 1) == 3
    @test lowercase("DATA") == "data"
    @test join(["data", "science"], " ") == "data science"
    @test string("score=", 3) == "score=3"
    @test ncodeunits("ASCII") == length("ASCII")
end
```
