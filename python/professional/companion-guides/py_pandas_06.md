# Timezones, DST, and Calendar Boundaries

**Stable ID:** `python-pandas-06`. This lesson develops the distinction between
an instant, a displayed clock reading and a business calendar period. Allow
about three hours for reading, prediction, implementation and verification.

## How to run this lesson

Run `./classroom`, choose **Python** in `/classroom`, and open this unit. Read
the capability notice, paste the complete learner script into the coding pad,
save and Run. The Docker Python environment supplies pandas and timezone data.
Windows learners use the same launcher in WSL 2. All timestamps are original
inline fixtures; nothing is downloaded or read from your computer's calendar.

The opening script runs two complete worked examples. Its six task functions
remain unimplemented until you write them and explicitly call them. Keep the
imports and fixture construction in the saved source because every browser Run
starts a fresh process. Your code, notes and saved output live in the Docker
learning volume. A new process does not recover variables from an earlier Run.
Inspect the actual output and first exception before comparing a separate
reference answer. Passing the demonstrations does not prove the tasks are done.

An optional prepared contributor environment can execute
`uv run --no-sync python python/professional/lessons/py_pandas_06.py` from the
repository root. That host process has its own checkout-local files; it does
not read or update the Docker browser's saved volume. See
[classroom usage](../../../docs/classroom-experience.md) and the optional
[contributor setup](../../../CONTRIBUTING.md) for their different boundaries.

## Level and prerequisites

- **Level:** Advanced.
- **Direct prerequisite:** `python-21`, [companion guide](../../ds-60day/companion-guides/day21_time_series_pandas.md).
- **Direct prerequisite:** `python-pandas-02`, [companion guide](py_pandas_02.md).
- **Direct prerequisite:** `python-data-02`, [companion guide](py_data_02_exact_values_time_text.md).
- **Artifacts:** [learner](../lessons/py_pandas_06.py) · [explanations](../solutions/py_pandas_06_solutions.md) · [executable reference](../solutions/py_pandas_06_solution.py).

This advanced practice lesson directly requires `python-21`,
`python-pandas-02` and `python-data-02`. Review timestamp parsing, Boolean row
selection and explicit data-cleaning policies first. You do not need to know
distributed processing or install a database. The examples use the prepared
pandas 2.3 environment and explicitly name `America/New_York` or UTC rather than
depending on the host machine's local timezone.

## Learning objectives

Parse offset-bearing event timestamps without silently assigning a timezone to
naive text. Resolve repeated or nonexistent wall times under an explicit policy.
Convert the display of an instant without moving it. Construct half-open local
day windows in UTC, distinguish elapsed and wall-clock durations, and resample
complete local calendar windows without inventing a fixed 24-hour day.

## Vocabulary and concepts

- **Instant:** A point on a timeline. Two timestamp strings with different offsets
  can identify the same instant. UTC is a convenient common representation for
  comparison and storage; it does not determine which business date an event
  belongs to in a named local timezone.

- **Wall time:** The date and clock reading displayed in a place. A naive timestamp
  stores those fields without a timezone interpretation. It is incomplete as an
  instant when a task requires comparison across locations or daylight-saving
  transitions.

- **Localization:** Assigning a timezone interpretation to naive wall fields.
  `tz_localize` must resolve whether a local clock reading is valid, repeated or
  nonexistent. It answers a different question from converting an already known
  instant for display in another zone.

- **Conversion:** Changing the timezone display of an aware timestamp while
  preserving the instant. `tz_convert` keeps the underlying timeline value and
  changes local fields and offset. Calling it on naive data is a sign that an
  interpretation decision is still missing.

- **Ambiguous time:** A repeated local clock reading during a backward clock
  change. In the New York fall fixture, two occurrences of 01:30 are an hour
  apart. A bare 01:30 does not tell you which occurrence a producer meant.

- **Nonexistent time:** A skipped local reading during a forward clock change.
  New York's 02:30 on the selected spring transition never occurred. Shifting
  that reading forward is a data-repair policy, not recovery of the producer's
  original intended instant.

- **Calendar period:** A date or schedule interval defined in local calendar
  terms. A local day runs from one local midnight to the next. Its elapsed length
  can differ from 24 hours. A latency measurement or a fixed-duration window is
  a different contract.

## Syntax anatomy and policy boundaries

`pd.to_datetime(texts, utc=True)` converts offset-aware inputs to a common UTC
representation, but it also interprets naive inputs as UTC. It therefore cannot
serve as proof that the producer actually supplied an offset. The first task
requires an explicit `Z` or numeric offset in the accepted ISO text before
constructing UTC instants. Original row order remains meaningful and is retained.

