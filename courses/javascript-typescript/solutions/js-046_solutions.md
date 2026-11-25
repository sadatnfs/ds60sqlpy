# js-046: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

A scale maps values from a data domain to a visual range. A linear scale preserves proportional differences: equal changes in input produce equal changes in output. The domain is expressed in data units, while the range can be pixels or SVG coordinates. Mixing those spaces is a common source of invisible or misleading marks.

A vertical quantitative scale often has range `[bottom, top]` because SVG y increases downward. This reversal makes larger values appear higher. A band scale maps categories to discrete bands and provides a bandwidth for bars. The category order is an explicit design decision.

Bars encode magnitude by length, so a zero baseline is usually essential. A line chart can sometimes use a narrower vertical domain if the axis clearly communicates it and the analytical purpose warrants it. Log scales require positive values in an ordinary positive domain; zero cannot be inserted casually. Explain the scale choice as part of the claim.

A linear scale is callable: `x(5)` returns a coordinate. Its `.invert(pixel)` maps a coordinate back to data, useful for interactions. `.clamp(true)` bounds output to the range but can hide out-of-domain values if used without a clear policy. `.nice()` adjusts domain endpoints for readable ticks; it does not modify the raw data.

For the example, domain `[0, 10]` and range `[40, 600]` maps 0 to 40, 5 to 320 and 10 to 600. The zero-origin formula is simple enough to check by hand before relying on the library.

## Exercise 1: Predict midpoint and endpoint positions.

The scale maps data space into visual space. These exact cases catch a reversed or incorrectly offset range. The scale in this task has domain `[0, 10]` and range `[40, 600]`, so each unit is 56 pixels: 0 to 40, 5 to 320, 10 to 600. Forgetting the 40 offset would map 0 to 0, 5 to 280 and 10 to 560. Call the scale on all three values and compare.

**Expected:** 0 maps to 40, 5 to 320 and 10 to 600.

## Exercise 2: Reverse a vertical range.

The data order stays the same while the coordinate direction reverses. Explain this before changing bar y and height formulas. The reference y has domain [0, 10] and range [300, 30], so y(0) is 300 and y(10) is 30; larger values sit higher. Using range `[30, 300]` would put 10 at the bottom. The check y(0) === 300 && y(10) === 30 catches the reversal.

**Expected:** Higher values move upward in SVG coordinates.

## Exercise 3: Build a scale-based bar chart.

Use y(0)-y(value) for positive bar height rather than treating a coordinate as a magnitude. With y(0) = 300, A (2) sits at y 246 with height 54, B (5) at 165 with height 135 and C (8) at 84 with height 216. The band scale over `[60, 600]` with padding 0.2 gives each bar width 135. Verify heights are positive and proportional to 2:5:8.

**Expected:** Bar geometry derives from a zero baseline and a named domain.

## Exercise 4: Diagnose using y(value) as bar height.

A vertical coordinate measures from the SVG origin. A bar height measures the distance from its baseline. Using y(value) as height gives A 246 and C 84, so the smallest value draws the tallest bar. Compute y(0) - y(value) and confirm the heights increase with value.

**Expected:** Position and length were confused.

## Exercise 5: Handle an unknown band category.

An undefined mapping should not silently remove a category. Keep the category domain aligned with the intended dataset. x("D") returns undefined because D is not in the domain, and the rect's x attribute becomes invalid. Check rows against x.domain() before drawing and throw on a missing name.

**Expected:** Reject or explicitly extend the domain rather than emit undefined geometry.

## Exercise 6: Defend a scale choice for signed residuals.

Scale design should expose the analytical reference point. A zero baseline has a different role for signed residual position than for positive bar length. Residuals around 0 need a domain such as [-5, 5] with a visible zero line; starting at the minimum hides the sign. Confirm the zero line sits at the scale's midpoint.

**Expected:** A diverging domain with visible zero and explicit units.

## After comparison

Replace the linear scale with `scaleLog` for values from 1 to 10,000 and decide what to do with zero, which a log scale cannot map. Draw both versions of the chart and write one sentence on when each scale misleads.
