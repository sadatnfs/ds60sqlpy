# r-051: reference reasoning

Use the [complete reference](r-051_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference produces at most two graphics: one in the caller's active device and one in an owned temporary PNG device. It checks the underlying pairs and explicit coordinate range, then separately validates file structure and cleanup.

The row-order example is numerical so the cause of a misleading connected line is inspectable without relying on an image. Actual classroom delivery and readability still require the browser/figure acceptance workflow; a successful Rscript exit does not establish those observations.

## Explained practice

### Exercise 1

Draw the five paired observations with labeled axes.

A scatterplot establishes the coordinate system and identifies the measured quantities.

**Expected evidence:** One labeled base plot.

**Approach:** Call plot on d$x and d$y with xlab, ylab and main set, so the high level call opens the page and fixes the coordinates.

**Why it holds here:** The five pairs (0, 0) through (4, 8) are the measured quantities, and naming the axes Input value and Response value tells a reader which is which before any rule is drawn.

**Tempting mistake:** Starting with points or abline on a fresh device. Low level functions need an existing plot, so R stops with plot.new has not been called yet.

**Verify:** `all(d$y == 2 * d$x)` returns TRUE, and the device shows five filled points with both axis titles.

### Exercise 2

Overlay the rule y=2x without starting another plot.

The overlay shares the established axes and passes through the authored points.

**Expected evidence:** Correct shared-coordinate overlay.

**Approach:** Add the rule with abline(a = 0, b = 2) on the same plot.

**Why it holds here:** abline draws in the coordinates plot already set, so the line from (0, 0) to (4, 8) passes through every observed pair. That agreement is visible because the data were generated as y = 2x.

**Tempting mistake:** Drawing the rule with a second plot call such as `plot(d$x, 2 * d$x, type = "l")`. That opens a new page, so the points disappear and the line is never compared with them.

**Verify:** The device shows one line passing through all five points on a single panel.

### Exercise 3

Set and inspect exact limits 0:4 and 0:8.

With xaxs/yaxs set to i, par("usr") matches the four declared bounds.

**Expected evidence:** Expected coordinate limits.

**Approach:** Pass xlim = c(0, 4), ylim = c(0, 8) together with xaxs = "i" and yaxs = "i", then read par("usr").

**Why it holds here:** The "i" style uses the limits exactly, so the plotting region runs from 0 to 4 across and 0 to 8 up, which is what the coordinate check expects.

**Tempting mistake:** Setting the limits but keeping the default "r" style. R then pads each range by 4 percent, so usr becomes about -0.16 to 4.16 and -0.32 to 8.32, and an exact comparison fails.

**Verify:** `max(abs(par("usr") - c(0, 4, 0, 8))) < 1e-12` returns TRUE.

### Exercise 4

Diagnose connecting unsorted rows in a time-series line.

lines follows supplied order. Sort by the declared time variable or use an appropriate grouping/order rule before implying a trajectory.

**Expected evidence:** Ordering defect and repair identified.

**Approach:** Order the rows by time with `unsorted[order(unsorted$time), ]` before passing them to lines.

**Why it holds here:** lines joins points in the order supplied. The rows arrive as times 3, 1 and 2, so the path would run from time 3 back to 1 and then forward to 2, which is not a trajectory.

**Tempting mistake:** Trusting the picture to reveal the problem. These three values sit exactly on value = 10 times time, so the backtracking path overlaps itself and looks like a clean line; only the order check exposes it.

**Verify:** `ordered$time` returns 1, 2, 3 and `ordered$value` returns 10, 20, 30.

### Exercise 5

Create, close and validate an owned PNG tempfile.

The file has a valid PNG signature and is removed by scoped cleanup; unrelated devices remain owned by their callers.

**Expected evidence:** Actual file evidence and scoped cleanup.

**Approach:** Open png on a tempfile, record its device number, register cleanup with on.exit, draw, call dev.off, and only then read the first 8 bytes.

**Why it holds here:** The PNG is complete only after dev.off. Its first bytes, 137 80 78 71 13 10 26 10, mark a real PNG file, and the cleanup closes the owned device only if it is still current before removing the file.

**Tempting mistake:** Reading the bytes before dev.off, which can find an empty or partial file, or cleaning up with graphics.off, which also closes devices the caller opened.

**Verify:** `readBin(path, "raw", n = 8)` returns the 8 signature bytes inside the function, and `file.exists(removed)` returns FALSE afterward.

### Exercise 6

Distinguish numerical, file and browser evidence for the graphic.

Data assertions check values, signature checks file structure, and a browser inspection checks delivery/readability. None automatically substitutes for the others.

**Expected evidence:** Three evidence layers stated.

**Approach:** List the three checks separately: assertions on d, the signature and size of the PNG file, and a browser view of the delivered figure.

**Why it holds here:** The assertions confirm y = 2x and the coordinate range. The signature confirms the file is a PNG. Neither says whether the axis labels are legible or the line color is distinguishable on the page.

**Tempting mistake:** Treating a clean Rscript exit as proof that the figure works for students. The script can pass while labels overlap or the image fails to load in the classroom.

**Verify:** Running the reference prints r-051 reference checks passed, and a separate browser screenshot shows the labels readable.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
