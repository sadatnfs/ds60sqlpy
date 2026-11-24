# js-051: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A histogram groups quantitative observations into intervals and displays their counts or density. The bins are numerical intervals, not arbitrary categories. Their boundaries affect the apparent distribution, especially with small samples. A meaningful histogram states the sample, units, domain and binning policy.

A bin usually includes its lower boundary and excludes its upper boundary, except the final bin includes its upper endpoint. This convention prevents double-counting values exactly on a threshold. Values outside the declared domain require a policy and should not disappear without explanation.

Count and density are different vertical quantities. With unequal bin widths, equal counts do not imply equal density. A density histogram uses height proportional to count divided by sample size and bin width, so area represents probability mass. The reference uses equal-width bins and counts to keep the first reasoning explicit.

`d3.bin().domain([0, 10]).thresholds([2, 4, 6, 8])` creates intervals with known edges. Each returned bin is an array of observations with x0 and x1 properties. The count is its length. A rectangle’s width follows x(x1)-x(x0), and its height follows the count scale.

Test boundary values explicitly. The sample `[0, 2, 2, 4, 9, 10]` produces counts `[1, 2, 1, 0, 2]` for the chosen bins. The total count must equal the number of included finite observations. This simple conservation check catches many accidental exclusions.

## Exercise 1: Predict membership of value 2.

The interval convention avoids counting one observation twice at a shared boundary. d3.bin uses half-open bins [x0, x1), so both 2s land in the bin from 2 to 4, not the one from 0 to 2. Using inclusive upper edges would count 2 in the first bin and leave the bins summing correctly but with the wrong shape. Inspect `bins[1]` and confirm it holds the two 2s.

**Expected:** It enters the bin whose lower edge is 2.

## Exercise 2: Change thresholds while retaining the data.

Binning is a view of the same observations. A stable count invariant helps distinguish presentation choices from data loss. Switching thresholds from [2, 4, 6, 8] to, say, [5] gives two bins with counts 3 and 3. The bars change, but d3.sum(bins, b => b.length) stays 6. A threshold list that ends before 10 without a domain would still keep 6 here because the last bin is closed on the right.

**Expected:** The shape changes while included total count remains six.

## Exercise 3: Build the explicit-boundary count histogram.

Use x0 and x1 for geometry rather than assuming all bin indices are data values. With domain [0, 10] and thresholds [2, 4, 6, 8], the counts are 1 (the 0), 2 (both 2s), 1 (the 4), 0 and 2 (9 and 10). Placing bars at index * width rather than x(d.x0) works only while every bin is equal width. The reference checks "1,2,1,0,2" and that the total is values.length.

**Expected:** Five bins with counts 1, 2, 1, 0, 2.

## Exercise 4: Diagnose a missing maximum value.

A value equal to the final endpoint should be included under the stated D3 bin contract. Test it separately. If the domain were [0, 9], the value 10 would fall outside and the total would drop to 5 with no error. Keep the domain covering the data and assert the sum equals the input length.

**Expected:** The final boundary convention or declared domain is wrong.

## Exercise 5: Explain unequal-width bin heights.

Raw counts with unequal widths can mislead visual comparisons. Normalize by width and sample size when using area semantics. Merging the last two bins into [6, 10] would put 2 values in a 4-wide bin; plotting raw count makes it look like the 2-wide bin from 2 to 4 with the same count. Divide by width times n to compare density.

**Expected:** Density is needed when area should represent probability mass.

## Exercise 6: Compare two groups with different sample sizes.

Counts show workload magnitude; density compares shapes. State which claim the chart supports. For groups of 6 and 60 values, raw counts would dwarf the small group; switch to density when comparing shapes and say which you chose.

**Expected:** Choose counts or normalized density according to the comparison question.
