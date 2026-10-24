# js-050: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A scatterplot uses two quantitative positions to show the joint distribution of observations. Each point should have a defined row grain, such as one person or one experiment. A visible association does not by itself establish causality, and a few synthetic points cannot support a population conclusion.

When a third quantity controls circle size, decide whether the quantity maps to radius or area. Viewers perceive the filled area, so a square-root radius scale often makes area proportional to a nonnegative quantity. Doubling a radius quadruples area. A legend should explain the size meaning.

Overplotting occurs when points overlap. Opacity, smaller marks, aggregation or a density representation can help, but each changes what the reader can infer. Jitter can reveal repeated values while deliberately moving positions; explain and bound it rather than presenting moved points as exact measurements.

Use independent x and y scales for their units. A `scaleSqrt` radius range maps nonnegative magnitude to radius. A circle at `(x(d.x), y(d.y))` encodes one record. Colors can represent categories, but labels or shapes should support readers who cannot distinguish the colors.

The reference validates finite positions and the area relationship for magnitudes 1 and 4. It does not perform a statistical test. Use a tooltip or table for exact records and make missing or invalid coordinates an explicit data policy.

## Exercise 1: Predict circle radii for sizes 1 and 4.

The radius ratio is two while the area ratio is four. This preserves the magnitude-to-area relation.

**Expected:** 10 and 20 under the stated square-root scale.

## Exercise 2: Add two identical coordinate records.

Overlap can conceal multiplicity. Record counts remain a data check even when marks visually coincide.

**Expected:** The record count exceeds the unique visible position count.

## Exercise 3: Build a three-variable scatterplot.

A chart should let a reader distinguish spatial coordinates from the meaning of marker area.

**Expected:** Position and area mappings have named units and a size explanation.

## Exercise 4: Diagnose mapping magnitude directly to radius.

If area is the intended quantity encoding, use an appropriate radius transformation and validate a known ratio.

**Expected:** Area exaggerates large values quadratically.

## Exercise 5: Choose a justified overplotting strategy.

Opacity, jitter and bins solve different tasks. Do not hide the transformation from readers.

**Expected:** The strategy and its effect on interpretation are stated.

## Exercise 6: Explain a correlation without claiming causation.

Selection, confounding and reverse causality can create patterns. Visualization supports inquiry, not automatic causal identification.

**Expected:** Describe association and identify alternative explanations.
