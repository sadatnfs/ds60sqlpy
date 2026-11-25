# js-050: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

A scatterplot uses two quantitative positions to show the joint distribution of observations. Each point should have a defined row grain, such as one person or one experiment. A visible association does not by itself establish causality, and a few synthetic points cannot support a population conclusion.

When a third quantity controls circle size, decide whether the quantity maps to radius or area. Viewers perceive the filled area, so a square-root radius scale often makes area proportional to a nonnegative quantity. Doubling a radius quadruples area. A legend should explain the size meaning.

Overplotting occurs when points overlap. Opacity, smaller marks, aggregation or a density representation can help, but each changes what the reader can infer. Jitter can reveal repeated values while deliberately moving positions; explain and bound it rather than presenting moved points as exact measurements.

Use independent x and y scales for their units. A `scaleSqrt` radius range maps nonnegative magnitude to radius. A circle at `(x(d.x), y(d.y))` encodes one record. Colors can represent categories, but labels or shapes should support readers who cannot distinguish the colors.

The reference validates finite positions and the area relationship for magnitudes 1 and 4. It does not perform a statistical test. Use a tooltip or table for exact records and make missing or invalid coordinates an explicit data policy.

## Exercise 1: Predict circle radii for sizes 1 and 4.

The radius ratio is two while the area ratio is four. This preserves the magnitude-to-area relation. With scaleSqrt and a range ending at 20 for size 4, size 1 gives 20 * sqrt(1/4) = 10. The reference uses [0, 24], giving 12 and 24, the same 2 to 1 radius ratio and 4 to 1 area ratio. A linear radius scale would make the area ratio 16 to 1. The check (r(4) * r(4)) / (r(1) * r(1)) === 4 confirms the square-root mapping.

**Expected:** 10 and 20 under the stated square-root scale.

## Exercise 2: Add two identical coordinate records.

Overlap can conceal multiplicity. Record counts remain a data check even when marks visually coincide. Add two rows at x 2, y 4; three circles stack at one point but selectAll("circle").size() still counts every record. Judging the count by eye would undercount. Assert the size matches rows.length.

**Expected:** The record count exceeds the unique visible position count.

## Exercise 3: Build a three-variable scatterplot.

A chart should let a reader distinguish spatial coordinates from the meaning of marker area. The reference maps x and y to position with axes and size to area with scaleSqrt, plus a title on each circle giving all three values. Without a size legend, readers will read radius rather than area. Verify the tooltip text for B reads "B: x 2, y 4, size 4".

**Expected:** Position and area mappings have named units and a size explanation.

## Exercise 4: Diagnose mapping magnitude directly to radius.

If area is the intended quantity encoding, use an appropriate radius transformation and validate a known ratio. d3.scaleLinear for radius makes size 4 cover 16 times the area of size 1. Compare r(4)^2 / r(1)^2: 4 means area encodes size, 16 means radius does.

**Expected:** Area exaggerates large values quadratically.

## Exercise 5: Choose a justified overplotting strategy.

Opacity, jitter and bins solve different tasks. Do not hide the transformation from readers. The reference uses fill-opacity 0.65 so overlaps darken. Jitter would move points off their true coordinates; say so in the caption if used, and keep counts in tooltips.

**Expected:** The strategy and its effect on interpretation are stated.

## Exercise 6: Explain a correlation without claiming causation.

Selection, confounding and reverse causality can create patterns. Visualization supports inquiry, not automatic causal identification. In the fixture, y rises with x for A and B but C at x 3 has y 3. Describe association only; three points cannot rule out a confounder. Adding a regression line to three points would suggest more certainty than the data holds; report the three tuples in a table instead.

**Expected:** Describe association and identify alternative explanations.

## After comparison

Add 200 synthetic points with heavy overlap and compare two strategies on the same data: transparency, and a count of points per grid cell. Record what each strategy hides and which one keeps the record count readable.
