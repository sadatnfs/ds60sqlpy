# Scientist and ML engineer learning roadmap

This is the maintained map from the 25 October 2026 scientist review to the
implemented 0.5 and 1.0 learning paths. The earlier review was a planning
snapshot: R, JAX, prepared Bayesian tools and several deeper workflows were
absent then. They are not a current missing-features list. This page describes
checked-in teaching and supported execution contracts, not a claim that every
platform or release image has passed qualification.

Start the [Docker classroom](../README.md), choose a subject, and follow its
direct prerequisites. Existing projects keep their saved runtime selection.
Use `./classroom --all` to add the current ordinary set deliberately, or choose
specific [profiles](docker-profiles.md). `./classroom resume` never builds or
pulls. Historical day numbers and lesson IDs are stable labels, not a deadline.

## Where each recommendation is taught

| Recommendation from the review | Existing foundation and 0.5 implementation | 1.0 continuation and useful outcome |
| --- | --- | --- |
| Experimentation depth | [Twelve experiment tutorials](../courses/statistics-ml/tutorials/experimentation/README.md): estimands, denominators, instrumentation, power, A/A and SRM, adjusted comparisons, sequential monitoring, factorials, interference, switchbacks and ramp decisions | [Applied Science](../courses/applied-science/README.md) extends identification and decisions; [LLM evaluation](../courses/llm-evaluation/README.md) applies sampling, paired/clustered inference, multiplicity and online evaluation to language systems. These extend experimentation rather than replacing its foundations. |
| Mathematical and learning-theory foundations | [Eight learning tutorials](../courses/statistics-ml/tutorials/learning/README.md): geometry, numerical fitting, likelihood, logistic curvature, forests, boosting, PCA, whole-procedure validation and formal generalization bounds | `science-023` examines high-dimensional identification; Julia and Bayesian Computing add numerical oracles and computational diagnostics. A fit, a bound and a deployment guarantee remain different claims. |
| Practical Bayesian computation | [Scientific tutorial sequence](../courses/statistics-ml/tutorials/science/README.md), including actual PyMC hierarchy and diagnostics in `statistics-science-009` | [Bayesian Computing](../courses/bayesian-computing/README.md): 24 units from generative reasoning through PyMC/ArviZ and native Stan. Compare parameterizations, check predictions, investigate diagnostic failures and quantify decision uncertainty. |
| Applied causal analysis | Original causal chapters and `statistics-science-001/008` cover cross-fitting, sensitivity and target-trial timing | `science-001` through `science-006` connect transported estimands, overlap, sensitivity, staggered adoption, sequential g-formula and treatment weights. Assumptions and target populations precede estimator selection. |
| Forecasting workflows | Original time-series chapters, Python ARIMA and `statistics-science-003` provide the baseline | `science-007` through `science-009` add data vintages and revisions, overlapping origins, covariance-weighted hierarchical reconciliation, calibration and asymmetric decision losses. |
| Survival and duration models | Original censoring/competing-risk coverage and `statistics-science-004`; R adds fitted survival work | `science-010` through `science-012` fit and diagnose risk-set/Cox and AFT likelihoods, delayed entry and competing incidence. `bayes-024` adds a native Stan censored, left-truncated survival model. |
| Recommenders and ranking | Existing retrieval, ranking metrics and `statistics-science-005` establish candidate and policy concepts | `science-013` through `science-015` connect actual candidate generation, cold start, a learned pairwise ranker, exposure/availability-aware negatives and logged-policy evaluation. They do not claim to operate a large recommendation service. |
| Decisions under uncertainty | Existing real SciPy solver examples and the scientific tutorial decision case | `science-016` through `science-018` develop LP duality, local shadow-price interpretation, MILP bounds, scenario loss, minimax choices and information value. `bayes-015` separates posterior decisions from Monte Carlo error. |
| Research synthesis and reproducibility | Original synthesis chapter and `statistics-science-006/007` provide the baseline | `science-019/020` estimate heterogeneity, distinguish mean and prediction uncertainty, model dependent effects and examine explicit missing-study scenarios. `science-024` builds a reproducible decision dossier with rollback conditions. |
| Spatial, survey and high-dimensional methods | Original topic capsules and neighboring modeling lessons | `science-021` through `science-023` add actual spatial permutation/blocked reasoning, inclusion-weight and cluster calculations, and regularization/nonidentifiability cases. These are bounded worked extensions, not every specialized method in those fields. |
| R language and graphics | [R](../courses/r/README.md): 60 units, including vectors, missingness, S3/S4/R6/S7, data pipelines, models, base graphics, ggplot2 and Plotly | R remains the distinct statistical-language route. Use its idioms to compare scientific questions across languages rather than translating Python syntax mechanically. |
| JAX scientific computing | [JAX](../courses/jax/README.md): 34 units, CPU transformations, explicit randomness/state, derivatives, JIT, numerical models and explicit optional accelerator continuations | Julia and Bayesian Computing provide complementary numerical and modeling routes. GPU/TPU and multi-host JAX remain separately prepared and qualified environments. |
| DAX and semantic-model analytics | [DAX](../courses/dax/README.md): 60 units of editable offline code, model/context reasoning and hand-derived references | The deliberate offline contract remains: edits do not recalculate worked tables, and there is no Run/Compile operation or required external account. |
| Polars and real dbt | Existing Arrow/Parquet/DuckDB and the bridge's dbt-style dependency-graph project remain useful prerequisites | [Polars](../courses/polars/README.md): 18 units of actual expression/lazy/data-contract work. [dbt](../courses/dbt/README.md): 26 units of actual Core/DuckDB projects, plus four beginner SQL-model variants. |
| Integrated ML systems, features and governance | Python already teaches MLflow, Prefect, point-in-time joins, leakage prevention, delivery and service foundations | [ML engineering](../courses/ml-engineering/README.md): 18 units connect contracts, feature/training state, tracking, decisions and operations. The [owned local system](../courses/ml-engineering/projects/local-system/README.md) performs real local training, Feast retrieval, MLflow recording, HTTP serving and rollback. |
| End-to-end data and ML engineering | Python/SQL, Polars, dbt and the focused ML engineering route provide language and system prerequisites | [Data and ML Engineering](../courses/data-ml-engineering/README.md): 72 tutorial chapters connect ingestion, contracts, state, storage, features, model decisions, reliability and complete request-to-SSE inference. Its owned data-product and inference projects provide actual HTTP and persistence workflows. |
| Apache and open-data infrastructure | Arrow, Spark and relational foundations provide the starting vocabulary | [Apache and open-data platforms](../courses/apache-data-platforms/README.md): 88 units explain library APIs, distributed services, failure and recovery. Read the project-specific [qualification ledger](../courses/apache-data-platforms/authoring/ENVIRONMENTS.md); an executed library example is distinct from a running cluster or prepared Atlas/Delta Sharing client. |
| Statistical evaluation for LLM/NLP and alignment objectives | [NLP](../courses/nlp/README.md), [LLM theory](../courses/llm-theory/README.md) and [applied LLMs](../courses/llm-applied/README.md) already cover mechanisms, retrieval and adaptation | [LLM evaluation](../courses/llm-evaluation/README.md): 24 units plus three Plotly variants. Sampling, annotation, judge calibration and held-out decisions lead to Bradley-Terry, DPO, PPO and GRPO mechanisms, including tiny actual PyTorch updates. Synthetic success is not pretrained capability evidence. |
| A distinct additional scientific language | The review deferred another language until it supplied a clear learning outcome | [Julia](../courses/julia/README.md): 32 units explain multiple dispatch, parametric types, arrays, DataFrames, numerical stability, automatic differentiation, optimization, concurrency and reproducible scientific reports. It adds language-specific mechanisms rather than another generic ML survey. |

