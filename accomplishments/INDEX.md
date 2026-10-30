# DS60 accomplishment and learning index

Generated from the repository's maintained catalog, course manifests, package exports, native registry and study/reference registries. The running accomplishment log is maintained separately in `RUNNING.md`.

Use `python index.py search QUERY` to find a lesson, model, package or API. Every path below is relative to the repository root. Status describes the cited evidence tier, not learner mastery or current publication.

## Coverage

| Kind | Entries |
| --- | ---: |
| track | 40 |
| lesson | 2074 |
| package | 2 |
| api | 27 |
| likelihood-model | 6 |
| model-factory | 7 |
| native-model | 23 |
| scala-api | 14 |
| torch-api | 8 |
| r-model | 4 |
| r-case | 24 |
| study | 37 |
| capability | 11 |

## Learning tracks

| Track | Lessons | Source |
| --- | ---: | --- |
| Advanced Spark modeling: likelihoods, autodiff and engine internals (`track:advanced-spark-modeling`) | 38 | [source](../courses/advanced-spark-modeling/lessons.json) |
| Apache and open data platforms (`track:apache-data-platforms`) | 88 | [source](../courses/apache-data-platforms/lessons.json) |
| Applied science: identification, prediction and decisions (`track:applied-science`) | 24 | [source](../courses/applied-science/lessons.json) |
| Bayesian computing: exact inference, PyMC and Stan (`track:bayesian-computing`) | 24 | [source](../courses/bayesian-computing/lessons.json) |
| Python and PostgreSQL engineering (`track:bridge`) | 13 | [source](../curriculum/catalog.json) |
| C: memory, systems and reliable native programs (`track:c`) | 42 | [source](../courses/c/lessons.json) |
| C++20: from first program to reliable systems (`track:cpp`) | 42 | [source](../courses/cpp/lessons.json) |
| C#: from the first program to reliable .NET applications (`track:csharp`) | 48 | [source](../courses/csharp/lessons.json) |
| GPU computing: CUDA, Python, machine learning and Spark (`track:cuda`) | 319 | [source](../courses/cuda/lessons.json) |
| Custom likelihoods in PyTorch (`track:custom-likelihood-pytorch`) | 20 | [source](../courses/custom-likelihood-pytorch/lessons.json) |
| Data and ML Engineering (`track:data-ml-engineering`) | 72 | [source](../courses/data-ml-engineering/lessons.json) |
| Scientific visualization with Plotly: Python and JavaScript (`track:data-visualization`) | 16 | [source](../courses/data-visualization/lessons.json) |
| DAX: semantic models, context and analytical reasoning (`track:dax`) | 60 | [source](../courses/dax/lessons.json) |
| dbt and analytics engineering (`track:dbt`) | 30 | [source](../courses/dbt/lessons.json) |
| Deep Learning with PyTorch: tensors to reliable model releases (`track:deep-learning-pytorch`) | 36 | [source](../courses/deep-learning-pytorch/lessons.json) |
| Deep learning with TensorFlow and Keras (`track:deep-learning-tensorflow`) | 36 | [source](../courses/deep-learning-tensorflow/lessons.json) |
| Docker: images, applications and operating containers (`track:docker`) | 42 | [source](../courses/docker/lessons.json) |
| Go: practical programs, concurrency and Kubernetes controllers (`track:go`) | 48 | [source](../courses/go/lessons.json) |
| Java: from the first compile to reliable applications (`track:java`) | 36 | [source](../courses/java/lessons.json) |
| JavaScript and TypeScript: language, browser and Node applications (`track:javascript-typescript`) | 66 | [source](../courses/javascript-typescript/lessons.json) |
| JAX: numerical functions to independent scientific work (`track:jax`) | 34 | [source](../courses/jax/lessons.json) |
| Julia language and scientific computing (`track:julia`) | 32 | [source](../courses/julia/lessons.json) |
| Kubernetes: from first object to platform reasoning (`track:kubernetes`) | 66 | [source](../courses/kubernetes/lessons.json) |
| Applied LLMs: subject assistants, retrieval and adaptation (`track:llm-applied`) | 24 | [source](../courses/llm-applied/lessons.json) |
| LLM evaluation and alignment (`track:llm-evaluation`) | 27 | [source](../courses/llm-evaluation/lessons.json) |
| Language models: mechanisms, training and evidence (`track:llm-theory`) | 48 | [source](../courses/llm-theory/lessons.json) |
| Machine learning engineering (`track:ml-engineering`) | 18 | [source](../courses/ml-engineering/lessons.json) |
| Natural Language Processing: from text to reliable language systems (`track:nlp`) | 24 | [source](../courses/nlp/lessons.json) |
| Polars: columnar data engineering (`track:polars`) | 18 | [source](../courses/polars/lessons.json) |
| Python and data science (`track:python`) | 102 | [source](../curriculum/catalog.json) |
| Python web development: HTTP, Flask, FastAPI and Django (`track:python-web`) | 72 | [source](../courses/python-web/lessons.json) |
| R: programming, statistical computing and visualization (`track:r`) | 60 | [source](../courses/r/lessons.json) |
| Rust: ownership, reliable systems and Arrow data engineering (`track:rust`) | 48 | [source](../courses/rust/lessons.json) |
| Scala and Apache Spark: Correct Data, Measured Execution, Recoverable Products (`track:scala-spark`) | 72 | [source](../courses/scala-spark/lessons.json) |
| Spark deployment: Compose, notebooks and Kubernetes (`track:spark-deployment`) | 18 | [source](../courses/spark-deployment/lessons.json) |
| PostgreSQL (`track:sql`) | 86 | [source](../curriculum/catalog.json) |
| Statistics and Machine Learning for Data Scientists End To End (`track:statistics-ml`) | 69 | [source](../courses/statistics-ml/manifest.json) |
| Swift: portable language foundations and Apple app architecture (`track:swift`) | 48 | [source](../courses/swift/lessons.json) |
| TMB modeling with R and C++ (`track:tmb-modeling`) | 48 | [source](../courses/tmb-modeling/lessons.json) |
| Web development: HTML, CSS and PHP (`track:web-development`) | 60 | [source](../courses/web-development/lessons.json) |

