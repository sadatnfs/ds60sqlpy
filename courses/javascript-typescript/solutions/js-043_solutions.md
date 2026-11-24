# js-043: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

D3 is a collection of JavaScript tools for transforming data and connecting it to visual output. It does not choose a correct chart or statistical question for you. A visual encoding maps a data property to a perceptual property such as position, length, area or color. Begin by naming the quantity and units before choosing a mark.

SVG is a document tree of vector shapes. A rectangle has x and y coordinates, width and height. In the usual SVG coordinate system x increases to the right and y increases downward. A viewBox describes the internal coordinate system; CSS controls how that system fits the available display area. A shape can be present in the DOM while lying outside the visible viewBox.

The first chart maps three synthetic counts to horizontal bar lengths. A zero-length bar corresponds to zero, making length comparisons interpretable. Labels provide category identity and exact values. The chart is intentionally small enough that you can calculate every coordinate by hand.

`d3.select(host)` wraps one existing DOM element in a selection. `.append('svg')` creates an SVG child and returns a selection containing it. `.attr(name, value)` changes an attribute; a callback receives the bound datum and index. A chain is a sequence of operations, not special chart syntax.

This lesson first uses a simple multiplier rather than a scale to expose the arithmetic. With width equal to count times 20, counts 2, 5 and 8 produce widths of 40 units, 100 units and 160 units. Later lessons replace the literal multiplier with a scale whose domain and range are explicit. Keep text separate from rectangle geometry.

## Exercise 1: Predict the three bar widths.

The same linear multiplier maps all counts. A consistent baseline makes the length ratio represent the count ratio. In the reference, width is d.value * 20, so A (2), B (5) and C (8) give widths of 40 units, 100 units and 160 units. A tempting mistake is to compute widths from the cumulative total, which would make C look three times longer than its count justifies. The check reads each rect's width attribute and compares the joined string with "40,100,160".

**Expected:** widths of 40 units, 100 units and 160 units.

## Exercise 2: Change the multiplier to 10.

This changes display geometry, not the data. Keep labels and the explanation of units consistent. With 10 instead of 20, the bars become 20, 50 and 80 while the text still reads A: 2, B: 5, C: 8. If the labels were built from the computed width rather than d.value, they would wrongly halve too. Update the width assertion and confirm the label text did not change.

**Expected:** All widths halve while category values remain unchanged.

## Exercise 3: Create three labeled bars from a saved blank pad.

Use a small input array and inspect mark count before styling. Every record should have a visible representation. Join the three records to rect and text separately, as the reference does with selectAll("rect") and selectAll("text"). Appending a rect inside a forEach works once but gives no way to reconcile later. Verify with svg.selectAll("rect").size() === 3 and three matching text nodes.

**Expected:** Exactly three rectangles with matching labels and counts.

## Exercise 4: Diagnose a rectangle outside the viewBox.

Inspect coordinates and viewBox bounds. Adding another append does not repair a coordinate error. The viewBox is 0 0 640 360, so a bar at x 100 with width 600 extends to 700 and is clipped. The rect still exists, so the DOM count passes while the visible bar is cut. Compare x + width with 640 for each rect, or read getBoundingClientRect against the svg's box.

**Expected:** Its DOM presence differs from its visible intersection.

## Exercise 5: Add a zero-count category.

Zero is data, not missingness. Keep its label so the absence of length has an explicit interpretation. A record { name: "D", value: 0 } produces width 0. Filtering it out before the join would make D vanish, and a reader would assume the category was never measured. Confirm four text labels and a rect whose width attribute is exactly 0.

**Expected:** A zero-length bar with a visible category/value label.

## Exercise 6: Explain why position and length suit count comparison.

Choose the encoding to match the task. Area and decorative shapes can make a simple comparison harder. All three bars start at x 100, so their right edges can be compared directly. Mapping counts to circle radius would make C's area 16 times A's for a 4 to 1 count ratio.

**Expected:** A common baseline supports meaningful magnitude comparison.
