# js-046: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A scale maps values from a data domain to a visual range. A linear scale preserves proportional differences: equal changes in input produce equal changes in output. The domain is expressed in data units, while the range can be pixels or SVG coordinates. Mixing those spaces is a common source of invisible or misleading marks.

A vertical quantitative scale often has range `[bottom, top]` because SVG y increases downward. This reversal makes larger values appear higher. A band scale maps categories to discrete bands and provides a bandwidth for bars. The category order is an explicit design decision.

Bars encode magnitude by length, so a zero baseline is usually essential. A line chart can sometimes use a narrower vertical domain if the axis clearly communicates it and the analytical purpose warrants it. Log scales require positive values in an ordinary positive domain; zero cannot be inserted casually. Explain the scale choice as part of the claim.

A linear scale is callable: `x(5)` returns a coordinate. Its `.invert(pixel)` maps a coordinate back to data, useful for interactions. `.clamp(true)` bounds output to the range but can hide out-of-domain values if used without a clear policy. `.nice()` adjusts domain endpoints for readable ticks; it does not modify the raw data.

For the example, domain `[0, 10]` and range `[40, 600]` maps 0 to 40, 5 to 320 and 10 to 600. The zero-origin formula is simple enough to check by hand before relying on the library.

## Exercise 1: Predict midpoint and endpoint positions.

The scale maps data space into visual space. These exact cases catch a reversed or incorrectly offset range.

**Expected:** 0 maps to 40, 5 to 320 and 10 to 600.

## Exercise 2: Reverse a vertical range.

The data order stays the same while the coordinate direction reverses. Explain this before changing bar y and height formulas.

**Expected:** Higher values move upward in SVG coordinates.

## Exercise 3: Build a scale-based bar chart.

Use y(0)-y(value) for positive bar height rather than treating a coordinate as a magnitude.

**Expected:** Bar geometry derives from a zero baseline and a named domain.

## Exercise 4: Diagnose using y(value) as bar height.

A vertical coordinate measures from the SVG origin. A bar height measures the distance from its baseline.

**Expected:** Position and length were confused.

## Exercise 5: Handle an unknown band category.

An undefined mapping should not silently remove a category. Keep the category domain aligned with the intended dataset.

**Expected:** Reject or explicitly extend the domain rather than emit undefined geometry.

## Exercise 6: Defend a scale choice for signed residuals.

Scale design should expose the analytical reference point. A zero baseline has a different role for signed residual position than for positive bar length.

**Expected:** A diverging domain with visible zero and explicit units.