`naive.tz_localize(zone, ambiguous=..., nonexistent=...)` interprets wall fields.
This lesson defaults to rejection. For the repeated New York reading, an
explicit Boolean choice selects the daylight-saving or standard occurrence
using pandas' documented rule. Do not assume that inference from row order
establishes the producer's intention. For the spring gap, `shift_forward` is an
optional declared policy that changes the clock reading, sometimes mapping
several invalid inputs to the same repaired instant.

`aware.tz_convert(zone)` changes display. `aware.tz_localize(None)` instead
removes timezone information while retaining displayed clock fields. The latter
is useful for the deliberately requested wall-duration comparison here; it is
unsafe as an accidental normalization before comparing event instants.

## Worked example / walkthrough

### Worked example 1: The same displayed clock reading can identify two instants

```python
import pandas as pd

events = pd.to_datetime(
    ["2026-11-01T01:30:00-04:00", "2026-11-01T01:30:00-05:00"], utc=True
)
local = events.tz_convert("America/New_York")
assert [stamp.hour for stamp in local] == [1, 1]
assert events[1] - events[0] == pd.Timedelta(hours=1)
assert local.asi8.tolist() == events.asi8.tolist()
print("UTC hours:", [stamp.hour for stamp in events])
```

The first string becomes 05:30 UTC; the second becomes 06:30 UTC. Both display
01:30 locally, with different offsets. Dropping the offset and deduplicating
the displayed strings would erase a real event. Conversion preserves the
underlying instant values; it does not reinterpret the original fields as if
they were entered in another location.

If the input instead contains two naive 01:30 readings, localization needs
two explicit decisions. In this fixture `[True, False]` selects the daylight
occurrence and the standard occurrence respectively. Check the resulting UTC
instants. If that evidence is unavailable, retaining an unresolved state or
rejecting the record is more accurate than guessing which event happened first.

### Worked example 2: Build a local day before measuring its duration

```python
zone = "America/New_York"
day = pd.Timestamp("2026-03-08")
start = day.tz_localize(zone)
end = (day + pd.DateOffset(days=1)).tz_localize(zone)
fixed_duration_end = start + pd.Timedelta(hours=24)
assert end - start == pd.Timedelta(hours=23)
assert end.hour == 0 and fixed_duration_end.hour == 1
print("Local-day elapsed hours:", (end - start).total_seconds() / 3600)
```

The naive calendar first advances from March 8 to March 9; each midnight is
then interpreted in the named zone. The UTC boundaries are 05:00 on March 8
and 04:00 on March 9, so only 23 elapsed hours lie between them. Adding 24
elapsed hours to the starting instant reaches 01:00 on the next local day.
On November 1, the corresponding local-day interval contains 25 elapsed hours.

For local date \(d\), let \(u_d\) be the UTC instant of that date's midnight
in the chosen zone. Its membership window is \([u_d,u_{d+1})\).
The inclusive start and exclusive end assign an event at a shared boundary
to exactly one day. An event one instant before the end belongs to the earlier
day; an event exactly at the end belongs to the next day. Do not substitute
23:59:59 and accidentally exclude finer timestamp precision.

## Coverage and aggregation

The daily amount example counts selected events separately from known amounts.
With one known ten-cent amount and one unknown amount, the known partial sum
is ten and the accepted complete sum is unknown. Timezone correctness does not
repair incomplete measurement coverage. Preserve both facts in the result.

The fixture explicitly represents a complete event window. Under that teaching
assumption a day with no events has a known zero count. An empty production feed
might instead mean that ingestion failed. A resampling command cannot establish
source completeness. Carry an independent availability or watermark contract
before interpreting empty windows as business zeroes in a real pipeline.

The last task uses local-time `resample("D", closed="left", label="left")`
and reindexes to an explicitly supplied calendar. Reindexing keeps requested
zero-count days at the beginning and end, where no observed timestamp would
otherwise create a bin. It also makes the bounded requested window visible.
The exercise allows at most 366 calendar days and excludes events outside the
declared interval. The general API supports more time rules, but this contract
does not pretend to implement every fiscal calendar or exchange schedule.

## Exercises

1. **Require explicit offset evidence.**

**Inputs:** A list of ISO timestamp strings using T and an explicit Z or numeric offset; empty input is allowed. No naive or missing timestamp is accepted.

**Expected:** Return an aware UTC DatetimeIndex preserving input order and all supplied instants. Reject malformed/naive text instead of coercing it to NaT. Empty input retains an aware UTC schema.

**Verify:** Compare both fall 01:30 occurrences with independent UTC hours five and six. Assert naive text rejection and preserve the row count/order.

2. **Resolve repeated and nonexistent wall clocks.**

**Inputs:** A list of naive ISO wall-time strings, an explicit zone, optional one-Boolean-per-input ambiguity choices, and gap policy raise or shift_forward. Default policies reject ambiguity and gaps.

**Expected:** Return an aware DatetimeIndex in the requested zone. In the New York fall fixture, True/False resolve repeated 01:30 to the daylight/standard instants. The explicit spring shift policy returns 03:00; unresolved cases raise ValueError with the original cause retained.

