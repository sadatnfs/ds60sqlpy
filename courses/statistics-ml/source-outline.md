# Comprehensive Data Science Methods and Methodology Reference

For a staff, principal, distinguished, head of data science, or chief scientist role, the knowledge base extends beyond algorithms. You need to understand how to formulate questions, collect trustworthy data, identify effects, build models, quantify uncertainty, validate results, and turn evidence into decisions.

This competency map includes methods, model families, theoretical concepts, study designs, diagnostics, and methodological pitfalls.

You do not need research-level mastery of every specialty. For the areas relevant to your work, you should be able to explain:

- What problem the method solves.
- What assumptions make its results valid.
- What it estimates or predicts.
- How it can fail.
- How to evaluate it.
- Whether its output supports the intended decision.

## 1. Problem Formulation and Statistical Reasoning

- **Descriptive analysis:** Summarizes what happened or what a population looks like.
- **Exploratory analysis:** Searches for patterns, anomalies, relationships, and hypotheses without treating every discovery as confirmed.
- **Confirmatory analysis:** Evaluates prespecified hypotheses using a defined analysis plan.
- **Predictive modeling:** Estimates unknown or future outcomes from available information.
- **Causal inference:** Estimates how outcomes would change under an intervention.
- **Prescriptive analytics:** Recommends actions using predictions, causal effects, constraints, and objectives.
- **Statistical decision theory:** Chooses actions by considering uncertainty, consequences, and losses.
- **Data-generating processes:** Describes the mechanisms producing the observations you analyze.
- **Estimands:** Defines precisely the quantity an analysis aims to estimate.
- **Target populations:** Specifies the people, entities, or situations to which conclusions should apply.
- **Units of observation:** Identifies what each recorded row or measurement represents.
- **Units of analysis:** Identifies the entities over which statistical conclusions are drawn.
- **Units of assignment:** Identifies what receives a randomized or assigned intervention.
- **Identification:** Determines whether the desired quantity can be recovered from available data and assumptions.
- **Identifiability:** Determines whether distinct parameter values imply distinguishable observable distributions.
- **Internal validity:** Assesses whether a study supports its conclusions within the studied setting.
- **External validity:** Assesses whether conclusions extend to other populations or settings.
- **Construct validity:** Assesses whether measurements represent the concepts they are intended to capture.
- **Practical significance:** Evaluates whether an effect is large enough to matter operationally.
- **Statistical versus substantive uncertainty:** Separates sampling uncertainty from uncertainty about definitions, assumptions, and mechanisms.
- **Sensitivity analysis:** Examines how conclusions change when assumptions or analytical choices change.
- **Triangulation:** Compares evidence from different methods, datasets, or designs with different weaknesses.

## 2. Mathematical Foundations

- **Linear algebra:** Provides the language for regression, transformations, embeddings, and multivariate models.
- **Vector spaces and projections:** Explains approximation, least squares, orthogonality, and dimension reduction.
- **Matrix rank:** Determines redundancy, solvability, and whether model parameters can be uniquely estimated.
- **Eigenvalues and eigenvectors:** Characterizes transformations, variance directions, stability, and spectral methods.
- **Singular value decomposition:** Factorizes matrices for dimensionality reduction, approximation, and numerical computation.
- **Positive definite matrices:** Underpins covariance matrices, quadratic optimization, kernels, and Gaussian models.
- **Matrix calculus:** Computes derivatives needed to optimize multivariate statistical models.
- **Differential calculus:** Describes local change, gradients, curvature, and optimization conditions.
- **Integral calculus:** Supports probability calculations, expectations, marginalization, and continuous distributions.
- **Multivariable calculus:** Handles models with many interacting variables and parameters.
- **Taylor expansions:** Approximates functions and derives asymptotic results and uncertainty estimates.
- **Convex analysis:** Studies problems where local optima are global optima.
- **Numerical conditioning:** Measures how sensitive computed solutions are to small input changes.
- **Numerical stability:** Assesses whether algorithms amplify rounding and approximation errors.
- **Real analysis fundamentals:** Supports rigorous understanding of convergence, continuity, and limiting arguments.
- **Measure-theoretic probability:** Provides a general foundation for probability, integration, and conditional expectation.
- **Differential equations:** Models systems evolving continuously over time.
- **Information theory:** Quantifies information, uncertainty, compression, and differences between distributions.

## 3. Probability Fundamentals and Stochastic Processes

- **Conditional probability:** Describes probabilities after accounting for observed information.
- **Bayes’ theorem:** Updates probabilities using evidence and a prior distribution.
- **Independence:** States that learning one variable does not change the distribution of another.
- **Conditional independence:** States that variables become independent after conditioning on other variables.
- **Random variables:** Represents uncertain quantities mathematically.
- **Joint distributions:** Describes the combined behavior of multiple random variables.
- **Marginal distributions:** Describes individual variables after integrating or summing over others.
- **Conditional distributions:** Describes outcomes given values of other variables.
- **Expectation:** Calculates a probability-weighted average.
- **Variance and covariance:** Measures dispersion and joint linear variation.
- **Correlation:** Standardizes association, usually to a scale between negative one and one.
- **Law of total expectation:** Computes expectations by averaging conditional expectations.
- **Law of total variance:** Decomposes variability into within-condition and between-condition components.
- **Law of large numbers:** Establishes conditions under which averages approach their expected values.
- **Central limit theorem:** Establishes conditions under which normalized sums approach a normal distribution.
- **Concentration inequalities:** Bounds how far random quantities can deviate from their expectations.
- **Jensen’s inequality:** Relates transformations of expectations to expectations of convex transformations.
- **Exchangeability:** Describes observations whose joint distribution is unchanged by reordering.
- **Markov chains:** Models systems whose next state depends on the current state.
- **Poisson processes:** Models event arrivals under assumptions about independent increments and event rates.
- **Renewal processes:** Models repeated events separated by random waiting times.
- **Martingales:** Models processes whose conditional expected future value equals their current value.
- **Brownian motion:** Models continuous random fluctuations and supports stochastic modeling.
- **Ergodicity:** Describes conditions allowing long-run observations to represent distributional averages.
- **Copulas:** Models dependence separately from individual variables’ marginal distributions.

## 4. Probability Distributions You Should Recognize

- **Bernoulli distribution:** Models a single binary outcome.
- **Binomial distribution:** Models success counts across a fixed number of independent trials with common success probability.
- **Beta-binomial distribution:** Models binomial counts with additional variation in success probabilities.
- **Categorical distribution:** Models a single outcome from multiple categories.
- **Multinomial distribution:** Models category counts across repeated categorical observations.
- **Poisson distribution:** Models nonnegative counts with equal mean and variance.
- **Negative binomial distribution:** Models counts with more variation than a Poisson model allows.
- **Geometric distribution:** Models waiting until the first success in repeated Bernoulli trials.
- **Hypergeometric distribution:** Models successes when sampling without replacement from a finite population.
- **Normal distribution:** Models symmetric continuous variation and appears in many approximation results.
- **Multivariate normal distribution:** Models jointly Gaussian variables with a mean vector and covariance matrix.
- **Student’s t distribution:** Provides heavier tails than the normal distribution and appears in mean inference.
- **Chi-square distribution:** Describes sums of squared independent standard normal variables.
- **F distribution:** Describes ratios of scaled independent chi-square variables.
- **Uniform distribution:** Assigns equal density or probability across a bounded support.
- **Exponential distribution:** Models memoryless positive waiting times.
- **Gamma distribution:** Models positive quantities and sums of exponential waiting times.
- **Beta distribution:** Models quantities restricted to the interval between zero and one.
- **Dirichlet distribution:** Models vectors of probabilities that sum to one.
- **Lognormal distribution:** Models positive quantities whose logarithms are normally distributed.
- **Weibull distribution:** Models lifetimes with flexible increasing or decreasing hazard rates.
- **Pareto distribution:** Models heavy-tailed quantities such as extreme wealth or event sizes.
- **Generalized extreme value distribution:** Models normalized block maxima under suitable conditions.
- **Generalized Pareto distribution:** Models exceedances above a sufficiently high threshold.
- **Mixture distributions:** Represents a population as a weighted combination of component distributions.
- **Truncated distributions:** Conditions a distribution on values lying within an observed range.
- **Zero-inflated distributions:** Adds a separate source of zeros to a standard count distribution.

## 5. Sampling, Surveys, and Data Collection

- **Simple random sampling:** Gives each eligible sample of a specified size equal selection probability.
- **Stratified sampling:** Samples separately within defined population subgroups.
- **Cluster sampling:** Samples groups of units rather than only individual units.
- **Multistage sampling:** Selects samples through multiple hierarchical stages.
- **Systematic sampling:** Selects observations at regular intervals after an initial starting point.
- **Probability-proportional-to-size sampling:** Selects groups with probabilities related to their sizes.
- **Unequal-probability sampling:** Allows different population members to have different selection probabilities.
- **Survey weights:** Corrects for selection probabilities and sometimes nonresponse or population imbalances.
- **Horvitz–Thompson estimation:** Estimates population totals using inverse inclusion probabilities.
- **Hájek estimation:** Uses normalized weighting to estimate population quantities.
- **Poststratification:** Adjusts sample estimates to known population subgroup totals.
- **Raking:** Iteratively adjusts weights to match multiple population margins.
- **Calibration weighting:** Adjusts weights to satisfy known auxiliary population constraints.
- **Design effects:** Quantifies how a sampling design changes variance relative to simple random sampling.
- **Finite population correction:** Adjusts uncertainty when sampling a substantial fraction of a finite population.
- **Coverage error:** Occurs when the sampling frame misses or incorrectly includes population members.
- **Nonresponse bias:** Occurs when respondents differ systematically from nonrespondents.
- **Convenience sampling:** Uses readily available observations, often limiting representativeness.
- **Selection bias:** Arises when inclusion mechanisms distort relationships or population representation.
- **Capture–recapture estimation:** Estimates population size from overlap between partially observed samples.
- **Adaptive sampling:** Changes data collection based on observations already collected.
- **Optimal allocation:** Distributes sampling effort to improve precision under cost constraints.
- **Measurement study design:** Plans how, when, and with what precision variables will be measured.

## 6. Measurement, Exploratory Analysis, and Data Quality

