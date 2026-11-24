# julia-018: explained reference

The executable reference is `julia-018_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Calendar periods and fixed durations are different types: `Month(1)` clamps to the end of a shorter month while `Day(30)` counts days. `historical_value` keeps only rows for the requested entity whose event time and availability time are both at or before the lookup time, then takes the last row ordered by event, availability and version.

## 1. Choose a calendar window

The window definition changes which observations belong to a period.

**Expected observation:** They end on February 29 and March 1.

**Why it holds here:** Starting at 2024-01-31, `Month(1)` clamps to the leap-year end of February, 2024-02-29, while `Day(30)` lands on 2024-03-01.

**Plausible wrong approach:** Using `Day(30)` as a month makes reporting windows drift and, here, skips the last day of February entirely.

**How to verify:** Example A asserts both dates; the reference also checks `Date(2024, 2, 28) + Day(1) == Date(2024, 2, 29)`.

## 2. Inspect repeated month addition

Calendar operations should follow the intended business rule rather than an assumed arithmetic identity.

**Expected observation:** The fixture ends on March 29 versus March 31.

**Why it holds here:** Adding one month twice goes January 31 to February 29 and then to March 29, while `Month(2)` jumps straight to March 31.

**Plausible wrong approach:** Assuming `start + Month(1) + Month(1)` and `start + Month(2)` always agree ignores that the first form stores a clamped intermediate.

**How to verify:** Example A asserts `february + Month(1) == Date(2024, 3, 29)` and `start + Month(2) == Date(2024, 3, 31)`.

## 3. Exclude a future correction

A correction about a past event can still be future information.

**Expected observation:** The available value is 10.

**Why it holds here:** On January 3, the version 2 row is not yet available because its availability time is January 4, so only the value 10 qualifies.

**Plausible wrong approach:** Filtering on event time alone returns 20, using a correction that nobody could have known on January 3.

**How to verify:** Example B asserts `historical_value(rows, "a", DateTime(2024, 1, 3)) == 10`.

## 4. State cutoff equality

Real ingestion timing may require another rule, which must be documented and tested.

**Expected observation:** The inclusive cutoff returns the row whose availability time equals the lookup time.

**Why it holds here:** The filter uses `row.available <= at`, so at exactly January 4 the version 2 row is eligible and the result is 20.

**Plausible wrong approach:** Switching to `<` without saying so moves every boundary lookup one row earlier and changes the training features.

**How to verify:** The reference asserts the single-row case returns `missing` on January 3 and 7 on January 4.

## 5. Preserve entity identity

An information boundary also needs the correct relational key.

**Expected observation:** The result is missing.

**Why it holds here:** Entity `b` has no rows, so the eligible list is empty and the function returns `missing`.

**Plausible wrong approach:** Dropping the entity condition would return the latest value of entity `a`, assigning one subject's history to another.

**How to verify:** Example B asserts `ismissing(historical_value(rows, "b", DateTime(2024, 1, 5)))`.

## 6. Handle local civil time

Use a separately prepared timezone-aware policy rather than silently labeling a local clock value as UTC.

**Expected observation:** The standard fixture does not resolve it.

**Why it holds here:** A `DateTime` from the Dates standard library has no zone, so a local time repeated by a daylight-saving change is just two equal-looking values.

**Plausible wrong approach:** Treating local clock readings as UTC shifts availability by the offset and can reorder events across the change.

**How to verify:** Record the source zone, convert with a timezone-aware package outside this fixture and test both occurrences of the repeated hour.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-018: all reference checks passed`:

```julia
function exercise_checks()
    @test Date(2024, 2, 28) + Day(1) == Date(2024, 2, 29)
    @test Date(2023, 2, 28) + Day(1) == Date(2023, 3, 1)
    @test DateTime(2024, 1, 1, 1) - DateTime(2024, 1, 1) == Millisecond(3_600_000)
    @test ismissing(historical_value(NamedTuple[], "a", DateTime(2024, 1, 1)))
    row = (
        entity = "a",
        event = DateTime(2024, 1, 2),
        available = DateTime(2024, 1, 4),
        version = 1,
        value = 7,
    )
    @test ismissing(historical_value([row], "a", DateTime(2024, 1, 3)))
    @test historical_value([row], "a", DateTime(2024, 1, 4)) == 7
end
```
