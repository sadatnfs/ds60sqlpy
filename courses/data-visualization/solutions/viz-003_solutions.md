# viz-003: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

The three intervals are [-.596,-.204], [-.388,.788], [.408,1.192]. Each uses its own estimate plus/minus 1.96 SE under the stated normal approximation.

## Exercise 2

Plotly expects distances: upper minus estimate and estimate minus lower. For these symmetric examples both equal 1.96 SE. Check resulting endpoints against the table.

## Exercise 3

South excludes zero, but its lower endpoint .408 is below .5. It therefore does not establish an improvement greater than the practical margin at the stated interval level.

## Exercise 4

For estimate .8 with [.3,1.5], minus distance is .5 and plus distance is .7. Absolute endpoints supplied as distances would misdraw the interval.

## Exercise 5

With SD two and n=100, the independent mean SE is .2. A mean confidence interval uses uncertainty about the mean; an SD bar describes observed variation. Relabeling is required when the target changes.

## Exercise 6

For three prespecified comparisons and family alpha .05, Bonferroni intervals use critical level 1-.05/(2*3), approximately z=2.394. This provides conservative simultaneous coverage when each constituent bound is valid.

## Complete references and evidence

[Python reference](../references/viz-003.py) and [JavaScript reference](../references/viz-003.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
