# 38. Product, Customer, Marketing, and Business Analytics

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-038`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Business analytics connects observed behavior to decisions about products, customers and resources. The danger is not a shortage of metrics; it is measuring a convenient proxy and giving it a stronger interpretation than the design supports. A conversion rate, a customer-value prediction and an incremental treatment effect answer different questions. Define the population, time window, unit and intended action before selecting a method.

### Build a metric from accountable events

A metric tree decomposes an outcome into components whose units and denominators agree. Revenue might equal active customers times orders per active customer times revenue per order, provided all three use the same window and eligible population. A funnel needs explicit transition rules: whether stages must occur in order, whether users or sessions are counted, and how repeated attempts are handled. Duplicate events and delayed ingestion can change apparent conversion without any product change.

Cohorts preserve time since an entry event so retention comparisons do not confuse age with calendar period. A recent cohort cannot yet contribute a twelve-month retention observation. Include only mature follow-up in the denominator or use a method that accounts for censoring. A declining aggregate retention rate can arise from acquiring more early-stage users even when every cohort's trajectory is unchanged.

### Predictive value is not incremental value

A churn model predicts who may leave under the observed policy. A retention intervention should target people whose outcome is improved by the intervention after accounting for cost, not automatically those with highest baseline risk. Similarly, attribution allocates credit among observed touchpoints, while incrementality asks what would have happened without an action. The latter requires an experimental or credible causal identification strategy.

Customer lifetime value is a discounted expectation of future contribution over a stated horizon. Write \(\mathrm{CLV}=\sum_t\frac{\mathbb{E}[\mathrm{margin}_t\,\mathrm{active}_t]}{(1+r)^t}\) minus relevant acquisition or service costs. The discount rate, margin definition, churn process and forecast horizon are assumptions. A point prediction is not a known customer asset value, and a high-revenue customer can have low contribution after costly service or incentives.

### Model market response with its identification limits

Demand and choice models relate outcomes to prices, attributes and marketing. Prices are often changed in response to anticipated demand, so an observational price coefficient can be confounded. Adstock represents carryover and saturation represents diminishing response, but adding those curves does not create causal identification. Use randomized or quasi-experimental evidence where possible, document controls and sensitivity, and distinguish interpolation within observed spend from extrapolation to a radically different policy.

### Use language models as measured analytical components

Customer messages, reviews and support notes can enrich analysis through extraction or classification. Define a schema for complaint type, product, event time and supporting text span. Measure extraction error on a representative human-reviewed sample, including ambiguous and multilingual cases. Preserve missing/uncertain labels rather than forcing every message into a confident category. If the resulting fields feed a churn model, propagate their provenance and consider how measurement error affects conclusions.

A subject-matter assistant can retrieve KPI definitions, query documentation and prior experiment reports, then explain an executed table. It should link a conversion percentage to the actual numerator/denominator output and a policy statement to the relevant document version. Fine-tuning may improve consistent extraction or report format, while RAG supplies current definitions and evidence. Neither turns observational segmentation into causal incrementality. The final business narrative must preserve this distinction even when the prose sounds persuasive.

### Compare actions with complete economics

Report volume, rate and mix changes separately when an aggregate moves. Include cannibalization, service costs and delayed effects in intervention evaluation. Prefer an explicit feasible decision rule with uncertainty and ownership over a collection of impressive dashboards. The examples show funnel denominators, cohort maturity, adstock and exact price/quantity decomposition, with assertions that keep the arithmetic auditable.

## Methods, mechanisms, and limits

### stat-38-01

**Metric trees**

A metric tree links an outcome to component drivers through explicit arithmetic or causal hypotheses. An arithmetic identity such as \(\mathrm{revenue}=\mathrm{orders}\times\mathrm{revenue\ per\ order}\) is exact only when units and populations align. A causal arrow requires additional evidence. Use the tree to locate where a change occurred, then investigate why. Avoid double-counting correlated branches as independent contributions to the same business improvement.

### stat-38-02

**KPI design**

KPI design specifies a measurable indicator, eligible population, time window, data source and intended decision. Include guardrails against gaming or harmful tradeoffs. A metric can be computed accurately and still be a poor proxy for value. Document late data, exclusions and revisions so teams do not compare incompatible numbers under the same name.

### stat-38-03

**North-star metrics**

A north-star metric attempts to summarize sustained product value, such as successful meaningful usage rather than raw activity. Its usefulness depends on whether it tracks the value users and the organization actually seek. One scalar can hide distributional harms or quality deterioration. Pair it with diagnostic and guardrail metrics, and revisit the relationship when product behavior or incentives change.

### stat-38-04

**Funnel analysis**

Funnel analysis tracks progression through ordered stages with clearly defined identities and eligibility. A user-based funnel differs from a session-based one, and repeated attempts can change denominators. Specify whether stage B must follow stage A within a time window. A drop in one transition identifies an investigation point but does not establish which interface or customer factor caused it.

### stat-38-05

**Cohort analysis**

Cohort analysis groups entities by a shared starting event or characteristic and compares behavior at equal ages. It separates lifecycle effects from calendar composition more clearly than aggregate trends. Cohort definitions and follow-up maturity must be consistent. A recent acquisition campaign can change cohort mix, so compare both within-cohort trajectories and the composition of the overall population.

### stat-38-06

**Retention analysis**

Retention analysis measures continued activity under a stated activity definition and follow-up window. Rolling, exact-period and bracket retention are different metrics. Right censoring occurs when recent users have not had enough time to return. A missing observation should not be counted as a confirmed churn event. Use mature denominators or duration methods and report which convention was chosen.

### stat-38-07

**Churn modeling**

Churn modeling predicts departure or inactivity over a defined horizon from information available at a decision time. Label definitions, delayed outcomes and repeated customer rows create leakage risks. High predicted churn does not imply high treatment responsiveness. Evaluate calibration and utility under the actual intervention policy, with segment checks and a clear distinction between prediction and causal retention targeting.

### stat-38-08

**Customer lifetime value**

Customer lifetime value forecasts discounted future contribution over a stated horizon. It combines transaction frequency, margin, retention and costs, with uncertainty in each component. Revenue-only calculations omit economically important service or incentive costs. Validate by acquisition cohort and time horizon, and distinguish expected value for a group from a precise guaranteed value for one customer.

### stat-38-09

**RFM analysis**

RFM analysis summarizes recency, frequency and monetary activity for descriptive segmentation. Each component depends on the observation window and what counts as a transaction. Quantile bins are convenient but can create unstable boundaries and mix customers with different tenure. RFM is a useful baseline for targeting hypotheses, not proof that a segment will respond incrementally to a campaign.

### stat-38-10

**Customer segmentation**

Customer segmentation groups entities using behavior, needs or value features to support differentiated actions. A segment should be stable enough, interpretable and reachable through a meaningful decision. Clusters can reflect scaling or data availability rather than useful business structure. Validate the action associated with a segment, and avoid assigning causal explanations or sensitive traits from unsupervised grouping alone.

### stat-38-11

**BG/NBD models**

BG/NBD models represent repeat purchasing while alive and dropout associated with transaction opportunities, with heterogeneity in purchase and dropout behavior. They use recency, frequency and observation duration to infer future transactions in noncontractual settings. The behavioral assumptions can fail with seasonality, reactivation or changing marketing. Compare calibration across customer histories rather than treating inferred alive probability as an observed state.

### stat-38-12

**Pareto/NBD models**

Pareto/NBD models combine a purchase process with a continuous-time latent dropout process and heterogeneity across customers. They distinguish inactivity from permanent departure probabilistically when churn is not directly observed. Purchase/dropout assumptions and independence structure shape extrapolation. A good aggregate transaction forecast can conceal poor individual uncertainty, so inspect calibration by recency and frequency groups.

### stat-38-13

**Purchase timing models**

Purchase timing models estimate when the next transaction will occur, using duration, renewal or hazard formulations. The observation window creates censoring for customers who have not yet returned. Promotions and changing needs can make interpurchase intervals nonstationary. Define whether the target is the next purchase conditional on remaining active or a joint purchase/dropout outcome.

### stat-38-14

**Demand estimation**

Demand estimation relates quantity to prices, product attributes and other drivers. Identification is difficult when prices respond to anticipated demand or omitted supply conditions. Instrumental variables, experiments or structural assumptions may be needed for causal price-response claims. Distinguish observed sales from latent demand under stockouts, and specify the market and time aggregation used by the model.

### stat-38-15

**Price elasticity**

Price elasticity is the proportional change in demand associated with a proportional price change, often a derivative of log quantity with respect to log price. A log-log coefficient has that interpretation under the model. It is causal only with an appropriate identification argument. Elasticity can vary by price range, customer segment and time horizon, so extrapolating one estimate far beyond observed prices is risky.

### stat-38-16

**Cross-price elasticity**

Cross-price elasticity measures how demand for one offering changes with another's price. Positive values often suggest substitution and negative values complementarity under a suitable causal model. Common promotions, seasonality and simultaneous pricing can confound estimates. Define the choice set and market exposure; an omitted competitor can distort the apparent relationships among observed products.

### stat-38-17

**Discrete-choice models**

Discrete-choice models assign probabilities to alternatives based on utility components and a distribution of unobserved preference. The choice set must include options genuinely available to the decision-maker. Standard multinomial logit imposes a particular substitution pattern through its error assumptions. A predictive choice fit is not automatically a valid counterfactual model for a new product or major price change.

### stat-38-18

**Nested and mixed logit models**

Nested logit groups alternatives with correlated unobserved utility within nests, while mixed logit integrates over heterogeneous preference parameters. These relax different restrictions of simple logit. Nest structure, mixing distribution and identification matter. Simulation-based estimation adds numerical error, and flexible heterogeneity can overfit sparse individual histories. Validate substitution behavior using domain knowledge and external variation.

### stat-38-19

**Conjoint analysis**

Conjoint analysis elicits preferences through designed choices or ratings of attribute combinations. Experimental design determines which tradeoffs can be identified. Hypothetical choices may differ from real purchasing under budget, availability and social context. Analyze respondent heterogeneity and task quality, and distinguish stated-preference utility estimates from guaranteed market-share predictions.

### stat-38-20

**Marketing mix modeling**

Marketing mix modeling relates aggregate outcomes to media and other drivers, often using lag and saturation transformations. Correlated channels, seasonality, endogenous spend and limited variation make effects hard to separate. Experimental calibration can strengthen inference but does not remove every assumption. Report response-curve uncertainty and avoid interpreting a fitted allocation of historical outcome as automatically causal incremental return.

### stat-38-21

**Adstock models**

Adstock models represent carryover by accumulating current and decayed past exposure, for example \(a_t=x_t+\lambda a_{t-1}\). The decay parameter controls persistence and the chosen time unit matters. Alternative kernels can allow delayed peaks. Carryover can be confused with seasonality or autocorrelated demand, so infer it with controls, experiments or sensitivity rather than only a better in-sample fit.

### stat-38-22

**Saturation curves**

Saturation curves encode diminishing incremental response as exposure increases, using functions such as a Hill curve. Shape parameters determine where response rises and levels off. Sparse spend variation can leave the plateau unidentified. Extrapolating beyond observed support may dominate a budget recommendation, so show the data range and uncertainty rather than only a smooth response curve.

### stat-38-23

**Attribution modeling**

Attribution allocates observed conversion credit across touchpoints using a rule or model. Last-touch, multi-touch and algorithmic allocations can produce different answers from the same journey. They do not by themselves estimate what conversions would disappear without a channel. Exposure selection and missing touchpoints further complicate interpretation. Use attribution for descriptive accounting only unless a separate causal design supports incrementality.

### stat-38-24

**Incrementality measurement**

Incrementality measurement estimates the outcome caused by an intervention relative to its counterfactual absence. Randomized experiments are often the clearest design, while observational methods require explicit identifying assumptions. Interference, noncompliance and delayed effects affect the target. Report absolute incremental outcomes and uncertainty, not only relative lift among a selected exposed population.

### stat-38-25

**Cannibalization analysis**

Cannibalization analysis asks whether gains in one product or channel displace outcomes elsewhere. The relevant unit may be portfolio contribution rather than individual-product sales. Promotions can change timing as well as product choice, so use a sufficient post-period. A positive local metric can coexist with zero or negative total value if substitution and costs are ignored.

### stat-38-26

**Unit economics**

Unit economics measures revenue and costs per meaningful operational unit, such as order, active customer or completed service. Fixed versus variable costs and marginal versus average costs answer different decisions. A model-assisted workflow should include inference and human-review costs, not only API or compute cost. Keep cost timing and allocation assumptions visible so a favorable ratio is not created by inconsistent denominators.

### stat-38-27

**Decomposition analysis**

Decomposition analysis explains an aggregate change through components such as price, volume, mix and rate. The allocation of interaction terms depends on the chosen convention, so multiple valid decompositions can exist. An arithmetic contribution is not necessarily a causal contribution. Reconcile components exactly to the observed total before interpreting them.

### stat-38-28

**Oaxaca–Blinder decomposition**

Oaxaca-Blinder decomposition splits group mean differences into portions associated with covariate differences and coefficient differences under fitted linear models. The reference coefficient structure affects the decomposition, and omitted variables or selection can alter results. The unexplained portion is not automatically discrimination or a causal effect. State the model, comparison population and descriptive interpretation.

### stat-38-29

**Index-number methods**

Index-number methods separate aggregate value change into price and quantity components using base-period, current-period or combined weights. Laspeyres and Paasche indices answer different weighted comparisons, while Fisher combines them geometrically. Product entry, quality changes and substitution complicate interpretation. Report the weighting convention and coverage so an index is not mistaken for an unambiguous universal inflation or volume measure.

### stat-38-30

**Seasonal adjustment**

Seasonal adjustment removes estimated recurring seasonal/calendar patterns to support comparisons of underlying movement. It is model-based and can be revised when new data arrive. One-time shocks should not automatically be absorbed into seasonality, and endpoint estimates are uncertain. Keep raw and adjusted series available, document the method and avoid treating an adjusted change as causal evidence.

## Worked Python demonstrations

Complete offline program: [chapter_38.py](../examples/chapter_38.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_38.py
```

