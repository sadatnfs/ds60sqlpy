# js-047: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

An axis makes a scale interpretable by displaying reference positions and labels. D3 axis generators create SVG elements from a scale; they do not choose the right statistical units or description. The chart author must name the quantity and make tick formatting consistent with the values.

Ticks are selected reference values, not necessarily every data point. A requested tick count is often a hint rather than an exact guarantee. Explicit tick values are useful for small controlled examples. Formatting changes displayed text, not the underlying numeric scale.

Percent data illustrates a common mistake. A formatter expecting fractions displays 0.25 as 25%. If the data is already 25 and you apply that formatter, it displays 2500%. Keep the stored representation, axis label and annotation units aligned. Precision should communicate measurement meaning rather than decorate every value with many decimals.

Call an axis generator on a group: `g.call(d3.axisBottom(x))`. Translate that group to the bottom coordinate, leaving the scale range in the chart’s coordinate system. Recalling the generator on the same group updates its ticks.

Use a visible axis title and a chart description. Avoid assuming that a bare dollar sign, abbreviation or color legend communicates enough context. Units and denominator matter, especially for rates and normalized comparisons.

## Exercise 1: Predict percent formatting for 0.4.

The format treats the input as a fraction. It scales displayed text without changing the data domain.

**Expected:** 40%.

## Exercise 2: Change explicit tick values to four named values.

Tick selection is a presentation decision. Keep the scale shared so a separate formatting change does not shift data positions.

**Expected:** The axis labels match that list and remain aligned with the marks.

## Exercise 3: Build a labeled quantitative axis.

A reader should understand what a coordinate means without opening the source code.

**Expected:** Visible quantity, units and correctly formatted tick values.

## Exercise 4: Diagnose 2500% for a value intended as 25%.

Repair the representation contract at the data boundary or choose a formatter matching stored units. Do not merely remove the percent sign.

**Expected:** The stored percentage was treated as a fraction.

## Exercise 5: Compare fixed precision and meaningful precision.

More decimals are not more accuracy. Choose enough precision to avoid hiding meaningful differences without implying unsupported measurement certainty.

**Expected:** Displayed digits reflect measurement and comparison needs.

## Exercise 6: Design axes for counts and rates side by side.

A count and a rate answer different questions. Shared colors do not make their numeric scales interchangeable.

**Expected:** Separate unit labels and denominators make the comparison explicit.
