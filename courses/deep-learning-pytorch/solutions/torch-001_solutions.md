# torch-001: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A deep-learning investigation asks a model to predict a defined target from available inputs, then tests what evidence supports using that prediction. Training adjusts parameters using exposed examples. Validation supports choices such as model size or learning rate. A final holdout estimates behavior on units excluded from those choices. A tiny fixture can establish arithmetic and software contracts while remaining far too small to establish population reliability. This course uses PyTorch to make those contracts visible rather than treating a framework import as proof of learning.

The paired TensorFlow route uses the same mathematical investigations where useful. Compare input and target shapes, units, loss denominator, initial parameters, update rule and evaluation state before comparing outputs. Two implementations can agree on a first loss while having different gradients because broadcasting created a different pairing. Framework comparison is therefore an experimental design problem, not a search for similarly named functions.

**Prediction unit:** The independently identified item receiving one prediction.

**Training:** Using exposed examples to change model parameters.

**Holdout:** Data excluded from fitting and selection for a final assessment.

**Baseline:** A simple comparison rule evaluated under the same task contract.

## Reading the implementation

Write an experiment card before executing code. Name the prediction unit, input availability, target, training/validation/holdout identities, baseline, metric and forbidden claims. Distinguish source inspection, an executed reference, an independent arithmetic check and held-out task evidence. Record an unexecuted runtime as unverified. The default course uses CPU tensors and local fixtures; no pretrained weights or external datasets are required.

## Build an auditable experiment card

An experiment needs a timeline as well as a table. First define the target and which inputs exist when a prediction is made. Next choose training and selection populations. Then fit parameters or preprocessing using only their allowed data. Freeze those decisions before examining the final assessment. If a later result changes the learning rate, feature set, threshold or stopping point, that result has become selection information even if the file is still named test.

The training-only constant in this chapter is four. Its value comes from targets 2, 4 and 6. Keep it fixed when calculating the later errors:

| Assessment input | Target | Fixed prediction | Prediction minus target | Squared error |
| --- | --- | --- | --- | --- |
| 4 | 8 | 4 | -4 | 16 |
| 5 | 10 | 4 | -6 | 36 |
| 6 | 12 | 4 | -8 | 64 |
| 7 | 14 | 4 | -10 | 100 |

The squared-error numerator is 216 and the denominator is four, giving MSE 54 in squared target units. Choosing the assessment mean 11 as the constant would lower the error, but it would be a different experiment because the prediction rule used assessment labels. A number cannot identify that information leak by itself; the decision history does.

Notice a second assumption: all assessment inputs lie outside the training input range 1..3. The fixture therefore includes extrapolation. A larger error than on training does not uniquely diagnose overfitting; a different input range is also relevant. In a real application, report both the population relationship and the fitted rule. A random row split, a source-family split and a forward-time split answer different questions.

The hand-written rule y=2x has zero error here. That establishes its arithmetic on the visible points. It does not establish that an optimizer learned the rule, that an unknown population follows it, or that another feature pipeline preserves the same units. A training claim additionally needs an initial parameter state, an actual update sequence and an observed resulting state. Later chapters provide those receipts one operation at a time.

A framework comparison is another controlled experiment. Match record identities, feature order, dtype, parameter initialization, objective denominator, optimizer rule and model mode. Compare forward predictions before loss, loss before gradients, and gradients before updated parameters. If one implementation returns a matching scalar but a different gradient, the comparison has already failed even though the headline loss agrees.

A defensible card ends with a bounded conclusion and the next evidence needed. For this fixture: arithmetic and procedure can be checked; population reliability remains unestablished. For a later deployment: define the independent unit, intended operating range, error costs and operational acceptance before treating a model score as permission to use it.

## Exercise 1: Name the unit for grouped rows

The question is: A table has six rows from three customers, two rows per customer, and the task predicts next month's spend for each customer. Name the prediction unit and the unit that must stay together in a split.

