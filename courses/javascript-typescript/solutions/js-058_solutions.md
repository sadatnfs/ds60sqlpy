# js-058: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

Zoom changes the mapping between data space and the visible viewport. A transform typically contains a scale factor and translation. Panning changes which portion of the data is visible; it does not change the underlying observations. Keep the original scale and data separate from the transformed view.

Simply scaling an SVG group can also enlarge text and marker sizes, which may or may not be intended. Rescaling an axis from the zoom transform can preserve readable labels while changing the displayed data domain. Clipping keeps marks within the intended plot region.

A usable zoom interface needs bounds and a reset. Pointer gestures can conflict with page scrolling, so test the actual browser behavior. Keyboard controls or preset views provide an alternative to wheel and drag gestures. Never use zoom to conceal a misleading initial domain.

`event.transform.rescaleX(baseScale)` creates a scale for the transformed horizontal view. Use that same scale for marks and axis ticks. The base scale remains unchanged so reset has a stable reference.

Set explicit extent and scaleExtent for predictable behavior. The reference applies a known transform programmatically, checks the visible domain narrows and then resets. This establishes the transformation logic; manual interaction acceptance still includes pointer and keyboard behavior.

## Exercise 1: Predict transformed coordinate 100.

Transform order is encoded by the D3 transform representation. Test a known value before applying it to all marks. D3 applies scale then translate: k * x + tx, so 2 * 100 - 100 = 100. Translating first would give (100 - 100) * 2 = 0. Call d3.zoomIdentity.translate(-100, 0).scale(2).applyX(100) to confirm.

**Expected:** 100 under translation-100 and scale 2.

## Exercise 2: Compare original and zoomed domains.

Zoom is a view state. Mutating the base repeatedly can accumulate errors and make reset unreliable. With translate(-60, 0).scale(2), rescaleX maps the range `[60, 590]` back through the transform, giving a view domain of [0, 5] while base stays [0, 10]. Assigning base = view on each zoom would compound the change. The reference checks the view span is under 10 and base is still "0,10".

**Expected:** The view domain narrows while the base domain stays unchanged.

## Exercise 3: Implement linked mark and axis zooming.

A moving chart with a stale axis gives false numeric meaning. Treat axis updates as part of the interaction contract. In the zoom handler, the reference sets every circle's cx with view and calls axisBottom(view) in the same step. Updating only the circles would leave ticks reading 0 to 10 over data that now spans 0 to 5. Read the first and last tick labels after zooming.

**Expected:** Both use the same rescaled view.

## Exercise 4: Diagnose enlarged labels after scaling the whole group.

Decide which visual properties should stay constant. Rescale positions and redraw axes when readable text is the goal. Applying event.transform as an SVG transform on a group scales circles and tick text by 2 as well. Rescale x positions and redraw the axis so 5-pixel radii stay 5.

**Expected:** Geometry and text were transformed together.

## Exercise 5: Add a native reset button.

Reset should use the stable base transform, not infer an inverse from partially mutated state. "Reset zoom" applies d3.zoomIdentity, which makes view equal to base again; the check confirms "0,10". Undoing by dividing the current domain would accumulate rounding.

**Expected:** The initial domain and mark positions are restored.

## Exercise 6: Review zoom for a long time series.

Navigation should help analysis without trapping scrolling or hiding context. Keep an overview or clear current-domain label when needed. With scaleExtent [1, 4], the narrowest view spans 2.5 units of 10; label the current domain so readers know which part of the sine they see. Add Reset zoom near the chart and keep a small overview that shows where the zoomed window sits in the full 0 to 10 range, so wheel scrolling does not strand the reader.

**Expected:** Bounds, clipping, readable ticks and accessible alternate controls.
