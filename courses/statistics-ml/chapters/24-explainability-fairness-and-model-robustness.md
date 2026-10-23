# 24. Explainability, Fairness, and Model Robustness

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-024`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

An explanation describes a model's behavior relative to a question and reference. It does not automatically describe the data-generating cause or a feasible intervention. A feature can have high predictive importance because it is a proxy, a downstream symptom or a leakage artifact. Explainability must therefore be paired with data provenance, validation and causal reasoning when actions are proposed.

### Attribution requires a value function

For two features, let v(S) be the prediction value assigned when coalition S is known under a specified reference construction. Shapley attribution averages each feature's marginal contribution over the possible orders. Thus phi1=[v({1})-v(empty)+v({1,2})-v({2})]/2, with a parallel expression for phi2. The attributions sum to v({1,2})-v(empty). Their values change when the reference background or dependence treatment changes. Conditional and interventional constructions answer different questions, especially for correlated features.

Permutation importance asks how performance changes when a feature is disrupted. If another feature duplicates its information, marginal permutation importance can be small despite the signal being useful. PDP replaces one feature across all rows and averages predictions, potentially creating impossible combinations. ICE retains separate curves; ALE uses local changes within observed regions to reduce some extrapolation. None of these curves is automatically a causal response curve.

### Fairness criteria condition on different quantities

Demographic parity compares P(predicted positive|group). Equalized odds compares prediction rates conditional on both group and true outcome; equal opportunity focuses on true positives. Group calibration compares actual outcome rates among people receiving the same predicted probability in different groups. When base rates differ and prediction is imperfect, desirable criteria can conflict. This is a consequence of conditioning, not simply an implementation bug.

Select criteria according to the decision, harms, affected people and quality of labels. Historical labels can encode unequal opportunity, so matching their error rates is not a complete ethical analysis. Quantify uncertainty and intersectional support before interpreting group differences. A feasible recourse plan must account for immutable attributes, costs, causal dependencies and whether the model will remain stable.

## Methods, mechanisms, and limits

### stat-24-01

**Global interpretability**

Describe model behavior over a population using structure, summaries or global surrogates. State the population and fidelity of the explanation. A simple global summary can hide important interactions or rare-region failures.

### stat-24-02

**Local interpretability**

Explain a particular prediction or its neighborhood. The result depends on the locality and reference. A faithful local explanation need not generalize to other cases or reveal the real cause of the outcome.

### stat-24-03

**Permutation importance**

Shuffle a feature on held-out data and measure performance degradation. Correlated substitutes can mask importance; unrealistic shuffled combinations can exaggerate it. Repeat permutations and report variability with the chosen metric.

### stat-24-04

**Partial dependence plots**

Average predictions after replacing one feature across observations. This reveals model response under the replacement distribution. Correlated features can create unsupported combinations, so inspect support before interpreting the curve.

### stat-24-05

**Individual conditional expectation**

Plot each observation's prediction as one feature varies while others stay fixed. Diverging curves reveal interactions hidden by averaging. The same unrealistic-combination concern applies, especially for tightly dependent features.

### stat-24-06

**Accumulated local effects**

Estimate local prediction differences within observed feature bins and accumulate them. ALE reduces some extrapolation from correlated predictors but depends on local support, binning and interaction structure.

### stat-24-07

**SHAP values**

Allocate a prediction-reference difference using Shapley axioms and a specified coalition value. Background distribution and feature-dependence handling determine the explanation. Attribution sums are not causal-effect decompositions by default.

### stat-24-08

**LIME**

Fit a simple surrogate to weighted perturbations near an instance. Fidelity depends on sampling, locality and surrogate class. Different seeds or perturbation policies can yield different explanations for the same model.

### stat-24-09

**Counterfactual explanations**

Find an input differing from the observed case whose prediction crosses a desired boundary. The change may be infeasible or causally incoherent. State constraints and distinguish model counterfactuals from real-world intervention outcomes.

### stat-24-10

**Recourse analysis**

Evaluate actions people could realistically take to obtain a different decision. Include cost, immutability, causal relations and uncertainty. A recommendation is incomplete if changing one feature necessarily changes others the model assumes fixed.

### stat-24-11

**Monotonic models**

Constrain predictions to move in a specified direction with selected features. This can enforce domain expectations and improve stability. Incorrect monotonic constraints can hide interactions or worsen subgroup fit.

### stat-24-12

**Adversarial robustness**

Evaluate deliberately chosen perturbations within a specified threat model. Define allowed features, magnitudes and attacker knowledge. Robustness to one norm-bounded attack does not certify robustness to semantic or distributional changes.

### stat-24-13

**Stress testing**

Construct plausible adverse scenarios such as sensor loss, extreme load or shifted populations. Compare both model metrics and downstream decisions. Unrealistic stress cases can waste attention, while easy ones provide false reassurance.

### stat-24-14

**Subgroup performance analysis**

Estimate performance separately in meaningful groups and intersections. Small groups have wide uncertainty and multiple comparisons. Overall accuracy can improve while the most affected population becomes worse off.

### stat-24-15

**Demographic parity**

Compare positive decision rates across groups. Equal rates can matter for allocation fairness but ignore true outcomes and context. It is not equivalent to equal error rates or calibrated risk estimates.

### stat-24-16

**Equalized odds**

Require equal true-positive and false-positive rates across groups. Achieving it may need group-dependent thresholds or randomization. The appropriateness depends on decision context and reliability of observed labels.

### stat-24-17

**Equal opportunity**

Equalize true-positive rates across groups, focusing on access among positive cases. False-positive disparities may remain. Clarify which class represents opportunity and whether labels themselves reflect unequal access.

### stat-24-18

**Group calibration**

Check whether a predicted probability corresponds to the same observed frequency within each group. Sparse bins and selection into observed outcomes complicate assessment. Calibration alone permits different error and acceptance rates.

### stat-24-19

**Individual fairness**

Require similar decisions for individuals deemed similar under a justified task-specific metric. Defining that similarity is the substantive challenge. A learned metric can reproduce the same biases it is intended to prevent.

### stat-24-20

**Intersectional fairness**

Analyze intersections such as region by age rather than only broad marginal groups. Marginal parity can hide severe small-group disparities. Retain uncertainty and privacy considerations when subgroup counts are tiny.

### stat-24-21

**Fairness tradeoffs**

Different criteria can be mutually incompatible with unequal prevalences and imperfect predictions. Make tradeoffs explicit and involve accountable decision owners. A single composite score can conceal which harms are being exchanged.

### stat-24-22

**Proxy discrimination analysis**

Assess whether nominally neutral features encode sensitive distinctions or historical disadvantage. Removing the sensitive field does not remove correlated proxies. Evaluate behavior and mechanisms, not only a feature-name blacklist.

### stat-24-23

**Causal fairness analysis**

Specify permitted and prohibited causal paths and evaluate counterfactual or path-specific criteria. The conclusions depend on a credible causal model and normative choices. Observational association alone cannot determine which pathways are legitimate.

## Worked Python demonstrations

Complete offline program: [chapter_24.py](../examples/chapter_24.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_24.py
```