The row count overstates the evidence when rows share an identity. Grouping the split by customer keeps one customer's history from appearing on both sides.

```text
Rows: 6 (c1, c1, c2, c2, c3, c3)
Prediction unit: one customer-month forecast
Split unit: customer; both rows of a customer go to the same side
Independent units available: 3
```

**Expected:** prediction unit: one customer for the next month; split unit: customer, so 3 independent units rather than 6 rows.

**Verify:** Your worksheet names the customer as both the prediction and split unit and states the count 3; a split that places c1 rows on both sides is marked invalid.

## Exercise 2: Recompute a training-only baseline

The question is: Use training targets 1, 3, 5 to predict a constant on holdout targets 7 and 9. Report the constant, the holdout residuals and the holdout MSE.

The constant comes only from training targets. Using the holdout mean 8 would give MSE 1 but would make the holdout part of fitting.

```text
Training mean=(1+3+5)/3=3
Holdout residuals=7-3, 9-3 = 4, 6
Squared errors=16, 36
MSE=52/2=26
```

**Expected:** constant 3; residuals 4 and 6; squared errors 16 and 36; MSE 26.

**Verify:** Your table shows the mean 3 computed from training targets only and the two squared errors summing to 52 over a denominator of 2; a version that uses the holdout mean 8 is labeled leaked.

## Exercise 3: Classify evidence for a generated fixture

The question is: A notebook reports zero error for the rule y = 3x on points that were generated from y = 3x, and it contains no optimizer log. Classify what the zero error establishes.

Agreement between a rule and the process that generated its test points is an arithmetic check. A training claim needs a recorded optimizer run, and a population claim needs independent data.

```text
Rule source: written by hand, identical to the generator
Observed error: 0 on generated points
Training evidence: absent (no initial state, updates or final state recorded)
Population evidence: absent (no independent sample)
```

**Expected:** an analytic oracle consistent with the generator; no training evidence; no evidence about unseen data.

**Verify:** Your answer separates the three evidence types and names the missing optimizer record and missing independent sample as the two absent items.

## Exercise 4: Audit selection leakage

The question is: After looking at holdout errors, a researcher changes the learning rate and reports the better result as final.

The name of a file does not determine whether it remained untouched. The sequence of decisions determines its role.

```text
Observed holdout -> learning-rate change -> second score
Information boundary: crossed
Repair: treat these observations as validation and reserve new final data
```

**Expected:** holdout was used for selection; new untouched assessment needed.

**Verify:** Your timeline shows the holdout score influencing the learning-rate change and relabels that data as validation; the report names a new untouched set as the only valid final assessment.

## Exercise 5: Align a framework comparison

The question is: List the contracts that must match before comparing one PyTorch and one TensorFlow update.

An equal initial loss can hide a different gradient. The paired route repeatedly uses intermediate-state comparisons to expose such failures.

```text
Match: x/y shapes,example IDs,dtype,w0,mean-versus-sum,learning rate,SGD convention.
Compare separately: forward loss,gradient,new weight,new loss.
Do not infer equivalence from a matching first scalar alone.
```

**Expected:** same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.

**Verify:** Your checklist names all six contracts (pairing, dtype, initial weight, reduction, rate and optimizer rule) and orders the comparisons forward loss, gradient, updated weight and new loss.

## Exercise 6: Bound the conclusion

The question is: Write a report for a successful tiny CPU reference that avoids a production-quality claim.

A bounded conclusion preserves the value of the experiment without making claims it was not designed to support.

```text
Checked: literal fixture arithmetic and executed local assertions.
Not established: unseen-population quality,privacy,fairness,GPU throughput or production safety.
Next evidence: representative independent units and task-specific acceptance tests.
```

**Expected:** report says arithmetic/software checked; population reliability unestablished.

**Verify:** Your report contains one sentence on what the CPU run checked and one listing unestablished properties, and contains no production-quality claim.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
