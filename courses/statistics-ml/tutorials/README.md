# Worked statistics and machine learning tutorials

These routes extend the original 40-chapter reference and retain its 1,005-topic
outline. Each tutorial explains the question, assumptions, mathematics, complete
Python example and interpretation. They have no exams, mandatory problem sets or
hidden answers. Direct prerequisites are recorded in the classroom catalog.

Start the classroom with the [main installation instructions](../../../README.md).
Most examples use Python Core. The final PyMC tutorial uses the separately pinned
bayesian-cpu profile. After initial preparation, examples use local synthetic data
and do not download models or datasets.

## Routes

| Route | Focus | Start |
| --- | --- | --- |
| Experimentation | Assignment, metrics, integrity, power, effects, adjustment, monitoring, designs and decisions | [Experiment lifecycle](experimentation/README.md) |
| Statistical learning | Likelihood, logistic regression, forests, boosting, PCA, validation and generalization | [Learning mechanisms](learning/README.md) |
| Scientific analysis | Causality, posterior decisions, forecasting, survival, ranking, synthesis and reproducible workflows | [Scientific workflows](science/README.md) |

## Tutorial index

| Lesson ID | Tutorial | Runtime |
| --- | --- | --- |
| `statistics-exp-001` | [Assignment, exposure and the causal estimand](experimentation/01-question-and-estimand.md) | `python-core` |
| `statistics-exp-002` | [Metric contracts and denominators](experimentation/02-metric-contracts.md) | `python-core` |
| `statistics-exp-003` | [Instrumentation, joins and selection](experimentation/03-instrumentation-and-selection.md) | `python-core` |
| `statistics-exp-004` | [Power, allocation and duration](experimentation/04-power-and-duration.md) | `python-core` |
| `statistics-exp-005` | [A/A calibration and integrity diagnosis](experimentation/05-aa-and-integrity.md) | `python-core` |
| `statistics-exp-006` | [Fixed-horizon effects and uncertainty](experimentation/06-fixed-horizon-analysis.md) | `python-core` |
| `statistics-exp-007` | [CUPED and adjusted treatment comparisons](experimentation/07-cuped-and-adjustment.md) | `python-core` |
| `statistics-exp-008` | [Sequential monitoring and multiplicity](experimentation/08-monitoring-and-multiplicity.md) | `python-core` |
| `statistics-exp-009` | [Replicated factorial effects and aliases](experimentation/09-factorial-analysis.md) | `python-core` |
| `statistics-exp-010` | [Interference, exposure mappings and saturation](experimentation/10-interference-and-saturation.md) | `python-core` |
| `statistics-exp-011` | [Switchbacks, clusters and carryover](experimentation/11-switchbacks-and-carryover.md) | `python-core` |
| `statistics-exp-012` | [Ramping, long-term effects and decision memos](experimentation/12-ramping-and-decision-memo.md) | `python-core` |
| `statistics-learning-001` | [Geometry, calculus and numerical fitting](learning/01-geometry-and-calculus.md) | `python-core` |
| `statistics-learning-002` | [Likelihood, estimation and interval coverage](learning/02-likelihood-and-inference.md) | `python-core` |
| `statistics-learning-003` | [Logistic regression from model to decision](learning/03-logistic-model-to-decision.md) | `python-core` |
| `statistics-learning-004` | [Random forests and measured diversity](learning/04-forests-and-validation.md) | `python-core` |
| `statistics-learning-005` | [Boosting objectives, trajectories and stopping](learning/05-boosting-loss-and-stopping.md) | `python-core` |
| `statistics-learning-006` | [PCA compression versus prediction](learning/06-pca-compression-and-prediction.md) | `python-core` |
| `statistics-learning-007` | [Validation of the complete learning procedure](learning/07-validation-as-a-procedure.md) | `python-core` |
| `statistics-learning-008` | [Formal learning theory and generalization bounds](learning/08-learning-theory-and-bounds.md) | `python-core` |
| `statistics-science-001` | [Cross-fitted causal estimation and sensitivity](science/01-causal-estimation-and-sensitivity.md) | `python-core` |
| `statistics-science-002` | [Posterior prediction, pooling and decisions](science/02-posterior-prediction-and-decision.md) | `python-core` |
| `statistics-science-003` | [Vintage-aware multi-series forecasting](science/03-vintage-aware-forecasting.md) | `python-core` |
| `statistics-science-004` | [Censored survival models and competing events](science/04-survival-and-competing-events.md) | `python-core` |
| `statistics-science-005` | [Ranking, policy evaluation and constrained allocation](science/05-ranking-policy-and-allocation.md) | `python-core` |
| `statistics-science-006` | [Research synthesis and heterogeneous effects](science/06-research-synthesis.md) | `python-core` |
| `statistics-science-007` | [An integrated scientific workflow](science/07-integrated-scientific-workflow.md) | `python-core` |
| `statistics-science-008` | [Longitudinal regimes and target-trial timing](science/08-longitudinal-regimes-and-target-trials.md) | `python-core` |
| `statistics-science-009` | [PyMC hierarchical modeling and diagnostic evidence](science/09-pymc-hierarchy-and-diagnostics.md) | `bayesian-cpu` |

## Interpreting the examples

A small synthetic example checks a mechanism under stated assumptions. It does
not establish an effect in an external population or convergence of every
sampling run. Retain the unit of analysis, denominator, time order, uncertainty
and decision rule when adapting a case. The PyMC example intentionally reports
its actual diagnostics; a successful process exit does not certify inference.

The [reference comparison](../../../docs/statistics-reference-map.md) explains how
the expansion relates to established textbooks. [Authoring notes](authoring/README.md)
describe maintained casebooks, generated standalone programs and source checks.
