# viz-006: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

For u6, A loss is one and B loss is 2.25, so A minus B equals -1.25. The negative sign favors A under squared loss.

## Exercise 2

Use common observed/predicted limits [0,10] and an identity line. In a second panel, plot each user's loss difference with squared units. The two panels expose different aspects of the same evaluation.

## Exercise 3

Changing B's final error to two changes its loss to four and that paired difference to -3. The new average difference is -.59625.

## Exercise 4

A wider axis compresses visual errors without changing predictions. Restore shared limits before comparing distances, and retain the same observation IDs in both traces.

## Exercise 5

The first four users have mean difference -.115 and the last four -.64. With equal counts their average is -.3775. With unequal groups, recombine using the relevant user weights.

## Exercise 6

Resample customers with all their visits, or aggregate an explicitly defined user-level loss first. Independently resampling visits treats correlated observations as new users and can understate uncertainty.

## Solution reasoning

**Approach.** `case_06` compares two models on the same eight held-out users with observed values 1 to 8. Model A's errors are 0.2, -0.2, 0.5, -0.5, 0.1, -0.1, 1 and -1; model B's are larger in each position. For each user the code computes A's squared error minus B's squared error, so the comparison is paired. The left subplot plots predicted against observed for both models on identical 0 to 10 axes with an identity line, using circles for A and squares for B. The right subplot draws the eight paired differences as bars in squared units.

**Why it is correct.** Every difference is negative, so A has the smaller loss for every user, and the mean difference is -0.3775, which the reference asserts. That number also equals A's mean squared error of 0.325 minus B's of 0.7025, because both models are scored on the same users. Users u6 and u7 have the largest gap, -1.25 each, since A misses by 1 and B by 1.5, giving 1 minus 2.25. Shared axis ranges in the left panel let a reader compare the vertical distance from the identity line directly between models. The identity line is the set of perfect predictions, so every marker's vertical gap from it is that model's error for that user, and B's squares sit farther away in all eight positions.

**A plausible wrong approach.** One plausible error compares mean losses computed on different subsets, such as A on users u0 to u3 and B on u4 to u7. The difference then mixes model quality with user difficulty, and the pairing that makes each bar meaningful is gone. Another error lets Plotly choose separate y ranges for two panels, one per model, so a wider axis visually shrinks B's errors. Exercise 4 asks you to diagnose that. Treating the eight negative bars as proof that A is better for the whole population ignores that eight users are a small sample. Plotting the two models' errors on a pooled histogram would also discard the user pairing.

**How to verify.** Run `.venv/bin/python courses/data-visualization/references/viz-006.py`. The table lists each user with observed, A, B and the paired difference, from about -0.12 for u0 to -1.25 for u6 and u7, then `viz-006 Plotly complete`. For exercise 3, change B's final error from -1.5 to 2, recompute, and confirm that user's difference becomes -3 and the mean becomes -0.59625. For exercise 5, average the first four and last four differences separately to get -0.115 and -0.64, and check their equal-weight average is -0.3775. Hover a bar on the right panel and confirm its user ID matches the row whose difference it shows.

## Complete references and evidence

[Python reference](../references/viz-006.py) and [JavaScript reference](../references/viz-006.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
