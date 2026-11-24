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

## Solution reasoning

**Approach.** `case_03` stores three prespecified regional estimates, North -0.4, Central 0.2 and South 0.8, with standard errors 0.1, 0.3 and 0.2. It computes each 95 percent interval as the estimate plus or minus 1.96 standard errors, then draws diamond markers at the estimates with asymmetric `error_x` bars. Plotly's `array` and `arrayminus` expect distances from the marker, so the code passes `upper - effect` and `effect - lower`, not the endpoints. A dashed vertical line marks zero, the x axis is titled Mean difference (points), and `customdata` carries the endpoints for the hover text and the table. Listing the three regions in a fixed order on the y axis means the reading order matches the printed table.

**Why it is correct.** The arithmetic gives North [-0.596, -0.204], Central [-0.388, 0.788] and South [0.408, 1.192], which match the table the reference prints apart from floating-point digits. Because the distances are derived from the same endpoints, the drawn bars end exactly at those values. The assertions check the interpretation directly: South's lower bound is above zero, Central's interval contains zero, and every interval's width divided by its standard error equals 3.92, which is two times 1.96. The caption states that these are separate marginal intervals under a normal approximation, which is the claim the arithmetic supports and no more. Using 1.96 rather than a rounded 2 keeps the drawn widths consistent with the stated 95 percent level.

**A plausible wrong approach.** One plausible error passes the upper endpoints as the `array` values. For South that is 1.192, so Plotly would extend the bar from 0.8 to 1.992 and the drawn interval would be far wider than the table says. Exercise 4 shows the same problem with an asymmetric interval. A second error reads South's interval as proof of an improvement larger than 0.5; its lower bound of 0.408 does not support that. A third treats the three bars as a family that jointly holds at 95 percent, when simultaneous coverage would need a wider critical value such as the Bonferroni 2.394 from exercise 6.

**How to verify.** Run `.venv/bin/python courses/data-visualization/references/viz-003.py`. The table should list each region with its effect and the endpoints above, and the program ends with `viz-003 Plotly complete`. Hover each diamond and confirm the interval in the tooltip equals the table row, and check that North's whole bar sits left of the dashed zero line. For exercise 4, build one marker at 0.8 with endpoints 0.3 and 1.5, pass distances 0.7 and 0.5, and check the drawn ends. For exercise 6, recompute the intervals with z = 2.394 and confirm every one widens while the estimates stay put.

## Complete references and evidence

[Python reference](../references/viz-003.py) and [JavaScript reference](../references/viz-003.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
