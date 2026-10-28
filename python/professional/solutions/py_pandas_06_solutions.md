# python-pandas-06: Explained timezone and calendar solutions

The [complete executable reference](py_pandas_06_solution.py) implements all
six functions and checks the selected 2026 New York transitions in the prepared
runtime. The [guide](../companion-guides/py_pandas_06.md) explains why clock
fields, instants and calendar periods require different operations. Keep those
definitions beside the observed outputs when comparing your own implementation.

## Exercise 1: Require actual offset evidence before UTC normalization

**Inputs:** A list of ISO timestamp strings using T and an explicit Z or numeric offset; empty input is allowed. No naive or missing timestamp is accepted.

**Expected:** Return an aware UTC DatetimeIndex preserving input order and all supplied instants. Reject malformed/naive text instead of coercing it to NaT. Empty input retains an aware UTC schema.

**Verify:** Compare both fall 01:30 occurrences with independent UTC hours five and six. Assert naive text rejection and preserve the row count/order.

The reference accepts a list of ISO timestamp strings in a declared format.
Every string needs `T` between its date and time and an explicit `Z` or numeric
offset. It does not infer a timezone from the host computer or interpret a
naive event as UTC merely because a parser can do so.

```python
values = [pd.Timestamp(text).tz_convert("UTC") for text in texts]
result = pd.DatetimeIndex(values, tz="UTC")
```

The lexical check precedes conversion. Invalid calendar fields still fail the
timestamp parser; they are not converted to `NaT` and silently excluded from a
later calculation. Row order is preserved, because order can carry provenance
even though an aggregate might not require it. An empty accepted list produces
an empty aware UTC index, retaining the output schema without inventing events.

The two fall-back strings map to UTC hours five and six. Comparing only their
local 01:30 displays would miss the distinction. A negative test supplies a
naive timestamp and requires rejection even if the machine itself is set to UTC.

## Exercise 2: Resolve local ambiguity deliberately

**Inputs:** A list of naive ISO wall-time strings, an explicit zone, optional one-Boolean-per-input ambiguity choices, and gap policy raise or shift_forward. Default policies reject ambiguity and gaps.

**Expected:** Return an aware DatetimeIndex in the requested zone. In the New York fall fixture, True/False resolve repeated 01:30 to the daylight/standard instants. The explicit spring shift policy returns 03:00; unresolved cases raise ValueError with the original cause retained.

**Verify:** Compare resolved UTC instants with the offset-bearing oracle. Assert both default failures and the actual changed 03:00 clock fields, rather than treating any successful localization as correct.

The function validates naive local text, the named zone and the optional
decision list before localization. A decision list must contain exactly one
ordinary Boolean per input; integer one is not accepted as an implicit policy.
The default ambiguity and gap policies both reject an unresolved clock reading.

```python
localized = naive.tz_localize(
    zone, ambiguous="raise" if choices is None else choices, nonexistent=gap
)
```

In the selected New York example, True chooses the daylight-saving occurrence
of 01:30 and False chooses the standard occurrence. Their UTC representations
match the independently supplied offset-bearing strings from Exercise 1. Do
not generalize “True always means the earlier instant” to every historical
timezone rule; the public rule is pandas' DST decision and this fixture verifies
the particular resulting instants.

The nonexistent 02:30 spring reading fails by default. Explicit `shift_forward`
returns 03:00 here, not 03:30. It changes the input and can collapse distinct
invalid readings onto the same instant. Preserve original text and any event
identity if a real application adopts such a repair. The wrapper exposes a
stable ValueError while preserving the provider's original exception as its
cause, so diagnosis does not lose the actual localization failure.

## Exercise 3: Convert display without changing the instant

**Inputs:** A timezone-aware DatetimeIndex without NaT and a nonempty explicit destination zone. Duplicate instants and arbitrary row order are valid.

**Expected:** Return the same number of instants in the same order with the requested timezone display. Reject a naive or NaT-bearing index; do not sort, deduplicate or reinterpret naive fields.

**Verify:** Assert underlying asi8 values are identical before and after conversion and compare the two repeated local 01:30 displays with their distinct original UTC values.

```python
displayed = instants.tz_convert(zone)
```

The input must already be aware and contain no `NaT`. The result has the
requested timezone display while retaining row count, order and timeline values.
The reference compares `asi8` before and after conversion. It also verifies
that the two distinct fall instants both display hour one in New York, with
their appropriate offsets still available.

Localizing these UTC clock fields as if they were naive New York readings
would change the instants. Removing the zone first is therefore not a harmless
preparation step. A negative input that is still naive must fail instead of
receiving a guessed interpretation. Keep conversion separate from sorting or
deduplication so its observable contract remains easy to inspect.

