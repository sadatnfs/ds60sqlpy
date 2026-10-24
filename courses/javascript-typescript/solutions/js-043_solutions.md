# js-043: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

D3 is a collection of JavaScript tools for transforming data and connecting it to visual output. It does not choose a correct chart or statistical question for you. A visual encoding maps a data property to a perceptual property such as position, length, area or color. Begin by naming the quantity and units before choosing a mark.

SVG is a document tree of vector shapes. A rectangle has x and y coordinates, width and height. In the usual SVG coordinate system x increases to the right and y increases downward. A viewBox describes the internal coordinate system; CSS controls how that system fits the available display area. A shape can be present in the DOM while lying outside the visible viewBox.

The first chart maps three synthetic counts to horizontal bar lengths. A zero-length bar corresponds to zero, making length comparisons interpretable. Labels provide category identity and exact values. The chart is intentionally small enough that you can calculate every coordinate by hand.

`d3.select(host)` wraps one existing DOM element in a selection. `.append('svg')` creates an SVG child and returns a selection containing it. `.attr(name, value)` changes an attribute; a callback receives the bound datum and index. A chain is a sequence of operations, not special chart syntax.

This lesson first uses a simple multiplier rather than a scale to expose the arithmetic. With width equal to count times 20, counts 2, 5 and 8 produce widths 40, 100 and 160. Later lessons replace the literal multiplier with a scale whose domain and range are explicit. Keep text separate from rectangle geometry.

## Exercise 1: Predict the three bar widths.

The same linear multiplier maps all counts. A consistent baseline makes the length ratio represent the count ratio.

**Expected:** 40, 100 and 160 units.

## Exercise 2: Change the multiplier to 10.

This changes display geometry, not the data. Keep labels and the explanation of units consistent.

**Expected:** All widths halve while category values remain unchanged.

## Exercise 3: Create three labeled bars from a saved blank pad.

Use a small input array and inspect mark count before styling. Every record should have a visible representation.

**Expected:** Exactly three rectangles with matching labels and counts.

## Exercise 4: Diagnose a rectangle outside the viewBox.

Inspect coordinates and viewBox bounds. Adding another append does not repair a coordinate error.

**Expected:** Its DOM presence differs from its visible intersection.

## Exercise 5: Add a zero-count category.

Zero is data, not missingness. Keep its label so the absence of length has an explicit interpretation.

**Expected:** A zero-length bar with a visible category/value label.

## Exercise 6: Explain why position and length suit count comparison.

Choose the encoding to match the task. Area and decorative shapes can make a simple comparison harder.

**Expected:** A common baseline supports meaningful magnitude comparison.
