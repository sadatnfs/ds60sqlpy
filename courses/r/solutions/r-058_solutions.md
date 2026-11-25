# r-058: reference reasoning

Run the [complete reference](r-058_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The reference validates the identity metadata and the exact visibility vectors used by the controls. It also compares the full-data and selected-group means to demonstrate why a view change cannot silently inherit a full-data statistical label.

A static table accompanies the figure. The R and worker-capture checks can establish that these structures were emitted, but they cannot prove accessibility or interaction behavior in a browser. Those observations remain part of the separate classroom delivery qualification.

## Explained practice

### Exercise 1

Attach stable observation IDs independently of x/y coordinates.

Each trace retains the IDs belonging to its points even when the data is grouped.

**Expected evidence:** Correct point-associated IDs.

**Approach:** Loop over the groups A and B, subset d for each, and add a trace with customdata = ~id so every point carries its own ID.

**Why it holds here:** Within the B trace the first point is B1, but it is the third row of d. Attaching the ID as data on the point keeps that link no matter how the rows were split into traces.

**Tempting mistake:** Recovering the ID from the hovered point's position. Position 0 in the B trace would look up row 1 of d and report A1 for a point that is really B1.

**Verify:** `as.character(b$x$data[[1]]$customdata)` returns "A1", "A2", and the same expression for trace 2 returns "B1", "B2".

### Exercise 2

Define a hover template with labels and units.

The template identifies ID, input and measured value rather than presenting anonymous numbers.

**Expected evidence:** Readable field contract.

**Approach:** Write a hovertemplate that names each field: ID from customdata, Input from x, Value from y, and the group name in the extra box.

**Why it holds here:** Each point has an x of 1 or 2 and a y from 2 to 6. Labeling the fields tells the reader that 6 is the measured value for B2 at input 2, not an anonymous pair.

**Tempting mistake:** Keeping the default hover, which shows bare coordinates such as (2, 6) with the trace name. The ID that the table and any follow up depend on never appears.

**Verify:** `grepl("%{customdata}", b$x$data[[1]]$hovertemplate, fixed = TRUE)` returns TRUE.

### Exercise 3

Encode All and Group A visibility buttons for two known traces.

All uses TRUE/TRUE and Group A uses TRUE/FALSE.

**Expected evidence:** Correct button argument vectors.

**Approach:** Define the All groups button with visible TRUE, TRUE and the Group A button with TRUE, FALSE, matching the order in which the loop added the traces.

**Why it holds here:** The loop runs over c("A", "B"), so trace 1 is A and trace 2 is B. restyle applies the visibility list by position, so TRUE, FALSE shows A and hides B.

**Tempting mistake:** Changing the loop to unique(d$group) after the data are reordered, or to c("B", "A"), while keeping the buttons. The Group A button would then show group B, and the specification would still look valid.

**Verify:** `unlist(b$x$layout$updatemenus[[1]]$buttons[[2]]$args[[2]])` returns TRUE, FALSE, and `b$x$data[[1]]$name` returns "A".

### Exercise 4

Diagnose a global mean label that remains unchanged when a view hides one group.

A visibility toggle does not automatically recompute the mean. Label it as the full-data mean or implement an explicit selection-dependent calculation.

**Expected evidence:** Denominator/selection semantics clarified.

**Approach:** Name a fixed statistic by its denominator, for example Mean of all four points, or make the button also update the label with a group specific value.

**Why it holds here:** The y values sum to 15, so the overall mean is 3.75. Group A alone has 2 and 3 with mean 2.5. A restyle button only hides traces and never recomputes the label.

**Tempting mistake:** Placing a label Mean: 3.75 on the figure. In the Group A view it then overstates the visible mean by 1.25 while appearing to describe what is shown.

**Verify:** `mean(d$y)` returns 3.75 and `mean(d$y[d$group == "A"])` returns 2.5.

### Exercise 5

Provide a non-hover-dependent table or summary.

A small printed table preserves the core information without requiring pointer interaction.

**Expected evidence:** Static alternative supplied.

**Approach:** Print d next to the figure so the IDs, groups, inputs and values are readable without a pointer.

**Why it holds here:** Four rows are small enough to show in full, and the table gives keyboard, touch and screen reader users the same ID to value pairs that hover offers to mouse users.

**Tempting mistake:** Offering only the hover text, or printing just the two group means. The first hides the IDs from anyone who cannot hover, and the second drops the individual records the figure is about.

**Verify:** `print(d)` shows four rows with IDs A1, A2, B1 and B2 and their values 2, 3, 4 and 6.

### Exercise 6

Explain what remains unverified after inspecting the figure specification in R.

Clicking, keyboard use, hover readability, resizing and assistive-technology behavior require actual browser checks.

**Expected evidence:** No unsupported interaction-success claim.

**Approach:** List the checks the R build cannot perform and assign them to a browser review: clicking each button, keyboard access, hover legibility, resizing and screen reader output.

**Why it holds here:** The build proves the customdata vectors, the template text and the TRUE, FALSE argument. It does not run plotly.js, so it cannot show whether the buttons overlap the legend on a narrow screen or receive keyboard focus.

**Tempting mistake:** Reporting the controls as working because their argument vectors are correct. Correct arguments describe the intent, and only an observed click confirms the effect.

**Verify:** A browser session shows the Group A button hiding B1 and B2, and the page remains usable at a narrow width.

## What the checks establish

The checks confirm two traces carrying ids A1 and A2 and then B1 and B2 as custom data, a Group A button that sets visibility to TRUE and FALSE, an overall mean of 3.75 against a group A mean of 2.5, which is why a fixed global label is wrong in a filtered view, and a text summary that selects the two A rows. They do not test keyboard access or screen reader output.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
