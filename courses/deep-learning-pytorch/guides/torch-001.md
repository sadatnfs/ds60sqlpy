# torch-001: A bounded PyTorch investigation and framework comparison

## Level and prerequisites

Beginner; approximately 120 minutes. Direct prerequisites: . The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A deep-learning investigation asks a model to predict a defined target from available inputs, then tests what evidence supports using that prediction. The central investigation is concrete: Use three training points(1, 2), (2, 4), (3, 6) and four untouched points(4, 8)..(7, 14); name one row as the prediction unit. The finish condition is 3 training rows, 4 holdout rows, one prediction per row. report says arithmetic/software checked; population reliability unestablished. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A deep-learning investigation asks a model to predict a defined target from available inputs, then tests what evidence supports using that prediction. Training adjusts parameters using exposed examples. Validation supports choices such as model size or learning rate. A final holdout estimates behavior on units excluded from those choices. A tiny fixture can establish arithmetic and software contracts while remaining far too small to establish population reliability. This course uses PyTorch to make those contracts visible rather than treating a framework import as proof of learning.

The paired TensorFlow route uses the same mathematical investigations where useful. Compare input and target shapes, units, loss denominator, initial parameters, update rule and evaluation state before comparing outputs. Two implementations can agree on a first loss while having different gradients because broadcasting created a different pairing. Framework comparison is therefore an experimental design problem, not a search for similarly named functions.

## Design decisions and when to use this method

Use an experiment card whenever a dataset, objective or framework changes. Decide first whether the intended prediction concerns new rows from familiar sources, new source families, or a later time period. Those claims require different splits. A more complex model cannot repair a split that gives training access to the answer's source identity.

For the visible seven-point fixture, the useful decision is whether the implementation obeys its declared learning and evaluation procedure. The reader has already seen the relationship y=2x, so this fixture cannot serve as a blind test of scientific discovery. Treat a production decision as pending until a representative independent assessment and operational evidence exist.

## Paired TensorFlow comparison

Compare [tf-001](../../deep-learning-tensorflow/guides/tf-001.md) after deriving the shared numerical contract.

The TensorFlow orientation uses the same evidence hierarchy. PyTorch and TensorFlow are execution tools; neither changes the distinction between training, selection and independent assessment. Later paired lessons hold mathematical fixtures fixed while exposing framework-specific state and layout behavior.

## Vocabulary and concepts

**Prediction unit:** The independently identified item receiving one prediction.

**Training:** Using exposed examples to change model parameters.

**Holdout:** Data excluded from fitting and selection for a final assessment.

**Baseline:** A simple comparison rule evaluated under the same task contract.

## How to run this lesson

Use the reading worksheet. Write a reasoned response for each case; no execution or model download is required.

Read the three worked cases in order and write the assumptions, intermediate reasoning and conclusion for each one. These are text cases, not programs to execute. Compare your written interpretation with the stated expected observations, then answer the six exercises in your saved worksheet. A correct argument must state its evidence boundary; source presence does not establish a model run.

## Syntax anatomy and reasoning sequence

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

## Worked example / walkthrough

### Example A: Define a prediction unit

The unit determines the denominator and split design. If several rows later belong to one person or account, the independence assumption must be revisited.

```text
Training IDs: t1,t2,t3
Holdout IDs: h4,h5,h6,h7
Input: scalar x
Target: scalar y in the same declared target unit
Prediction unit: one identified row
```

**Expected:** 3 training rows, 4 holdout rows, one prediction per row.

### Example B: Calculate a mean baseline

The baseline uses no holdout target to fit its constant. A baseline fitted to the holdout mean would contaminate the comparison.

```text
Training mean=(2+4+6)/3=4
Holdout residuals=4,6,8,10
Squared errors=16,36,64,100
MSE=216/4=54
```

**Expected:** mean 4; holdout squared errors 16, 36, 64, 100; MSE 54.

### Example C: Separate an exact relation from learned evidence

A correct formula is useful as an oracle. It must not be presented as a trained-model result when no training occurred.

```text
Rule: yhat=2*x
Holdout predictions:8,10,12,14
Fixture error:0
Training execution evidence: absent unless an actual optimizer run is recorded
```

**Expected:** the hand rule predicts the fixture exactly but was not learned by running an optimizer.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: 3 training rows, 4 holdout rows, one prediction per row. report says arithmetic/software checked; population reliability unestablished. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Define a prediction unit.** Use three training points(1, 2), (2, 4), (3, 6) and four untouched points(4, 8)..(7, 14); name one row as the prediction unit.
   **Expected:** 3 training rows, 4 holdout rows, one prediction per row.
   **Verify:** Save the reasoning table for exercise 1, including 3 training rows, 4 holdout rows, one prediction per row.

2. **Calculate a mean baseline.** Use training targets 2, 4, 6 to predict the constant training mean on holdout 8, 10, 12, 14.
   **Expected:** mean 4; holdout squared errors 16, 36, 64, 100; MSE 54.
   **Verify:** Save the reasoning table for exercise 2, including mean 4; holdout squared errors 16, 36, 64, 100; MSE 54.

3. **Separate an exact relation from learned evidence.** Compare a hand-specified rule y=2x with a model trained on the three points.
   **Expected:** the hand rule predicts the fixture exactly but was not learned by running an optimizer.
   **Verify:** Save the reasoning table for exercise 3, including the hand rule predicts the fixture exactly but was not learned by running an optimizer.

4. **Audit selection leakage.** After looking at holdout errors, a researcher changes the learning rate and reports the better result as final.
   **Expected:** holdout was used for selection; new untouched assessment needed.
   **Verify:** Save the reasoning table for exercise 4, including holdout was used for selection; new untouched assessment needed.

5. **Align a framework comparison.** List the contracts that must match before comparing one PyTorch and one TensorFlow update.
   **Expected:** same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.
   **Verify:** Save the reasoning table for exercise 5, including same data pairing, dtype, initial weight, loss reduction, rate and optimizer rule.

6. **Bound the conclusion.** Write a report for a successful tiny CPU reference that avoids a production-quality claim.
   **Expected:** report says arithmetic/software checked; population reliability unestablished.
   **Verify:** Save the reasoning table for exercise 6, including report says arithmetic/software checked; population reliability unestablished.

## Common pitfalls and diagnosis

If a result seems unexpectedly strong, reconstruct which labels influenced every decision. A changed preprocessing statistic or threshold can use assessment data without appearing in the optimizer loop. Check row identities and source-family identities separately; distinct row names do not prevent a shared account or duplicated document from leaking across a split.

If the constant baseline differs from four, inspect which target population was averaged. If the MSE differs from 54, inspect the four residuals and denominator before changing a model. If a report calls y=2x trained, locate the actual initial state and updates. If no updates ran, label it an analytic oracle. Finally, distinguish the visible teaching holdout from an undisclosed assessment: preserving its programmatic split is valuable procedure evidence, but the learner already knows its answers.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Prediction unit, Training, Holdout using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite  if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does a matching loss prove two implementations are equivalent?**

No. A reduction or broadcasting error can preserve one scalar while changing derivatives. Compare shapes, per-example contributions, gradients and updated state under the same inputs.

**Why use a tiny fixture when real models are large?**

A tiny fixture makes every operation independently checkable. It is strong evidence about a local mechanism and weak evidence about deployment quality; the two questions require different experiments.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-001, A bounded PyTorch investigation and framework comparison.
Read courses/deep-learning-pytorch/guides/torch-001.md and courses/deep-learning-pytorch/lessons/torch-001.md. Direct prerequisites: .
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
