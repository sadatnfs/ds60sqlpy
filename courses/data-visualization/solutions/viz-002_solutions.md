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

## Complete references and evidence

[Python reference](../references/viz-002.py) and [JavaScript reference](../references/viz-002.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
