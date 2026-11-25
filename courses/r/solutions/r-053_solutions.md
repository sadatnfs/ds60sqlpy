# r-053: reference reasoning

Run the [complete reference](r-053_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference tests both mapping and constant-setting behavior rather than checking only that a ggplot object exists. The summary layer has independent data and explicitly controlled inheritance, making its numerical role inspectable.

Only two plots are printed. The built-data checks establish row/group/coordinate properties, while the actual classroom renderer must still be inspected for visual quality and delivery. No browser success is inferred from a bare Rscript pass.

## Explained practice

### Exercise 1

Map group to colour and shape for the four-row fixture.

The built point layer contains four observations and two encoded group identities.

**Expected evidence:** Four marks and two categories.

**Approach:** Put colour = group and shape = group inside the global aes, add geom_point, and set the two hex values with scale_colour_manual.

**Why it holds here:** group is a factor with levels A and B, so the scale maps the two A rows to #0072B2 and the two B rows to #D55E00. Mapping shape as well gives a second cue that survives a grayscale print.

**Tempting mistake:** Writing geom_point(colour = group) outside aes. The layer looks for an object called group in the calling environment, not in d, and stops with object group not found.

**Verify:** `nrow(b)` returns 4, and `length(unique(b$colour))` and `length(unique(b$shape))` both return 2.

### Exercise 2

Set a constant point colour outside aes and compare it with a group mapping.

The constant setting gives one colour to every row, while a group mapping uses a scale.

**Expected evidence:** One fixed colour versus two mapped colours.

**Approach:** Pass colour = "#0072B2" as an argument to geom_point, outside aes, in a second plot called constant.

**Why it holds here:** An argument outside aes is a setting, so every one of the four rows gets the same blue and no legend is created. The mapped plot instead sends group through a scale, which is what produces two colours and a legend.

**Tempting mistake:** Writing aes(colour = "#0072B2"). ggplot treats the hex string as a category, draws all points in the default hue for a single level, which is not blue, and adds a legend titled with the hex code.

**Verify:** `length(unique(ggplot2::ggplot_build(constant)$data[[1]]$colour))` returns 1, while the same expression for mapped returns 2.

### Exercise 3

Add a group-mean layer using its own data.

The layer has two rows with response means 2 and 4, separate from the four raw observations.

**Expected evidence:** Correct layer-specific row counts and coordinates.

**Approach:** Build means with aggregate(cbind(x, y) ~ group, d, mean), then add geom_point(data = means, aes(x, y), inherit.aes = FALSE) with a fixed black cross.

**Why it holds here:** Group A holds x = 1, 2 and y = 1, 3, so its mean point is (1.5, 2). Group B holds x = 3, 4 and y = 2, 6, giving (3.5, 4). The second layer therefore has exactly two rows, separate from the four raw points.

**Tempting mistake:** Adding geom_point(aes(y = mean(y))) to the raw data. The aesthetic is evaluated over all four rows at once, so it draws four marks at the overall mean 3 instead of two marks at 2 and 4.

**Verify:** `nrow(layers[[2]])` returns 2 and `sort(layers[[2]]$y)` returns 2 and 4.

### Exercise 4

Diagnose aes(colour="group") when the intended mapping is the group column.

The quoted string is one mapped category, not the data column. Use aes(colour=group) for variable mapping.

**Expected evidence:** Literal-versus-variable distinction stated.

**Approach:** Read aes(colour = "group") as a constant string being mapped, and replace it with the bare column name, aes(colour = group).

**Why it holds here:** Inside aes a quoted value is one literal repeated for every row, so all four points share one level called group and one colour. The bare name refers to the column, whose two levels give two colours.

**Tempting mistake:** Moving the quoted string outside aes as geom_point(colour = "group"). That turns it into a setting, and since group is not a colour name the build fails instead of showing the categories.

**Verify:** `length(unique(ggplot2::ggplot_build(literal)$data[[1]]$colour))` returns 1, compared with 2 for the mapped plot.

### Exercise 5

Print a plot object from a script or function.

The explicit call emits the graphic through the active device rather than merely storing an object.

**Expected evidence:** A rendered figure request occurs.

**Approach:** Store each plot in an object and call print(mapped) and print(layered) explicitly.

**Why it holds here:** A ggplot object is only a description until it is printed. Top level autoprinting does not happen inside a function body, a for loop, or a file run with source and default arguments, so explicit print is what reaches the device.

**Tempting mistake:** Looping with `for (g in list(mapped, layered)) g`. The loop evaluates each object and discards it, so the device stays blank and the script still exits cleanly.

**Verify:** Running the reference under Rscript shows two pages in the output device, one for each print call.

### Exercise 6

Explain what ggplot_build checks cannot establish about the delivered image.

Correct marks and groups do not prove readable labels, sufficient contrast or absence of clipping in the browser.

**Expected evidence:** Data and visual evidence separated.

**Approach:** Keep the build assertions and add a visual review of the delivered image as a separate step.

**Why it holds here:** ggplot_build confirms four marks, two colours, two shapes and mean coordinates 2 and 4. It would pass in the same way if the axis titles still read x and y, as they do in mapped, or if the crosses hid a raw point.

**Tempting mistake:** Treating the colourblind friendly pair #0072B2 and #D55E00 as proof of accessibility. The palette helps, but legend size, label text and contrast against the panel background can only be judged on the rendered figure.

**Verify:** A browser screenshot shows the legend keys, axis titles and black crosses legible at classroom size.

## What the checks establish

The assertions confirm that the mapped plot builds four points with two colours and two shapes, that a constant colour set outside `aes()` produces one colour, that a mean layer with its own data adds two points at 2 and 4 beside the four raw points, and that `aes(colour = "group")` yields a single colour because it maps a literal string. They inspect built data, not the rendered image.

The reference makes 4 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