- **Measurement scales:** Distinguishes nominal, ordinal, interval, and ratio measurements.
- **Operational definitions:** Converts abstract concepts into reproducible measurement rules.
- **Data provenance:** Records where data came from and how it was transformed.
- **Data grain:** Defines the level of detail represented by each record.
- **Uniqueness and duplicate analysis:** Detects repeated entities or events that could distort estimates.
- **Referential integrity:** Checks whether relationships between datasets remain valid.
- **Join cardinality analysis:** Detects accidental record multiplication or loss during joins.
- **Missingness profiling:** Examines where data is absent and whether absence follows meaningful patterns.
- **Distribution profiling:** Examines variable ranges, shapes, tails, and unusual values.
- **Quantiles and percentiles:** Summarizes distributions using ordered positions.
- **Skewness and kurtosis:** Describes asymmetry and aspects of tail behavior.
- **Empirical cumulative distribution functions:** Displays the fraction of observations at or below each value.
- **Histograms and density estimates:** Visualizes distribution shapes.
- **Box plots and violin plots:** Compares location, spread, and distribution shape across groups.
- **Quantile–quantile plots:** Compares observed quantiles with a reference distribution.
- **Scatterplots and conditional plots:** Examines relationships, nonlinearities, and subgroup differences.
- **Correlation analysis:** Measures association while requiring care about confounding and nonlinear relationships.
- **Partial correlation:** Measures linear association after accounting for specified other variables.
- **Simpson’s paradox:** Describes associations that reverse or change after aggregation or stratification.
- **Ecological fallacy:** Mistakenly applies group-level relationships to individuals.
- **Aggregation bias:** Arises when conclusions depend misleadingly on how observations are grouped.
- **Data leakage:** Allows information unavailable at prediction or decision time to influence model development.
- **Measurement invariance:** Tests whether a measurement system behaves comparably across groups or time.
- **Interrater reliability:** Measures agreement between people producing labels or judgments.
- **Test–retest reliability:** Measures consistency when the same construct is measured repeatedly.

## 7. Missing Data, Measurement Error, and Robust Statistics

- **Missing completely at random:** Missingness is independent of observed and unobserved data values.
- **Missing at random:** Missingness can depend on observed data but not missing values after conditioning.
- **Missing not at random:** Missingness still depends on unobserved values after accounting for observed information.
- **Complete-case analysis:** Uses only records with all required variables observed.
- **Single imputation:** Replaces each missing value with one estimate, usually understating uncertainty if treated as observed.
- **Multiple imputation:** Creates multiple completed datasets and combines analyses to reflect imputation uncertainty.
- **Chained-equations imputation:** Iteratively imputes variables using conditional models.
- **Joint-model imputation:** Imputes missing values from a model for their joint distribution.
- **Predictive mean matching:** Imputes using observed donor values with similar predicted outcomes.
- **Inverse-probability weighting for missingness:** Reweights observed cases to account for modeled observation probabilities.
- **Rubin’s rules:** Combines estimates and uncertainty across multiply imputed datasets.
- **Pattern-mixture models:** Models outcomes separately by missingness pattern.
- **Selection models:** Jointly models outcomes and the mechanism determining observation.
- **Missingness sensitivity analysis:** Evaluates conclusions under alternative assumptions about unobserved values.
- **Measurement error models:** Accounts for noisy predictors or outcomes.
- **Errors-in-variables regression:** Adjusts regression analysis when explanatory variables are measured with error.
- **Regression calibration:** Uses validation information to approximate correction for measurement error.
- **SIMEX:** Studies added measurement noise and extrapolates toward a hypothetical error-free setting.
- **Robust estimators:** Reduces sensitivity to outliers or deviations from model assumptions.
- **M-estimation:** Estimates parameters by optimizing a general objective or solving estimating equations.
- **Huber loss:** Combines squared-error behavior near zero with less outlier-sensitive behavior in the tails.
- **Trimmed and Winsorized estimators:** Limits extreme observations’ influence by removing or capping tail values.
- **Median absolute deviation:** Provides a robust measure of dispersion around the median.
- **Influence functions:** Describes how infinitesimal contamination affects an estimator.
- **Breakdown point:** Measures how much contamination an estimator can withstand before becoming arbitrarily unreliable.

## 8. Estimation and Statistical Inference

- **Point estimation:** Produces a single estimate of an unknown quantity.
- **Sampling distributions:** Describes how an estimator varies across hypothetical repeated samples.
- **Standard errors:** Quantifies an estimator’s sampling variability.
- **Bias:** Measures systematic deviation of an estimator’s expectation from its target.
- **Consistency:** Describes estimators approaching their targets as information increases.
- **Efficiency:** Compares estimators’ uncertainty under specified conditions.
- **Mean squared error:** Combines squared bias and variance into an estimation error criterion.
- **Maximum likelihood estimation:** Chooses parameters that maximize the probability density or mass assigned to observed data.
- **Maximum a posteriori estimation:** Maximizes a posterior density incorporating both likelihood and prior information.
- **Method of moments:** Matches theoretical moments with observed sample moments.
- **Generalized method of moments:** Estimates parameters using weighted moment conditions.
- **Estimating equations:** Defines estimates as solutions to equations with suitable expectation properties.
- **Sufficient statistics:** Retains all sample information about a parameter within a specified model.
- **Fisher information:** Quantifies information about parameters contained in a likelihood.
- **Cramér–Rao bounds:** Provides variance lower bounds for estimators under regularity conditions.
- **Asymptotic normality:** Approximates an estimator’s distribution by a normal distribution in large samples.
- **Delta method:** Approximates uncertainty for functions of asymptotically normal estimators.
- **Confidence intervals:** Uses procedures designed to cover the target parameter at a stated repeated-sampling rate.
- **Prediction intervals:** Gives ranges for future or otherwise unobserved outcomes.
- **Tolerance intervals:** Aims to cover a specified population proportion with a stated confidence level.
- **Profile likelihood:** Studies a target parameter while optimizing over nuisance parameters.
- **Sandwich variance estimation:** Estimates uncertainty robustly to some forms of model misspecification.
- **Cluster-robust standard errors:** Accounts for dependence within specified groups.
- **Heteroskedasticity-robust standard errors:** Allows error variance to differ across observations.
- **Bootstrap:** Approximates sampling behavior by repeatedly resampling observed data.
- **Jackknife:** Assesses estimator variability or bias by systematically omitting observations or groups.
- **Parametric bootstrap:** Simulates new datasets from an estimated probability model.
- **Block bootstrap:** Resamples blocks to preserve aspects of temporal or spatial dependence.
- **Wild bootstrap:** Resamples residuals using random multipliers, often for heteroskedastic settings.

## 9. Hypothesis Tests and Group Comparisons

- **Null and alternative hypotheses:** Defines the competing claims being evaluated.
- **P-values:** Measures incompatibility with a null model through outcomes at least as extreme as observed.
- **Type I error:** Rejects a true null hypothesis.
- **Type II error:** Fails to reject a false null hypothesis.
- **Statistical power:** Measures the probability of detecting a specified alternative.
- **Minimum detectable effect:** Specifies the effect size a study is designed to detect at chosen power.
- **One-sample t-test:** Tests a population mean against a reference value under suitable assumptions.
- **Paired t-test:** Tests the mean of within-pair differences.
- **Welch’s t-test:** Compares two means while allowing unequal variances.
- **Proportion tests:** Tests hypotheses about one or more population proportions.
- **Chi-square independence test:** Tests association between categorical variables using contingency tables.
- **Fisher’s exact test:** Tests contingency-table hypotheses using exact conditional probabilities.
- **McNemar’s test:** Tests paired binary outcomes for differences in marginal probabilities.
- **Analysis of variance:** Compares group means through a model-based variance decomposition.
- **Welch’s ANOVA:** Compares means while allowing unequal group variances.
- **Analysis of covariance:** Compares groups while adjusting for additional covariates.
- **Multivariate analysis of variance:** Tests group differences across several outcomes jointly.
- **Mann–Whitney U test:** Compares distributions or probabilistic ordering; a median interpretation requires additional assumptions.
- **Wilcoxon signed-rank test:** Tests paired differences using ranks under symmetry assumptions.
- **Sign test:** Tests whether positive and negative differences occur with equal probability.
- **Kruskal–Wallis test:** Compares multiple independent groups using ranks.
- **Friedman test:** Compares multiple conditions within matched blocks using ranks.
- **Kolmogorov–Smirnov test:** Compares cumulative distributions using their largest discrepancy.
- **Anderson–Darling test:** Tests distributional fit with particular sensitivity to tail discrepancies.
- **Shapiro–Wilk test:** Tests compatibility with a normal distribution.
- **Levene’s and Brown–Forsythe tests:** Tests equality of group variances.
- **Likelihood-ratio test:** Compares nested models through their maximized likelihoods.
- **Wald test:** Tests parameter restrictions using estimates and their covariance.
- **Score test:** Tests restrictions using likelihood derivatives evaluated under the null.
- **Permutation tests:** Uses rearrangements justified by the null hypothesis or assignment mechanism.
- **Randomization inference:** Derives inference from the actual treatment assignment design.
- **Equivalence testing:** Tests whether effects lie inside prespecified bounds of practical similarity.
- **Noninferiority testing:** Tests whether a treatment is not worse than a comparator beyond an allowed margin.

## 10. Multiple Testing, Sequential Inference, and Selective Inference

- **Family-wise error rate:** Measures the probability of at least one false rejection within a hypothesis family.
- **False discovery rate:** Measures the expected proportion of false rejections among rejected hypotheses.
- **Bonferroni correction:** Controls family-wise error using adjusted testing thresholds.
- **Holm’s procedure:** Controls family-wise error through sequentially adjusted thresholds.
- **Benjamini–Hochberg procedure:** Controls false discovery rate under appropriate dependence conditions.
- **Benjamini–Yekutieli procedure:** Controls false discovery rate under more general dependence.
- **Adjusted p-values:** Expresses multiplicity corrections on the p-value scale.
- **Simultaneous confidence intervals:** Provides joint coverage for multiple parameters.
- **Hierarchical testing:** Organizes hypotheses into families or trees with structured testing rules.
- **Gatekeeping procedures:** Tests later hypotheses only after earlier requirements are satisfied.
- **Alpha spending:** Allocates Type I error across interim analyses.
- **Group sequential designs:** Permits planned interim decisions using calibrated stopping boundaries.
- **Sequential probability ratio tests:** Compares accumulating likelihood ratios with decision boundaries.
- **Always-valid p-values:** Remains valid under permitted continuous monitoring and stopping rules.
- **Confidence sequences:** Provides intervals designed to cover a target simultaneously across time.
- **E-values and e-processes:** Supplies evidence measures supporting certain forms of optional stopping and aggregation.
- **Online false discovery control:** Controls false discoveries as hypotheses arrive sequentially.
- **Selective inference:** Accounts for data-dependent selection before reporting inferential claims.
- **Post-selection inference:** Adjusts uncertainty after selecting variables, models, or findings.
- **Knockoff methods:** Uses synthetic comparison variables to control false discoveries in feature selection.
- **Winner’s curse:** Describes upward bias among effects selected because they looked strongest.
- **Multiverse analysis:** Repeats an analysis across reasonable specifications to assess dependence on analytical choices.