## Independent packages and public APIs

- **ds60-spark-likelihood 0.2.0**: 20 exported names, [source](../packages/spark-likelihood/pyproject.toml). consult_release_receipts.
- **ds60-spark-tmbad 0.2.0**: 7 exported names, [source](../packages/spark-tmbad/python/pyproject.toml). consult_release_receipts.

## Registered Spark/PyTorch likelihood models

| ID | Title | Scope |
| --- | --- | --- |
| `likelihood-model:gaussian_random_intercept` | Gaussian Random Intercept | source_only_runtime_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `likelihood-model:linear_gaussian` | Linear Gaussian | source_only_runtime_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `likelihood-model:logistic` | Logistic | source_only_runtime_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `likelihood-model:nonlinear_gaussian` | Nonlinear Gaussian | source_only_runtime_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `likelihood-model:normal_mean` | Normal Mean | source_only_runtime_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `likelihood-model:poisson_exposure` | Poisson Exposure | source_only_runtime_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |

## Named PyTorch model factories

| ID | Title | Scope |
| --- | --- | --- |
| `model-factory:gaussian_random_intercept` | gaussian_random_intercept | runtime_evidence_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `model-factory:linear_gaussian` | linear_gaussian | runtime_evidence_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `model-factory:logistic` | logistic | runtime_evidence_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `model-factory:nonlinear_gaussian` | nonlinear_gaussian | runtime_evidence_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `model-factory:normal_mean` | normal_mean | runtime_evidence_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `model-factory:poisson_exposure` | poisson_exposure | runtime_evidence_separate ([guide](../packages/spark-likelihood/docs/custom-models.md)) |
| `model-factory:quadratic_model` | quadratic_model | not_builtin_registered ([guide](../packages/spark-likelihood/docs/custom-models.md)) |

## Primary Scala facade operations

| ID | Title | Scope |
| --- | --- | --- |
| `scala-api:PythonBridge.describe` | PythonBridge.describe | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.evaluateShared` | PythonBridge.evaluateShared | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.fitGroups` | PythonBridge.fitGroups | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.fitShared` | PythonBridge.fitShared | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.forecast` | PythonBridge.forecast | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.forecastAtParameters` | PythonBridge.forecastAtParameters | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.forecastGroups` | PythonBridge.forecastGroups | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.predict` | PythonBridge.predict | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.predictAtParameters` | PythonBridge.predictAtParameters | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.predictConditional` | PythonBridge.predictConditional | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.predictConditionalAtParameters` | PythonBridge.predictConditionalAtParameters | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.predictConditionalGroups` | PythonBridge.predictConditionalGroups | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.predictGroups` | PythonBridge.predictGroups | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |
| `scala-api:PythonBridge.probe` | PythonBridge.probe | operation_specific_runtime_evidence_required ([guide](../packages/spark-tmbad/docs/PROTOCOL.md)) |

## Integrated CPU Torch executor API