## Exercise 4: Summarize one half-open local day with coverage

**Inputs:** Aware event instants, a positional list of integer-cent or None measurements of equal length, a named zone, and one YYYY-MM-DD local date. The tiny event fixture is explicitly complete.

**Expected:** Return local_day,start_utc,end_utc,elapsed_hours,event_count,known_count,known_sum,accepted_total. Include the local midnight start and exclude the next local midnight. Accepted total is None if any selected amount is unknown; an empty complete fixture yields zero.

**Verify:** Inspect events immediately before/at both UTC boundaries. Assert the spring day spans 23 hours with two selected rows, known_sum ten and unknown accepted total, then verify the fall 25-hour case.

The calendar date is parsed strictly. The reference creates that date's naive
midnight and the next calendar date's naive midnight, then localizes both under
an explicit rejection policy. It does not add a 24-hour duration to an aware
starting instant.

```python
selected = (instants >= start) & (instants < end)
amounts = [value for value, keep in zip(values, selected, strict=True) if keep]
```

The integer-cent values correspond by position to the supplied event sequence;
they are not a separate indexed Series whose labels could trigger alignment.
The function checks their equal lengths and rejects Boolean measurements. Known
partial sum, known count, event count and accepted complete total are separate
outputs. Python integer summation avoids introducing a floating representation.

The spring fixture deliberately surrounds both boundaries. 04:59:59 UTC is on
the previous local day; 05:00 is included. The following 03:59:59 is included;
04:00 is excluded. Two selected events contain ten cents and an unknown amount,
so known sum is ten and accepted total is None. The elapsed window is 23 hours.
The fall example has 25 hours. A zero-event date is accepted as zero only under
the explicitly complete tiny-fixture assumption, not as proof of source uptime.

## Exercise 5: Compare elapsed and displayed-wall durations

**Inputs:** Two explicit-offset ISO timestamps with end not before start and a named local display zone.

**Expected:** Return (elapsed,wall) Timedeltas. Elapsed uses UTC instants; wall compares displayed local fields after deliberate zone removal. Reverse intervals are rejected.

**Verify:** Assert spring gives one elapsed hour versus two wall hours, fall gives one versus zero, and equal endpoints yield two zero durations.

```python
elapsed = instants[1] - instants[0]
local = instants.tz_convert(zone).tz_localize(None)
wall = local[1] - local[0]
```

The first subtraction uses the actual timeline. The second intentionally strips
the zone after converting to local display, because this task asks how the two
clock readings differ. Across the selected spring change, one elapsed hour
corresponds to two displayed hours. Across the selected fall change, one elapsed
hour corresponds to zero displayed-clock difference.

Neither number is intrinsically the right answer to every question. Duration
of an event interval normally needs the timeline; a human calendar display can
need the local fields. The function rejects an end instant before its start.
It does not reinterpret a negative or ambiguous interval merely to produce a
positive result. Equal endpoints correctly produce zero for both quantities.

## Exercise 6: Resample a declared complete local calendar window

**Inputs:** Aware event instants, named zone, inclusive first_day and exclusive end_day. Permit 1 through 366 calendar days. The fixture covers the complete declared window.

**Expected:** Return one sorted row per requested date with local_day,start_utc,end_utc,elapsed_hours,event_count, including zero-event dates. Exclude outside events and use local calendar days rather than fixed 24-hour windows.

**Verify:** Compare each count with a hand-assigned local-date oracle. Assert March counts one/two/one with hours 24/23/24, retained empty dates and no double-counted midnight event.

The requested start date is inclusive and end date exclusive. A positive
window of at most 366 calendar days bounds this teaching function. It builds
all local midnight boundaries before selecting events and resampling.

```python
counts = pd.Series(1, index=selected, dtype="int64").resample(
    "D", closed="left", label="left"
).sum().reindex(boundaries[:-1], fill_value=0)
```

One supplied event row contributes one, even if another event has the same
instant. Unique event identity is a separate input responsibility; this function
does not deduplicate timestamps. Reindexing to the declared calendar retains
zero-count boundary days that observed-data bins alone might omit.

The March 7/8/9 fixture returns counts one/two/one and elapsed-day lengths
24/23/24 hours. The empty fall-window fixture returns two zero rows, while its
first day still spans 25 elapsed hours. UTC start/end fields make each membership
window inspectable. Compare the counts against an independent per-event local
date calculation, then test exact midnight membership and a shuffled input order.
Agreement of a monthly grand total would not expose a one-day boundary shift.