## 11. Regression and Generalized Linear Models

- **Ordinary least squares:** Estimates linear conditional means by minimizing squared residuals.
- **Weighted least squares:** Assigns different observation weights, often to handle known variance differences.
- **Generalized least squares:** Accounts for a modeled residual covariance structure.
- **Polynomial regression:** Represents curved relationships using polynomial terms.
- **Interaction models:** Allows one predictor’s effect to depend on another predictor.
- **Spline regression:** Fits flexible curves using joined polynomial segments.
- **Restricted cubic splines:** Uses smooth cubic segments with constrained tail behavior.
- **Generalized additive models:** Combines smooth predictor effects through an additive model.
- **Generalized linear models:** Connects outcome distributions to predictors through a link function.
- **Logistic regression:** Models binary outcome probabilities through log-odds.
- **Probit regression:** Models binary probabilities using the standard normal cumulative distribution.
- **Multinomial logistic regression:** Models outcomes with multiple unordered categories.
- **Ordinal regression:** Models outcomes whose categories have a meaningful order.
- **Poisson regression:** Models conditional count means, commonly using a log link.
- **Negative binomial regression:** Models overdispersed counts.
- **Quasi-likelihood models:** Specifies mean–variance relationships without requiring a full probability distribution.
- **Zero-inflated models:** Combines a structural-zero process with a count model.
- **Hurdle models:** Separately models zero versus positive outcomes and the positive outcome distribution.
- **Gamma regression:** Models positive continuous outcomes with suitable mean–variance behavior.
- **Tweedie models:** Models outcomes that can combine exact zeros and positive continuous values.
- **Beta regression:** Models continuous outcomes within the open unit interval.
- **Fractional response models:** Models fractional outcomes, including settings permitting zeros and ones.
- **Quantile regression:** Models conditional quantiles rather than only conditional means.
- **Expectile regression:** Models asymmetric squared-error summaries of a conditional distribution.
- **Nonlinear least squares:** Fits mean functions nonlinear in their parameters.
- **Robust regression:** Reduces sensitivity to outliers or specified model deviations.
- **Ridge regression:** Shrinks coefficients using an L2 penalty.
- **Lasso regression:** Uses an L1 penalty that can set coefficients exactly to zero.
- **Elastic net:** Combines L1 and L2 penalties.
- **Group lasso:** Selects or shrinks predefined groups of coefficients together.
- **Firth regression:** Uses bias reduction that can address separation in logistic regression.
- **Generalized additive location, scale, and shape models:** Models multiple distributional parameters as functions of predictors.

## 12. Regression Diagnostics, Multilevel Models, and Longitudinal Analysis

- **Residual analysis:** Checks systematic errors, variance patterns, dependence, and unusual observations.
- **Leverage:** Measures how unusual an observation’s predictor configuration is.
- **Cook’s distance:** Measures how much fitted regression results change when an observation is removed.
- **Multicollinearity diagnostics:** Detects predictor redundancy that destabilizes coefficient estimates.
- **Variance inflation factors:** Quantifies coefficient variance inflation associated with correlated predictors.
- **Heteroskedasticity diagnostics:** Checks whether residual variability changes across observations.
- **Autocorrelation diagnostics:** Checks whether residuals remain related across time or ordering.
- **Model specification tests:** Looks for evidence that important functional structure has been omitted.
- **Linear mixed-effects models:** Combines population-level effects with group-specific random effects.
- **Generalized linear mixed models:** Extends mixed modeling to non-Gaussian outcomes.
- **Random intercept models:** Allows groups to have different baseline levels.
- **Random slope models:** Allows predictor relationships to vary across groups.
- **Partial pooling:** Shares information across groups while allowing meaningful differences.
- **Intraclass correlation:** Quantifies similarity among observations within the same group.
- **Cross-classified models:** Handles observations belonging to intersecting group structures.
- **Nested models:** Represents hierarchical membership, such as users within teams within organizations.
- **Generalized estimating equations:** Estimates population-average relationships with correlated observations.
- **Repeated-measures models:** Handles multiple measurements from the same units.
- **Growth curve models:** Models individual trajectories over time.
- **Panel fixed-effects models:** Controls for time-invariant unit characteristics through unit-specific effects.
- **Panel random-effects models:** Models unit-specific variation under assumptions about its relationship to predictors.
- **Dynamic panel models:** Includes lagged outcomes and addresses resulting estimation challenges.
- **Hausman tests:** Compares estimators to assess certain specification assumptions.
- **Multilevel regression and poststratification:** Combines hierarchical outcome models with population composition information.

## 13. Classical Experimental Design

- **Randomized controlled trials:** Uses random assignment to identify intervention effects under the study design.
- **Complete randomization:** Randomly assigns a fixed number of units to each condition.
- **Blocked randomization:** Randomizes within groups formed from important pre-treatment characteristics.
- **Matched-pair randomization:** Forms similar pairs and randomizes treatment within each pair.
- **Cluster randomized trials:** Randomizes groups when individual assignment is impractical or creates spillovers.
- **Stratified randomization:** Balances treatment assignment within prespecified strata.
- **Factorial designs:** Tests combinations of factor levels to estimate main effects and interactions.
- **Fractional factorial designs:** Uses selected combinations to reduce experimental cost.
- **Aliasing and confounding in designs:** Describes effects that cannot be separately estimated from chosen experimental runs.
- **Split-plot designs:** Handles factors randomized at different experimental levels.
- **Latin square designs:** Controls two blocking dimensions while assigning treatments.
- **Crossover designs:** Exposes the same units to different treatments across periods.
- **Washout periods:** Allows prior treatment effects to diminish between experimental periods.
- **Carryover effects:** Occurs when earlier treatments influence later outcomes.
- **Stepped-wedge designs:** Introduces interventions across clusters at different scheduled times.
- **Response surface methodology:** Models responses over experimental settings to locate favorable operating regions.
- **Central composite designs:** Adds experimental points to estimate quadratic response surfaces.
- **Box–Behnken designs:** Estimates quadratic surfaces using a structured set of factor combinations.
- **Optimal experimental design:** Chooses observations or settings to maximize a statistical information criterion.
- **D-optimal design:** Targets precision through the determinant of an information matrix.
- **A-optimal design:** Targets average parameter variance.
- **Power and sample-size analysis:** Determines how much experimental information is needed for a specified objective.
- **Simulation-based design:** Evaluates proposed experiments under realistic data-generating scenarios.
- **Blinding:** Reduces behavioral and measurement biases by withholding assignment information.
- **Preregistration and analysis plans:** Specifies hypotheses, outcomes, exclusions, and methods before results are examined.

## 14. Online Experimentation and A/B Testing

- **A/B testing:** Compares randomized product or operational alternatives.
- **A/B/n testing:** Compares a control with multiple treatment variants.
- **Randomization integrity checks:** Verifies that assignment followed the intended mechanism.
- **Sample ratio mismatch:** Detects unexpected treatment allocation counts that may indicate implementation problems.
- **A/A tests:** Compares nominally identical experiences to evaluate experimental infrastructure.
- **Intent-to-treat analysis:** Estimates effects of assignment, regardless of actual treatment uptake.
- **Treatment-on-the-treated effects:** Targets effects among treated or induced-to-treat units under additional assumptions.
- **Exposure definitions:** Specifies when users count as having encountered an experiment.
- **Triggered analysis:** Restricts analysis to relevant opportunities using rules that preserve valid treatment comparisons.
- **Guardrail metrics:** Tracks important adverse effects alongside the primary success metric.
- **Overall evaluation criteria:** Defines the principal metric or decision rule used to assess an experiment.
- **Ratio metrics:** Analyzes measures such as revenue per user or clicks per impression.
- **Delta-method ratio inference:** Approximates uncertainty for ratios of estimated quantities.
- **CUPED:** Reduces experimental variance using pre-experiment covariates.
- **Regression-adjusted experiment analysis:** Uses baseline covariates to improve precision.
- **Unequal treatment allocation:** Assigns different traffic shares to conditions while accounting for power implications.
- **Persistent holdouts:** Maintains long-term controls to measure cumulative or delayed effects.
- **Novelty effects:** Captures temporary responses to a new experience.
- **Primacy and learning effects:** Captures behavior influenced by prior familiarity or adaptation.
- **Treatment effect dilution:** Occurs when assignment affects only some analyzed observations.
- **Network interference:** Occurs when one unit’s assignment influences another unit’s outcome.
- **Switchback experiments:** Randomizes interventions across time blocks, often within locations or systems.
- **Geo experiments:** Randomizes or compares geographic units to evaluate interventions.
- **Marketplace experiments:** Accounts for interactions between buyers, sellers, prices, and shared supply.
- **Long-term effect estimation:** Examines whether short-term outcomes represent persistent impacts.
- **Surrogate metrics:** Uses intermediate outcomes to inform longer-term outcomes under explicit validation assumptions.
- **Experiment interaction analysis:** Studies whether concurrent interventions alter each other’s effects.
- **Experiment portfolio governance:** Coordinates overlapping studies, shared metrics, and decision standards.

## 15. Causal Inference Foundations

- **Potential outcomes:** Defines the outcomes a unit would experience under alternative interventions.
- **Counterfactual reasoning:** Compares observed outcomes with outcomes under unrealized alternatives.
- **Average treatment effect:** Measures the average outcome difference under treatment versus control.
- **Average treatment effect on the treated:** Measures the average effect for units that actually received treatment.
- **Conditional average treatment effect:** Measures average effects within covariate-defined groups.
- **Consistency:** Relates observed outcomes to the potential outcome for the intervention actually received.
- **Exchangeability and ignorability:** Describes conditions under which treatment groups are comparable for causal estimation.
- **Positivity and overlap:** Requires relevant treatment alternatives to occur within the populations being compared.
- **Stable unit treatment value assumptions:** Addresses treatment versions and interference between units.
- **Directed acyclic graphs:** Represents hypothesized causal relationships without directed cycles.
- **Structural causal models:** Represents variables as functions of their causes and external disturbances.
- **Confounding:** Occurs when common causes distort treatment–outcome comparisons.
- **Colliders:** Variables caused by two other variables whose conditioning can induce association.
- **Mediators:** Variables through which some of a treatment’s effect may operate.
- **Backdoor adjustment:** Identifies covariate adjustment sets that block noncausal paths under a causal graph.
- **Front-door identification:** Identifies certain effects through mediators under strong graphical assumptions.
- **Do-calculus:** Provides rules for identifying interventional distributions from causal assumptions.
- **Selection diagrams:** Represents differences between study selection mechanisms or populations.
- **Transportability:** Studies whether causal knowledge transfers across settings.
- **Partial identification:** Derives bounds when assumptions do not identify a single causal value.
- **Negative controls:** Uses variables expected to lack particular causal relationships to detect bias.
- **Target trial emulation:** Specifies an ideal randomized trial and designs an observational analysis to emulate it.

