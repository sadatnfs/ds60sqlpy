# viz-007: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

The stride keeps multiples of 100, so 2473 is absent. Its maximum is near one even though the full series reaches twelve.

## Exercise 2

Retain minimum and maximum indices from each of 50 blocks plus endpoints, deduplicate and sort. The upper bound is 102 points and the spike remains.

## Exercise 3

Blocks of 250 give 20 blocks and at most 42 retained indices. The global maximum still occurs as the maximum of its containing block.

## Exercise 4

The selected-point mean generally differs from the source mean because extreme values are intentionally overrepresented. Compute both with their own denominators and do not use display reduction for inference.

## Exercise 5

Resize the actual rendered preview, rerun after a source edit, then navigate away. Check for current errors and stale controls. Purge the owned Plotly graph on page exit; do not count a startup marker as interaction evidence.

## Exercise 6

For average utilization, use window means and a meaningful variation summary with the window definition stated. An extrema envelope answers a peak-preservation question instead.

## Solution reasoning

**Approach.** `case_07` builds a 5,000-sample sine wave and sets sample 2473 to 12, far above every other value. It then draws two reduced versions. The regular stride keeps indices 0, 100, 200 and so on. `envelope_indices` splits the series into blocks of 100, keeps the index of the minimum and the maximum in each block, adds the first and last index, and returns the sorted unique set. Both reductions are drawn as named traces over the same sample index axis, the stride one dotted. The browser variant computes the same envelope in `envelopeIndices`, renders with `responsive: true`, and purges the graph when the preview closes.

**Why it is correct.** 2473 is not a multiple of 100, so the stride skips it; its 50 points top out at about 0.945. The spike is the largest value in the block from 2400 to 2499, so the envelope must keep it. With 50 blocks and two indices per block plus two endpoints, the envelope can never exceed 102 points, and running the code gives 101 because some endpoints coincide with block extrema. The assertions check both facts: the spike index is in `keep` and not in `stride`, and the envelope's maximum equals the full series maximum of 12. Sorting the kept indices before drawing matters, because Plotly connects points in array order and an unsorted set would make the line jump backward in time.

**A plausible wrong approach.** A plausible error is to choose the stride because it looks smoother and has fewer points. The line looks like a clean sine wave and hides the one event a reader most needs to see. Another error treats the envelope as a fair sample and reports its mean. Running the case gives a full-series mean of about 0.004 but an envelope mean of about 0.104, because every block contributes its extremes and the spike is kept. Exercise 4 asks you to explain that bias. Using the reduced points for any statistical summary repeats this mistake. Shrinking the stride to every tenth sample only lowers the odds of missing a spike; it still offers no guarantee, and it keeps 500 points instead of about 100.

**How to verify.** Run `.venv/bin/python courses/data-visualization/references/viz-007.py`. The table should show original 5000 points with maximum 12, stride 50 points with maximum near 0.945 and no spike, and envelope 101 points with maximum 12, then `viz-007 Plotly complete`. For exercise 3, call `envelope_indices(y, 250)` and confirm 42 indices and a maximum of 12. For exercise 5, open the browser variant, resize the preview, rerun it after an edit, and leave it, then check the console for errors and that no old chart remains. Compare the two traces visually at the spike: the envelope rises to 12 near index 2473 while the dotted stride line passes through without a bump.

## Complete references and evidence

[Python reference](../references/viz-007.py) and [JavaScript reference](../references/viz-007.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
