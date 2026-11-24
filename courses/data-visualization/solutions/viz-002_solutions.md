# viz-002: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

Use left-closed/right-open bins, with the final upper edge included. Values at three and six enter the next bin. Counts are 4,2,2,2 and sum to ten.

## Exercise 2

Divide each count by ten and its bin width. Heights are 4/30,2/30,2/30,2/40; multiplying by widths and summing gives one.

## Exercise 3

With edges 0,6,13, counts are six and four. Density heights are 6/(10*6) and 4/(10*7), so equal-looking bar heights would not encode the same probability.

## Exercise 4

Replacing missing with zero produces eleven claimed durations and changes all probability denominators. Exclusion with a reported missing count preserves the distinction between unknown and observed zero.

## Exercise 5

Aggregate repeated values first. Counts at one and two are each two, so cumulative fractions are .2 and .4. Prepend an origin below the minimum with probability zero, then use horizontal-vertical steps.

## Exercise 6

Duplicating every observed record doubles counts but leaves a probability density and ECDF unchanged. State sample sizes ten and twenty; equal normalized shapes do not imply equal total volume.

## Solution reasoning

**Approach.** `case_02` starts from eleven raw durations, one of which is `None`. It drops the missing value before any calculation, leaving ten observations, and keeps the count of what was dropped. It then bins the values with the unequal edges 0, 3, 6, 9 and 13 using `np.histogram`, divides each count by the sample size times its own bin width to get a density, and draws bars whose `width` equals the bin width. A second panel builds an empirical CDF from `np.unique(values, return_counts=True)`, prepends the point (0, 0) and draws it with `line_shape="hv"` so each step stays flat until the next observed value.

**Why it is correct.** NumPy's bins are closed on the left and open on the right except the last, so 3 and 6 fall into the next bin and the counts are 4, 2, 2 and 2. Dividing by 10 and by the widths 3, 3, 3 and 4 gives heights of 4/30, 2/30, 2/30 and 2/40, which the reference prints as 0.133, 0.067, 0.067 and 0.05. Multiplying each height by its width and adding gives exactly one, which the `density @ widths` assertion confirms. For the CDF, the repeated values 1 and 2 each contribute two observations, so the fractions at 1 and 2 are 0.2 and 0.4, and the last step reaches 1. The assertion that `len(raw) - len(values) == 1` records the exclusion rather than hiding it.

**A plausible wrong approach.** A plausible mistake is to plot relative frequency, count divided by ten, against unequal bins. That gives heights 0.4, 0.2, 0.2 and 0.2, so the 9 to 13 bin looks as dense as the 3 to 6 bin even though its four-minute width spreads the same two observations more thinly. Heights times widths then sum to 3.2, not 1, so the bars are not a density. A second mistake replaces the missing duration with zero: the sample becomes eleven, the first bin gains a fictitious observation, and every probability changes. A third draws the CDF with straight line segments, which implies observations between the recorded values.

**How to verify.** Run `.venv/bin/python courses/data-visualization/references/viz-002.py` and read the table: lower and upper edges, counts 4, 2, 2, 2 and densities 0.1333, 0.0667, 0.0667 and 0.05, followed by `viz-002 Plotly complete`. Then call `np.histogram(values, bins=edges, density=True)` yourself and confirm it returns the same four heights, which shows the hand-written division matches NumPy's own definition. For exercise 3, change the edges to 0, 6 and 13 and confirm counts of six and four. For exercise 6, duplicate every record and confirm the density and the CDF are unchanged while the stated sample size doubles to twenty. Finally, hover the last CDF step and check that it reads 1 at 12.

## Complete references and evidence

[Python reference](../references/viz-002.py) and [JavaScript reference](../references/viz-002.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
