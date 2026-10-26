# 14. Online Experimentation and A/B Testing

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-014`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

An online experiment is a measurement system wrapped around random assignment. Eligibility, assignment, exposure, logging and outcome maturity can each alter the analysis population. A clean statistical formula cannot repair a treatment-dependent logging outage or an experiment that excludes users because the treatment changed their behavior.

### Derive CUPED adjustment

Let X be a pretreatment covariate and Y the experiment outcome. Define \(Y_{\mathrm{adjusted}}=Y-\theta\bigl(X-\mathbb{E}[X]\bigr)\). The adjustment has the same expectation when E[X] is correctly centered. Its variance is \(\operatorname{Var}(Y)+\theta^2\operatorname{Var}(X)-2\theta\operatorname{Cov}(X,Y)\), minimized at \(\theta=\frac{\operatorname{Cov}(X,Y)}{\operatorname{Var}(X)}\). The resulting variance is \(\operatorname{Var}(Y)(1-\rho^2)\). The covariate must not be affected by treatment, and practical estimation, missing preperiod values and adaptive reuse require care.

### Ratios and randomization units

Revenue per visit is a ratio of totals, \(\frac{\sum_i R_i}{\sum_i V_i}\), not generally the average of customer ratios \(\frac{R_i}{V_i}\). For independent customers, the first-order ratio influence is \(\frac{R_i-rV_i}{\bar{V}}\). Its sample standard deviation divided by \(\sqrt{n}\) estimates a delta-method standard error. This retains numerator-denominator covariance and customer-level dependence among visits. If treatment changes visits, the ratio and total revenue answer different questions.

An experiment decision should combine an effect interval, practical threshold, mature outcomes, integrity checks and guardrails. A statistically clear metric gain can coexist with unacceptable reliability or user harms. Those tradeoffs need explicit owners and criteria.

## Methods, mechanisms, and limits

### stat-14-01

**A/B testing**

Randomly compare a control and one alternative using a prespecified assignment unit and outcome horizon. Estimate the effect of assignment first; operational logging and interference can defeat assumptions despite a randomized label.

### stat-14-02

**A/B/n testing**

Compare multiple variants while controlling the intended family of comparisons. Shared controls create correlated estimates. Select the best variant using development evidence and acknowledge selection bias in its apparent lift.

### stat-14-03

**Randomization integrity checks**

Check assignment determinism, eligibility, hash distribution, reassignments and event delivery. Aggregate balance alone can miss correlated failures. Integrity failures should trigger investigation before interpreting outcome differences.

### stat-14-04

**Sample ratio mismatch**

Compare observed arm counts with expected allocation probabilities. A small SRM p-value signals incompatible allocation counts but does not identify the cause. Triggered populations and bot filtering can generate apparent or real mismatches.

### stat-14-05

**A/A tests**

Run identical experiences through the experimental pipeline to evaluate false positives, allocation and metric behavior. One clean A/A test does not guarantee all future experiments, devices or exposure paths are correct.

### stat-14-06

**Intent-to-treat analysis**

Analyze units according to assigned treatment regardless of uptake. This estimates assignment policy effects and preserves randomization. Excluding noncompliers can break comparability even if it seems closer to product exposure.

### stat-14-07

**Treatment-on-the-treated effects**

Effects among those treated or induced to comply require a precise target and assumptions. Dividing ITT by uptake can identify a complier effect under instrumental-variable conditions, not a universal effect for every treated unit.

### stat-14-08

**Exposure definitions**

Define exposure using logged opportunities and timestamps. Treatment can alter whether exposure is observed. Conditioning on such exposure without design justification can select different populations across arms.

### stat-14-09

**Triggered analysis**

Restrict to a prespecified relevant trigger measured symmetrically and unaffected by assignment, or use an appropriate counterfactual trigger design. Naively retaining only actual treatment users destroys the randomized comparison.

### stat-14-10

**Guardrail metrics**

Track adverse outcomes such as latency, complaints or failures alongside the primary metric. Specify actionable margins and multiplicity policy. A nonsignificant guardrail estimate with wide uncertainty does not establish safety.

### stat-14-11

**Overall evaluation criteria**

Define the main outcome or utility rule before results. A composite metric embeds weights and value judgments. Explain how the criterion handles tradeoffs rather than searching metrics until a positive story appears.

### stat-14-12

**Ratio metrics**

Distinguish ratio of sums from mean of unit ratios and specify denominator eligibility. Zero denominators and treatment-driven denominator changes require explicit interpretation. Aggregate both numerator and denominator at assignment grain.

### stat-14-13

**Delta-method ratio inference**

Linearize the ratio around mean numerator and denominator, retaining covariance. Near-zero denominators or heavy tails can make normal approximations unreliable. Cluster at the assignment unit before computing the variance.

### stat-14-14

**CUPED**

Subtract a centered pretreatment covariate with a variance-minimizing coefficient. Correlation with the outcome determines potential gain. Post-treatment covariates can remove part of the treatment effect or introduce bias.

### stat-14-15

**Regression-adjusted experiment analysis**

Regress outcomes on assignment and baseline predictors, with appropriate interactions and robust uncertainty when needed. Adjustment can improve precision without changing the target if designed correctly; model-driven subgroup selection can compromise inference.

### stat-14-16

**Unequal treatment allocation**

Allocate traffic unevenly when cost, risk or capacity warrants it. Equal allocation is optimal only under particular variance/cost conditions. Very small control shares can limit precision despite enormous treatment traffic.

### stat-14-17

**Persistent holdouts**

Maintain a randomly selected control over an extended period to assess cumulative impacts. Attrition, cross-exposure and changes in the intervention can erode interpretation. A long holdout is a maintained study, not a forgotten flag.

### stat-14-18

**Novelty effects**

A temporary response to newness can exaggerate short-term lift. Examine effects by time since exposure and preserve controls through a meaningful adaptation window. Calendar trends and cohort composition can mimic decay.

### stat-14-19

**Primacy and learning effects**

Prior habits and accumulated skill can change response over repeated use. Compare coherent exposure cohorts and timing. Users who remain long enough to learn may themselves be a selected subgroup.

### stat-14-20

**Treatment effect dilution**

When only some assigned units can be affected, the overall ITT effect is diluted. This is a real policy effect for the full eligible population, not automatically a defect requiring post-treatment exclusions.

### stat-14-21

**Network interference**

One unit's treatment changes another's outcome through sharing or competition. Individual randomization may estimate a mixed-saturation effect. Cluster or network designs need an explicit exposure mapping and spillover estimand.

### stat-14-22

**Switchback experiments**

Alternate randomized treatment across time blocks, often within locations. Handle serial dependence, carryover and transition periods. Rapid switching increases nominal blocks but may reduce the number of informative independent comparisons.

### stat-14-23

**Geo experiments**

Use geographic units when spillovers or implementation make individual assignment unsuitable. Few heterogeneous regions create power and balance challenges. Analyze assignment at geography level and consider cross-border contamination.

### stat-14-24

**Marketplace experiments**

Treatments can change supply, demand and competition for shared resources. Buyer-only effects in a mixed experiment may differ from full-market rollout. Two-sided or cluster designs make the equilibrium target explicit.

### stat-14-25

**Long-term effect estimation**

Estimate effects over sufficient follow-up and distinguish calendar time from exposure age. Short-term surrogate gains can miss retention loss or strategic adaptation. Long-term extrapolation needs evidence about persistence.

### stat-14-26

**Surrogate metrics**

An intermediate outcome can predict a later outcome without preserving treatment effects. Causal surrogacy requires stronger assumptions or empirical validation across interventions, not merely high individual-level correlation.

### stat-14-27

**Experiment interaction analysis**

Factorial or otherwise planned overlap can reveal whether interventions amplify or offset each other. Untracked concurrent experiments change the effective treatment context and complicate attribution.

### stat-14-28

**Experiment portfolio governance**

Coordinate eligibility layers, shared holdouts, metric definitions, sequential rules and owners. Governance preserves interpretation across many studies. A portfolio optimized only for number of significant wins invites selection and reproducibility problems.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: a conversion lift caused by logging

A control arm logs all eligible users, while a new treatment page drops some failed visits before the exposure event is emitted. Conversion among logged exposed users rises, even if no customer's purchase behavior improves. The observed denominator is now affected by treatment and correlated with outcome. Randomization at assignment remains valid, but the exposed-only analysis no longer compares equivalent populations.

An intent-to-treat analysis beginning from assignment logs can reveal the issue if outcome collection remains complete. Compare assignment counts, exposure rates, event funnels and missing outcomes by arm and device. A sample-ratio mismatch in the exposed population is diagnostic evidence, not a standalone estimate of the resulting bias. Repair the measurement path and preserve both the original and corrected definitions so the result can be reconstructed.

Triggered analysis can be valid when a trigger identifies a relevant opportunity independently of assignment, or when a carefully designed counterfactual trigger is recorded symmetrically. It is not valid merely because the remaining users look engaged. The important distinction is whether treatment changed entry into the analyzed subset.

### Case study: CUPED with incomplete prehistory

Existing users have a previous-month activity measure that strongly predicts experiment activity. New users have no preperiod record. Dropping new users yields a different population; filling their covariate with zero treats absence of history as genuine zero activity. A practical design can include a missing-history indicator and define adjustment separately or model the baseline information available for each group.

CUPED's ideal variance reduction factor 1-rho-squared describes a linear adjustment with the relevant covariance. If \(\rho=0.8\), the remaining variance is .36 of the original, which can substantially improve precision. That does not imply every metric or user segment receives the same gain. Sparse counts, outliers and low pre/post correlation may yield little benefit. Estimate and validate the adjustment without permitting outcome-informed exclusion rules or future data to enter the baseline.

The adjustment coefficient can be estimated from pooled data with an appropriate analysis, from a separate historical sample, or using cross-fitting in more flexible variants. The precise inferential treatment should follow the implemented estimator. The central scientific condition is that the covariate precedes and is unaffected by the intervention, not that it happens to have a column name containing pre.

### Case study: ratios can hide a beneficial or harmful total change

An interface reduces low-value browsing sessions, leaving total purchases unchanged while sessions fall. Purchases per session rises. This could indicate improved efficiency, but it does not establish higher total customer value. Conversely, a feature may attract exploratory sessions that lower conversion per session while increasing total purchases and long-term retention.

Define the primary estimand before choosing which ratio to celebrate. Revenue per assigned user, revenue per exposed user and revenue per session have different denominators, causal interpretations and sensitivity to behavior changes. Analyze numerator and denominator components alongside the ratio. The delta-method covariance term matters because high-activity users can contribute large values to both.

When ratios have rare or zero denominators, inspect the distribution of unit contributions. A few power users can dominate a ratio of totals, while averaging unit ratios can overemphasize users with one opportunity. Resampling must preserve the randomized unit and the joint numerator-denominator record. A simple standard error computed on individual sessions may badly understate uncertainty in a user-randomized study.

### Case study: rollout effects differ from mixed-experiment effects

A marketplace search change improves the chance that treated buyers obtain scarce inventory. Control buyers may then lose access to that inventory. The treatment-control contrast measures an effect within a mixed marketplace at that saturation, not necessarily the effect of treating every buyer. Full rollout removes the same competitive comparison and can shift seller behavior, pricing or supply.

Choose a design that addresses the desired policy, such as geographic or market clusters, time-based switchbacks with adequate washout, or explicit saturation experiments. Each introduces its own costs: few clusters, serial dependence, spillovers across boundaries or carryover. Document the exposure mapping and the target equilibrium or short-run effect. Statistical precision is secondary if the experiment does not represent the rollout question.

Long-term holdouts and cohort analyses help assess novelty, learning and cumulative harms, but their populations must remain comparable as users enter, leave and cross devices. A persistent identifier policy is part of study validity. A short-term surrogate should be validated against the outcome that ultimately matters across relevant interventions, not only shown to correlate with it among users.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_14.py](../examples/chapter_14.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_14.py
```

