# js-049: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A time series associates measurements with times. A JavaScript Date represents an instant, while formatting can use local time or UTC. If the lesson uses UTC dates, use UTC parsing, scales and formatting consistently so a chart does not shift a day in another time zone.

A line connects observations in the supplied order. D3 does not automatically sort your records by time. Connecting unsorted points can produce a zigzag that implies a path the data never took. Sorting a copy preserves the source order when other code owns the original data.

Missing intervals deserve visible treatment. A line generator’s defined predicate can break a path at missing observations. Connecting across a long outage can imply continuous measurement when none exists. Explain whether a gap means missing data, no activity or a deliberate sampling interval.

`d3.scaleUtc` maps instants to x positions. A line generator uses x and y accessors to produce an SVG path string. `.defined(d => Number.isFinite(d.value))` controls which records form continuous segments. Set `fill: none` for an ordinary line so the path is not treated as a filled polygon.

A null value must be rejected explicitly because `Number(null)` becomes zero. Sorting and missingness policies are data decisions, not merely chart styling. The reference checks ordering and the number of separate path segments in a small fixture.

## Exercise 1: Predict date order after sorting.

The line generator uses array order. Sorting is an explicit preprocessing step rather than a hidden property of time scales.

**Expected:** Chronological order by numeric instant.

## Exercise 2: Insert a missing observation.

A missing value is not a measured zero. Preserve enough records to represent the missing interval.

**Expected:** The path has a visible gap under the stated policy.

## Exercise 3: Build a UTC line chart with a gap.

Use matching time parsing, scale and formatting conventions. Check the data ordering independently of the rendered path.

**Expected:** Time-ordered points and separate defined segments.

## Exercise 4: Diagnose a line that doubles back in time.

Inspect numeric timestamps before changing interpolation. A curve style cannot repair incorrect temporal ordering.

**Expected:** Input order is unsorted or dates were parsed incorrectly.

## Exercise 5: Handle an empty or all-missing series.

Extent on no valid data does not define a meaningful chart scale. Make the empty state part of the component contract.

**Expected:** Show an explicit no-data message rather than invalid domains.

## Exercise 6: Explain interpolation limits for irregular observations.

Label gaps and sampling intervals. A smooth curve can suggest precision or continuity the data does not support.

**Expected:** Connecting samples is a visual assumption, not evidence between measurements.
