# viz-008: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

Eight plus three plus one equals twelve. Pending remains a separate observation state; classifying it as failure changes the reported outcome.

## Exercise 2

Use labels, values and patterns alongside color, then provide a caption and semantic table. The table is an exact-value alternative rather than a claim that an ARIA attribute alone guarantees accessibility.

## Exercise 3

Serialize data and layout, reconstruct the figure, and compare count arrays and table rows. A JSON round-trip proves specification preservation, not identical pixels on every browser.

## Exercise 4

If failed changes to two, the total becomes thirteen. Recompute the title/caption or reject the inconsistency before export; a hardcoded denominator can survive correct chart rendering.

## Exercise 5

Inspect narrow width and zoom in the actual browser, including keyboard controls and table reading. Record observable clipping or focus defects; DOM existence is insufficient evidence of usable access.

## Exercise 6

For an effect chart, record outcome units, estimator, interval construction, population, source version and limitations. A source-bound receipt, JSON specification and screenshot establish different evidence and should be labeled separately.

## Solution reasoning

**Approach.** `case_08` records twelve jobs at a stated cutoff: 8 completed, 3 pending and 1 failed. It draws one bar per status with the count printed above each bar, and it uses both distinct colors and distinct patterns, none, diagonal lines and crosses, so the statuses stay distinguishable without color. `describe` adds a caption and a two-column table. The case then serializes the figure with `fig.to_json()`, rebuilds a new figure from the parsed JSON, and prints the specification's byte count and SHA256 hash as a reviewable receipt. The title and caption are literal strings written for these counts, which is why exercise 4 asks what must change when one count changes.

**Why it is correct.** The counts add to 12, matching the title. Pending is kept as its own category rather than merged into failed, so the chart reports what was known at the cutoff. The round-trip assertions read the rebuilt figure: its y values are 8, 3 and 1, they sum to 12, and its stored table rows equal the original's. That proves the exported specification preserves the data and the accessible table. It does not prove identical pixels, which depend on the browser and fonts that render the JSON. Running the case on this machine printed 7,458 bytes, a size well under the 200 KiB limit that `describe` enforces. Printing the count above each bar means a reader who cannot distinguish the patterns can still read the values directly.

**A plausible wrong approach.** A tempting simplification counts pending jobs as failures because they did not complete. The chart would then show 8 completed and 4 failed, which changes the reported outcome even though nothing failed yet. Another error encodes status by color alone, red for failed and green for completed, so readers with red and green color deficiency cannot tell those bars apart. Exercise 4 describes a third: hardcoding 12 in the title, so that when failed becomes 2 the bars show 13 jobs while the title still says twelve. Comparing only the byte count after a round trip would also be weak, because two different specifications can share a size; the hash and the y values are stronger checks.

**How to verify.** Run `.venv/bin/python courses/data-visualization/references/viz-008.py` and confirm the table shows completed 8, pending 3 and failed 1, followed by a line with the specification byte count and its SHA256 hash and then `viz-008 Plotly complete`. Compare the hash with a second run of the same source; it should match because the specification is deterministic. For exercise 4, change failed to 2 and check that the title and caption are recomputed or the build stops. For exercise 5, view the browser variant at a narrow width and 200 percent zoom and note any clipped labels.

## Complete references and evidence

[Python reference](../references/viz-008.py) and [JavaScript reference](../references/viz-008.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
