# r-057: reference reasoning

Use the [complete reference](r-057_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference inspects resolved traces rather than only checking an object class. Observed data and a comparison rule have separate names, and the bar example preserves category identity with precomputed heights. A row-order control shows why line connections need an explicit sequence.

Exactly two Plotly figures are printed. The prepared worker can capture their JSON specifications offline; browser delivery, zoom, hover and accessibility remain separate visual/interaction checks.

## Explained practice

### Exercise 1

Construct one marker trace from the three observed pairs.

The trace contains the three source coordinates without an implied connecting trajectory.

**Expected evidence:** Three markers with exact values.

**Approach:** Call plot_ly on d with x = ~x, y = ~observed, type = "scatter" and mode = "markers", and name the trace Observed.

**Why it holds here:** The three pairs (1, 2), (2, 4) and (3, 3) are separate measurements. Markers show each one without suggesting that the response moved smoothly from one input to the next.

**Tempting mistake:** Drawing the observations with add_lines. The segment from 4 down to 3 then reads as a measured decline between inputs 2 and 3, which no observation supports.

**Verify:** `as.numeric(built$x$data[[1]]$y)` returns 2, 4, 3, and `built$x$data[[1]]$mode` returns "markers".

### Exercise 2

Add and name the rule y=2x as a line trace.

The second trace has values 2,4,6 and a distinct explanatory name.

**Expected evidence:** Two identifiable traces.

**Approach:** Add the rule with add_lines(p, y = ~rule, name = "Rule: 2x"), which reuses x from the plot_ly call.

**Why it holds here:** The rule column holds 2, 4 and 6, so the line agrees with the observations at inputs 1 and 2 and sits 3 above the observed value at input 3. A separate named trace keeps that modeled comparison distinct from the data.

**Tempting mistake:** Adding the rule as a second unnamed marker trace. It shares the marker style, and the legend falls back to a generic trace label, so a reader cannot tell which points were measured.

**Verify:** `length(built$x$data)` returns 2, and `as.numeric(built$x$data[[2]]$y)` returns 2, 4, 6.

### Exercise 3

Set axis titles through layout.

The layout identifies the x and y quantities while trace coordinates remain unchanged.

**Expected evidence:** Correct labels and unchanged data.

**Approach:** Pass xaxis = list(title = "Input") and yaxis = list(title = "Response") to layout.

**Why it holds here:** Without them plotly titles the axes from the formulas, so the y axis would read observed even though it also carries the rule. layout changes the labels without touching any trace values.

**Tempting mistake:** Renaming the data columns to carry display text, such as a column called Response value. Every formula and check then has to quote that name, and the label is still tied to one trace rather than the axis.

**Verify:** `as.numeric(built$x$data[[1]]$y)` still returns 2, 4, 3 after layout, and the rendered figure shows Input and Response as axis titles.

### Exercise 4

Diagnose an unsorted line trace.

A line follows supplied order; sort or group under a declared trajectory contract before connecting observations.

**Expected evidence:** Ordering repair identified.

**Approach:** Reorder whole rows with `unsorted[order(unsorted$x), ]` before using a trace that connects points in row order, such as mode = "lines" or add_paths.

**Why it holds here:** The rows arrive as x = 3, 1, 2 with y = 6, 2, 4, so a row order path runs from (3, 6) back to (1, 2) and then to (2, 4). add_lines sorts by x for you, but the other connectors do not, so the order should be declared rather than assumed.

**Tempting mistake:** Sorting only the x column with sort(unsorted$x). The pairs become (1, 6), (2, 2) and (3, 4), so the line connects values that were never observed together.

**Verify:** `ordered$x` returns 1, 2, 3 and `ordered$y` returns 2, 4, 6.

### Exercise 5

Build a bar figure from the supplied count table and inspect its values.

Trace coordinates preserve category names and 2,1,3 heights.

**Expected evidence:** Exact bar data.

**Approach:** Map category to x and count to y on the counts table with type = "bar", and keep zero on the y axis with `rangemode = "tozero"`.

**Why it holds here:** counts already holds one row per category with heights 2, 1 and 3. A bar trace draws those values as given, and the character categories keep the order A, B, C in which they appear.

**Tempting mistake:** Using type = "histogram" with x = ~category. The histogram counts rows, and each category occurs once in counts, so every bar has height 1.

**Verify:** `as.character(b$x)` returns "A", "B", "C", and `as.numeric(b$y)` returns 2, 1, 3.

### Exercise 6

Explain what explicit printing and figure-specification checks establish.

Printing requests capture; data checks validate the specification. Actual browser rendering and interactions need separate observation.

**Expected evidence:** Evidence boundaries retained.

**Approach:** Record what each check covers: plotly_build confirms the trace values, print(p) and print(bar) request the two figures for capture, and the browser view confirms what students see.

**Why it holds here:** The built specification proves two traces with 2, 4, 3 and 2, 4, 6 and a bar trace with 2, 1, 3. It cannot show whether plotly.js loads on the classroom page, or whether hover, zoom and the legend respond.

**Tempting mistake:** Treating the closing cat line as proof that the interactive page works. The script reaches that line even when the widget later fails to load its JavaScript in the browser.

**Verify:** The reference prints r-057 reference checks passed, and a separate browser session shows both figures with working hover text.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