## 16. Quasi-Experiments and Causal Study Designs

- **Natural experiments:** Uses externally generated variation that may approximate random treatment assignment.
- **Difference-in-differences:** Compares outcome changes between treated and comparison groups.
- **Parallel trends:** Assumes untreated outcome changes would have followed comparable patterns.
- **Event-study designs:** Estimates effects relative to intervention timing and examines temporal patterns.
- **Staggered adoption designs:** Handles interventions introduced at different times across groups.
- **Two-way fixed-effects limitations:** Recognizes misleading comparisons or weights when effects vary across groups or time.
- **Triple differences:** Adds another comparison dimension to a difference-in-differences design.
- **Synthetic control:** Constructs a comparison unit from weighted untreated units.
- **Augmented synthetic control:** Adds outcome modeling to improve synthetic-control estimation.
- **Synthetic difference-in-differences:** Combines weighting and difference-in-differences ideas.
- **Interrupted time series:** Estimates changes following an intervention while modeling prior temporal behavior.
- **Regression discontinuity:** Uses a treatment assignment cutoff to identify local causal effects.
- **Sharp regression discontinuity:** Applies when treatment status changes deterministically at a cutoff.
- **Fuzzy regression discontinuity:** Uses a cutoff-induced change in treatment probability as an instrument.
- **Regression kink designs:** Uses changes in assignment-rule slopes to identify certain local effects.
- **Instrumental variables:** Uses a variable affecting treatment to identify causal effects under additional restrictions.
- **Two-stage least squares:** Estimates linear instrumental-variable models.
- **Local average treatment effects:** Identifies effects for units whose treatment changes because of an instrument.
- **Weak instrument diagnostics:** Evaluates whether instruments provide enough treatment variation for reliable inference.
- **Exclusion restrictions:** Requires an instrument to affect the outcome only through specified treatment pathways.
- **Encouragement designs:** Randomizes an encouragement that influences treatment uptake.
- **Placebo and falsification tests:** Checks implications that should hold if a causal interpretation is credible.

## 17. Causal Estimation, Heterogeneous Effects, and Policy Learning

- **Outcome regression:** Models outcomes conditional on treatment and covariates to estimate causal contrasts.
- **G-computation:** Calculates intervention outcomes by averaging predictions from a fitted causal outcome model.
- **Propensity scores:** Models treatment assignment probabilities given observed covariates.
- **Propensity score matching:** Forms treatment comparisons using similar estimated assignment probabilities.
- **Inverse-probability treatment weighting:** Reweights observations to construct a target treatment comparison.
- **Overlap weighting:** Emphasizes units with more comparable treatment assignment probabilities.
- **Entropy balancing:** Constructs weights satisfying specified covariate balance constraints.
- **Covariate balance diagnostics:** Evaluates whether adjusted treatment groups are comparable on observed variables.
- **Augmented inverse-probability weighting:** Combines treatment and outcome models in a doubly robust estimator.
- **Doubly robust estimation:** Can remain consistent if one of two nuisance models is correctly specified, given other assumptions.
- **Targeted maximum likelihood estimation:** Updates an initial outcome model to target an estimand through a semiparametric procedure.
- **Double/debiased machine learning:** Uses orthogonal estimating equations and cross-fitting to reduce nuisance-estimation bias under suitable conditions.
- **Cross-fitting:** Estimates nuisance functions on separate folds from those used to evaluate estimating equations.
- **Marginal structural models:** Uses weighting to estimate effects with time-varying treatment and confounding.
- **Structural nested models:** Models treatment effects across time through nested counterfactual contrasts.
- **G-estimation:** Estimates structural nested models using identifying restrictions.
- **Mediation analysis:** Studies pathways through which interventions influence outcomes.
- **Direct and indirect effects:** Separates effects through specified mediators from effects through other pathways.
- **Causal forests:** Estimates heterogeneous treatment effects using specialized tree ensembles.
- **S-learners:** Uses one outcome model containing treatment as an input to estimate treatment contrasts.
- **T-learners:** Fits separate outcome models for treatment groups.
- **X-learners:** Combines outcome models and imputed treatment effects, often useful with unequal group sizes.
- **R-learners:** Estimates treatment heterogeneity after residualizing outcomes and treatments.
- **Uplift modeling:** Predicts incremental intervention effects to guide targeting.
- **Qini and uplift curves:** Evaluates treatment targeting under suitable randomized data or identification assumptions.
- **Policy learning:** Learns intervention rules that optimize expected outcomes or utility.
- **Off-policy evaluation:** Estimates the value of a policy using data generated under another policy.
- **Sensitivity to unmeasured confounding:** Quantifies how hidden confounding could change causal conclusions.
- **Causal discovery:** Infers candidate causal structures under strong assumptions about data and mechanisms.

## 18. Bayesian Statistics and Probabilistic Modeling

- **Prior distributions:** Encodes uncertainty about parameters before incorporating current data.
- **Likelihoods:** Describes how observed data depend on model parameters.
- **Posterior distributions:** Combines prior information with observed data.
- **Conjugate models:** Uses prior–likelihood combinations with analytically convenient posterior distributions.
- **Weakly informative priors:** Regularizes estimates while allowing a broad range of plausible values.
- **Prior elicitation:** Translates domain knowledge into probability distributions.
- **Prior predictive checks:** Simulates data before fitting to assess the implications of chosen priors.
- **Posterior predictive distributions:** Describes future observations after accounting for posterior uncertainty.
- **Posterior predictive checks:** Compares simulated and observed data to diagnose model mismatch.
- **Hierarchical Bayesian models:** Shares information across related groups through probability distributions.
- **Empirical Bayes:** Estimates aspects of a prior distribution from observed data.
- **Bayesian shrinkage:** Pulls unstable estimates toward shared structure using prior information.
- **Credible intervals:** Describes parameter ranges containing specified posterior probability.
- **Bayesian decision analysis:** Chooses actions using posterior expected utility or loss.
- **Bayes factors:** Compares models through marginal likelihood ratios and can be sensitive to prior choices.
- **Bayesian model averaging:** Averages predictions or quantities across models using posterior model weights.
- **Markov chain Monte Carlo:** Generates dependent draws approximating a target probability distribution.
- **Metropolis–Hastings:** Constructs a Markov chain through proposals and probabilistic acceptance.
- **Gibbs sampling:** Iteratively samples from conditional distributions.
- **Hamiltonian Monte Carlo:** Uses gradients and simulated dynamics to explore continuous distributions.
- **No-U-Turn sampling:** Adaptively determines trajectory lengths within Hamiltonian Monte Carlo.
- **Variational inference:** Approximates a probability distribution by solving an optimization problem.
- **Laplace approximation:** Approximates a posterior locally using a Gaussian distribution.
- **Approximate Bayesian computation:** Performs inference using simulations when likelihood evaluation is difficult.
- **Simulation-based inference:** Learns parameter or likelihood approximations from simulated datasets.
- **MCMC diagnostics:** Uses chain behavior, effective sample size, and convergence diagnostics to detect sampling problems.
- **Simulation-based calibration:** Checks inference implementation using repeated simulations from the model.
- **Bayesian nonparametrics:** Uses flexible priors whose effective complexity can grow with available data.
- **Dirichlet process models:** Provides a flexible prior for distributions, commonly used in mixture modeling.
- **Gaussian processes:** Defines distributions over functions for flexible regression, classification, and optimization.

## 19. Statistical Learning and Classical Supervised Models

- **Empirical risk minimization:** Fits models by minimizing average training loss.
- **Regularized risk minimization:** Balances training fit against a complexity penalty.
- **Bias–variance tradeoff:** Describes competing sources of prediction error associated with model flexibility.
- **Overfitting:** Learns sample-specific patterns that do not generalize.
- **Underfitting:** Uses insufficient flexibility to capture relevant structure.
- **Nearest-neighbor methods:** Predicts using nearby observations under a chosen distance measure.
- **Naive Bayes:** Uses conditional-independence assumptions to construct a probabilistic classifier.
- **Linear discriminant analysis:** Classifies using Gaussian class models with a shared covariance matrix.
- **Quadratic discriminant analysis:** Allows different Gaussian covariance matrices across classes.
- **Decision trees:** Partitions predictors into regions with simple local predictions.
- **Bagging:** Averages models fitted to resampled datasets to reduce instability.
- **Random forests:** Combines randomized trees to produce flexible predictions.
- **Extremely randomized trees:** Adds stronger randomness to tree split construction.
- **Gradient boosting:** Sequentially adds models that improve a specified loss.
- **Boosted decision trees:** Uses trees as components in a gradient-boosted ensemble.
- **AdaBoost:** Reweights observations to emphasize classification errors across successive learners.
- **Support vector machines:** Fits margin-based decision rules, optionally using kernels.
- **Kernel methods:** Expresses nonlinear relationships through similarities corresponding to feature-space operations.
- **Kernel ridge regression:** Combines kernel representations with L2-regularized regression.
- **Gaussian process regression:** Produces probabilistic function predictions using a kernel-defined prior.
- **Multilayer perceptrons:** Uses layered nonlinear transformations for supervised learning.
- **Multitask learning:** Shares information across related prediction problems.
- **Multioutput learning:** Predicts multiple outcomes jointly.
- **Learning to rank:** Learns orderings rather than only numeric values or classes.
- **Cost-sensitive learning:** Accounts for unequal consequences of different prediction errors.
- **Positive–unlabeled learning:** Learns from labeled positives and unlabeled examples under explicit labeling assumptions.
- **Semi-supervised learning:** Uses both labeled and unlabeled data.
- **Active learning:** Chooses which observations should receive labels next.
- **Transfer learning:** Reuses learned representations or parameters across tasks.
- **Domain adaptation:** Adjusts learning when source and deployment distributions differ.

## 20. Feature Engineering and Representation Learning

