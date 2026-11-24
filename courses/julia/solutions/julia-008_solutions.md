# julia-008: explained reference

The executable reference is `julia-008_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Pick each container for the question it answers. Tuples hold fixed positional fields, named tuples label them, a count dictionary keeps multiplicity that a `Set` drops, `haskey` separates absence from a stored zero, and dictionary keys follow `isequal`. Presentation order is imposed with `sort`, never inherited from hashing.

## 1. Make one tuple element

The tuple syntax distinguishes a one-field collection from the scalar value.

**Expected observation:** Use `(7,)`, including its comma.

**Why it holds here:** `(7,)` is a one-element tuple; the trailing comma is what makes it a tuple, since `(7)` is just the integer 7.

**Plausible wrong approach:** Writing `(7)` and calling `length` returns 1 by accident for an integer, hiding that the value is not a collection.

**How to verify:** Check `typeof((7,)) == Tuple{Int}` and `typeof((7)) == Int`.

## 2. Name a returned record

The representation makes a small fixed schema inspectable.

**Expected observation:** Callers can access fields by their names.

**Why it holds here:** Returning `(id = 1, score = 0.8, eligible = true)` lets callers write `result.score` instead of remembering that score is second.

**Plausible wrong approach:** Returning a plain tuple and reading `result[2]` breaks silently if a field is later inserted before score.

**How to verify:** Access each field by name and assert `keys(result) == (:id, :score, :eligible)`.

## 3. Preserve multiplicity

Deduplication intentionally discards multiplicity and can change a scientific denominator.

**Expected observation:** Counts are 1 and 2 while the set has two distinct labels.

**Why it holds here:** Counting `a`, `b`, `b` gives `a => 1` and `b => 2`, while `Set(["a", "b", "b"])` keeps only two members.

**Plausible wrong approach:** Converting to a set first and then counting reports one of each label, which halves the weight of `b`.

**How to verify:** Assert the count dictionary has `b => 2` and `length(Set(labels)) == 2`.

## 4. Control presentation order

Stable presentation requires an explicit contract rather than an incidental implementation order.

**Expected observation:** The report follows the chosen ordering rule.

**Why it holds here:** Iterating `sort(collect(keys(d)))` gives a fixed order regardless of how the dictionary hashed its keys.

**Plausible wrong approach:** Printing `d` directly and pasting it into a report assumes insertion order, which `Dict` does not promise.

**How to verify:** Print the report twice with differently built dictionaries holding the same pairs and compare the transcripts.

## 5. Separate absent and zero

Only use an absent-to-zero convention when the measurement contract justifies it.

**Expected observation:** haskey distinguishes them.

**Why it holds here:** `Dict("a" => 0)` stores a real zero for `a`, while `b` is absent, so `haskey` gives true and false.

**Plausible wrong approach:** Reading with `get(values, key, 0)` reports both as 0 and loses the difference between measured zero and no record.

**How to verify:** The reference checks `haskey`, `get(values, "b", -1) == -1` and `@test_throws KeyError values["b"]`.

## 6. Inspect special keys

Dictionary equality semantics should match the application meaning of the keys.

**Expected observation:** NaN is retrievable and the signed zeros remain distinct in this fixture.

**Why it holds here:** Keys use `isequal`, so `NaN` finds itself and `0.0` and `-0.0` are different keys, leaving three entries.

**Plausible wrong approach:** Expecting `==` semantics predicts that NaN cannot be retrieved and that the signed zeros collapse into two entries.

**How to verify:** The reference asserts `special[NaN] == "present"` and `length(special) == 3`.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-008: all reference checks passed`:

Lookup behavior differs by method. `haskey` asks without failing, `get` supplies the fallback -1, and direct indexing of a missing key raises `KeyError`, which is the right signal when the key must exist. The `special` dictionary uses `isequal` for keys, so NaN finds itself and `0.0` and `-0.0` stay separate entries, giving length 3. Code that compares keys with `==` would merge the zeros and lose NaN.

```julia
function exercise_checks()
    values = Dict("a" => 0)
    @test haskey(values, "a")
    @test !haskey(values, "b")
    @test get(values, "b", -1) == -1
    @test_throws KeyError values["b"]
    special = Dict(NaN => "present", 0.0 => "positive", -0.0 => "negative")
    @test special[NaN] == "present"
    @test length(special) == 3
end
```
