# js-064: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

SVG keeps a DOM node for each mark, making styling and interaction convenient. Canvas draws pixels into one bitmap, which can reduce DOM overhead for many simple marks. Canvas does not automatically provide a separate accessible or interactive element for each point. The author must supply semantics and hit testing.

A Canvas has a backing resolution and a CSS display size. Device pixel ratio can make a one-to-one backing bitmap look blurry on high-density screens. Scale the backing dimensions and drawing context deliberately while keeping analytical coordinates in the documented logical space.

Performance depends on data size, transformations, layout, rendering and interactions. Switching to Canvas does not fix an expensive quadratic data algorithm. Measure the slow stage, avoid repeated allocations where appropriate and preserve an accessible data summary or table.

Set canvas.width and height for the backing bitmap, set CSS width and height for display, then transform the context by the device pixel ratio. Draw circles with beginPath, arc and fill. A quadtree can search nearby points efficiently, but its coordinates must match the pointer coordinate space.

The reference draws a bounded grid of 100 points and performs a known nearest-point lookup. It does not benchmark a million records or claim universal Canvas superiority. The SVG is hidden for this lesson because the output is the Canvas plus a textual summary.

## Exercise 1: Predict DOM mark count for a Canvas plot.

The reduced DOM cost comes with extra responsibility for interaction and semantics. The reference hides the SVG and draws 100 arcs on one canvas, so the page gains one canvas element and no circles. Querying host.querySelectorAll("circle") returns 0. That is the saving and also the cost: there is nothing to attach a title or click handler to. With 100 points the DOM cost is small either way; the benefit grows with tens of thousands.

**Expected:** One Canvas can draw many points without one DOM node per point.

## Exercise 2: Change device pixel ratio while retaining logical positions.

Do not apply the ratio twice to pointer coordinates or mark positions. The canvas bitmap is 600 * ratio by 320 * ratio, capped at ratio 2, and context.setTransform(ratio, 0, 0, ratio, 0, 0) lets drawing code keep using 600 by 320 logical units. Multiplying point positions by ratio as well would place them at double scale off the right edge. Compare a screenshot at zoom 100% and 200%.

**Expected:** The plot geometry stays the same size while bitmap resolution changes.

## Exercise 3: Draw 100 bounded points and a textual summary.

A bitmap alone is not an accessible data representation. Provide the information needed for the analytical task outside pixels. The grid places point i at x 30 + (i % 10) * 58 and y 25 + floor(i / 10) * 30, all within 600 by 320. The canvas has role img and an aria-label, and a paragraph states the count. The checks confirm 100 rows and that tree.find(31, 26) returns record 0.

**Expected:** The Canvas is visible and the count is available as text.

## Exercise 4: Diagnose a hit test that selects the wrong point after scaling.

Convert once into the logical coordinate system and query the index there. Random offsets are not a stable repair. If the canvas is displayed at 300 CSS pixels wide, a pointer offsetX of 150 is logical x 300. Divide by the CSS-to-logical ratio before calling tree.find.

**Expected:** Pointer and indexed coordinates use different spaces.

## Exercise 5: Compare transformation and rendering costs.

Canvas can reduce mark rendering overhead while leaving aggregation or layout cost unchanged. Time the data build and the drawing loop separately with performance.now(); for 100 points both are tiny, so switching from SVG would not be justified by speed here.

**Expected:** Measure the actual slow stage before replacing the renderer.

## Exercise 6: Design an accessible large-scatter interface.

Performance and accessibility are joint requirements. A faster unreadable bitmap is not a complete product improvement. Pair the canvas with a filter control and a table of the nearest records so keyboard users reach exact values.

**Expected:** Canvas marks plus keyboard filtering, summary and exact-record access.

## After comparison

Scale the Canvas demo to 10,000 seeded points, time transformation and drawing separately with `performance.now()`, and compare with an SVG version at 1,000 points. Record which stage dominates and whether the quadtree hit test stays fast.
