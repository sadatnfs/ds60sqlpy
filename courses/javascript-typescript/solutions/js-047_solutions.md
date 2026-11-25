# js-047: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

An axis makes a scale interpretable by displaying reference positions and labels. D3 axis generators create SVG elements from a scale; they do not choose the right statistical units or description. The chart author must name the quantity and make tick formatting consistent with the values.

Ticks are selected reference values, not necessarily every data point. A requested tick count is often a hint rather than an exact guarantee. Explicit tick values are useful for small controlled examples. Formatting changes displayed text, not the underlying numeric scale.

Percent data illustrates a common mistake. A formatter expecting fractions displays 0.25 as 25%. If the data is already 25 and you apply that formatter, it displays 2500%. Keep the stored representation, axis label and annotation units aligned. Precision should communicate measurement meaning rather than decorate every value with many decimals.

Call an axis generator on a group: `g.call(d3.axisBottom(x))`. Translate that group to the bottom coordinate, leaving the scale range in the chart’s coordinate system. Recalling the generator on the same group updates its ticks.

Use a visible axis title and a chart description. Avoid assuming that a bare dollar sign, abbreviation or color legend communicates enough context. Units and denominator matter, especially for rates and normalized comparisons.

## Exercise 1: Predict percent formatting for 0.4.

The format treats the input as a fraction. It scales displayed text without changing the data domain. d3.format(".0%") multiplies by 100 and appends the sign, so 0.4 prints 40%. Writing a custom formatter as value + "%" would print 0.4%. The reference shows the same behavior on its axis: tick 0.25 reads 25%.

**Expected:** 40%.

## Exercise 2: Change explicit tick values to four named values.

Tick selection is a presentation decision. Keep the scale shared so a separate formatting change does not shift data positions. Replace [0, 0.25, 0.5, 0.75, 1] with four values, say [0, 0.2, 0.6, 1], and keep the same x. The circle at x(0.25) stays at 200 pixels because the scale did not change. Building a second scale just for the axis would let ticks and marks drift apart; check the new tick count is 4 and the circle's cx is unchanged.

**Expected:** The axis labels match that list and remain aligned with the marks.

## Exercise 3: Build a labeled quantitative axis.

A reader should understand what a coordinate means without opening the source code. The reference puts the axis at translate(0,280) and a centered caption "Conversion rate (fraction of eligible visits)" at y 330. An axis with percent ticks but no caption still leaves the reader guessing the denominator. Verify the five tick labels join to "0%,25%,50%,75%,100%" and the caption text exists.

**Expected:** Visible quantity, units and correctly formatted tick values.

## Exercise 4: Diagnose 2500% for a value intended as 25%.

Repair the representation contract at the data boundary or choose a formatter matching stored units. Do not merely remove the percent sign. If the data stores 25 for twenty-five percent, ".0%" prints 2500%. Deleting the percent sign leaves 2500, which is still wrong. Either divide by 100 when loading, or use a plain number format with a "%" unit in the caption, then confirm 25 renders as 25%.

**Expected:** The stored percentage was treated as a fraction.

## Exercise 5: Compare fixed precision and meaningful precision.

More decimals are not more accuracy. Choose enough precision to avoid hiding meaningful differences without implying unsupported measurement certainty. For example, ".2%" would show 25.00%, implying hundredths of a percent that a handful of visits cannot support, while ".0%" could merge 24.6% and 25.4%. Choose digits from the sample size and check that two values you need to distinguish print differently.

**Expected:** Displayed digits reflect measurement and comparison needs.

## Exercise 6: Design axes for counts and rates side by side.

A count and a rate answer different questions. Shared colors do not make their numeric scales interchangeable. Give each panel its own scale and caption, for example "visits (count)" and "conversion rate (fraction)". Sharing one y scale would squash the rates near zero.

**Expected:** Separate unit labels and denominators make the comparison explicit.

## After comparison

Add a second axis for rates per 1,000 beside the counts axis, each with its own title and units. Format counts with thousands separators using `d3.format(',')` and rates with one decimal place, then justify both precision choices in a sentence each.
