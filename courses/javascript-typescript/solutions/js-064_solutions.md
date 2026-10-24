# js-064: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

SVG keeps a DOM node for each mark, making styling and interaction convenient. Canvas draws pixels into one bitmap, which can reduce DOM overhead for many simple marks. Canvas does not automatically provide a separate accessible or interactive element for each point. The author must supply semantics and hit testing.

A Canvas has a backing resolution and a CSS display size. Device pixel ratio can make a one-to-one backing bitmap look blurry on high-density screens. Scale the backing dimensions and drawing context deliberately while keeping analytical coordinates in the documented logical space.

Performance depends on data size, transformations, layout, rendering and interactions. Switching to Canvas does not fix an expensive quadratic data algorithm. Measure the slow stage, avoid repeated allocations where appropriate and preserve an accessible data summary or table.

Set canvas.width and height for the backing bitmap, set CSS width and height for display, then transform the context by the device pixel ratio. Draw circles with beginPath, arc and fill. A quadtree can search nearby points efficiently, but its coordinates must match the pointer coordinate space.

The reference draws a bounded grid of 100 points and performs a known nearest-point lookup. It does not benchmark a million records or claim universal Canvas superiority. The SVG is hidden for this lesson because the output is the Canvas plus a textual summary.

## Exercise 1: Predict DOM mark count for a Canvas plot.

The reduced DOM cost comes with extra responsibility for interaction and semantics.

**Expected:** One Canvas can draw many points without one DOM node per point.

## Exercise 2: Change device pixel ratio while retaining logical positions.

Do not apply the ratio twice to pointer coordinates or mark positions.

**Expected:** The plot geometry stays the same size while bitmap resolution changes.

## Exercise 3: Draw 100 bounded points and a textual summary.

A bitmap alone is not an accessible data representation. Provide the information needed for the analytical task outside pixels.

**Expected:** The Canvas is visible and the count is available as text.

## Exercise 4: Diagnose a hit test that selects the wrong point after scaling.

Convert once into the logical coordinate system and query the index there. Random offsets are not a stable repair.

**Expected:** Pointer and indexed coordinates use different spaces.

## Exercise 5: Compare transformation and rendering costs.

Canvas can reduce mark rendering overhead while leaving aggregation or layout cost unchanged.

**Expected:** Measure the actual slow stage before replacing the renderer.

## Exercise 6: Design an accessible large-scatter interface.

Performance and accessibility are joint requirements. A faster unreadable bitmap is not a complete product improvement.

**Expected:** Canvas marks plus keyboard filtering, summary and exact-record access.
