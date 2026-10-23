# 15. Causal Inference Foundations

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-015`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A causal question compares interventions, not merely rows with different labels. Let Y(1) and Y(0) be the outcome the same unit would have under treatment and control. Only one is observed. The average treatment effect is E[Y(1)-Y(0)], so missing counterfactual outcomes are built into the question, even in a perfectly logged dataset.

### Derive backdoor standardization

Suppose X contains a sufficient set of pretreatment common causes. Under consistency, conditional exchangeability Y(a) independent of A given X, and positivity P(A=a|X=x)>0, the intervention mean is E[Y(a)]=sum_x E[Y|A=a,X=x]P(X=x). Consistency connects observed outcomes to potential outcomes, exchangeability permits using comparable observed groups, and positivity ensures each required conditional mean is supported. The formula averages both interventions over the same target covariate distribution.

### Read a graph before adjusting

A common cause X with arrows to A and Y creates a backdoor path, which conditioning on X can block. A mediator M on A->M->Y carries part of the treatment effect; conditioning on M changes a total-effect question. A collider C on A->C<-U->Y blocks a path until conditioning on C opens it. These are different roles. Including every available predictor is not a safe causal-adjustment strategy.

The graph is a record of assumptions, not a picture discovered with certainty from correlations. Ask what causes selection, measurement and follow-up. Then identify the target before selecting an estimator. Predictive model accuracy evaluates a different property from identification.

## Methods, mechanisms, and limits

### stat-15-01

**Potential outcomes**

Potential outcomes index the response under each well-defined intervention. Their joint distribution is generally not observed, so individual treatment effects are not directly measurable even when average effects are identified.

### stat-15-02

**Counterfactual reasoning**

A counterfactual states what would happen under a specified alternative intervention while holding the relevant background context fixed. Vague alternatives such as better service require operational definition before the question is estimable.

### stat-15-03

**Average treatment effect**

ATE averages Y(1)-Y(0) over the chosen target population. Changing eligibility or population weights changes the effect target even when all conditional response models remain identical.

### stat-15-04

**Average treatment effect on the treated**

ATT averages treatment effects over the covariate distribution of actually treated units. It generally differs from ATE when effects vary and treatment selection changes population composition.

### stat-15-05

**Conditional average treatment effect**

CATE is an average effect within covariate-defined groups, not the unobservable effect for a specific person. Fine-grained heterogeneity estimates require sufficient overlap and independent validation against overfitting.

### stat-15-06

**Consistency**

Consistency equates observed Y with Y(a) when the observed intervention is a. Multiple materially different versions labeled identically can violate the intended meaning. Define dosage, timing and implementation clearly.

### stat-15-07

**Exchangeability and ignorability**

Conditional exchangeability says treatment assignment carries no additional potential-outcome information after conditioning on an adequate covariate set. It is not established by balancing measured variables alone or by a high-quality propensity fit.

### stat-15-08

**Positivity and overlap**

Every intervention being compared must have positive probability within relevant covariate strata. Structural absence of an option prevents nonparametric identification there. Extreme but nonzero probabilities create practical instability.

### stat-15-09

**Stable unit treatment value assumptions**

SUTVA typically combines no interference and suitably well-defined treatment versions. Network spillovers or differing versions require expanded potential-outcome definitions rather than pretending each person's assignment acts in isolation.

### stat-15-10

**Directed acyclic graphs**

A DAG encodes hypothesized directional causes without directed cycles. Missing arrows are substantive claims. Time-indexing can represent feedback systems while retaining an acyclic graph over ordered events.

### stat-15-11

**Structural causal models**

Structural equations describe each variable as a function of parents and external noise. Interventions replace an equation rather than merely condition on its observed output. Disturbance assumptions determine which causal claims are identified.

### stat-15-12

**Confounding**

A common cause of treatment and outcome creates a noncausal association. Adjustment must address the relevant path using pretreatment information. Good prediction of treatment alone does not identify all confounders.

### stat-15-13

**Colliders**

Conditioning on a shared effect can associate otherwise independent causes. Selection into hospitalization, employment or completed follow-up can act this way. More covariates can therefore increase rather than reduce causal bias.

### stat-15-14

**Mediators**

A mediator lies on a causal pathway from treatment to outcome. Adjusting for it generally removes some total effect and may open additional bias paths. Mediation estimands need stronger assumptions than a total ATE.

### stat-15-15

**Backdoor adjustment**

Average conditional outcome contrasts over a shared target distribution after blocking all relevant backdoor paths with a valid adjustment set. Positivity, consistency and measurement adequacy remain necessary.

### stat-15-16

**Front-door identification**

A mediator can identify certain total effects despite unmeasured treatment-outcome confounding if strong front-door conditions hold. All treatment-to-mediator paths and mediator-to-outcome backdoor paths must satisfy the required restrictions.

### stat-15-17

**Do-calculus**

Do-calculus manipulates interventional distributions using graphical separation rules to determine identification. It does not estimate effects from a graph alone; observed distributions and credible causal assumptions are both required.

### stat-15-18

**Selection diagrams**

Add selection nodes to encode which mechanisms or distributions differ across settings. These assumptions clarify whether reweighting is enough or whether a changed outcome mechanism prevents transport.

### stat-15-19

**Transportability**

Transfer a causal estimand between populations using shared causal structure and suitable information on effect modifiers. Similar demographics alone do not ensure comparable intervention delivery or outcome mechanisms.

### stat-15-20

**Partial identification**

When assumptions identify a range rather than a point, report bounds. Wider honest bounds can support a robust decision or show that more information is valuable; imposing an arbitrary point assumption conceals uncertainty.

### stat-15-21

**Negative controls**

Use exposures or outcomes expected to have no specified causal effect to reveal residual bias or measurement problems. A failed negative control challenges assumptions; a passed one does not rule out every confounder.

### stat-15-22

**Target trial emulation**

Specify eligibility, treatment strategies, assignment, follow-up, outcomes, estimand and analysis as if designing a trial, then map observational data to it. Align time zero to avoid immortal-time and selection biases.

## Worked Python demonstrations

Complete offline program: [chapter_15.py](../examples/chapter_15.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_15.py
```

