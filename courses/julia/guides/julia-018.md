# julia-018: Dates, availability time and historical features

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-017`.

Use calendar arithmetic deliberately and reconstruct features using both event and availability time.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Calendar time is not one uniform integer

A date identifies a calendar day, while a datetime adds a clock value. A calendar month does not have a fixed number of days. Adding a month and adding thirty days can therefore produce different results. The difference is meaningful for billing periods, cohorts and scientific observation windows.

Julia's standard Dates types do not automatically attach an IANA time zone or resolve daylight-saving ambiguity. The fixture datetimes in this unit are explicitly interpreted as UTC by the application contract. They are not a demonstration of timezone conversion. A real local-time workflow needs a separately prepared timezone-aware approach and a policy for ambiguous or nonexistent local times.

Historical data also has more than one relevant timestamp. Event time records when something happened. Availability time records when a decision-maker could use that information. A later correction can describe an earlier event without having been available to the original decision.

## Worked case A: month arithmetic and clamping

The first program contrasts a calendar month with a fixed day count. It also shows how clamping an end-of-month date can make two successive month additions differ from adding two months at once. The intermediate February result is stored explicitly. A chained `start + Month(1) + Month(1)` is an n-argument addition in Julia and combines the periods before applying them, so it gives March 31. This is calendar behavior, not a floating-point error. A business or scientific window must state its intended rule.

```julia
using Test
using Dates

function historical_value(rows, entity, at)
    eligible =
        [row for row in rows if row.entity == entity && row.event <= at && row.available <= at]
    isempty(eligible) && return missing
    ordered = sort(eligible; by = row -> (row.event, row.available, row.version))
    return last(ordered).value
end

function worked_a()
    start = Date(2024, 1, 31)
    @test start + Month(1) == Date(2024, 2, 29)
    @test start + Day(30) == Date(2024, 3, 1)
    february = start + Month(1)
    @test february + Month(1) == Date(2024, 3, 29)
    @test start + Month(1) + Month(1) == Date(2024, 3, 31)
    @test start + Month(2) == Date(2024, 3, 31)
    println("Calendar month and fixed days differ")
end

worked_a()
```

## Worked case B: choose an available historical value

The feature ledger contains a measurement and two later versions. The lookup requires both event and availability time to be no later than the request. It then chooses the latest eligible version using an explicit event/availability/version ordering. A request before the correction is published receives the earlier information, even though the correction refers to a past event.

```julia
using Test
using Dates

function historical_value(rows, entity, at)
    eligible =
        [row for row in rows if row.entity == entity && row.event <= at && row.available <= at]
    isempty(eligible) && return missing
    ordered = sort(eligible; by = row -> (row.event, row.available, row.version))
    return last(ordered).value
end

function worked_b()
    rows = [
        (
            entity = "a",
            event = DateTime(2024, 1, 1),
            available = DateTime(2024, 1, 1),
            version = 1,
            value = 10,
        ),
        (
            entity = "a",
            event = DateTime(2024, 1, 2),
            available = DateTime(2024, 1, 4),
            version = 2,
            value = 20,
        ),
        (
            entity = "a",
            event = DateTime(2024, 1, 2),
            available = DateTime(2024, 1, 5),
            version = 3,
            value = 25,
        ),
    ]
    @test historical_value(rows, "a", DateTime(2024, 1, 3)) == 10
    @test historical_value(rows, "a", DateTime(2024, 1, 4)) == 20
    @test historical_value(rows, "a", DateTime(2024, 1, 5)) == 25
    @test ismissing(historical_value(rows, "b", DateTime(2024, 1, 5)))
    println("Historical values: 10, 20, 25 at the declared cutoffs")
end

worked_b()
```

## Define boundaries and tie rules

Specify whether a cutoff is inclusive. A value published exactly at a decision timestamp may or may not be usable under a real ingestion process, but the policy must be consistent. The small reference uses inclusive comparisons and an explicit version number to resolve ties. A real pipeline may need transaction or ingestion sequence information as well.

Use stable entity identifiers in addition to timestamps. A latest-row lookup without an entity restriction can mix unrelated subjects. A duplicate or contradictory version should be diagnosed rather than hidden by whichever row happens to sort last.

## Diagnose leakage

If a historical model performs suspiciously well, inspect whether features or labels were reconstructed from their current corrected state. Event-time filtering alone can admit information published after the decision. Preserve source versions and availability evidence so the historical feature table can be audited.

A correct point-in-time lookup does not by itself establish that a feature is causal, valid or appropriate for the target. It establishes an information boundary under the recorded timestamps and policy. Delayed labels and incomplete event feeds still require their own treatment.

The examples use literal dates and a tiny authored ledger. They do not connect to a live feature store or certify the accuracy of real timestamps. They provide an executable contract that later modeling and capstone units can preserve when building a reproducible data workflow.


## Six investigations

### 1. Choose a calendar window

Compare one month with thirty days from January 31 in the fixture.

**Expected:** They end on February 29 and March 1.

**Hint:** A month is not a fixed day duration.

### 2. Inspect repeated month addition

Compare two successive month additions with one two-month addition.

**Expected:** The fixture ends on March 29 versus March 31.

**Hint:** End-of-month clamping affects the intermediate state.

### 3. Exclude a future correction

Look up the feature on January 3.

**Expected:** The available value is 10.

**Hint:** Filter availability as well as event time.

### 4. State cutoff equality

Look up at the exact availability timestamp.

**Expected:** The inclusive fixture admits the row.

**Hint:** Use the declared boundary policy.

### 5. Preserve entity identity

Look up an absent entity.

**Expected:** The result is missing.

**Hint:** Do not choose the latest row from another entity.

### 6. Handle local civil time

Receive a daylight-saving-ambiguous local timestamp.

**Expected:** The standard fixture does not resolve it.

**Hint:** Dates alone does not supply timezone identity.

## Primary references

- [Julia Dates](https://docs.julialang.org/en/v1/stdlib/Dates/)
- [Existing point-in-time data workflows](../../../python/professional/README.md)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