### Count integrity before evaluating lift

A nominally equal assignment with 600 versus 400 users yields a chi-square statistic of 40 and an extremely small p-value. This does not diagnose the bug, but it makes the intended 50/50 sampling model implausible. Investigate assignment and logging before reading conversion results.

### Remove predictable baseline variation

The baseline feature and noise were constructed to be uncorrelated. CUPED recovers theta three, leaves the mean unchanged and reduces variance from 26 to 3.5. The code verifies the exact sample covariance identity, isolating the variance-reduction mechanism without pretending this fixture is a real experiment.

### Preserve numerator-denominator covariance

Four customers produce total revenue 22 and ten visits, so the ratio is 2.2. The mean of customer ratios is two. The influence calculation centers each customer's contribution and produces a positive SE, but four customers are too few to trust a high-accuracy asymptotic coverage claim.

### Complete executable example

```python
import numpy as np
import statsmodels.api as sm
from scipy import stats


def allocation_integrity():
    result = stats.chisquare([600, 400], f_exp=[500, 500])
    assert result.pvalue < 1e-8
    print("SRM statistic/p:", result.statistic, result.pvalue)


def cuped():
    x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    noise = np.array([1.0, -2.0, 2.0, -2.0, 1.0])
    y = 10 + 3 * x + noise
    theta = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    adjusted = y - theta * (x - x.mean())
    assert np.isclose(theta, 3) and np.isclose(adjusted.mean(), y.mean())
    rho = np.corrcoef(x, y)[0, 1]
    assert np.isclose(adjusted.var(ddof=1), y.var(ddof=1) * (1 - rho**2))
    print("CUPED theta:", theta, "variance before/after:", y.var(ddof=1), adjusted.var(ddof=1))


def ratio_metric():
    revenue = np.array([1.0, 9.0, 4.0, 8.0])
    visits = np.array([1.0, 3.0, 2.0, 4.0])
    ratio = revenue.sum() / visits.sum()
    influence = (revenue - ratio * visits) / visits.mean()
    se = influence.std(ddof=1) / np.sqrt(len(visits))
    assert np.isclose(ratio, 2.2) and np.isclose(np.mean(revenue / visits), 2.0)
    assert abs(influence.mean()) < 1e-12 and se > 0
    print("Ratio of totals:", ratio, "mean user ratio:", np.mean(revenue / visits), "delta SE:", se)


def adjusted_randomized_comparison():
    rng = np.random.default_rng(1407)
    n = 240
    baseline = rng.normal(size=n)
    assigned = rng.permutation(np.repeat([0.0, 1.0], n // 2))
    outcome = 10 + 2 * assigned + 3 * baseline + rng.normal(size=n)
    centered = baseline - baseline.mean()
    design = np.column_stack([np.ones(n), assigned, centered, assigned * centered])
    fit = sm.OLS(outcome, design).fit(cov_type="HC2")
    treated, control = outcome[assigned == 1], outcome[assigned == 0]
    raw = treated.mean() - control.mean()
    raw_se = np.sqrt(treated.var(ddof=1) / len(treated) + control.var(ddof=1) / len(control))
    adjusted, se = fit.params[1], fit.bse[1]
    interval = adjusted + np.array([-1, 1]) * stats.norm.ppf(0.975) * se
    assert se < raw_se and abs(adjusted - 2) < 0.5
    assert np.linalg.matrix_rank(design) == 4
    print(
        "Assignment effect raw/adjusted:",
        raw,
        adjusted,
        "SE raw/HC2:",
        raw_se,
        se,
        "adjusted approximate 95% CI:",
        interval,
    )
    # This fixture illustrates precision; one interval cannot establish coverage.


def main():
    allocation_integrity()
    cuped()
    ratio_metric()
    adjusted_randomized_comparison()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Can CUPED change the treatment effect?** Correct baseline adjustment targets the same assignment effect in expectation and can change its realized estimate by removing chance imbalance. Using treatment-affected covariates or asymmetric missingness can instead change the target or create bias.

**Interview: Your experiment is significant but has SRM. Ship it?** Investigate the allocation inconsistency and its impact first. Significance assumes a valid analysis process; a logging or eligibility defect can create an apparent effect. Record the affected scope and rerun or repair the study as justified.

**Interview: Why does a user-randomized ratio metric need user-level uncertainty?** Visits within a user share assignment and behavior. Treating visits as independent inflates the nominal information. Aggregate user numerator/denominator contributions and retain their covariance.

## Primary sources and official APIs

- [Deng et al., original CUPED paper](https://ai.stanford.edu/~ronnyk/2013-02CUPEDImprovingSensitivityOfControlledExperiments.pdf).

- [Microsoft Research, variance reduction in online experiments](https://www.microsoft.com/en-us/research/articles/deep-dive-into-variance-reduction/).

## Connected worked tutorial

[The complete experimentation route](../tutorials/experimentation/README.md). Follow twelve connected units from assignment and metric construction through integrity, power, adjusted effects, interference and a decision memo.

## Reading connections

[Previous chapter](13-classical-experimental-design.md) | [Book contents](../README.md) | [Next chapter](15-causal-inference-foundations.md)