- **Scaling and standardization:** Changes feature magnitudes to support model fitting and comparability.
- **Categorical encoding:** Represents categories numerically for use in models.
- **Target encoding:** Encodes categories using outcome summaries with safeguards against leakage.
- **Feature hashing:** Maps high-cardinality inputs into a fixed-dimensional representation.
- **Interaction feature construction:** Creates variables representing joint predictor effects.
- **Temporal feature engineering:** Constructs lags, rolling summaries, recency, and seasonal features.
- **Feature selection:** Chooses a subset of predictors.
- **Filter methods:** Selects features using criteria computed separately from the final predictive model.
- **Wrapper methods:** Evaluates feature subsets through repeated model fitting.
- **Embedded selection:** Selects features as part of model optimization.
- **Mutual information:** Measures general statistical dependence between variables.
- **Principal component analysis:** Finds orthogonal directions capturing maximal variance.
- **Independent component analysis:** Seeks statistically independent latent components.
- **Nonnegative matrix factorization:** Produces additive nonnegative latent representations.
- **Sparse coding:** Represents observations using a small number of learned components.
- **Dictionary learning:** Learns reusable basis elements for representing data.
- **Autoencoders:** Learns representations by reconstructing inputs through a constrained internal representation.
- **Contrastive learning:** Learns representations by distinguishing related from unrelated examples.
- **Metric learning:** Learns a distance or similarity function suited to a task.
- **Embeddings:** Represents discrete or complex entities as vectors.
- **Feature stability analysis:** Evaluates whether selected features persist across samples or conditions.
- **Representation leakage analysis:** Detects unwanted target, identity, or future information in learned features.

## 21. Unsupervised Learning and Multivariate Analysis

- **K-means clustering:** Groups observations around centroids using squared Euclidean distances.
- **K-medoids clustering:** Uses representative observed points as cluster centers.
- **Hierarchical clustering:** Builds nested groupings through merging or splitting.
- **DBSCAN:** Finds dense regions and marks sufficiently isolated observations as noise.
- **HDBSCAN:** Extends density clustering across varying density scales.
- **Gaussian mixture models:** Represents a distribution as a mixture of Gaussian components.
- **Model-based clustering:** Defines clusters through an explicit probabilistic model.
- **Spectral clustering:** Uses graph or similarity-matrix eigenvectors to construct clusters.
- **Biclustering:** Finds related subsets of rows and columns simultaneously.
- **Fuzzy clustering:** Allows observations to have graded memberships across clusters.
- **Latent class analysis:** Models discrete latent groups underlying observed categorical responses.
- **Latent profile analysis:** Models latent groups characterized by continuous measurements.
- **Factor analysis:** Explains covariance through lower-dimensional latent variables.
- **Exploratory factor analysis:** Discovers possible latent factor structures.
- **Confirmatory factor analysis:** Tests a specified latent measurement structure.
- **Canonical correlation analysis:** Finds maximally related linear combinations from two variable sets.
- **Partial least squares:** Learns components emphasizing relationships between predictors and outcomes.
- **Multidimensional scaling:** Embeds observations to preserve specified dissimilarities.
- **t-SNE:** Visualizes local similarity structure in a low-dimensional representation.
- **UMAP:** Constructs low-dimensional representations using neighborhood-based structure.
- **Manifold learning:** Seeks lower-dimensional structure in nonlinear data.
- **Correspondence analysis:** Explores relationships in contingency tables.
- **Multiple correspondence analysis:** Extends correspondence analysis to multiple categorical variables.
- **Cluster validation:** Assesses separation, stability, usefulness, and agreement with external information.
- **Cluster stability analysis:** Examines whether groupings persist under resampling or perturbations.
- **Consensus clustering:** Combines multiple clustering results into a more stable grouping.

## 22. Model Validation and Predictive Performance

- **Training, validation, and test separation:** Separates model fitting, development choices, and final evaluation.
- **K-fold cross-validation:** Evaluates models using repeated held-out partitions.
- **Stratified cross-validation:** Preserves relevant class proportions across folds.
- **Grouped cross-validation:** Keeps related observations together to prevent leakage.
- **Nested cross-validation:** Separates hyperparameter selection from performance estimation.
- **Temporal validation:** Evaluates predictions on observations occurring after training data.
- **Rolling-origin evaluation:** Repeatedly advances the forecasting origin to assess deployment-like performance.
- **Spatial cross-validation:** Holds out geographic regions to test spatial generalization.
- **External validation:** Evaluates performance using independently collected data.
- **Out-of-distribution evaluation:** Tests behavior outside the training distribution.
- **Learning curves:** Shows how performance changes with training sample size.
- **Validation curves:** Shows how performance changes with model settings.
- **Ablation studies:** Removes components to assess their contribution.
- **Baseline comparisons:** Checks whether complexity improves meaningfully over simple alternatives.
- **Mean absolute error:** Measures average absolute prediction error.
- **Mean squared error and RMSE:** Penalizes large errors more heavily through squaring.
- **R-squared:** Measures squared-error improvement relative to a specified mean baseline.
- **Log loss:** Evaluates probabilistic classification by penalizing assigned probability to incorrect outcomes.
- **Brier score:** Measures squared error of predicted probabilities.
- **Precision and recall:** Measures positive prediction reliability and positive-case detection.
- **Specificity and sensitivity:** Measures correct negative and positive identification rates.
- **F-scores:** Combines precision and recall with a chosen relative weighting.
- **ROC curves and AUC:** Summarizes ranking across false-positive and true-positive rates.
- **Precision–recall curves:** Summarizes performance across positive prediction thresholds.
- **Calibration curves:** Compares predicted probabilities with observed outcome frequencies.
- **Threshold optimization:** Selects decision cutoffs using costs, benefits, or operational constraints.
- **Top-k and ranking metrics:** Evaluates performance among the highest-ranked predictions.
- **Business utility evaluation:** Converts prediction behavior into expected operational value.
- **Paired model comparisons:** Uses matched evaluation observations to compare model performance.
- **Performance uncertainty:** Quantifies how much measured performance could vary across samples or settings.

## 23. Uncertainty Quantification and Distribution Shift

- **Aleatoric uncertainty:** Represents outcome variability that remains even with a known model.
- **Epistemic uncertainty:** Represents uncertainty about the model or its parameters.
- **Uncertainty propagation:** Carries uncertain inputs and parameters through downstream calculations.
- **Predictive distributions:** Represents uncertainty over possible outcomes rather than only point predictions.
- **Quantile prediction:** Estimates specified percentiles of the conditional outcome distribution.
- **Prediction set construction:** Produces sets of possible outcomes with an intended coverage property.
- **Conformal prediction:** Constructs prediction sets with finite-sample marginal coverage under conditions such as exchangeability.
- **Split conformal prediction:** Uses separate model-fitting and calibration data to construct prediction sets.
- **Conformalized quantile regression:** Calibrates quantile-model intervals using conformal methods.
- **Conditional versus marginal coverage:** Distinguishes coverage within specific conditions from average population coverage.
- **Distribution-free inference:** Derives guarantees without assuming a particular parametric distribution, while retaining other assumptions.
- **Deep ensembles:** Uses variation across independently trained neural models to inform predictive uncertainty.
- **Bayesian neural networks:** Places probability distributions over neural-network parameters or related model components.
- **Selective prediction:** Allows a model to abstain when confidence or expected utility is insufficient.
- **Covariate shift:** Changes predictor distributions while preserving the conditional outcome mechanism.
- **Label shift:** Changes class prevalence while preserving class-conditional predictor distributions.
- **Concept drift:** Changes the relationship between predictors and outcomes.
- **Importance weighting:** Adjusts contributions to account for differences between source and target distributions.
- **Distributionally robust prediction:** Optimizes performance against a defined neighborhood of possible distributions.
- **Out-of-distribution detection:** Identifies inputs that differ materially from the model’s development data.

## 24. Explainability, Fairness, and Model Robustness

- **Global interpretability:** Describes overall model behavior across the input space.
- **Local interpretability:** Explains individual predictions or nearby behavior.
- **Permutation importance:** Measures performance deterioration after disrupting a feature.
- **Partial dependence plots:** Averages predictions over other features, potentially creating unrealistic feature combinations.
- **Individual conditional expectation:** Shows how predictions change with one feature for individual observations.
- **Accumulated local effects:** Summarizes local prediction changes while reducing some correlated-feature extrapolation.
- **SHAP values:** Allocates prediction differences across features using a Shapley-value framework and a chosen reference construction.
- **LIME:** Approximates model behavior locally using a simpler surrogate.
- **Counterfactual explanations:** Finds input changes that would alter a model’s prediction.
- **Recourse analysis:** Studies feasible actions people can take to change model-based decisions.
- **Monotonic models:** Enforces specified directional relationships between predictors and predictions.
- **Adversarial robustness:** Studies behavior under intentionally chosen input perturbations.
- **Stress testing:** Evaluates models under extreme or adverse scenarios.
- **Subgroup performance analysis:** Checks whether model quality differs across meaningful population groups.
- **Demographic parity:** Compares positive prediction rates across groups.
- **Equalized odds:** Compares error rates conditional on actual outcomes across groups.
- **Equal opportunity:** Compares true-positive rates across groups.
- **Group calibration:** Checks whether predicted probabilities have comparable meanings within groups.
- **Individual fairness:** Seeks similar treatment for individuals considered similar under a specified definition.
- **Intersectional fairness:** Examines groups defined by combinations of characteristics.
- **Fairness tradeoffs:** Recognizes that desirable fairness criteria can conflict.
- **Proxy discrimination analysis:** Examines whether apparently neutral features reproduce sensitive distinctions.
- **Causal fairness analysis:** Uses causal assumptions to distinguish permitted and impermissible pathways.

## 25. Time-Series Foundations and Diagnostics

- **Temporal dependence:** Recognizes that observations can depend on earlier observations.
- **Strict stationarity:** Requires joint distributions to remain unchanged under time shifts.
- **Weak stationarity:** Requires stable means and autocovariances depending only on lag.
- **Trend:** Represents persistent changes in the level of a series.
- **Seasonality:** Represents recurring patterns at known calendar frequencies.
- **Cycles:** Represents fluctuations without a strictly fixed seasonal period.
- **Autocorrelation functions:** Measures correlation between a series and its lagged values.
- **Partial autocorrelation functions:** Measures lag relationships after accounting for intervening lags.
- **White noise:** Represents uncorrelated disturbances with stable first and second moments.
- **Differencing:** Transforms observations into changes to address certain nonstationary patterns.
- **Seasonal differencing:** Removes differences relative to a previous seasonal period.
- **Unit roots:** Describes a form of persistent nonstationarity.
- **Augmented Dickey–Fuller tests:** Tests a unit-root null under specified time-series models.
- **KPSS tests:** Tests stationarity around a level or trend.
- **Cointegration:** Describes stationary combinations of individually nonstationary series.
- **Granger causality:** Tests whether past values improve prediction beyond a specified information set; it does not establish intervention causality.
- **Cross-correlation analysis:** Examines relationships between series across lags.
- **Spectral analysis:** Studies how variation is distributed across frequencies.
- **Periodograms:** Estimates frequency-domain power from observed data.
- **Fourier representations:** Represents periodic behavior using sine and cosine components.
- **Wavelet analysis:** Studies behavior localized in both time and frequency.
- **Time-series decomposition:** Separates trend, seasonal, and residual components.
- **STL decomposition:** Uses local regression to estimate seasonal and trend components.
- **Ljung–Box tests:** Checks whether a collection of autocorrelations is jointly consistent with zero.
- **Structural breaks:** Represents changes in a series’ underlying parameters or mechanisms.

