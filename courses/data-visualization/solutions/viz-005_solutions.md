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

## Complete references and evidence

[Python reference](../references/viz-005.py) and [JavaScript reference](../references/viz-005.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