### Attribute an interaction transparently

A specified value function assigns zero to no features, one to A, two to B and seven to both. Each feature receives its standalone contribution plus half the interaction, giving three and four. The calculation is exact for this game; another background construction could define different coalition values.

### Equal error rates do not imply equal decision rates

Both groups have sensitivity .8 and false-positive rate .1, but prevalences differ. Positive decision rates are .24 and .66, while precisions are about .667 and .970. This arithmetic demonstrates that conditioning on outcomes and conditioning on predictions are different fairness questions.

### State the perturbation model

For a linear score with weights (2,-1), an L-infinity perturbation of radius .4 can reduce the score by .4 times the L1 norm of the weights, or 1.2. The sign flips from one to minus .2. Whether changing both inputs this way is feasible is a separate threat-model question.

### Complete executable example

```python
import numpy as np

def exact_shapley_game():
    empty,a,b,ab=0.,1.,2.,7.
    phi_a=.5*((a-empty)+(ab-b))
    phi_b=.5*((b-empty)+(ab-a))
    assert phi_a==3 and phi_b==4 and phi_a+phi_b==ab-empty
    print("Specified two-feature game attributions:",phi_a,phi_b)

def fairness_conditioning():
    # Rows are groups; columns are TP, FN, FP, TN.
    counts=np.array([[16.,4.,8.,72.],[64.,16.,2.,18.]])
    tp,fn,fp,tn=counts.T
    tpr=tp/(tp+fn);fpr=fp/(fp+tn)
    positive_rate=(tp+fp)/counts.sum(axis=1)
    precision=tp/(tp+fp)
    assert np.allclose(tpr,[.8,.8]) and np.allclose(fpr,[.1,.1])
    assert not np.isclose(positive_rate[0],positive_rate[1])
    assert not np.isclose(precision[0],precision[1])
    print("Equalized odds rates:",tpr,fpr,"positive rates:",positive_rate,"precision:",precision)

def adversarial_linear_margin():
    weights=np.array([2.,-1.]);x=np.array([1.,1.]);epsilon=.4
    delta=-epsilon*np.sign(weights)
    before=weights@x;after=weights@(x+delta)
    assert before==1 and np.isclose(after,-.2)
    assert np.isclose(before-after,epsilon*np.abs(weights).sum())
    print("Linear margin before/after bounded perturbation:",before,after)

def main():
    exact_shapley_game();fairness_conditioning();adversarial_linear_margin()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does SHAP tell you what to change to improve an outcome?** It attributes a model prediction relative to a specified reference. It does not establish that changing a feature causes the desired outcome, that the change is feasible or that other features remain fixed. Recourse needs an action and causal model.

**Interview: Why can equalized odds coexist with unequal precision?** Error rates condition on actual class, while precision conditions on the prediction. Different base rates change the mixture of true and false positives even when class-conditional error rates match.

**Interview: A sensitive field is removed. Is discrimination removed?** No. Other features can encode proxies and historical disadvantage, and labels can be biased. Evaluate subgroup behavior, data processes and relevant causal pathways rather than relying on feature exclusion alone.

## Primary sources and official APIs

- [Lundberg and Lee, A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874).

- [Hardt et al., Equality of Opportunity in Supervised Learning](https://arxiv.org/abs/1610.02413).

- [scikit-learn permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html).

- [scikit-learn partial dependence and ICE](https://scikit-learn.org/stable/modules/partial_dependence.html).

## Reading connections

[Previous chapter](23-uncertainty-quantification-and-distribution-shift.md) | [Book contents](../README.md) | [Next chapter](25-time-series-foundations-and-diagnostics.md)