## 26. Classical Forecasting Methods

- **Naive forecasts:** Uses the most recent observation as a future forecast.
- **Seasonal naive forecasts:** Uses the corresponding observation from a previous season.
- **Drift forecasts:** Extrapolates an average historical rate of change.
- **Moving-average smoothing:** Averages nearby observations to reduce short-term variation.
- **Simple exponential smoothing:** Recursively updates a level estimate using exponentially decreasing weights.
- **Holt’s method:** Adds a trend component to exponential smoothing.
- **Holt–Winters methods:** Adds seasonal components to level-and-trend forecasting.
- **Damped-trend methods:** Gradually reduces extrapolated trend growth over longer horizons.
- **ETS models:** Provides a state-space framework for error, trend, and seasonal components.
- **Autoregressive models:** Predicts using lagged values of the series.
- **Moving-average time-series models:** Models dependence through lagged disturbances.
- **ARMA models:** Combines autoregressive and moving-average components.
- **ARIMA models:** Combines differencing with autoregressive and moving-average components.
- **Seasonal ARIMA:** Extends ARIMA with seasonal dependence and differencing.
- **Dynamic regression:** Combines explanatory predictors with time-series error structure.
- **Distributed-lag models:** Represents predictors’ effects across multiple time lags.
- **Transfer-function models:** Models dynamic responses from input series to output series.
- **Vector autoregression:** Models several series using their joint lagged histories.
- **Vector error-correction models:** Combines short-term dynamics with cointegrating relationships.
- **State-space models:** Represents observed series through evolving latent states.
- **Kalman filtering:** Updates latent-state estimates in linear Gaussian state-space models.
- **Kalman smoothing:** Estimates historical states using observations from the full available period.
- **Structural time-series models:** Explicitly represents components such as level, trend, and seasonality.
- **Bayesian structural time series:** Estimates structural time-series models using Bayesian inference.
- **Dynamic linear models:** Uses time-varying latent states in a linear state-space framework.
- **ARCH and GARCH:** Models time-varying conditional volatility.

## 27. Advanced Forecasting and Forecast Evaluation

- **Hierarchical forecasting:** Forecasts related series organized into aggregation hierarchies.
- **Grouped forecasting:** Handles series aggregated across multiple intersecting dimensions.
- **Forecast reconciliation:** Adjusts forecasts so they obey known aggregation constraints.
- **Minimum-trace reconciliation:** Uses forecast error covariance information to improve coherent forecasts.
- **Intermittent demand forecasting:** Handles series with many zero-demand periods.
- **Croston’s method:** Separately smooths positive demand sizes and interarrival intervals.
- **Bias-corrected intermittent methods:** Adjusts known biases in intermittent-demand forecasting.
- **Dynamic harmonic regression:** Models complex seasonality with Fourier terms and time-series errors.
- **TBATS:** Handles complex seasonal patterns using transformations, trigonometric seasonality, and state-space components.
- **Piecewise trend models:** Allows trend slopes to change at estimated or specified changepoints.
- **Global forecasting models:** Learns shared patterns across many related series.
- **Local forecasting models:** Fits each series separately.
- **Machine-learning forecasting:** Uses engineered temporal features with supervised learning models.
- **Recurrent neural forecasting:** Models sequences through recurrent neural-network states.
- **Temporal convolutional forecasting:** Uses convolutions over temporal sequences.
- **Transformer forecasting:** Uses attention-based architectures to model temporal relationships.
- **Neural basis forecasting:** Represents forecasts through learned basis expansions.
- **Probabilistic forecasting:** Predicts outcome distributions or quantiles.
- **Forecast combinations:** Combines multiple forecasting methods to improve accuracy or stability.
- **Direct multistep forecasting:** Trains separate predictions for specified future horizons.
- **Recursive forecasting:** Generates future steps using earlier predictions as subsequent inputs.
- **Multihorizon forecasting:** Produces several future horizons jointly.
- **Scenario forecasting:** Conditions forecasts on alternative assumptions about external drivers.
- **Cold-start forecasting:** Forecasts new entities with limited or no individual history.
- **Censored demand estimation:** Accounts for observed sales being limited by stockouts or capacity.
- **MASE and RMSSE:** Scales forecast errors relative to a reference forecasting method.
- **Pinball loss:** Evaluates quantile forecasts.
- **Continuous ranked probability score:** Evaluates an entire univariate predictive distribution.
- **Prediction interval coverage and width:** Assesses whether forecast intervals are reliable and useful.
- **Diebold–Mariano tests:** Compares forecast losses while accounting for appropriate temporal dependence.

## 28. Survival Analysis, Duration Models, and Reliability

- **Time-to-event analysis:** Models how long it takes for an event to occur.
- **Survival functions:** Gives the probability that an event time exceeds a specified duration.
- **Hazard functions:** Describes instantaneous event risk among units that have not yet experienced the event.
- **Right censoring:** Observes that an event has not happened by the end of observation.
- **Left censoring:** Knows an event occurred before a threshold without observing its exact time.
- **Interval censoring:** Knows an event occurred within a time interval.
- **Left truncation:** Includes units only if they survive or remain eligible until an entry time.
- **Kaplan–Meier estimation:** Estimates survival curves from right-censored data.
- **Nelson–Aalen estimation:** Estimates cumulative hazard.
- **Log-rank tests:** Compares survival experiences across groups.
- **Cox proportional hazards models:** Models relative hazards without specifying a baseline hazard shape.
- **Proportional-hazards diagnostics:** Checks whether hazard ratios remain compatible with the model’s temporal assumptions.
- **Accelerated failure-time models:** Models covariate effects as stretching or compressing event times.
- **Parametric survival models:** Assumes a specific event-time distribution.
- **Time-varying covariates:** Allows predictor values to change during follow-up.
- **Time-varying effects:** Allows predictor relationships with event risk to change over time.
- **Frailty models:** Adds latent random effects to capture unobserved risk heterogeneity.
- **Competing risks:** Handles different events that prevent each other from occurring first.
- **Cause-specific hazard models:** Models event-specific instantaneous risk among currently event-free units.
- **Cumulative incidence functions:** Estimates the probability of a specific event in the presence of competing events.
- **Fine–Gray models:** Models covariate relationships with the subdistribution hazard.
- **Recurrent-event models:** Handles events that can happen repeatedly to the same unit.
- **Multistate models:** Models transitions among multiple states.
- **Joint longitudinal–survival models:** Combines repeated measurements with event-time outcomes.
- **Restricted mean survival time:** Summarizes expected event-free time up to a specified horizon.
- **Reliability engineering:** Studies component and system failure behavior.
- **Accelerated life testing:** Infers operating-condition reliability from tests conducted under higher stress.

## 29. Anomaly Detection, Changepoints, and Statistical Process Control

- **Point anomalies:** Identifies individual observations inconsistent with expected behavior.
- **Contextual anomalies:** Identifies observations unusual for their particular circumstances.
- **Collective anomalies:** Identifies unusual sequences or groups of observations.
- **Robust z-scores:** Standardizes deviations using outlier-resistant location and scale estimates.
- **Mahalanobis distance:** Measures multivariate deviation while accounting for covariance.
- **Local outlier factor:** Detects points with unusually low density relative to their neighbors.
- **Isolation forests:** Detects observations that are unusually easy to isolate through random partitioning.
- **One-class support vector machines:** Learns a boundary around typical observations.
- **Reconstruction-based anomaly detection:** Flags inputs that a learned representation reconstructs poorly.
- **Density-based anomaly detection:** Flags observations assigned low density by a fitted model.
- **Extreme-value anomaly thresholds:** Sets tail thresholds using extreme-value models.
- **Offline changepoint detection:** Identifies historical changes after observing the full sequence.
- **Online changepoint detection:** Detects changes as observations arrive.
- **CUSUM charts:** Accumulates deviations to detect persistent process shifts.
- **EWMA charts:** Uses exponentially weighted averages to detect process changes.
- **Shewhart charts:** Monitors process statistics against calibrated control limits.
- **Multivariate control charts:** Monitors several related process measurements jointly.
- **Process capability analysis:** Compares a stable process distribution with specification limits.
- **Alert threshold calibration:** Balances detection sensitivity against false alarms.
- **Detection delay analysis:** Measures how quickly a monitoring system identifies a real change.
- **Root-cause localization:** Identifies dimensions, components, or segments associated with detected deviations.

## 30. Spatial and Spatiotemporal Statistics

- **Spatial autocorrelation:** Describes similarity or dependence associated with geographic proximity.
- **Moran’s I:** Measures global spatial autocorrelation.
- **Geary’s C:** Measures spatial autocorrelation using neighboring differences.
- **Local spatial association statistics:** Identifies localized clusters and spatial outliers.
- **Variograms:** Describes how variability changes with spatial separation.
- **Kriging:** Predicts spatial quantities using a modeled covariance structure.
- **Gaussian random fields:** Defines jointly Gaussian variables indexed over space.
- **Conditional autoregressive models:** Models area-level spatial dependence through conditional relationships.
- **Simultaneous autoregressive models:** Represents spatial dependence through systems of related observations.
- **Spatial lag models:** Includes neighboring outcomes in a spatial dependence structure.
- **Spatial error models:** Represents spatial dependence in unexplained variation.
- **Geographically weighted regression:** Fits location-dependent regression relationships using local weighting.
- **Spatial point processes:** Models the locations of events or objects.
- **Log-Gaussian Cox processes:** Uses a latent Gaussian field to model spatially varying event intensity.
- **Spatial scan statistics:** Searches for regions with unusual event rates.
- **Geostatistics:** Studies prediction and uncertainty for spatially indexed measurements.
- **Small-area estimation:** Combines local information and broader structure to estimate sparsely observed regions.
- **Spatiotemporal models:** Models geographic and temporal dependence jointly.
- **Modifiable areal unit problem:** Recognizes that findings can depend on geographic aggregation choices.
- **Spatial confounding:** Occurs when spatially patterned omitted variables distort estimated relationships.

