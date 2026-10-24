# 1. Problem Formulation and Statistical Reasoning

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-001`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A service team asks whether a new routing rule will reduce delay. Three different questions hide inside that sentence: what delays occurred, which requests will be late, and what delay would occur if the rule changed. The first is descriptive, the second predictive, and the third causal. A model can answer one well while being uninformative about another.

Begin with an analysis contract: action, outcome, population, unit, time horizon, estimand and loss. For example, estimate the difference in mean seven-day delay per assigned customer, with all eligible customers retained. The contract determines aggregation, assignment, missing-data handling and validation. A narrow interval around the wrong quantity is precise evidence for the wrong decision.

## Methods, mechanisms, and limits

### stat-01-01

**Descriptive analysis**

Compute a clearly denominated summary such as total delay divided by eligible requests. This describes the recorded population; changing the denominator from requests to customers changes the question even with identical events.

### stat-01-02

**Exploratory analysis**

Use plots and subgroup summaries to discover candidate mechanisms. Because the same observations suggest the hypothesis, apparent extremes require fresh validation before they become confirmed findings. Record discoveries separately from prespecified comparisons.

### stat-01-03

**Confirmatory analysis**

Freeze the outcome, exclusions, estimator and decision threshold before inspecting treatment differences. Confirmation concerns the entire procedure, including planned comparisons; a small p-value after many unreported attempts does not restore that procedure.

### stat-01-04

**Predictive modeling**

Estimate an outcome using information available at prediction time, then evaluate on deployment-like held-out observations. A predictor can exploit a symptom of a cause without revealing an intervention that would improve outcomes.

### stat-01-05

**Causal inference**

Compare potential outcomes under explicit interventions. Randomization or justified adjustment connects observed comparisons to that target. Similar treated and untreated averages can hide treatment effects when selection into treatment differs.

### stat-01-06

**Prescriptive analytics**

Convert evidence into actions using feasible options, resource limits and a stated objective. A staffing recommendation must account for capacity and intervention consequences; a forecast of high demand alone is not an optimal staffing rule.

### stat-01-07

**Statistical decision theory**

For each action a, average its loss L(a,theta) over uncertainty about theta and choose the smallest expected loss. Asymmetric harms imply asymmetric decision thresholds, even when a probability model is perfectly calibrated.

### stat-01-08

**Data-generating processes**

Specify how entities enter the sample, receive treatment, generate measurements and leave observation. A plausible simulation of this mechanism reveals which dependencies or censoring rules an analysis must preserve.

### stat-01-09

**Estimands**

Write the target as a mathematical quantity, such as E[Y(1)-Y(0)] for eligible customers at day seven. An estimator is the recipe used to approximate it, not the estimand itself.

### stat-01-10

**Target populations**

Define eligibility and the time/place scope before generalizing. A model evaluated on existing customers does not automatically describe prospective customers, who may have different behavior and no history.

### stat-01-11

**Units of observation**

A row might be a request, an account-day or a labeler judgment. Repeated rows from one customer are not independent customers. Identify the record key before computing uncertainty.

### stat-01-12

**Units of analysis**

The entity summarized in conclusions may differ from the row. Average customer-level means to estimate a typical customer's experience; average requests to estimate a typical request's experience. Heavy users receive different influence.

### stat-01-13

**Units of assignment**

If entire teams receive a change, team assignment determines independent treatment variation. Treating every team member as independently randomized understates uncertainty even when millions of member records exist.

### stat-01-14

**Identification**

Ask whether the observable distribution and assumptions uniquely determine the estimand. No amount of flexible fitting identifies an intervention effect if uncontrolled common causes can explain the observed association equally well.

### stat-01-15

**Identifiability**

In a model with two identical predictor columns, their coefficient sum is estimable while the separate coefficients are not. Distinct parameter values make identical predictions, so more optimization cannot resolve the ambiguity.

### stat-01-16

**Internal validity**

Check whether assignment, attrition, measurement and analysis support the intended inference inside the study. Randomization at enrollment does not protect a comparison restricted to a treatment-affected subset of survivors.

### stat-01-17

**External validity**

Transporting evidence requires relevant effect modifiers and context to align, or a justified adjustment. A laboratory efficiency gain may disappear under production load even if the laboratory experiment was internally valid.

### stat-01-18

**Construct validity**

A count of clicks is an operational measure, not automatically satisfaction. Validate the connection with user research or independent outcomes; optimizing a convenient proxy can degrade the underlying construct.

### stat-01-19

**Practical significance**

Compare the effect and its uncertainty with an operational threshold. A 0.01% improvement may be detectable with huge traffic but insufficient to pay implementation cost or justify rollout risk.

### stat-01-20

**Statistical versus substantive uncertainty**

Sampling uncertainty shrinks with additional independent observations. Ambiguous labels, unobserved confounding and disputed objectives may not. Report these uncertainties separately instead of compressing them into one standard error.

### stat-01-21

**Sensitivity analysis**

Change defensible assumptions systematically, such as attrition effects or cost ratios, and locate the point where the decision reverses. A stable estimate across cosmetic settings does not establish robustness to the important untestable assumption.

### stat-01-22

**Triangulation**

Seek evidence with different failure modes, such as randomized assignment, operational logs and qualitative investigations. Agreement is stronger when the sources do not share the same measurement error or selection mechanism.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: turn a vague performance question into an analysis contract

A service owner says the new routing rule makes things faster. Start by identifying the decision: whether to deploy the rule to all eligible requests next month. Define the outcome as elapsed time from accepted request to completed response, specify timeout handling, and decide whether retries belong to the original request or create new events. A mean that excludes timeouts measures speed among completions, not the overall customer experience.

Next specify the population and unit. A typical request gives heavy users more influence because they generate more requests. A typical customer gives each customer equal weight after summarizing their experience. A typical site can weight a small site as much as a large one. These are different estimands, not alternate coding styles. If assignment is by site, the independent treatment variation also occurs by site even if the outcome is request-level.

Choose the time horizon and practical margin. A two-millisecond improvement can be statistically detectable with huge traffic but irrelevant if deployment adds maintenance cost. A ten-second reduction in rare timeouts may matter greatly even if the median is unchanged. The primary estimand might be average latency, a tail quantile, failure probability, or expected cost combining delay and failures. Each requires its own estimator and uncertainty treatment.

Finally define what would change the decision. A point estimate alone does not specify whether to act under uncertainty. A conservative rollout policy might require evidence that expected benefit exceeds cost with an acceptable downside probability, plus guardrails on failures. The analysis should expose the assumptions controlling that choice, not simply produce a favorable metric.

### Case study: distinguish identification from estimation

Suppose treatment and outcome are strongly associated in a million records. More data can reduce uncertainty about the observational association. It cannot by itself determine whether treatment caused the outcome, whether the outcome influenced treatment, or whether a common cause generated both. If those mechanisms imply the same observed distribution but different intervention effects, the causal target is not identified by that distribution alone.

Estimation begins after assumptions connect the target to observables. Randomization can supply an assignment argument; a justified adjustment set can supply another. Once the target is identified, finite samples, model fitting and numerical errors determine how precisely it is estimated. Reporting a tiny regression standard error addresses estimation variability under a model, not the prior identification gap.

Parameter identifiability is a related but distinct concept. If two predictor columns are identical, separate coefficients cannot be distinguished even under a fully specified regression model. Their sum may remain identifiable and predictions can be unique. This distinction helps avoid demanding a unique scientific interpretation from a model that contains redundant parameterizations.

### Case study: communicate uncertainty that a confidence interval omits

An analysis estimates a benefit of five units with a narrow interval from four to six. That interval may represent repeated-sample uncertainty conditional on a fixed outcome definition, model, population and measurement process. If a different reasonable timeout rule changes the estimate to minus two, substantive uncertainty dominates the narrow interval.

A useful sensitivity analysis changes consequential assumptions: outcome definitions, missing-outcome scenarios, unmeasured-confounding strength, target population weights or decision costs. It identifies where the conclusion reverses and explains why the examined range is plausible. Changing graph colors or an optimizer's irrelevant tolerance is not meaningful robustness analysis.

Triangulation compares evidence that fails differently. A randomized pilot, a carefully designed observational study and qualitative operational evidence may reinforce or challenge one another. Their agreement is less informative if they share the same erroneous logging table or exclude the same affected population. Describe the dependence between evidence sources rather than counting them as independent votes.

### An analyst's explanation to a decision owner

A clear report can say: the assignment-defined study estimates a mean reduction of five units for existing eligible customers over seven days; uncertainty from the randomized comparison is four to six units; the result excludes new customers and assumes the missing outcomes are comparable after adjustment; plausible adverse missing-outcome scenarios reduce the estimated benefit to one; deployment cost corresponds to two units of benefit. This statement makes the remaining decision tension visible.

The same evidence should not be compressed into the model says deploy. Decision ownership belongs to the person or process accountable for consequences. Statistical work supplies a well-defined target, defensible evidence, uncertainty and a transparent connection to the available actions.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_01.py](../examples/chapter_01.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_01.py
```