### Keep funnel and cohort denominators visible

One thousand entrants produce four hundred intermediate events and one hundred completions. Step conversions are 0.4 and 0.25, whose product is the overall 0.1. For the retention example, only the first cohort has mature follow-up, so the reported mature-cohort rate is \(\frac{60}{100}=0.6\). The second cohort is not silently treated as a completed observation.

### Separate carryover from diminishing response

A one-time exposure of ten decays through adstock values [10,5,2.5,1.25] when \(\lambda=0.5\). Separately, \(\frac{x}{1+x}\) gives responses \([0,0.5,\frac{2}{3},0.8]\) at exposures [0,1,2,4]. These curves demonstrate chosen mechanisms. Their parameters would need estimation and causal assumptions before supporting a marketing allocation.

### Reconcile the interaction term

Price rises from ten to twelve and quantity from one hundred to one hundred ten. Value increases by 320, decomposed as price contribution 200, quantity contribution 100 and interaction 20 under this convention. Dropping the interaction loses part of the actual change. Another allocation convention could distribute it across price and quantity while preserving the total.

### Reject a polished but wrong numerical claim

An assistant-written claim of 25 percent conversion conflicts with the executed counts \(\frac{100}{1000}=10\) percent. The program produces a small report packet containing both counts and the derived rate. A narrative should cite this packet and explain its scope; it should not override the arithmetic because the text sounds plausible.

