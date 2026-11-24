# julia-032: explained reference

The executable reference is `julia-032_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`analyze` reads the eight-row `SENSOR_CSV` with declared types, runs `validate_sensor` for row count, unique ids, finite values, known splits, feature and label availability and split counts of 4, 2 and 2, then fits ridge lines on the four training rows. It selects the penalty by development MSE and writes a memo with the fixture SHA-256.

## 1. Audit the grain

The eight-row contract fixes grain and denominators; repeated entities in real data would need additional grouping.

**Expected observation:** One synthetic prediction record with declared availability evidence.

**Why it holds here:** Each row has a unique id such as `s01` and represents one synthetic prediction with its own feature and label availability dates.

**Plausible wrong approach:** Treating the ids as entities that may repeat would require grouping rules that this fixture does not define.

**How to verify:** The reference duplicates `id[8]` and asserts `validate_sensor` throws `ArgumentError`.

## 2. Reproduce the selection

The declared rule chooses the minimum development MSE in fixed candidate order.

**Expected observation:** Penalty 2 is selected.

**Why it holds here:** The training rows are the same x and y values as lesson julia-021, so the four penalties give the same development errors and penalty 2 wins.

**Plausible wrong approach:** Choosing by final error reuses the assessment rows for selection and makes the reported final MSE optimistic.

**How to verify:** Worked example A asserts `result.memo["penalty"] == 2` and `development_mse ≈ 1/98`.

## 3. Verify final arithmetic

This independent rational calculation verifies the reported floating result.

**Expected observation:** Residuals are -1/7 and -2/7; MSE is 5/98.

**Why it holds here:** Predictions 90/7 and 103/7 against 13 and 15 leave residuals -1/7 and -2/7, whose squares 1/49 and 4/49 average to 5/98.

**Plausible wrong approach:** Averaging the absolute residuals gives 3/14, a different metric from the mean squared error stored in the memo.

**How to verify:** Example A asserts `result.memo["final_mse"] ≈ 5/98`; compute the fractions by hand beside it.

## 4. Inject information leakage

A future-known feature cannot enter the historical decision under the declared contract.

**Expected observation:** The data validator rejects the fixture.

**Why it holds here:** Setting row 7's feature date to 2024-02-01, after its prediction date 2024-01-07, breaks `feature_available_at .<= prediction_at`.

**Plausible wrong approach:** Checking only that dates parse lets a future feature enter the model and makes the historical evaluation impossible in practice.

**How to verify:** The reference asserts `ArgumentError` for that change and for a label date after the 2024-01-10 cutoff.

## 5. Inspect accessible evidence

Descriptions explain scope; exact tables support inspection without relying on visual position.

**Expected observation:** The values and IDs must match exactly.

**Why it holds here:** The Plotly table and markers come from the same `final` rows and `predictions`, so ids, observations and predictions must match exactly.

**Plausible wrong approach:** Reading values off the chart by eye introduces rounding and misses an id paired with the wrong row.

**How to verify:** Compare each table row with `result.final` and `result.predictions` programmatically.

## 6. Write the decision memo

Require representative sampling, uncertainty, domain validation and monitoring before making a deployment claim.

**Expected observation:** Synthetic computation passes; deployment is not justified.

**Why it holds here:** The synthetic workflow passes all checks, but two final rows and a hand-built fixture cannot support a deployment decision.

**Plausible wrong approach:** Writing that the model is ready because the final MSE is small ignores sample size, selection history and domain validity.

**How to verify:** Confirm the memo's decision text says deployment evidence is insufficient and that `fixture_sha256` matches `bytes2hex(sha256(SENSOR_CSV))`.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-032: all reference checks passed`:

```julia
function exercise_checks()
    table = load_sensor()
    duplicate = copy(table)
    duplicate.id[8] = duplicate.id[1]
    @test_throws ArgumentError validate_sensor(duplicate)
    future = copy(table)
    future.feature_available_at[7] = Date(2024, 2, 1)
    @test_throws ArgumentError validate_sensor(future)
    late = copy(table)
    late.label_available_at[8] = Date(2024, 2, 1)
    @test_throws ArgumentError validate_sensor(late)
    invalid = copy(table)
    invalid.x[1] = NaN
    @test_throws ArgumentError validate_sensor(invalid)
    @test_throws ArgumentError validate_sensor(table[1:7, :])
    @test analyze().memo["fixture_sha256"] == bytes2hex(sha256(SENSOR_CSV))
end
```
