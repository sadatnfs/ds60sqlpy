# viz-005: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

History ends January 6 and forecast dates are January 7,8,9. This ordering is checked before any line is drawn.

## Exercise 2

Forecast errors are -1,+1,-1, giving RMSE one. A last-value forecast of 15 gives squared errors 4,1,16, so RMSE is sqrt(7), approximately 2.646.

## Exercise 3

Concatenate dates forward with upper values, then reversed dates with reversed lower values. Reversing only one array creates a crossed polygon and is not a valid interval display.

## Exercise 4

To display an actual missing-day gap, retain January 4 with a missing y value and disable gap connection. Merely deleting the row can still draw a line between adjacent remaining dates.

## Exercise 5

A mean-confidence band concerns the conditional mean; an outcome-prediction band includes outcome variability. The illustrative plus/minus two band has neither guarantee until a construction and validation are supplied.

## Exercise 6

If labels arrive two days later, an origin at January 6 can use outcomes through January 4. Filter by availability before selecting the latest revision for each event.

## Solution reasoning

**Approach.** `case_05` separates three kinds of data in time. History covers January 1 to 6 with values 10 to 15. A forecast of 16, 17 and 18 for January 7 to 9 is treated as frozen before the outcomes arrive, and the later actual values are 17, 16 and 19. The code draws history as a line, the forecast as a dashed line, and actuals as x markers. A shaded band from forecast minus 2 to forecast plus 2 is drawn as one closed polygon: the dates run forward with the upper values, then backward with the lower values, and `fill="toself"` fills the shape. It also computes the root mean squared error of the forecast.

**Why it is correct.** The errors are -1, +1 and -1, so each squared error is 1 and the RMSE is exactly 1.0, which the program prints and asserts. The assertion that the earliest forecast date is later than the last history date guarantees the forecast never overlaps the data it was built from. The band polygon is valid because its upper edge is traced left to right and its lower edge right to left, so the outline never crosses itself; the assertion `lower <= upper` holds everywhere. The caption calls the band illustrative because nothing in the code estimates its coverage. The x markers for actuals sit inside the band on all three days, but three points say nothing reliable about coverage.

**A plausible wrong approach.** A common polygon error passes both the dates and the lower values in forward order. The outline then jumps from January 9 back to January 7 along a diagonal, and the fill becomes a crossed bow-tie shape that no longer represents an interval. Exercise 3 asks you to diagnose this. A more serious error refits or edits the forecast after seeing the January 7 to 9 actuals and reports the smaller RMSE, which is no longer an out-of-sample evaluation. Calling the plus or minus two band a 95 percent prediction interval would also claim a calibration nobody checked. Drawing the forecast with the same solid style as history would also blur the boundary between observed and predicted values.

**How to verify.** Run `.venv/bin/python courses/data-visualization/references/viz-005.py`. It prints `Forecast RMSE: 1.0`, then a table with dates January 7 to 9, forecasts 16 to 18, actuals 17, 16 and 19 and band limits, then `viz-005 Plotly complete`. For exercise 2, replace the forecast with the last observed value 15 and confirm the squared errors 4, 1 and 16 give an RMSE of about 2.646. For exercise 3, reverse only one array of the band and look at the drawn shape. For exercise 4, keep January 4 with a missing y value and confirm the line breaks there.

## Complete references and evidence

[Python reference](../references/viz-005.py) and [JavaScript reference](../references/viz-005.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
