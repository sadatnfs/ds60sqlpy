# js-063: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A choropleth colors geographic regions according to a value. The map’s geometry and the statistical table usually come from different sources, so they must be joined by a stable identifier. A display name is often a weak key because spelling, language and boundary definitions can change.

Raw counts often track population or exposure rather than the phenomenon of interest. A rate divides an event count by a relevant denominator, such as eligible people or observation time. The denominator must match the numerator’s geography, period and population. A beautiful map cannot repair a mismatched denominator.

Missing data needs its own visual state. A region with no measurement is not equivalent to a measured zero. Keep an explicit missing color or pattern, a legend and a table. Be cautious about ecological inference: a region-level association does not necessarily describe individuals within that region.

Create a Map from stable region ID to validated data, then look up each feature’s ID. Validate duplicate statistical IDs and report unmatched features and rows. Compute rates only for positive valid denominators. Choose a sequential scale for nonnegative ordered rates and explain its domain.

The reference uses synthetic planar regions with `geoIdentity`, so the lesson isolates join and rate logic without introducing a global projection. It includes one missing region deliberately. This is a map-like teaching fixture, not a real-world geographic claim.

## Exercise 1: Predict rates for 10/100 and 20/100.

A rate is a derived quantity. Preserve numerator and denominator so the calculation can be audited.

**Expected:** 0.1 and 0.2 with an explicit common denominator meaning.

## Exercise 2: Add a region with no statistical row.

Do not default a failed join to zero. Missingness is an observation about data availability.

**Expected:** It receives the documented missing-data appearance.

## Exercise 3: Build a stable-ID choropleth join.

A join audit prevents silent region loss and name-based mismatches. Keep unmatched statistical rows visible too.

**Expected:** Every feature is matched or explicitly listed as missing.

## Exercise 4: Diagnose a map of raw events interpreted as risk.

Choose a denominator appropriate to the question and verify its geographic and temporal alignment.

**Expected:** Population or exposure may explain the count pattern.

## Exercise 5: Handle a zero denominator.

An invalid denominator cannot support a meaningful color. The chart should expose the limitation.

**Expected:** Reject or mark the rate undefined rather than divide to infinity.

## Exercise 6: Explain ecological inference limits.

Aggregation can create or reverse relationships. State the unit of analysis and avoid unsupported individual conclusions.

**Expected:** Regional summaries do not automatically describe individuals.
