# r-055: reference reasoning

Run the [complete reference](r-055_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The fitted-line comparison verifies a real change in the statistic's input data, not only a cosmetic zoom. Its expected removal warning should be interpreted as part of that mechanism. Facet metadata and transformed coordinates supply separate checks for scale behavior.

The reference prints only two plots. Correct layer metadata does not guarantee that the delivered visual comparison is clear, so captions, scales and missing-category policies remain part of the graphical review.

## Explained practice

### Exercise 1

Build the coordinate-zoom and scale-limited fitted-line comparison.

The coordinate zoom retains all four observations in the fit, while the scale limit removes the extreme y value before fitting.

**Expected evidence:** Different fitted numerical layers.

**Approach:** Add coord_cartesian(ylim = c(0, 4)) to base for one plot and scale_y_continuous(limits = c(0, 4)) for the other, then build both and inspect the smoothing layer, data[[2]].

**Why it holds here:** A scale limit is applied before the statistic, so y = 100 becomes missing and lm fits only (1, 1), (2, 2), (3, 3), giving y = x. The coordinate zoom acts after fitting, so lm still sees all four points and fits slope 29.8 and intercept -48.

**Tempting mistake:** Comparing only the two pictures and dismissing the removed rows warning as noise. The warning is the sign that an observation left the fit, not a display message.

**Verify:** `max(ggplot2::ggplot_build(zoom)$data[[2]]$y, na.rm = TRUE)` returns about 71.2, while the same expression for limited returns 3.

### Exercise 2

Choose a zoom that preserves the model-fitting data.

Use coord_cartesian and retain the full-data fit; document any points outside the displayed window.

**Expected evidence:** Model inputs preserved.

**Approach:** Use coord_cartesian for the zoom and state in the caption that the point (4, 100) lies above the window.

**Why it holds here:** The four observations remain the model input. With slope 29.8 the full data line crosses the 0 to 4 band only between x of about 1.61 and 1.75, so the zoom shows a steep sliver of a fit driven by the extreme point, which is honest about the model.

**Tempting mistake:** Using the ylim(0, 4) shortcut, or subsetting d to rows with y at most 4 first. Both remove y = 100 before lm runs, so the window shows a tidy y = x line that the full data never produced.

**Verify:** `max(ggplot2::ggplot_build(zoom)$data[[2]]$y, na.rm = TRUE) > 4` returns TRUE.

### Exercise 3

Compare fixed and free-y facet scale assignments.

Fixed panels share one y-scale assignment; free_y gives one per panel in this fixture.

**Expected evidence:** One versus two scale assignments.

**Approach:** Build fixed and free and read the SCALE_Y column of the panel layout table in each.

**Why it holds here:** Group A spans y 1 to 2 and group B spans 100 to 200. Fixed panels share one y scale running to 200, which flattens A near the floor. free_y gives each panel its own scale.

**Tempting mistake:** Comparing the built layer data. The y values are 1, 2, 100 and 200 in both plots, because facet scales change the panel layout and not the data, so this check finds no difference.

**Verify:** `length(unique(ggplot2::ggplot_build(fixed)$layout$layout$SCALE_Y))` returns 1, and the same expression for free returns 2.

### Exercise 4

Transform positive values 1,10,100 with a log10 x scale.

The built x coordinates are 0,1,2, representing equal ratios as equal spacing.

**Expected evidence:** Expected transformed positions.

**Approach:** Confirm every x is positive, then add scale_x_log10 to the plot of 1, 10 and 100.

**Why it holds here:** log10 sends 1, 10 and 100 to 0, 1 and 2, so equal ratios of 10 become equal steps while the axis still labels the original values. The positivity check matters because a zero would become minus infinity and be dropped.

**Tempting mistake:** Mapping aes(log(x), y) instead. Natural log places the points at 0, 2.30 and 4.61, and the axis shows those logs rather than 1, 10 and 100, so a reader must convert every label back.

**Verify:** `all(positive$x > 0)` returns TRUE, and `ggplot2::ggplot_build(log_plot)$data[[1]]$x` returns 0, 1, 2.

### Exercise 5

Diagnose a new category missing from a named palette contract.

Admit the category with an explicit mapping or reject it under the application contract; do not silently change existing identities.

**Expected evidence:** Unmapped category detected.

**Approach:** Compare the observed labels with names(palette) before plotting, and either add C to the named palette or reject the data under the contract.

**Why it holds here:** The palette fixes A as #0072B2 and B as #D55E00. Since C has no entry, any automatic choice for it is a decision nobody made, and A and B must keep their colours across reports.

**Tempting mistake:** Dropping the manual scale so the default hue scale absorbs C. The default spaces hues by level count, so going from two levels to three recolours A and B as well, and earlier figures no longer match.

**Verify:** `setdiff(c("A", "C"), names(palette))` returns "C".

### Exercise 6

Explain when free scales can mislead a magnitude comparison.

Free scales can make a small and a large range occupy similar panel heights; shared scales or explicit annotation are needed for direct magnitude comparison.

**Expected evidence:** Comparison limit stated.

**Approach:** Before comparing panels, compare the numerical ranges behind each panel's height and decide whether the reader needs shared scales.

**Why it holds here:** Under free_y, A's rise from 1 to 2 and B's rise from 100 to 200 fill the same panel height, so the two slopes look equal although B rises 100 times as far.

**Tempting mistake:** Reading the free panels side by side as a magnitude comparison. Free scales suit shape within a panel; magnitude across panels needs fixed scales or an explicit annotation of each range.

**Verify:** `diff(range(f$y[f$group == "B"])) / diff(range(f$y[f$group == "A"]))` returns 100.

## What the checks establish

The assertions confirm that the zoomed fit still rises above 4 because the extreme row is kept, that the limited fit stays at or below 4 because that row is dropped, that fixed facets share one y scale while free facets get two, that only positive values reach the log axis and 1, 10 and 100 map to 0, 1 and 2, and that a palette missing a category name is detected. They do not judge whether free scales mislead a reader.

The reference makes 7 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
