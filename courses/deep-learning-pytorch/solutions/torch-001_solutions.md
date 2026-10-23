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

## Exercise 1: Define a prediction unit

The question is: Use three training points(1, 2), (2, 4), (3, 6) and four untouched points(4, 8)..(7, 14); name one row as the prediction unit.

The unit determines the denominator and split design. If several rows later belong to one person or account, the independence assumption must be re visited.

```text
Training IDs: t1,t2,t3
Holdout IDs: h4,h5,h6,h7
Input: scalar x
Target: scalar y in the same declared target unit
Prediction unit: one identified row
```

**Expected:** 3 training rows, 4 holdout rows, one prediction per row.

**Verify:** Compare the computed values or written argument with 3 training rows, 4 holdout rows, one prediction per row.

## Exercise 2: Calculate a mean baseline

The question is: Use training targets2, 4, 6 to predict the constant training mean on holdout8, 10, 12, 14.

The baseline uses no holdout target to fit its constant. A baseline fitted to the holdout mean would contaminate the comparison.

```text
Training mean=(2+4+6)/3=4
Holdout residuals=4,6,8,10
Squared errors=16,36,64,100
MSE=216/4=54
```

**Expected:** mean4; holdout squared errors16, 36, 64, 100; MSE54.

**Verify:** Compare the computed values or written argument with mean4; holdout squared errors16, 36, 64, 100; MSE54.

## Exercise 3: Separate an exact relation from learned evidence

The question is: Compare a hand-specified rule y=2x with a model trained on the three points.

A correct formula is useful as an oracle. It must not be presented as a trained-model result when no training occurred.

```text
Rule: yhat=2*x
Holdout predictions:8,10,12,14
Fixture error:0
Training execution evidence: absent unless an actual optimizer run is recorded
```

**Expected:** the hand rule predicts the fixture exactly but was not learned by running an optimizer.

**Verify:** Compare the computed values or written argument with the hand rule predicts the fixture exactly but was not learned by running an optimizer.

## Exercise 4: Audit selection leakage

The question is: After looking at holdout errors, a research e r changes the learning rate and reports the better result as final.

The name of a file does not determine whether it remained untouched. The sequence of decisions determines its role.

```text
Observed holdout -> learning-rate change -> second score
Information boundary: crossed
Repair: treat these observations as validation and reserve new final data
```

**Expected:** holdout was used for selection; new untouched assessment needed.

**Verify:** Compare the computed values or written argument with holdout was used for selection; new untouched assessment needed.

## Exercise 5: Align a framework comparison

The question is: List the contracts that must match before comparing one PyTorch and one TensorFlow update.

An equal initial loss can hide a different gradient. The paired route repeatedly uses intermediate-state comparisons to expose such failures.

```text
Match: x/y shapes,example IDs,dtype,w0,mean-versus-sum,learning rate,SGD convention.
Compare separately: forward loss,gradient,new weight,new loss.
Do not infer equivalence from a matching first scalar alone.
```

**Expected:** same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.

**Verify:** Compare the computed values or written argument with same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.

## Exercise 6: Bound the conclusion

The question is: Write a report for a successful tiny CPU reference that avoids a production-quality claim.

A bounded conclusion preserves the value of the experiment without making claims it was not designed to support.

```text
Checked: literal fixture arithmetic and executed local assertions.
Not established: unseen-population quality,privacy,fairness,GPU throughput or production safety.
Next evidence: representative independent units and task-specific acceptance tests.
```

**Expected:** report says arithmetic/software checked; population reliability u n established.

**Verify:** Compare the computed values or written argument with report says arithmetic/software checked; population reliability u n established.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