## 31. Network and Graph Analysis

- **Graph representations:** Describes entities as nodes and relationships as edges.
- **Degree distributions:** Summarizes how many connections nodes have.
- **Centrality measures:** Quantifies different forms of node importance.
- **PageRank:** Measures importance through recursively weighted links.
- **Community detection:** Finds groups with stronger internal connectivity.
- **Modularity:** Measures a community partition relative to a specified network baseline.
- **Stochastic block models:** Models connections through latent group memberships.
- **Degree-corrected block models:** Adds flexibility for differing node connectivity within groups.
- **Latent-space network models:** Models connections through unobserved positions or similarities.
- **Exponential random graph models:** Represents network probabilities through structural statistics.
- **Link prediction:** Predicts missing or future relationships.
- **Graph embeddings:** Represents nodes or graphs as vectors.
- **Graph neural networks:** Learns through aggregation along graph relationships.
- **Network diffusion models:** Describes the spread of information, behavior, or disease.
- **Hawkes processes:** Models event sequences in which previous events influence future event intensity.
- **Network interference models:** Studies interventions when effects travel through relationships.
- **Graph sampling bias:** Examines distortions caused by observing only part of a network.

## 32. Recommendation, Information Retrieval, and Ranking

- **Collaborative filtering:** Recommends using patterns in users’ interactions with items.
- **Content-based recommendation:** Recommends using item attributes and user preferences.
- **Matrix factorization:** Represents user–item interactions using lower-dimensional latent factors.
- **Implicit-feedback models:** Learns from behavior such as views or purchases rather than explicit ratings.
- **Factorization machines:** Models interactions between sparse input features through shared latent representations.
- **Two-tower retrieval models:** Learns separate query and candidate representations for efficient matching.
- **Nearest-neighbor retrieval:** Retrieves candidates close to a query in a representation space.
- **Approximate nearest-neighbor search:** Trades some retrieval exactness for speed and scalability.
- **Learning-to-rank objectives:** Optimizes item ordering using pointwise, pairwise, or listwise losses.
- **Pairwise ranking:** Learns which of two items should rank higher.
- **Listwise ranking:** Optimizes properties of an entire ranked list.
- **NDCG:** Evaluates ranking quality with graded relevance and position-dependent discounting.
- **Mean reciprocal rank:** Measures how early the first relevant result appears.
- **Mean average precision:** Summarizes precision at relevant positions across queries.
- **Position bias:** Occurs when item placement affects observed engagement independently of relevance.
- **Counterfactual ranking evaluation:** Adjusts logged interactions for exposure or assignment mechanisms.
- **Diversity-aware recommendation:** Balances relevance with variety.
- **Novelty and serendipity:** Evaluates whether recommendations introduce useful, less obvious items.
- **Cold-start recommendation:** Handles users or items with limited interaction history.
- **Feedback-loop analysis:** Studies how recommendations reshape the data used to train future recommendations.

## 33. Deep Learning, Language, and Generative Modeling

- **Backpropagation:** Computes gradients through compositions of differentiable operations.
- **Convolutional neural networks:** Learns local patterns using shared convolutional filters.
- **Recurrent neural networks:** Maintains state while processing sequences.
- **LSTMs and gated recurrent units:** Uses gating mechanisms to learn temporal dependencies.
- **Attention mechanisms:** Weighs information according to relevance to a representation or prediction.
- **Transformers:** Uses attention-based layers to model relationships within sequences or structured inputs.
- **Residual connections:** Adds shortcut paths that facilitate optimization of deep networks.
- **Normalization methods:** Stabilizes or reshapes activation and optimization behavior.
- **Dropout:** Randomly removes components during training as a regularization technique.
- **Self-supervised learning:** Creates learning objectives from the data itself.
- **Masked modeling:** Learns by predicting deliberately hidden portions of inputs.
- **Autoregressive modeling:** Predicts each element conditional on preceding elements.
- **Sequence-to-sequence modeling:** Maps an input sequence to an output sequence.
- **Language modeling:** Estimates probability distributions over text sequences.
- **Topic modeling:** Discovers latent themes in collections of documents.
- **Latent Dirichlet allocation:** Models documents as mixtures of latent word-distribution topics.
- **Variational autoencoders:** Learns latent-variable generative models through variational inference.
- **Generative adversarial networks:** Trains generators against discriminators.
- **Normalizing flows:** Constructs flexible densities using invertible transformations.
- **Diffusion models:** Learns generation by reversing a progressive noise-corruption process.
- **Energy-based models:** Assigns relative compatibility scores rather than directly normalized probabilities.
- **Multimodal models:** Learns from combinations such as text, images, audio, and structured data.
- **Fine-tuning:** Adapts pretrained model parameters to a task or domain.
- **Parameter-efficient adaptation:** Updates a limited subset or low-dimensional parameterization.
- **Knowledge distillation:** Trains a smaller or different model using a teacher model’s behavior.
- **Retrieval-augmented generation:** Supplies retrieved information as context for generation.
- **Preference optimization:** Adjusts model behavior using comparisons or preferences over outputs.

## 34. Generative AI and Language-Model Evaluation

- **Task-specific evaluation:** Measures whether generated outputs accomplish the intended task.
- **Reference-based evaluation:** Compares outputs with one or more accepted answers.
- **Reference-free evaluation:** Assesses quality without requiring a fixed target answer.
- **Human evaluation design:** Defines sampling, rubrics, raters, and analysis for human judgments.
- **Pairwise preference testing:** Compares alternative outputs through direct preference judgments.
- **Bradley–Terry models:** Estimates relative strengths from pairwise comparison outcomes.
- **Interrater agreement analysis:** Quantifies consistency among evaluators.
- **Judge-model validation:** Checks whether automated evaluators agree with relevant human standards.
- **Position and verbosity bias:** Detects evaluation preferences driven by presentation rather than actual quality.
- **Factuality evaluation:** Measures whether generated claims are accurate.
- **Groundedness evaluation:** Measures whether claims are supported by supplied evidence.
- **Retrieval evaluation:** Measures whether the system retrieves useful and relevant information.
- **Citation quality evaluation:** Checks whether cited material supports the associated claims.
- **Benchmark contamination analysis:** Detects overlap between evaluation material and training or development data.
- **Prompt sensitivity analysis:** Measures output variation across reasonable prompt formulations.
- **Robustness and adversarial evaluation:** Tests failure under difficult, misleading, or manipulated inputs.
- **Agent trajectory evaluation:** Assesses intermediate actions, tool choices, and final task completion.
- **Repeated-trial reliability:** Estimates how consistently a system succeeds across repeated runs.
- **Cost–latency–quality analysis:** Evaluates tradeoffs between output quality and operational resources.
- **End-to-end system evaluation:** Measures the complete workflow rather than isolated model components.

## 35. Bandits, Reinforcement Learning, and Adaptive Decisions

- **Multi-armed bandits:** Allocates repeated choices while learning their rewards.
- **Exploration–exploitation tradeoffs:** Balances learning about alternatives against using currently promising options.
- **Epsilon-greedy policies:** Randomizes some choices while otherwise choosing the estimated best action.
- **Upper confidence bound methods:** Selects actions using estimates plus uncertainty bonuses.
- **Thompson sampling:** Samples plausible reward models and acts optimally under the sampled model.
- **Contextual bandits:** Chooses actions using current user or situation information.
- **Combinatorial bandits:** Chooses sets or combinations of actions.
- **Nonstationary bandits:** Adapts when action rewards change over time.
- **Regret analysis:** Measures cumulative loss relative to an appropriate benchmark policy.
- **Markov decision processes:** Models sequential decisions through states, actions, transitions, and rewards.
- **Partially observable decision processes:** Handles decision-making when the underlying state is incompletely observed.
- **Bellman equations:** Expresses relationships between present value and expected future value.
- **Dynamic programming:** Solves sequential problems through recursive subproblems.
- **Q-learning:** Learns action values from temporal-difference updates.
- **Policy gradients:** Optimizes parameterized policies using reward-based gradients.
- **Actor–critic methods:** Combines policy learning with value estimation.
- **Model-based reinforcement learning:** Uses learned or specified environment dynamics.
- **Offline reinforcement learning:** Learns policies from previously collected interaction data.
- **Importance-sampling policy evaluation:** Reweights logged trajectories to evaluate another policy.
- **Doubly robust policy evaluation:** Combines outcome modeling with assignment-probability adjustment.
- **Constrained reinforcement learning:** Optimizes reward while respecting specified constraints.
- **Reward design:** Defines incentives that represent the actual operational objective.
- **Reward hacking:** Occurs when an agent exploits a reward definition without achieving the intended goal.

## 36. Optimization and Operations Research

- **Linear programming:** Optimizes a linear objective under linear constraints.
- **Integer programming:** Requires some or all decisions to take integer values.
- **Mixed-integer programming:** Combines continuous and integer decision variables.
- **Quadratic programming:** Optimizes a quadratic objective under specified constraints.
- **Convex optimization:** Optimizes convex objectives over convex feasible sets.
- **Nonconvex optimization:** Handles objectives or constraints with potentially many local optima.
- **Lagrange multipliers:** Incorporates constraints into optimization conditions.
- **Karush–Kuhn–Tucker conditions:** Characterizes candidate constrained optima under suitable assumptions.
- **Duality:** Relates optimization problems to companion problems that provide bounds or alternative solutions.
- **Gradient descent:** Updates parameters in the direction of decreasing objective value.
- **Stochastic gradient descent:** Estimates update directions from subsets or random observations.
- **Newton and quasi-Newton methods:** Uses curvature information or approximations to guide optimization.
- **Coordinate descent:** Optimizes subsets of variables in turn.
- **Proximal optimization:** Handles objectives containing difficult or nonsmooth penalty terms.
- **Constrained optimization:** Finds solutions satisfying practical or mathematical restrictions.
- **Multiobjective optimization:** Balances several potentially competing objectives.
- **Pareto frontiers:** Identifies solutions where improving one objective requires worsening another.
- **Stochastic programming:** Optimizes decisions while explicitly representing uncertain future outcomes.
- **Robust optimization:** Optimizes against uncertainty sets rather than a single assumed scenario.
- **Distributionally robust optimization:** Protects performance against a class of probability distributions.
- **Chance-constrained optimization:** Requires constraints to hold with a specified probability.
- **Bayesian optimization:** Uses a probabilistic surrogate to optimize expensive functions.
- **Optimal transport:** Studies efficient transformations between distributions.
- **Assignment and matching optimization:** Allocates entities to opportunities under objectives and constraints.
- **Scheduling and routing:** Optimizes the timing and movement of resources.
- **Queueing theory:** Studies waiting, congestion, service capacity, and system utilization.
- **Inventory optimization:** Balances availability, holding cost, replenishment, and shortage risk.

