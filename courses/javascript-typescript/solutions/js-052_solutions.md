# js-052: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A summary reduces a distribution to selected quantities. The median is a central order statistic; quartiles describe the middle part of the distribution. A box plot communicates chosen quantiles and whisker rules, which must be stated because conventions differ. It does not preserve every feature of the raw observations.

An uncertainty interval describes uncertainty about a parameter under a statistical procedure and assumptions. It is not the same as the spread of individual observations. A box showing sample quartiles and an interval around a mean answer different questions. Label both the statistic and the interval method when presenting estimates.

The lesson uses tiny synthetic samples to make quartiles and interval endpoints inspectable. It does not claim a confidence interval from an arbitrary pair of numbers. A visualization may render a supplied estimate and bounds correctly while the upstream statistical method is invalid; those checks remain separate.

Sort numerical values before using a function that assumes sorted input. `d3.quantileSorted` computes a quantile of an ordered array. For `[1, 2, 3, 4, 5]`, median is 3 and the first and third quartiles are 2 and 4. A simple box can map those values to x positions, with a median line inside.

For a supplied interval, check lower <= estimate <= upper before drawing a segment and point. If the interval spans zero, that visual fact should not be hidden by a truncated axis. The statistical interpretation still depends on the stated estimator and procedure.

## Exercise 1: Predict the three quantiles.

The small ordered input makes the definition visible. Different quantile conventions should be documented when comparing tools.

**Expected:** 2, 3, 4 for the stated five-value sample.

## Exercise 2: Add an extreme value and recompute.

A summary is a function of data. Inspect how much information the box retains and which tail behavior it hides.

**Expected:** Quantiles and the visible range change according to the new sample.

## Exercise 3: Draw a labeled box and median.

The geometry should encode actual statistics, not decorative percentages of chart width.

**Expected:** The box endpoints map to Q1 and Q3 and the line maps to median.

## Exercise 4: Diagnose calling an unsorted-only contract incorrectly.

A function with a sorted-input precondition can return misleading values when that precondition is violated. The data pipeline owns the guarantee.

**Expected:** Sort a copy before quantileSorted.

## Exercise 5: Distinguish individual spread from estimate uncertainty.

They are not interchangeable error bars. Name the population quantity and method behind any inferential interval.

**Expected:** Quartiles describe observations; a confidence interval concerns an estimator.

## Exercise 6: Design a comparison of two estimated effects.

Visual overlap alone is not a complete hypothesis test. Explain the actual comparison procedure separately.

**Expected:** Show estimates, interval method, units and a meaningful zero reference.
