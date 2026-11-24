# r-059: reference reasoning

Use the [complete reference](r-059_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference strengthens coordinate-set checks by comparing paired x/y keys, so a permutation of y values cannot pass merely because the marginal coordinate sets match. It separately counts marker observations and auxiliary line geometry.

Only the static baseline and one converted widget are printed. Their payload checks establish the stated supported conversion, while the final visual and interaction contract still requires browser inspection. This is not a blanket compatibility claim for every ggplot extension.

## Explained practice

### Exercise 1

Translate the supported scatterplot and inspect marker traces.

The marker payload retains the source coordinates; do not count line or auxiliary traces as additional observations.

**Expected evidence:** Four retained markers.

**Approach:** Convert p with ggplotly, build it, and keep only scatter traces whose mode contains markers before collecting x and y.

**Why it holds here:** Mapping colour to group splits the four points into two marker traces, A with (1, 1) and (2, 3) and B with (3, 2) and (4, 6). The observations are the points inside those traces, not the traces themselves.

**Tempting mistake:** Counting the entries of the built data list as observations. This plot yields 2, one per colour, and a plot with a reference line yields more, so the count tracks legend entries rather than rows of d.

**Verify:** `length(traces)` returns 2, and `length(pairs)` returns 4.

### Exercise 2

Compare paired coordinates rather than only independent sorted x and y values.

Matching paired coordinate keys detects a permutation that separately matching coordinate sets could miss.

**Expected evidence:** Pair identity preserved.

**Approach:** Join each marker's x and y into one key with paste(x, y, sep = ":") and compare the sorted keys with the same keys built from d.

**Why it holds here:** d holds the pairs 1:1, 2:3, 3:2 and 4:6. A key keeps each response attached to its input, so a translation that shuffled responses between inputs would no longer match.

**Tempting mistake:** Comparing sort(xs) with sort(d$x) and sort(ys) with sort(d$y) separately. If the first two responses were swapped, giving pairs 1:3 and 2:1, both sorted vectors would still be 1, 2, 3, 4 and 1, 2, 3, 6, so the check would pass.

**Verify:** `identical(sort(pairs), sort(paste(d$x, d$y, sep = ":")))` returns TRUE.

### Exercise 3

Add a mean reference line and inspect the translated structure.

The result contains extra trace geometry without adding source observations.

**Expected evidence:** Four markers and at least one additional trace.

**Approach:** Add geom_hline at mean(d$y), convert it again, and count markers only in traces whose mode contains markers.

**Why it holds here:** The responses sum to 12, so the dashed line sits at 3. ggplotly draws it as an extra line trace across the panel, which adds geometry and x values but no observations.

**Tempting mistake:** Summing the length of x over every trace. The line trace contributes its own x values, so the total exceeds 4 and the reference line is counted as data.

**Verify:** `marker_count` returns 4, and `length(all_traces) >= 3` returns TRUE.

### Exercise 4

Choose a bounded tooltip field set.

Avoid exposing unrelated implementation fields; test actual tooltip readability in the browser.

**Expected evidence:** An explicit tooltip contract.

**Approach:** Pass tooltip = c("x", "y", "group") so the hover shows only the input, the response and the group for each point.

**Why it holds here:** Those three fields identify a point in this fixture. The tooltip labels come from the variable names x, y and group rather than the axis titles Input and Response, so readable wording must be supplied deliberately, for example through a text aesthetic.

**Tempting mistake:** Leaving the default of all mapped aesthetics. In a richer plot that also exposes fields such as size or alpha, which mean nothing to a reader, and it still does not show the axis titles.

**Verify:** `grepl("group: A", traces[[1]]$text[1], fixed = TRUE)` returns TRUE, and a browser hover shows whether that wording is readable.

### Exercise 5

Diagnose claiming complete visual equivalence from a successful conversion call.

Legend ordering, clipping, facets, themes, hover, keyboard interaction and final size still require visual/interaction checks.

**Expected evidence:** No unsupported parity claim.

**Approach:** List the properties the conversion call does not establish and check them on the two printed figures side by side.

**Why it holds here:** The payload checks confirm four points with the right pairs. They say nothing about legend order, whether size 3 becomes a comparable marker size, whether the Group legend title and axis titles carry over, or how the widget fits its container.

**Tempting mistake:** Stating that the interactive figure matches the static one because ggplotly returned without error. Conversion can succeed while dropping or restyling parts of the ggplot specification.

**Verify:** Viewing print(p) and print(interactive) together in a browser shows any difference in legend order, marker size or titles.

### Exercise 6

Choose direct Plotly construction when translation obscures the intended interaction.

A direct trace specification can make IDs, controls and payloads easier to validate when automatic translation does not preserve the required contract clearly.

**Expected evidence:** A justified implementation choice.

**Approach:** Build the figure directly with plot_ly when the interaction needs IDs, named traces or buttons with known positions.

**Why it holds here:** This fixture has no ID column, and ggplotly decides how many traces to create and in which order. A direct specification fixes both, so customdata and visibility vectors can be checked against an intended layout.

**Tempting mistake:** Patching the converted widget by index, such as editing the third entry of its data list. The index depends on how the translator split the layers, so the edit can land on the wrong trace after a change to the ggplot.

**Verify:** A direct plot_ly version with two add_trace calls returns exactly 2 traces from plotly_build.

## What the checks establish

The reference makes 4 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
