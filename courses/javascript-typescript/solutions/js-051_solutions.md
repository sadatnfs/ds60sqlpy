# js-051: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A histogram groups quantitative observations into intervals and displays their counts or density. The bins are numerical intervals, not arbitrary categories. Their boundaries affect the apparent distribution, especially with small samples. A meaningful histogram states the sample, units, domain and binning policy.

A bin usually includes its lower boundary and excludes its upper boundary, except the final bin includes its upper endpoint. This convention prevents double-counting values exactly on a threshold. Values outside the declared domain require a policy and should not disappear without explanation.

Count and density are different vertical quantities. With unequal bin widths, equal counts do not imply equal density. A density histogram uses height proportional to count divided by sample size and bin width, so area represents probability mass. The reference uses equal-width bins and counts to keep the first reasoning explicit.

`d3.bin().domain([0, 10]).thresholds([2, 4, 6, 8])` creates intervals with known edges. Each returned bin is an array of observations with x0 and x1 properties. The count is its length. A rectangle’s width follows x(x1)-x(x0), and its height follows the count scale.

Test boundary values explicitly. The sample `[0, 2, 2, 4, 9, 10]` produces counts `[1, 2, 1, 0, 2]` for the chosen bins. The total count must equal the number of included finite observations. This simple conservation check catches many accidental exclusions.

## Exercise 1: Predict membership of value 2.

The interval convention avoids counting one observation twice at a shared boundary.

**Expected:** It enters the bin whose lower edge is 2.

## Exercise 2: Change thresholds while retaining the data.

Binning is a view of the same observations. A stable count invariant helps distinguish presentation choices from data loss.

**Expected:** The shape changes while included total count remains six.

## Exercise 3: Build the explicit-boundary count histogram.

Use x0 and x1 for geometry rather than assuming all bin indices are data values.

**Expected:** Five bins with counts 1, 2, 1, 0, 2.

## Exercise 4: Diagnose a missing maximum value.

A value equal to the final endpoint should be included under the stated D3 bin contract. Test it separately.

**Expected:** The final boundary convention or declared domain is wrong.

## Exercise 5: Explain unequal-width bin heights.

Raw counts with unequal widths can mislead visual comparisons. Normalize by width and sample size when using area semantics.

**Expected:** Density is needed when area should represent probability mass.

## Exercise 6: Compare two groups with different sample sizes.

Counts show workload magnitude; density compares shapes. State which claim the chart supports.

**Expected:** Choose counts or normalized density according to the comparison question.
