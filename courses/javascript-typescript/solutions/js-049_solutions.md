# js-049: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

A time series associates measurements with times. A JavaScript Date represents an instant, while formatting can use local time or UTC. If the lesson uses UTC dates, use UTC parsing, scales and formatting consistently so a chart does not shift a day in another time zone.

A line connects observations in the supplied order. D3 does not automatically sort your records by time. Connecting unsorted points can produce a zigzag that implies a path the data never took. Sorting a copy preserves the source order when other code owns the original data.

Missing intervals deserve visible treatment. A line generator’s defined predicate can break a path at missing observations. Connecting across a long outage can imply continuous measurement when none exists. Explain whether a gap means missing data, no activity or a deliberate sampling interval.

`d3.scaleUtc` maps instants to x positions. A line generator uses x and y accessors to produce an SVG path string. `.defined(d => Number.isFinite(d.value))` controls which records form continuous segments. Set `fill: none` for an ordinary line so the path is not treated as a filled polygon.

A null value must be rejected explicitly because `Number(null)` becomes zero. Sorting and missingness policies are data decisions, not merely chart styling. The reference checks ordering and the number of separate path segments in a small fixture.

## Exercise 1: Predict date order after sorting.

The line generator uses array order. Sorting is an explicit preprocessing step rather than a hidden property of time scales. The fixture lists January 3 first; `sort((a, b) => a.date - b.date)` subtracts Date objects as milliseconds and puts January 1 first. Sorting the ISO strings would also work here, but sorting a formatted label such as "Jan 10" before "Jan 9" would not. The reference checks that `rows[0]` is 2024-01-01.

**Expected:** Chronological order by numeric instant.

## Exercise 2: Insert a missing observation.

A missing value is not a measured zero. Preserve enough records to represent the missing interval. January 3 has value null, and line.defined excludes it, so the path has two segments: January 1 to 2 and January 4 to 5. Removing the null row entirely would instead draw a straight line from January 2 to 4, hiding the missing day. Count "M" commands in the path string.

**Expected:** The path has a visible gap under the stated policy.

## Exercise 3: Build a UTC line chart with a gap.

Use matching time parsing, scale and formatting conventions. Check the data ordering independently of the rendered path. Use scaleUtc with UTC dates and utcFormat("%b %d") for ticks. Mixing local parsing with UTC formatting can shift labels by a day in some time zones. Verify both that rows are sorted and that the path contains two M commands.

**Expected:** Time-ordered points and separate defined segments.

## Exercise 4: Diagnose a line that doubles back in time.

Inspect numeric timestamps before changing interpolation. A curve style cannot repair incorrect temporal ordering. A line that runs right then jumps left means the array order is not time order. Changing curve to curveMonotoneX would not help. Print rows.map(d => +d.date) and confirm it increases.

**Expected:** Input order is unsorted or dates were parsed incorrectly.

## Exercise 5: Handle an empty or all-missing series.

Extent on no valid data does not define a meaningful chart scale. Make the empty state part of the component contract. With all values null, d3.extent over valid values returns [undefined, undefined] and the y domain becomes NaN. Check for zero defined points first and render a "no data" message instead of an axis.

**Expected:** Show an explicit no-data message rather than invalid domains.

## Exercise 6: Explain interpolation limits for irregular observations.

Label gaps and sampling intervals. A smooth curve can suggest precision or continuity the data does not support. Here observations are daily, so a straight segment between January 4 and 5 says nothing about hours in between; label the sampling interval. If a gap is real, keep it visible as the break line.defined already draws.

**Expected:** Connecting samples is a visual assumption, not evidence between measurements.

## After comparison

Convert the reference to hourly data across a daylight-saving change in New York. Keep the instants in UTC, label the axis in local time, and check that the transition day has 23 or 25 hourly points rather than a silent gap or duplicate.