### A denominator changes the estimand

Three fast requests belong to one customer and one slow request to another. The request mean is 3; the customer mean is 5. Neither arithmetic result is defective. They answer different questions because the first weights customers by activity. The assertion fixes that distinction in a tiny auditable table.

### A probability is not an action

With false-alarm cost 2 and missed-event cost 8, intervening costs `2*(1-p)` in expectation while doing nothing costs `8*p`. Equating them gives a threshold of 0.2, so probabilities 0.3 and 0.8 trigger action. A default threshold of 0.5 would ignore the stated consequences.

### Complete executable example

```python
import numpy as np


def compare_units():
    delays = np.array([1.0, 1.0, 1.0, 9.0])
    customer = np.array([0, 0, 0, 1])
    per_request = delays.mean()
    per_customer = np.mean([delays[customer == k].mean() for k in [0, 1]])
    assert per_request == 3 and per_customer == 5
    print("Request mean:", per_request, "customer mean:", per_customer)


def choose_action():
    probability = np.array([0.1, 0.3, 0.8])
    false_alarm_cost, miss_cost = 2.0, 8.0
    threshold = false_alarm_cost / (false_alarm_cost + miss_cost)
    intervene = probability > threshold
    assert intervene.tolist() == [False, True, True]
    assert np.all(np.minimum(2 * (1 - probability), 8 * probability) <= 8 * probability)
    print("Loss-derived threshold:", threshold, "intervene:", intervene.tolist())


def main():
    compare_units()
    choose_action()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why can an accurate churn model fail to improve retention?** It identifies likely departures, not necessarily customers whose departure an offer can prevent. Some high-risk customers cannot be retained; some low-risk customers would accept discounts unnecessarily. Estimate incremental treatment effects and evaluate net value under the actual offer policy.

**Interview: What would you clarify before analyzing an experiment?** Ask what was randomized, who was eligible, what outcome and horizon define success, and which decision the evidence will inform. These facts determine the estimand and independent variation before any significance test is selected.

## Primary sources and official APIs

- [Hernán and Robins, Causal Inference: What If, author-maintained text](https://miguelhernan.org/whatifbook).

- [NIST statistical methods handbook](https://www.itl.nist.gov/div898/handbook/dtoc.htm).

## Reading connections

[Book contents](../README.md) | [Next chapter](02-mathematical-foundations.md)