| ID | Source | Scope |
| --- | --- | --- |
| `torch-api:CheckpointRef` | [source](../packages/spark-likelihood/src/ds60_torch_training/checkpoint.py) | installed_wheel_and_runtime_evidence_required |
| `torch-api:TrainingProgram` | [source](../packages/spark-likelihood/src/ds60_torch_training/program.py) | installed_wheel_and_runtime_evidence_required |
| `torch-api:assign_shards` | [source](../packages/spark-likelihood/src/ds60_torch_training/data.py) | installed_wheel_and_runtime_evidence_required |
| `torch-api:load_manifest` | [source](../packages/spark-likelihood/src/ds60_torch_training/data.py) | installed_wheel_and_runtime_evidence_required |
| `torch-api:load_rank` | [source](../packages/spark-likelihood/src/ds60_torch_training/checkpoint.py) | installed_wheel_and_runtime_evidence_required |
| `torch-api:prepare_dataframe` | [source](../packages/spark-likelihood/src/ds60_torch_training/data.py) | installed_wheel_and_runtime_evidence_required |
| `torch-api:prepare_rows` | [source](../packages/spark-likelihood/src/ds60_torch_training/data.py) | installed_wheel_and_runtime_evidence_required |
| `torch-api:run_training` | [source](../packages/spark-likelihood/src/ds60_torch_training/launch.py) | installed_wheel_and_runtime_evidence_required |

## Native custom models

| ID | Title | Evidence status |
| --- | --- | --- |
| `native-model:ar1` | Ar1 | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/ar1.md)) |
| `native-model:bernoulli_logistic` | Bernoulli Logistic | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/bernoulli_logistic.md)) |
| `native-model:beta_binomial` | Beta Binomial | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:beta_regression` | Beta Regression | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:binomial_logistic` | Binomial Logistic | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:gamma_regression` | Gamma Regression | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/gamma_regression.md)) |
| `native-model:gaussian_ar1_random_intercept` | Gaussian Ar1 Random Intercept | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/gaussian_ar1_random_intercept.md)) |
| `native-model:gaussian_correlated_random_slope` | Gaussian Correlated Random Slope | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:gaussian_random_intercept` | Gaussian Random Intercept | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/gaussian_random_intercept.md)) |
| `native-model:gaussian_random_intercept_laplace` | Gaussian Random Intercept Laplace | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/gaussian_random_intercept_laplace.md)) |
| `native-model:hurdle_poisson` | Hurdle Poisson | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:linear_gaussian` | Linear Gaussian | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/linear_gaussian.md)) |
| `native-model:lognormal_regression` | Lognormal Regression | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:negative_binomial2` | Negative Binomial2 | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/negative_binomial2.md)) |
| `native-model:normal` | Normal | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/normal.md)) |
| `native-model:poisson_exposure` | Poisson Exposure | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/poisson_exposure.md)) |
| `native-model:poisson_random_intercept` | Poisson Random Intercept | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/poisson_random_intercept.md)) |
| `native-model:poisson_random_slope` | Poisson Random Slope | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/poisson_random_slope.md)) |
| `native-model:quadratic_gaussian` | Quadratic Gaussian | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/quadratic_gaussian.md)) |
| `native-model:saturating_growth` | Saturating Growth | see_architecture_receipts ([guide](../packages/spark-tmbad/docs/models/saturating_growth.md)) |
| `native-model:student_t_regression` | Student T Regression | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:zero_inflated_poisson` | Zero Inflated Poisson | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |
| `native-model:zero_truncated_poisson` | Zero Truncated Poisson | see_architecture_receipts ([guide](../packages/spark-tmbad/native/README.md)) |

## Optional R/TMB reference cases

| ID | Title | Evidence status |
| --- | --- | --- |
| `r-case:gaussian_random_slope` | Gaussian Random Slope | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:gaussian_ridge` | Gaussian Ridge | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_ar_forecast` | Glmm Ar Forecast | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_covariance-ar1` | Glmm Covariance Ar1 | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_covariance-cs` | Glmm Covariance Cs | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_covariance-diag` | Glmm Covariance Diag | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_covariance-ou` | Glmm Covariance Ou | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_covariance-toep` | Glmm Covariance Toep | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_covariance-us` | Glmm Covariance Us | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-Gamma` | Glmm Family Gamma | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-beta` | Glmm Family Beta | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-betabinomial` | Glmm Family Betabinomial | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-gaussian` | Glmm Family Gaussian | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-lognormal` | Glmm Family Lognormal | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-nbinom1` | Glmm Family Nbinom1 | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-nbinom2` | Glmm Family Nbinom2 | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-poisson` | Glmm Family Poisson | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_family-student` | Glmm Family Student | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_hurdle` | Glmm Hurdle | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_map` | Glmm Map | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:glmm_zero_inflation` | Glmm Zero Inflation | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:nonlinear_growth` | Nonlinear Growth | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:panel_ar1` | Panel Ar1 | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |
| `r-case:regularization_posterior` | Regularization Posterior | historical_arm64_v2 ([guide](../packages/spark-tmbad/reference/docs/MODELS.md)) |

## Simulation study IDs

| ID | Title | Evidence status |
| --- | --- | --- |
| `study:sim-001` | Gaussian MLE, weights and partition invariance | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-002` | All-coordinate L2 and its actual prior | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-003` | Conventional ridge with selected coefficients | historical_local_partial_scope ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-004` | Exact lasso, soft thresholding and KKT conditions | historical_local_partial_scope ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-005` | Correlated designs and elastic-net paths | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-006` | Nonlinear growth and extrapolation | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-007` | Multiple starts and nonlinear identifiability | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-008` | Pooling and complete-group Gaussian likelihoods | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-009` | Independent fits and boundary variance estimates | historical_local_partial_scope ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-010` | MLE, MAP and exact posterior targets | host_reference_only ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-011` | Coordinates, priors and Jacobians | host_reference_only ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-012` | Conditional versus unseen-group forecasts | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-013` | AR1 innovations, stationary variance and cadence | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-014` | Random-intercept AR1 forecasting dossier | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-015` | AFModel-inspired covariates and recursive trends | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-016` | First differences, inverse transforms and uncertainty | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-017` | Process, latent and parameter uncertainty | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-018` | Separation and logistic regularization | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-019` | Poisson, NB1, NB2 and NB12 dispersion | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-020` | Zero inflation versus hurdle models | historical_local_incomplete ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-021` | Truncation, censoring and sample selection | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-022` | Binomial overdispersion and COM-binomial | historical_local_incomplete ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-023` | Beta, ordered-beta and ordinal boundaries | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-024` | Gamma, lognormal, Student-t and skewness | historical_local_incomplete ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-025` | Tweedie compound Poisson outcomes | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-026` | COM-Poisson, generalized Poisson and Bell | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-027` | Conditional mean, zero and dispersion submodels | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-028` | Correlated random intercepts and slopes | historical_local_partial_scope ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-029` | Diagonal, compound-symmetric and Toeplitz covariance | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-030` | Unequal-time OU and heteroskedastic AR1 | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-031` | Spatial exponential, Gaussian and Matern kernels | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-032` | Reduced rank, proportional and shared covariance | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-033` | ML, REML and variance-component comparisons | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-034` | Sandwich inference and cluster bootstrap | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-035` | SBC, posterior diagnostics and Monte Carlo error | not_attested ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-036` | Failure accounting and reproducible study operations | host_reference_only ([guide](../packages/spark-tmbad/studies/README.md)) |
| `study:sim-037` | Global Gaussian coupling through bounded sufficient statistics | host_reference_only ([guide](../packages/spark-tmbad/studies/README.md)) |

