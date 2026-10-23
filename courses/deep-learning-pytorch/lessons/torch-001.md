# torch-001: A bounded PyTorch investigation and framework comparison

Read the guide, record a prediction, then answer the six cases without opening solutions.

## Exercises

1. **Define a prediction unit.** Use three training points(1, 2), (2, 4), (3, 6) and four untouched points(4, 8)..(7, 14); name one row as the prediction unit.
   **Expected:** 3 training rows, 4 holdout rows, one prediction per row.
   **Verify:** Save the reasoning table for exercise 1, including 3 training rows, 4 holdout rows, one prediction per row.

2. **Calculate a mean baseline.** Use training targets2, 4, 6 to predict the constant training mean on holdout8, 10, 12, 14.
   **Expected:** mean4; holdout squared errors16, 36, 64, 100; MSE54.
   **Verify:** Save the reasoning table for exercise 2, including mean4; holdout squared errors16, 36, 64, 100; MSE54.

3. **Separate an exact relation from learned evidence.** Compare a hand-specified rule y=2 x with a model trained on the three points.
   **Expected:** the hand rule predicts the fixture exactly but was not learned by running an optimizer.
   **Verify:** Save the reasoning table for exercise 3, including the hand rule predicts the fixture exactly but was not learned by running an optimizer.

4. **Audit selection leakage.** After looking at holdout errors, a research e r changes the learning rate and reports the better result as final.
   **Expected:** holdout was used for selection; new untouched assessment needed.
   **Verify:** Save the reasoning table for exercise 4, including holdout was used for selection; new untouched assessment needed.

5. **Align a framework comparison.** List the contracts that must match before comparing one PyTorch and one TensorFlow update.
   **Expected:** same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.
   **Verify:** Save the reasoning table for exercise 5, including same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.

6. **Bound the conclusion.** Write a report for a successful tiny CPU reference that avoids a production-quality claim.
   **Expected:** report says arithmetic/software checked; population reliability u n established.
   **Verify:** Save the reasoning table for exercise 6, including report says arithmetic/software checked; population reliability u n established.
