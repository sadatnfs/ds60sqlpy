# julia-016: explained reference

The executable reference is `julia-016_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Before every join, state the expected cardinality and reconcile totals afterward. In the worked example two entities with weights 100 and 200 meet two observations for entity 1, which fans the left row out. `validate` turns the uniqueness assumption into an error, preaggregation restores one row per entity, and `matchmissing` must be chosen explicitly.

## 1. Trace the duplicate pair

Join multiplicity can inflate a sum even when every individual match is syntactically valid.

**Expected observation:** The left entity 1 weight appears twice.

**Why it holds here:** Entity 1 matches two observation rows and entity 2 matches none, so the left join has 3 rows and weight total 100 + 100 + 200 = 400.

**Plausible wrong approach:** Summing `weight` after the join and reporting 400 double counts entity 1, even though every pair matched correctly by key.

**How to verify:** Example A asserts `nrow(duplicated) == 3` and `sum(duplicated.weight) == 400`.

## 2. Enforce a lookup contract

An executable cardinality check prevents an unintended many-to-many relationship from passing silently.

**Expected observation:** The duplicate-key input is rejected.

**Why it holds here:** `validate = (true, true)` requires unique keys on both sides; the right side has id 1 twice, so `leftjoin` throws `ArgumentError`.

**Plausible wrong approach:** Relying on a visual check of a small table misses duplicates that appear only in production extracts.

**How to verify:** Example A asserts the `ArgumentError`; the reference checks a validated join on unique keys returning 2 rows.

## 3. Aggregate at a declared grain

Preaggregation is a semantic decision, not a universal repair for duplicates.

**Expected observation:** Two entity rows and weight total 300 are preserved.

**Why it holds here:** Summing observations per id first gives one row with value_total 30, so the validated join keeps 2 rows and weight total 300.

**Plausible wrong approach:** Taking the first observation per id also removes duplicates but silently discards the value 20.

**How to verify:** Example A asserts `nrow(reconciled) == 2`, `sum(reconciled.weight) == 300` and the value total 30.

## 4. Choose missing-key behavior

The policy must reflect the data model and should be reported with excluded counts.

**Expected observation:** The fixture yields 1 or 0 matched rows.

**Why it holds here:** With `matchmissing = :equal` the two missing ids pair to give 1 row; with `:notequal` they never match, giving 0 rows.

**Plausible wrong approach:** Picking `:equal` because it returns more rows assumes that two unknown ids refer to the same entity.

**How to verify:** Example B asserts both counts and that the default `innerjoin` throws `ArgumentError` on missing keys.

## 5. Inspect unmatched keys

A row-count total is not enough to explain which entities failed to match.

**Expected observation:** The fixture exposes left-only, both and right-only rows.

**Why it holds here:** `outerjoin` with `source = :origin` labels id 1 `left_only`, id 2 `both` and id 3 `right_only`.

**Plausible wrong approach:** Comparing only `nrow` before and after the join cannot show which ids were lost or added.

**How to verify:** The reference asserts `result.id == [1, 2, 3]` and the three origin strings, plus `antijoin` returning one row.

## 6. Avoid cosmetic deduplication

Distinct operations can conceal a modeling error and need their own justified rule.

**Expected observation:** The scientific meaning remains unresolved.

**Why it holds here:** `unique` after a fanout join removes identical rows but leaves the question of why the right side had several rows per key.

**Plausible wrong approach:** Deduplicating the output makes the total look right on this fixture while a later fixture with differing values still inflates it.

**How to verify:** Reconcile the left-side `sum(left.x) == 30` before and after the join, and record which key produced duplicates.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-016: all reference checks passed`:

```julia
function exercise_checks()
    left = DataFrame(id = [1, 2], x = [10, 20])
    right = DataFrame(id = [2, 3], y = [30, 40])
    result = sort(outerjoin(left, right; on = :id, source = :origin), :id)
    @test result.id == [1, 2, 3]
    @test string.(result.origin) == ["left_only", "both", "right_only"]
    @test nrow(innerjoin(left, right; on = :id)) == 1
    @test nrow(antijoin(left, right; on = :id)) == 1
    @test sum(left.x) == 30
    @test nrow(leftjoin(left, right; on = :id, validate = (true, true))) == 2
end
```