The original statistics outline still maps 1,005 named topics into 40 chapters.
That is topic traceability, not uniform textbook depth. [The reference comparison](statistics-reference-map.md)
explains how the connected tutorials deepen selected areas. Logistic regression,
random forests, XGBoost and PCA were already taught before these releases; they
must not be described as newly discovered gaps. The book comparison uses selected
author/publisher resources, not a claim to reproduce or replace those books.

## Choose a route for your current work

A first-time programmer should start with Python foundations and the SQL on-ramp
(`sql-start-01` through `sql-start-03`), then learn arrays, data frames, joins,
probability and model assessment. A different general-purpose language is not a
prerequisite for every scientific branch.

- **Experimentation and applied science:** statistics foundations, the experiment
  tutorials, then Applied Science cases relevant to the question. Treat causal
  identification, prediction and resource decisions as different objectives.
- **Bayesian and numerical modeling:** the probability/likelihood material,
  Bayesian Computing's numerical foundations, actual PyMC workflows, then Stan.
  JAX and Julia are complementary branches when derivatives or language/runtime
  semantics are the learning goal.
- **Data and ML engineering:** start with the [engineering book](../courses/data-ml-engineering/README.md)
  and its named Python/SQL prerequisites. Use Polars, dbt and the focused ML
  engineering route for deeper tool practice. Connect event time, availability
  time, trained state, inference and rollback in the owned projects, then choose
  relevant [platform workshops](../courses/apache-data-platforms/README.md).