### The same outcome models give a reversed naive contrast

Treatment improves both strata by one. Treated units are concentrated in the low-baseline stratum, while controls are mostly in the high-baseline stratum. Their raw mean difference is minus 5.4. Standardizing each intervention to the same population gives plus one, provided the strata are a valid adjustment set.

### Selection opens an association

A and U are independent binary variables in the full four-cell population. Retaining cases where either is one removes the joint-zero cell. Within that selected group, A and Y=U become negatively associated even though A never causes Y. This is the mechanism behind collider selection bias.

### ATE and ATT can both be correct

Conditional effects one and five average to 1.8 in a population mostly in the first stratum, but to 4.2 among treated units mostly in the second. The difference is target weighting, not estimator disagreement. State which population owns the decision.

### Complete executable example

```python
import numpy as np

def standardization():
    treated_mean=np.array([2.,10.]);control_mean=np.array([1.,9.])
    target=np.array([.5,.5])
    treated_composition=np.array([.9,.1]);control_composition=np.array([.1,.9])
    naive=treated_mean@treated_composition-control_mean@control_composition
    ate=(treated_mean-control_mean)@target
    assert np.isclose(naive,-5.4) and np.isclose(ate,1.)
    print("Naive difference:",naive,"standardized causal contrast under assumptions:",ate)

def collider_selection():
    a=np.array([0,0,1,1]);u=np.array([0,1,0,1]);y=u.copy()
    assert np.isclose(np.corrcoef(a,y)[0,1],0)
    selected=(a+u)>0
    selected_correlation=np.corrcoef(a[selected],y[selected])[0,1]
    assert selected_correlation < 0
    print("Unconditional correlation: 0; after selection:",selected_correlation)

def effect_targets():
    conditional=np.array([1.,5.])
    population=np.array([.8,.2]);treated=np.array([.2,.8])
    ate=conditional@population;att=conditional@treated
    assert np.isclose(ate,1.8) and np.isclose(att,4.2)
    print("ATE:",ate,"ATT:",att)

def main():
    standardization();collider_selection();effect_targets()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does adding more controls improve causal validity?** Only if their causal roles justify adjustment. Pretreatment common causes can block bias paths; colliders can open them, and mediators can remove part of the total effect. Use the estimand and a defensible causal model to choose controls.

**Interview: How can two accurate models disagree about an intervention?** Prediction learns the observational distribution. Different causal mechanisms can produce that same distribution yet imply different responses to intervention. Identification assumptions supply information that predictive fit cannot.

**Interview: What does lack of overlap mean for rollout?** Some target people have no credible observed comparator under one intervention. Restrict the target, collect new evidence, or explicitly state extrapolation assumptions. Weight clipping stabilizes numbers but does not create missing counterfactual support.

## Primary sources and official APIs

- [Hernán and Robins, Causal Inference: What If](https://miguelhernan.org/whatifbook).

- [Pearl, Causal inference in statistics: An overview](https://ftp.cs.ucla.edu/pub/stat_ser/r350.pdf).

## Reading connections

[Previous chapter](14-online-experimentation-and-a-b-testing.md) | [Book contents](../README.md) | [Next chapter](16-quasi-experiments-and-causal-study-designs.md)