## 37. Simulation and Computational Statistics

- **Monte Carlo simulation:** Uses repeated random draws to approximate quantities.
- **Monte Carlo error analysis:** Quantifies uncertainty caused by a finite simulation budget.
- **Importance sampling:** Samples from an alternative distribution and reweights to estimate target quantities.
- **Rejection sampling:** Generates target draws by accepting or rejecting proposal samples.
- **Sequential Monte Carlo:** Updates weighted samples as information arrives.
- **Particle filtering:** Estimates dynamic latent states using sequential weighted particles.
- **Quasi-Monte Carlo:** Uses structured low-discrepancy sequences to improve some numerical integrations.
- **Control variates:** Reduces simulation variance using quantities with known expectations.
- **Antithetic variates:** Uses negatively related simulation draws to reduce variance.
- **Stratified Monte Carlo:** Allocates simulation draws across defined regions.
- **Rare-event simulation:** Estimates probabilities too small for straightforward simulation to handle efficiently.
- **Discrete-event simulation:** Models systems through events that change system state.
- **Agent-based simulation:** Models interacting entities with individual behavioral rules.
- **System dynamics:** Models aggregate feedback loops, stocks, and flows.
- **Digital twins:** Uses a computational representation of a real system to support analysis and decisions.
- **Simulation metamodels:** Approximates expensive simulations with simpler predictive models.
- **Global sensitivity analysis:** Measures how uncertain inputs contribute to output variation.
- **Sobol indices:** Decomposes output variance into input and interaction contributions.
- **Value of information analysis:** Estimates how much better decisions could become with additional information.
- **Simulation optimization:** Uses simulation outputs to search for improved decisions.

## 38. Product, Customer, Marketing, and Business Analytics

- **Metric trees:** Connects overall outcomes to their component drivers.
- **KPI design:** Defines measurable indicators aligned with actual goals.
- **North-star metrics:** Selects a central measure intended to represent sustained product value.
- **Funnel analysis:** Studies progression and drop-off through sequential steps.
- **Cohort analysis:** Compares entities grouped by a shared starting event or characteristic.
- **Retention analysis:** Measures continued activity or relationship persistence over time.
- **Churn modeling:** Predicts or explains customer departure.
- **Customer lifetime value:** Estimates expected future customer contribution over a defined horizon.
- **RFM analysis:** Segments customers using recency, frequency, and monetary value.
- **Customer segmentation:** Groups customers to support differentiated decisions or strategies.
- **BG/NBD models:** Models repeat transactions and latent customer inactivity under specific behavioral assumptions.
- **Pareto/NBD models:** Models purchasing and dropout processes in noncontractual customer settings.
- **Purchase timing models:** Estimates when customers will transact again.
- **Demand estimation:** Models how purchases respond to prices and other drivers.
- **Price elasticity:** Measures proportional demand changes associated with proportional price changes.
- **Cross-price elasticity:** Measures how one product’s price relates to another product’s demand.
- **Discrete-choice models:** Models selection among available alternatives.
- **Nested and mixed logit models:** Adds structured substitution or preference heterogeneity to choice models.
- **Conjoint analysis:** Estimates preferences from choices or evaluations of product attribute combinations.
- **Marketing mix modeling:** Relates aggregate outcomes to marketing activity and other drivers.
- **Adstock models:** Represents advertising effects that persist over time.
- **Saturation curves:** Represents diminishing incremental response as exposure or spend increases.
- **Attribution modeling:** Allocates observed conversions across touchpoints; allocation alone does not establish causal incrementality.
- **Incrementality measurement:** Estimates outcomes caused by an intervention beyond what would have occurred otherwise.
- **Cannibalization analysis:** Measures whether gains in one offering displace another.
- **Unit economics:** Estimates contribution and costs at a meaningful operational unit.
- **Decomposition analysis:** Separates aggregate changes into components such as volume, mix, rate, and price.
- **Oaxaca–Blinder decomposition:** Decomposes group mean differences using modeled characteristics and coefficients.
- **Index-number methods:** Separates changes in aggregate value into price and quantity components.
- **Seasonal adjustment:** Removes estimated seasonal patterns to improve comparisons.

## 39. Research Synthesis and Specialized Statistical Methodologies

- **Systematic reviews:** Uses explicit procedures to find, assess, and synthesize relevant research.
- **Meta-analysis:** Combines estimates from multiple studies.
- **Fixed-effect meta-analysis:** Estimates a common effect under a shared-effect model.
- **Random-effects meta-analysis:** Models variation in underlying effects across studies.
- **Meta-regression:** Explains between-study effect variation using study characteristics.
- **Network meta-analysis:** Compares multiple interventions using direct and indirect evidence.
- **Publication bias assessment:** Investigates whether available studies differ systematically from unreported studies.
- **Evidence grading:** Evaluates confidence in a body of evidence.
- **Reproducibility:** Asks whether the same data and procedures reproduce the same results.
- **Replicability:** Asks whether new data support comparable findings.
- **Structural equation modeling:** Represents systems of relationships, often including latent variables.
- **Path analysis:** Models a specified system of relationships among observed variables.
- **Item response theory:** Models responses as functions of latent traits and item characteristics.
- **Rasch models:** Uses a constrained item-response framework for measurement.
- **Generalizability theory:** Decomposes measurement error across multiple sources.
- **Psychometrics:** Studies the measurement of latent attributes such as ability, attitudes, and preferences.
- **Compositional data analysis:** Analyzes quantities constrained by a shared total using appropriate relative representations.
- **Log-ratio transformations:** Represents compositions through ratios rather than unconstrained raw components.
- **Functional data analysis:** Treats curves or functions as the observational objects.
- **Circular statistics:** Analyzes angles, directions, and periodic positions.
- **Directional statistics:** Extends statistical analysis to directions on circles or spheres.
- **Symbolic and interval-valued data analysis:** Models observations represented by ranges or structured summaries.
- **High-dimensional inference:** Performs estimation or testing when the number of variables is large relative to observations.
- **Sparse precision-matrix estimation:** Estimates conditional dependency structures through inverse covariance matrices.
- **Graphical lasso:** Uses penalization to estimate sparse Gaussian graphical models.
- **Tensor decomposition:** Factorizes multidimensional arrays into lower-dimensional structures.
- **Topological data analysis:** Studies data shape using connectivity and higher-order structure.
- **Persistent homology:** Measures which topological features persist across scales.
- **Statistical disclosure control:** Reduces the risk of exposing individuals through released statistics.
- **Differential privacy:** Bounds how much a released result can reveal about any one participating individual.

## 40. Production Methodology, Governance, and Senior Scientific Judgment

- **Point-in-time correctness:** Ensures features contain only information available when a prediction would have been made.
- **Training–serving consistency:** Keeps production feature computation aligned with model development.
- **Data contracts:** Defines expectations about schemas, meanings, quality, and update behavior.
- **Dataset versioning:** Preserves the exact data used to produce a result.
- **Model versioning:** Records model artifacts and their relationships to code, data, and settings.
- **Reproducible pipelines:** Makes analyses rerunnable with controlled inputs and transformations.
- **Data drift monitoring:** Detects changes in incoming data distributions.
- **Performance monitoring:** Tracks whether deployed predictions remain useful.
- **Calibration monitoring:** Checks whether predicted probabilities retain their interpretation.
- **Label-delay handling:** Accounts for outcomes becoming available only after operational decisions.
- **Retraining policies:** Defines when models should be updated and what evidence justifies updates.
- **Shadow deployment:** Runs a model alongside production without using its outputs for live decisions.
- **Canary deployment:** Introduces a model to a limited operational scope before broader release.
- **Champion–challenger evaluation:** Compares an incumbent system with candidate replacements.
- **Rollback criteria:** Defines conditions requiring a deployment to be reversed.
- **Human-in-the-loop systems:** Integrates people into prediction, review, escalation, or decision processes.
- **Feedback-loop management:** Accounts for deployed decisions changing future observations and labels.
- **Model risk management:** Evaluates the consequences and controls associated with model failures.
- **Model documentation:** Records purpose, assumptions, development data, evaluation, limitations, and intended use.
- **Independent validation:** Uses separate review to challenge model design and supporting evidence.
- **Auditability:** Preserves enough evidence to reconstruct how results and decisions were produced.
- **Decision thresholds and escalation rules:** Translates model outputs into accountable operational actions.
- **Cost of false confidence:** Assesses the consequences of acting as though uncertain evidence were definitive.
- **Scope control:** Recognizes when available data cannot support the proposed claim.
- **Method selection:** Chooses the simplest adequate approach given the estimand, data, assumptions, and stakes.
- **Scientific communication:** Explains findings, uncertainty, assumptions, and implications clearly to different audiences.
- **Technical review:** Challenges identification, leakage, validation, implementation, and interpretation.
- **Research prioritization:** Allocates effort according to decision value and reducible uncertainty.
- **Experiment prioritization:** Selects studies based on expected information, impact, cost, and feasibility.
- **Decision ownership:** Makes clear who acts on evidence and who is accountable for consequences.

## Primary References

- [NIST/SEMATECH e-Handbook of Statistical Methods](https://www.itl.nist.gov/div898/handbook/dtoc.htm): Exploratory analysis, estimation, experimental design, process control, and reliability.
- [An Introduction to Statistical Learning](https://www.statlearning.com/): Regression, classification, resampling, regularization, trees, deep learning, survival analysis, and unsupervised learning.
- [Causal Inference: What If](https://miguelhernan.org/whatifbook): Causal reasoning, adjustment, causal models, and longitudinal causal inference.
- [Forecasting: Principles and Practice](https://otexts.com/fpp3/): Time-series exploration, decomposition, exponential smoothing, ARIMA, dynamic regression, and hierarchical forecasting.
- [Stan: Posterior Analysis](https://mc-stan.org/docs/reference-manual/analysis.html): Bayesian computation, effective sample size, and posterior diagnostics.
- [Stan: Posterior and Prior Predictive Checks](https://mc-stan.org/docs/stan-users-guide/posterior-predictive-checks.html): Simulation-based assessment of Bayesian model assumptions and fit.
- [A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification](https://arxiv.org/abs/2107.07511): Prediction sets, coverage guarantees, and uncertainty quantification.
- [Double/Debiased Machine Learning for Treatment and Causal Parameters](https://arxiv.org/abs/1608.00060): Orthogonal estimation, cross-fitting, and causal parameter estimation with machine learning.