**Verify:** Compare resolved UTC instants with the offset-bearing oracle. Assert both default failures and the actual changed 03:00 clock fields, rather than treating any successful localization as correct.

3. **Change display without moving events.**

**Inputs:** A timezone-aware DatetimeIndex without NaT and a nonempty explicit destination zone. Duplicate instants and arbitrary row order are valid.

**Expected:** Return the same number of instants in the same order with the requested timezone display. Reject a naive or NaT-bearing index; do not sort, deduplicate or reinterpret naive fields.

**Verify:** Assert underlying asi8 values are identical before and after conversion and compare the two repeated local 01:30 displays with their distinct original UTC values.

4. **Build half-open calendar-day membership and coverage.**

**Inputs:** Aware event instants, a positional list of integer-cent or None measurements of equal length, a named zone, and one YYYY-MM-DD local date. The tiny event fixture is explicitly complete.

**Expected:** Return local_day,start_utc,end_utc,elapsed_hours,event_count,known_count,known_sum,accepted_total. Include the local midnight start and exclude the next local midnight. Accepted total is None if any selected amount is unknown; an empty complete fixture yields zero.

**Verify:** Inspect events immediately before/at both UTC boundaries. Assert the spring day spans 23 hours with two selected rows, known_sum ten and unknown accepted total, then verify the fall 25-hour case.

5. **Distinguish timeline duration from displayed clock difference.**

**Inputs:** Two explicit-offset ISO timestamps with end not before start and a named local display zone.

**Expected:** Return (elapsed,wall) Timedeltas. Elapsed uses UTC instants; wall compares displayed local fields after deliberate zone removal. Reverse intervals are rejected.

**Verify:** Assert spring gives one elapsed hour versus two wall hours, fall gives one versus zero, and equal endpoints yield two zero durations.

6. **Resample a complete explicit local date window.**

**Inputs:** Aware event instants, named zone, inclusive first_day and exclusive end_day. Permit 1 through 366 calendar days. The fixture covers the complete declared window.

**Expected:** Return one sorted row per requested date with local_day,start_utc,end_utc,elapsed_hours,event_count, including zero-event dates. Exclude outside events and use local calendar days rather than fixed 24-hour windows.

**Verify:** Compare each count with a hand-assigned local-date oracle. Assert March counts one/two/one with hours 24/23/24, retained empty dates and no double-counted midnight event.


## Common pitfalls

If converting a timezone changes the event's underlying instant, inspect
whether you localized rather than converted. If two fall-back events collapse
into one, inspect dropped offsets or naive-string deduplication. If a spring
day includes 01:00 from the following date, inspect a fixed 24-hour addition.
If a gap repair creates duplicate times, retain event IDs and the original
fields; repaired clock equality does not establish duplicate event identity.

If a daily total changes when the host timezone changes, locate the missing
explicit zone argument. If a boundary event appears twice, inspect inclusive
end predicates. If an empty day disappears, inspect whether the bin index came
only from observed data. Keep the original localization exception: the
reference wraps provider-specific errors with a stable exercise error while
preserving their cause for diagnosis. Some zones have unusual transitions at
midnight; the boundary policy here rejects ambiguous/nonexistent midnights
rather than silently repairing them.

## Self-check

Explain why two equal wall strings may be different instants and why two
different offset strings may be the same instant. Trace the four March boundary
events without running a group operation. State when stripping timezone data
is intentional and when it loses required meaning. Predict elapsed and wall
durations across both transitions, then name the separate evidence required
to interpret a zero-count date as a complete business observation.

## Next step

Continue to [typed I/O and domains](py_pandas_07.md) after completing its text, pandas and join prerequisites. Choose the sequence through the catalog rather than assuming that day labels are deadlines.

Use these contracts before point-in-time joins, feature windows, retention
metrics or forecasting resampling. Add explicit market or business calendars
when an application needs holidays and operating sessions. Read the selected
[pandas timezone and time-series documentation](https://pandas.pydata.org/pandas-docs/version/2.3/user_guide/timeseries.html)
for API definitions. The fixture's accepted text format, rejection rules,
coverage policy and small date-window limit are deliberate application choices.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-pandas-06: Timezones, DST, and Calendar Boundaries.
Read python/professional/companion-guides/py_pandas_06.md and python/professional/lessons/py_pandas_06.py. Direct prerequisites: python-21, python-pandas-02, python-data-02.
Explain the vocabulary and the exact input/output meaning, then ask me to predict a concrete boundary result before my attempt. Give one hint at a time, review my row/value/schema/exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request a comparison or have made an honest attempt. Use only prepared offline fixtures and preserve my saved work.
Done when all six contracts and boundary cases have inspected evidence, and I can explain why a plausible inferred or silently repaired result violates the declared meaning.
```