### Complete executable example

```python
import numpy as np

def funnel_and_retention():
    stages=np.array([1000,400,100])
    step=stages[1:]/stages[:-1];overall=stages[-1]/stages[0]
    assert np.allclose(step,[.4,.25]) and np.isclose(np.prod(step),overall)
    cohort_size=np.array([100,80]);retained=np.array([60,56]);mature=np.array([True,False])
    observed=retained[mature].sum()/cohort_size[mature].sum()
    assert observed==.6
    print("Step conversions:",step,"overall:",overall,"mature-cohort retention:",observed)

def carryover_and_saturation():
    spend=np.array([10.,0.,0.,0.]);state=0.;adstock=[]
    for x in spend:state=x+.5*state;adstock.append(state)
    assert adstock==[10.,5.,2.5,1.25]
    exposure=np.array([0.,1.,2.,4.]);response=exposure/(1+exposure)
    assert np.allclose(response,[0.,.5,2/3,.8])
    print("Adstock:",adstock,"saturation:",response)

def price_quantity_decomposition():
    p0,q0=10.,100.;p1,q1=12.,110.
    change=p1*q1-p0*q0
    price=(p1-p0)*q0;quantity=p0*(q1-q0);interaction=(p1-p0)*(q1-q0)
    assert change==320 and price+quantity+interaction==change
    print("Value change and components:",change,price,quantity,interaction)

def verified_narrative_input():
    numerator,denominator=100,1000
    computed=numerator/denominator
    model_claim=.25
    assert computed==.1 and not np.isclose(model_claim,computed)
    packet={"numerator":numerator,"denominator":denominator,"conversion":computed}
    print("Code-verified report packet:",packet,"reject unsupported 25-percent narrative")

def main():
    funnel_and_retention();carryover_and_saturation();price_quantity_decomposition();verified_narrative_input()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why not target the highest churn scores with retention offers?** High baseline risk is not the same as high incremental response. Some high-risk customers will leave despite the offer, while some lower-risk customers may be persuadable. Use a treatment-effect design and account for intervention cost and capacity.

**Interview: What distinguishes attribution from incrementality?** Attribution distributes credit among observed touchpoints. Incrementality compares outcomes with a counterfactual intervention absence. A sophisticated allocation algorithm does not supply that missing causal comparison by itself.

**Interview: How can an LLM improve business analytics without becoming the source of truth?** Use it for schema-constrained extraction, retrieval of definitions and explanation of checked outputs. Measure extraction error, retain evidence spans and compute metrics in tested code. Preserve the difference between observed patterns and causal business effects.

## Primary sources and official APIs

- [Fader, Hardie and Lee, BG/NBD customer-base analysis](https://www.brucehardie.com/papers/018/)

- [Kenneth Train, Discrete Choice Methods with Simulation](https://eml.berkeley.edu/books/choice2.html)

- [Google Meridian model specification](https://developers.google.com/meridian/docs/advanced-modeling/model-spec?hl=en)

## Apply the text-to-analysis boundary

Use the [grounded claims guide](../../llm-applied/guides/llm-applied-011.md) when a business assistant explains reports from versioned sources, and the [retrieval/answer evaluation guide](../../llm-applied/guides/llm-applied-012.md) to diagnose missing evidence separately from unsupported narrative. Keep conversion, contribution and causal-effect calculations attached to executed analytical artifacts.

## Reading connections

[Previous chapter](37-simulation-and-computational-statistics.md) | [Book contents](../README.md) | [Next chapter](39-research-synthesis-and-specialized-statistical-methodologies.md)
