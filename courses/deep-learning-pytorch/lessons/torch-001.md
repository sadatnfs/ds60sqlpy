# torch-001: A bounded PyTorch investigation and framework comparison

Read the guide, record a prediction, then answer the six cases without opening solutions.

## Exercises

1. **Name the unit for grouped rows.** A table has six rows from three customers, two rows per customer, and the task predicts next month's spend for each customer. Name the prediction unit and the unit that must stay together in a split.
   **Expected:** prediction unit: one customer for the next month; split unit: customer, so 3 independent units rather than 6 rows.
   **Verify:** Your worksheet names the customer as both the prediction and split unit and states the count 3; a split that places c1 rows on both sides is marked invalid.

2. **Recompute a training-only baseline.** Use training targets 1, 3, 5 to predict a constant on holdout targets 7 and 9. Report the constant, the holdout residuals and the holdout MSE.
   **Expected:** constant 3; residuals 4 and 6; squared errors 16 and 36; MSE 26.
   **Verify:** Your table shows the mean 3 computed from training targets only and the two squared errors summing to 52 over a denominator of 2; a version that uses the holdout mean 8 is labeled leaked.

3. **Classify evidence for a generated fixture.** A notebook reports zero error for the rule y = 3x on points that were generated from y = 3x, and it contains no optimizer log. Classify what the zero error establishes.
   **Expected:** an analytic oracle consistent with the generator; no training evidence; no evidence about unseen data.
   **Verify:** Your answer separates the three evidence types and names the missing optimizer record and missing independent sample as the two absent items.

4. **Audit selection leakage.** After looking at holdout errors, a researcher changes the learning rate and reports the better result as final.
   **Expected:** holdout was used for selection; new untouched assessment needed.
   **Verify:** Your timeline shows the holdout score influencing the learning-rate change and relabels that data as validation; the report names a new untouched set as the only valid final assessment.

5. **Align a framework comparison.** List the contracts that must match before comparing one PyTorch and one TensorFlow update.
   **Expected:** same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.
   **Verify:** Your checklist names all six contracts (pairing, dtype, initial weight, reduction, rate and optimizer rule) and orders the comparisons forward loss, gradient, updated weight and new loss.

6. **Bound the conclusion.** Write a report for a successful tiny CPU reference that avoids a production-quality claim.
   **Expected:** report says arithmetic/software checked; population reliability unestablished.
   **Verify:** Your report contains one sentence on what the CPU run checked and one listing unestablished properties, and contains no production-quality claim.
