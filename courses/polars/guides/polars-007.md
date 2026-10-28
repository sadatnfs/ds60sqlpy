# polars-007: Time zones, elapsed time and interval boundaries

## Level and prerequisites

Intermediate. Direct prerequisites: `polars-003`, `polars-004`

**Outcome:** Define time semantics before aggregating a dataset.

## Question and mechanism

A timestamp identifies an instant only when its interpretation is unambiguous. A local clock display can repeat or skip during a daylight-saving transition. Storing a timezone-aware instant in UTC and converting it for display separates elapsed time from the local clock label. A one-hour elapsed interval can span two displayed hour numbers when a region moves its clocks forward.

Conversion and relabeling are different operations. Converting a known instant into another zone preserves the instant. Assigning a zone to a naive timestamp interprets previously ambiguous clock text and needs a policy for repeated or nonexistent times. The first case begins with UTC offsets, so no local-time ambiguity needs guessing. The region is named explicitly rather than inferred from the machine running the lesson.

Windows also need a boundary convention. A half-open interval includes its start and excludes its end. Adjacent periods can then share a boundary without counting the same event twice. This is a useful convention for daily metrics, feature windows and incremental processing, but the scientific question still determines which clock and which cutoff should be used.

## Syntax and data contract

str.to_datetime parses the source timestamp, time_zone="UTC" fixes its timezone representation, and dt.convert_time_zone produces a different display of the same instant. Filtering uses an explicit start comparison and a strict end comparison. Keep timezone-aware Python datetime objects at these boundaries; comparing naive and aware timestamps should not be treated as a harmless coercion.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: A clock change is not a two-hour duration

The two UTC observations are one hour apart. In New York they display as 01:30 and 03:30 on the spring transition date. The test checks elapsed seconds independently from the displayed hour numbers.

**Expected evidence:** Displayed hours are [1, 3], while elapsed time is 3,600 seconds.

```python
import polars as pl


def example_one():
    frame = pl.DataFrame({"stamp": ["2024-03-10T06:30:00+00:00", "2024-03-10T07:30:00+00:00"]})
    parsed = frame.with_columns(pl.col("stamp").str.to_datetime(time_zone="UTC").alias("utc"))
    local = parsed.with_columns(
        pl.col("utc").dt.convert_time_zone("America/New_York").alias("local")
    )
    assert local["local"].dt.hour().to_list() == [1, 3]
    assert (local["utc"][1] - local["utc"][0]).total_seconds() == 3600
    return {"display_hours": [1, 3], "elapsed_seconds": 3600}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Partition events without duplicating the boundary

The interval contains the first two timestamps and excludes the third. The next period begins at that excluded instant. Counts and amounts reconcile across the two groups, making the boundary policy inspectable.

**Expected evidence:** The first period totals 5, the next totals 5, and all three rows occur exactly once.

```python
from datetime import UTC, datetime

import polars as pl


def example_two():
    timestamps = [
        datetime(2024, 1, 1, tzinfo=UTC),
        datetime(2024, 1, 2, tzinfo=UTC),
        datetime(2024, 1, 3, tzinfo=UTC),
    ]
    frame = pl.DataFrame({"time": timestamps, "amount": [2, 3, 5]})
    start, end = timestamps[0], timestamps[2]
    period = frame.filter((pl.col("time") >= start) & (pl.col("time") < end))
    assert period["amount"].sum() == 5
    assert frame.filter(pl.col("time") >= end)["amount"].sum() == 5
    assert period.height + frame.filter(pl.col("time") >= end).height == frame.height
    return {"half_open_total": 5, "next_period_total": 5}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Display another zone

Convert the same UTC observations to a second named timezone.

**Check:** The instants and elapsed seconds stay unchanged.

**Hint:** Change display, not source meaning.


### 2. Explain a naive value

Describe what information is missing from 01:30 without a zone or date.

**Check:** The answer identifies unresolved instant interpretation.

**Hint:** A clock label alone is insufficient.


### 3. Test the end boundary

Add an observation exactly equal to end.

**Check:** It belongs to the following period.

**Hint:** Keep the end comparison strict.


### 4. Test a zero-length window

Set start equal to end.

**Check:** The half-open window is empty.

**Hint:** Both inequalities must hold.


### 5. Compare duration definitions

Explain the difference between one calendar day and 24 elapsed hours around a clock change.

**Check:** The answer allows a calendar day with a different elapsed duration.

**Hint:** Civil calendars and durations answer different questions.


### 6. Add a late arrival

Give an event an old event time but a later ingestion time.

**Check:** The two timestamps remain separate.

**Hint:** Display conversion does not solve data availability.


## Diagnose errors and misleading results

If a duration differs by an hour, inspect timezone interpretation before adding a correction constant. If rows appear in two adjacent reports, check both endpoint operators. If an incremental job misses late records, its event-time window alone is not an ingestion policy. Print UTC instants, local displays and the exact window boundaries while diagnosing the issue.

## Transfer to independent work

Define time semantics before aggregating a dataset. Use an explicit zone and interval convention, test the boundary observations and retain separate event and availability timestamps. Apply those rules consistently across training, dashboards and incremental data products.

## Primary references

- [Polars documentation: Time zones, elapsed time and interval boundaries](https://docs.pola.rs/user-guide/transformations/time-series/timezones/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-007`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
