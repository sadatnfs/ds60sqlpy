# julia-015: explained reference

The executable reference is `julia-015_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Track three things through every DataFrames step: column names, row counts and storage sharing. `select` with `ByRow` and `copycols = true` builds a new named column, `input[!, :score]` returns the stored column while `input[:, :score]` copies it, and grouped summaries pair `observed_mean` with row and observed counts.

## 1. Name the derived field

Names and shape are part of the resulting schema.

**Expected observation:** The output column contains 1, 2 and 3 under the explicit name `scaled`.

**Why it holds here:** `:score => ByRow(x -> x / 10) => :scaled` applies the function to each of 10, 20 and 30 and names the result `scaled`.

**Plausible wrong approach:** Writing `:score => (x -> x / 10)` without a name produces an automatic column name that downstream code has to guess.

**How to verify:** Example A asserts `names(selected) == ["id", "scaled"]` and `selected.scaled == [1, 2, 3]`.

## 2. Observe a shared column

A caller must request a copy when independent storage is required.

**Expected observation:** The source DataFrame changes.

**Why it holds here:** `input[!, :score]` returns the column object stored in the table, so `alias[1] = 99` makes `input.score[1]` equal 99.

**Plausible wrong approach:** Treating `!` as a harmless spelling of `:` assumes a copy, which leads to accidental edits of the source table.

**How to verify:** Example A asserts `input.score[1] == 99` after the alias write.

## 3. Retain a column snapshot

A snapshot is useful for comparison and provenance when future mutation is possible.

**Expected observation:** The copied values remain unchanged.

**Why it holds here:** `input[:, :score]` copies the column, so the snapshot still holds 10 after the alias write.

**Plausible wrong approach:** Checking only that the snapshot equals the column at creation time cannot reveal sharing; the test must mutate the source afterward.

**How to verify:** Example A asserts `snapshot[1] == 10`; the reference checks `select(...; copycols = true).id !== input.id`.

## 4. Report group coverage

Row accounting remains necessary after grouping.

**Expected observation:** It reports 2 rows, 1 observed score and mean 1.

**Why it holds here:** Group a has scores 1 and missing, so `nrow` is 2, the observed count is 1 and `observed_mean` gives 1.0.

**Plausible wrong approach:** Reporting only `mean_score` makes group a look as well supported as group b, which has two observed scores.

**How to verify:** Example B asserts `n_rows == [2, 2]`, `n_observed == [1, 2]` and `mean_score == [1.0, 4.0]`.

## 5. Handle an all-missing group

A fabricated zero could change later model or business decisions.

**Expected observation:** The result is missing.

**Why it holds here:** With every score missing, the observed set is empty and `observed_mean` returns `missing` rather than a number.

**Plausible wrong approach:** Using `mean(skipmissing(x))` directly throws on the empty iterator or, with a default, invents a zero.

**How to verify:** The reference asserts `ismissing(observed_mean([missing]))`.

## 6. Interpret a mean of means

Group-level and row-level summaries represent different populations.

**Expected observation:** The answers can differ.

**Why it holds here:** The unweighted mean of group means 1.0 and 4.0 is 2.5; weighting by observed counts 1 and 2 gives (1 + 8) / 3 = 3.0.

**Plausible wrong approach:** Averaging group means without weights and calling it the overall mean treats one observation in group a like two in group b.

**How to verify:** Compute both values from the summary table and compare 3.0 with `mean([1, 3, 5])`, the row-level observed mean.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-015: all reference checks passed`:

`observed_mean([missing])` returns missing because no observed value remains. The `DataFrame` lines confirm that `transform` returns a new table with a `square` column of `[4, 16]` while the input keeps only `id` and `x` with two rows. The final line checks that `select` with `copycols = true` gives a fresh `id` vector, so writing to the result cannot alter `input`.

```julia
function exercise_checks()
    @test ismissing(observed_mean([missing]))
    input = DataFrame(id = [1, 2], x = [2, 4])
    changed = transform(input, :x => ByRow(x -> x^2) => :square)
    @test changed.square == [4, 16]
    @test names(input) == ["id", "x"]
    @test nrow(input) == 2
    @test ncol(changed) == 3
    @test select(input, :id; copycols = true).id !== input.id
end
```