## Cross-cutting capabilities

- **Two-platform classroom image publication** (`capability:classroom-publisher`): maintained_workflow; version_and_run_specific. See [guide](../docs/dockerhub.md).
- **Owned Docker classroom start, stop and resume** (`capability:classroom-runtime`): maintained_source; release_specific_receipts_required. See [guide](../docs/one-command-classroom.md).
- **Registered lesson and course catalog** (`capability:course-catalog`): maintained_source; source_registered. See [guide](../docs/content-authoring.md).
- **Simulation study designs and bounded historical shards** (`capability:modeling-studies`): mixed_design_and_source; per_study_historical_status. See [guide](../packages/spark-tmbad/studies/README.md).
- **Native Spark TMBad model and JVM/Python interfaces** (`capability:native-modeling`): maintained_source; architecture_specific_receipts_required. See [guide](../packages/spark-tmbad/README.md).
- **Optional R/TMB/glmmTMB comparison recipe** (`capability:optional-r-reference`): maintained_optional_recipe; native_both_at_53b_run_41122123106_only. See [guide](../packages/spark-tmbad/reference/README.md).
- **Post-publication all-module pull and resume audit** (`capability:published-module-audit`): maintained_workflow; release_specific_receipts_required. See [guide](../docs/dockerhub.md).
- **Bounded R build-log condensation with complete raw logs** (`capability:r-build-logs`): maintained_source; run_specific_artifacts_required. See [guide](../docs/validation.md).
- **Bounded source-bound release artifact retrieval** (`capability:release-artifact-retrieval`): maintained_source; exact_run_receipts_required. See [guide](../docs/dockerhub.md).
- **Guarded course source and reader formatting** (`capability:source-formatting`): maintained_source; current_ci_required. See [guide](../docs/content-authoring.md).
- **Spark deployment course and owned cluster lab** (`capability:spark-deployment`): maintained_source; target_specific_runtime_required. See [guide](../courses/spark-deployment/README.md).

## Maintenance

Run `python index.py build --repo /path/to/ds60sqlpy` after a catalog, model, package, reference or study source change. Run `python index.py check --repo /path/to/ds60sqlpy` in CI. Edit `manual-capabilities.json` for cross-cutting capabilities and `RUNNING.md` for dated accomplishments; the build never overwrites the running log. Add the check to the repository's source/reader validation route after review.
