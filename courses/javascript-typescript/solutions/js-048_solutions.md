# js-048: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

CSV is a text format whose cells do not automatically have the domain types your analysis needs. Parsing a file into rows and interpreting strings as numbers or dates are separate steps. Empty strings, malformed values and duplicate IDs require explicit policies before visual encoding.

A missing measurement is not necessarily zero. Replacing absence with zero can distort averages, totals and visual trends. Reject invalid rows with a reason, retain a count of excluded rows, and make the policy visible to the chart reader. Trimming text and checking finite numeric values are small but important boundary operations.

Aggregation changes the row grain. A transaction table has one row per event; a category summary may have one row per group. The correct denominator and missing-value policy depend on that grain. A data scientist should be able to reconstruct the aggregate from the small source rows before rendering it.

`d3.csvParse` parses inline CSV without a network request. A row accessor can return a cleaned object or null to omit a row, but an omission should be counted and explained. `Number('')` is zero, which is why a blank-string check must precede numeric conversion.

`d3.rollup(rows, group => d3.sum(group, d => d.value), d => d.category)` returns a Map keyed by category. The grouping key should be normalized intentionally. Case-sensitive category names may be genuinely distinct or accidental inconsistencies; do not merge them without a domain decision.

## Exercise 1: Predict blank-string numeric conversion.

Blind conversion silently changes missingness into a measured zero. Keep those states distinct.

**Expected:** Number of an empty string is 0, so prevalidation is required.

## Exercise 2: Count rejected rows with reasons.

A chart should not silently shrink its sample. A small rejection ledger makes the cleaning policy reviewable.

**Expected:** Every omitted row is accounted for as blank or malformed.

## Exercise 3: Parse and aggregate the inline fixture.

Check the row-level interpretation before grouping. Aggregation can conceal a wrong conversion if only the final shape is inspected.

**Expected:** A totals to 5 and B totals to 4 from valid rows.

## Exercise 4: Diagnose treating a blank value as zero.

Repair the cleaning rule and compare the resulting counts or means. Merely hiding the zero mark does not fix the data.

**Expected:** The chart includes an invented measurement.

## Exercise 5: Handle a category with only missing rows.

Whether to retain an empty category depends on the analytical universe. Make that decision explicit.

**Expected:** Its absence or missing state is documented rather than called zero.

## Exercise 6: Transfer the pipeline to a rate metric.

Averaging percentages can differ from a ratio of sums. Choose the aggregation that matches the question.

**Expected:** Validate numerator and denominator at a defined grain before division.