- **Applied LLM science:** NLP and Transformer mechanisms, the applied retrieval
  and adaptation route, then LLM evaluation. Follow `dme-057` through `dme-072`
  for the request-to-SSE lifecycle and its actual CPU inference workshop. Keep
  retrieval quality, factual support, safety policy, preference objectives and
  held-out task utility distinct.

These are suggested connections, not access gates. Use each lesson's actual
prerequisite IDs. Applied Science, Bayesian Computing, Data and ML Engineering
and the statistics book are tutorials with complete answers and no required
exams. Programming practice routes retain separate attempts, exercises and
references. Reading markers and
reference executions do not certify expertise.

## What runs where

| Surface | Contract |
| --- | --- |
| `python-core` | Existing scientific stack, Applied Science and Bayesian foundations; LLM evaluation units that do not require PyTorch |
| `bayesian-cpu` | Actual pinned PyMC/ArviZ CPU fitting and diagnostic objects |
| `stan-cpu` | Native `main.stan`; tiny fixtures in `transformed data`; two fixed chains of 100 warmup plus 100 retained draws |
| `data-engineering` | Polars, complete Python-created dbt projects and ML engineering programs |
| `data-platforms-python` | Separately locked Arrow, DataFusion SQL and local PyIceberg library operations; persistent platform services use owned projects |
| `dbt-duckdb` | One SQL/Jinja `model.sql` in a fixed local dbt project; actual table and run metadata |
| `julia` | Fresh Julia 1.13.3 process, two threads, read-only prepared project/depot and scientific packages |
| `r-statistics`, `jax-cpu`, `llm-torch-cpu` | The corresponding separately prepared language/framework, with its own package and execution contract |

The [standard-data Stan project](../courses/bayesian-computing/projects/normal-mean/README.md)
uses a real `data.json`, CmdStanPy 1.3.0 and an explicit saved-output directory.
The [dbt retail project](../courses/dbt/projects/retail/README.md) supplies the
full project configuration and CLI workflow. The ML service has explicit
start/stop/resume/down commands and persistent state separate from classroom
volumes; the predictor mounts that state read-only. The engineering book's
[data product](../courses/data-ml-engineering/projects/data-product/README.md)
keeps ingestion and publication/recovery state separately; its
[inference service](../courses/data-ml-engineering/projects/inference-service/README.md)
retains model and SSE request history. Platform workshops have explicit native
architecture, preparation and ownership requirements. Atlas needs a separately
prepared supported server stack; a prepared Delta Sharing client does not
establish reference-server acceptance. None implies a multi-file
browser editor, arbitrary pad command arguments or a background cloud service.

Source-bound figures, tables and JSON reports make assumptions and numerical
results inspectable without rerunning code. They share the bounded
[output contract](plotting.md). Mathematical typesetting and syntax highlighting
work through bundled offline resources; TeX compilation checks syntax and layout,
not the correctness of a derivation.

## Boundaries and future additions

The maintained routes use small synthetic offline data. Short chains, local
Spark, single-machine services and tiny policy models teach mechanisms. They do
not establish convergence for every posterior, distributed fault tolerance,
production capacity or externally useful LLM behavior. GPU correctness,
profiling, distributed training, cloud deployment, external model acquisition,
Apple SDKs and proprietary DAX engines retain their explicit preparation and
qualification boundaries.

Future additions should name a concrete missing outcome, inspect the closest
existing guide and update its coverage ledger. Prefer a deeper worked case when
the subject already exists. A new language or tool needs a distinct mechanism,
prepared runtime, authoring/style support, actual success and failure evidence,
and saved-work acceptance. Use the [extension playbook](curriculum-extension-playbook.md)
and [authoring skill](../.agents/skills/add-learning-path/SKILL.md). Keep current
source registration, local execution, browser/persistence checks and hosted CI
as separate evidence; this roadmap is not a release acceptance report.
