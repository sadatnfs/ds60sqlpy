# Python and Data Science — 60-Lesson Plan

Overview  
- Goal: Progress from first Python programs to substantial data-science and
  production projects. “Day” is a stable lesson number, not a deadline.
- Structure: 4 Phases — Core Python & Good Coding (Days 1–15), Data Manipulation & Visualization (Days 16–30), Statistics & Machine Learning (Days 31–45), Advanced Topics, Production & Capstone (Days 46–60).  
- Each lesson: companion reading, a runnable learner notebook, hands-on
  exercises, a self-check, and a separate worked solution.

Start with the [track guide](ds-60day/README.md). The machine-readable paths,
prerequisites, dependency groups, and network notes live in
[`curriculum/catalog.json`](../curriculum/catalog.json).

---

## Phase 1 — Core Python & Good Coding Practices (Days 1–15)

Day 1 — Python setup & REPL, virtual environments, package management
- Objectives: Run the repository setup for Windows, macOS, or Linux; select the
  `.venv` interpreter in VS Code; use Python and Jupyter.
- Exercise: Verify the environment, run a simple script, and launch Jupyter.

Day 2 — Basic syntax, variables, data types (str, int, float, bool)  
- Exercise: Small script manipulating types and printing results.

Day 3 — Control flow: conditionals, truthiness, exceptions  
- Exercise: Implement input validation and custom exceptions.

Day 4 — Loops, comprehensions (list/dict/set), generator basics  
- Exercise: Convert loops to comprehensions; write a generator.

Day 5 — Functions, args/kwargs, scope, docstrings, type hints  
- Exercise: Write well-typed utility functions with docstrings.

Day 6 — Data structures: lists, tuples, sets, dicts — performance & use-cases  
- Exercise: Implement common tasks (frequency count, dedupe).

Day 7 — String manipulation, regex basics, pathlib for files  
- Exercise: Parse and clean a text file using regex.

Day 8 — Working with files, JSON, CSV, context managers  
- Exercise: Read/write CSV and JSON, ensure robust error handling.

Day 9 — Modules, packages, import system, __main__, packaging basics  
- Exercise: Create a small package and import it in a script.

Day 10 — Testing fundamentals: pytest, writing unit tests, assertions  
- Exercise: Add tests for previous utilities; run pytest.

Day 11 — Debugging, logging, profiling basics (cProfile, timeit)  
- Exercise: Profile a slow function and add logging.

Day 12 — OOP basics: classes, properties, inheritance, dataclasses  
- Exercise: Model a dataset/entity with dataclass and methods.

Day 13 — Functional tools: itertools, functools, map/filter, lambda  
- Exercise: Use itertools to create streaming transformations.

Day 14 — Code quality: linting and formatting with Ruff, type checking with mypy
- Exercise: Apply Ruff and mypy to existing code and fix issues.

Day 15 — Project: Small CLI data tool combining above skills  
- Exercise: Build a command-line script that ingests a CSV, cleans it, outputs summary; include tests and linting.

---

## Phase 2 — Data Manipulation & Visualization (Days 16–30)

Day 16 — NumPy fundamentals: arrays, vectorization, broadcasting  
- Exercise: Convert loops to vectorized NumPy operations.

Day 17 — Pandas intro: Series, DataFrame, indexing, selection  
- Exercise: Load CSV into DataFrame, inspect, and slice.

Day 18 — Pandas I/O & cleaning: handling missing, types, parsing dates  
- Exercise: Clean a messy dataset (NA handling, type conversions).

Day 19 — Data transformation: groupby, agg, pivot_table, melt  
- Exercise: Aggregations and reshaping on real dataset.

Day 20 — Merging & joins in pandas; efficient joins for large data  
- Exercise: Join multiple tables and resolve key issues.

Day 21 — Time series basics with pandas: date index, resampling, rolling  
- Exercise: Resample and compute rolling statistics.

Day 22 — Advanced pandas: apply vs vectorization, query, eval, categorical dtypes  
- Exercise: Optimize slow apply usage; convert high-cardinality to appropriate types.

Day 23 — Data pipelines: functions, generators, memory-efficient processing  
- Exercise: Build a pipeline to stream, clean, and yield batches.

Day 24 — Exploratory Data Analysis (EDA) best practices & checklist  
- Exercise: Produce an EDA summary notebook for a dataset.

Day 25 — Visualization with Matplotlib + Seaborn fundamentals
- Exercise: Plot distributions, pairplots, correlation heatmap.

Day 26 — Advanced visualizations: interactive plots with Plotly or Altair  
- Exercise: Create one interactive dashboard chart.

Day 27 — Geospatial basics with GeoPandas
- Exercise: Plot simple geospatial data; the optional map dataset has a
  disclosed first-use download and cache.

Day 28 — Feature engineering: encoding, scaling, bins, missing flags  
- Exercise: Engineer features for a modeling task.

Day 29 — Data validation & schemas with Pandera
- Exercise: Add schema checks to ingest pipeline.

Day 30 — Project: EDA + preprocessing notebook on a mid-size dataset  
- Exercise: Deliver cleaned dataset and EDA report with visuals.

---

## Phase 3 — Statistics & Machine Learning (Days 31–45)

Day 31 — Probability refresh: distributions, Bayes basics, sampling  
- Exercise: Simulate sampling and estimate probabilities.

Day 32 — Statistical inference: hypothesis testing, confidence intervals  
- Exercise: Run t-test/chi-square on dataset questions.

Day 33 — Linear algebra & matrices for ML intuition (NumPy practice)  
- Exercise: Implement simple linear regression with matrix ops.

Day 34 — scikit-learn intro: API, pipelines, fit/predict/transform  
- Exercise: Train a baseline classifier with pipeline.

Day 35 — Model evaluation: metrics for classification/regression, cross-validation  
- Exercise: Compare metrics and implement k-fold CV.

Day 36 — Feature selection & dimensionality reduction (PCA, SelectKBest)  
- Exercise: Apply PCA and interpret components.

Day 37 — Regularization & linear models (Ridge, Lasso, Logistic)  
- Exercise: Tune regularization and visualize coef shrinkage.

Day 38 — Tree-based models: Decision Trees, Random Forests, feature importances  
- Exercise: Train RF and analyze feature importances.

Day 39 — Gradient boosting intro: XGBoost/LightGBM basics, tuning tips  
- Exercise: Implement a GBM model, tune key params.

Day 40 — Model tuning & pipelines: GridSearchCV/RandomizedSearchCV, nested CV  
- Exercise: Build pipeline and run parameter search.

Day 41 — Handling imbalance: sampling, class weights, metrics for imbalanced data  
- Exercise: Apply SMOTE or class weighting and compare results.

Day 42 — Unsupervised learning basics: clustering (KMeans), anomaly detection  
- Exercise: Cluster a dataset and interpret clusters.

Day 43 — Model interpretation: SHAP, partial dependence, LIME basics  
- Exercise: Generate SHAP explanations for a model.

Day 44 — Model deployment basics: saving models with joblib, typed APIs with FastAPI
- Exercise: Save model and create a minimal prediction endpoint.

Day 45 — Project: End-to-end modeling mini-project (data → model → evaluation → save)  
- Exercise: Deliver notebook/script with reproducible pipeline and README.

---

## Phase 4 — Advanced Topics, Production & Capstone (Days 46–60)

Day 46 — Introduction to deep learning with PyTorch
- Exercise: Compare a neural model with a simpler baseline and run a small,
  deterministic example.

Day 47 — PyTorch basics: tensors, autograd, a small neural network, training loop
- Exercise: Train a small network on local generated data.

Day 48 — Transfer learning & convolutional-network basics
- Exercise: Adapt a model on a small local dataset, with pretrained weights as
  an explicitly optional first download.

Day 49 — NLP basics with Hugging Face and spaCy: tokenization and embeddings
- Exercise: Build a local text-classification baseline, then optionally compare
  it with a cached pretrained model.

Day 50 — Time-series modeling and forecast evaluation
- Exercise: Forecast a local time series, compare with a naive baseline, and
  evaluate without leakage.

Day 51 — Advanced feature engineering: target encoding, leakage prevention, pipelines  
- Exercise: Implement robust target encoding with CV folds.

Day 52 — Scalability with Dask and chunked processing
- Exercise: Process a bounded generated dataset with Dask and reason about
  partition and memory tradeoffs.

Day 53 — MLOps intro: experiment tracking (MLflow), reproducibility, CI basics  
- Exercise: Track experiments and log artifacts.

Day 54 — Monitoring & model governance: drift detection, retraining strategies  
- Exercise: Simulate data drift and design retraining triggers.

Day 55 — APIs & containerization: Dockerize a prediction service  
- Exercise: Create Dockerfile for model API and run locally.

Day 56 — Orchestration basics with Prefect
- Exercise: Write a local Prefect flow for preprocessing and training.

Day 57 — Security, data privacy & ethical considerations for data science  
- Exercise: Perform basic PII scan and redact sample dataset.

Day 58 — Code review, refactoring, and maintainer checklist for DS codebases  
- Exercise: Refactor a notebook into modular scripts; add tests.

Day 59 — Capstone project kickoff: define problem, dataset, evaluation plan  
- Exercise: Create project repo structure, baseline model, data pipeline.

Day 60 — Capstone completion & presentation: finalize model, prepare report & slides  
- Exercise: Present results (notebook + README), include reproducible run instructions.

---

## Professional extension (named modules after Day 60)

The maintained course now continues with ten executable modules. They retain
stable descriptive IDs so the original Days 1–60 never need renumbering:

- `python-pro-01`: package engineering and a local release workflow
- `python-svc-01`: reliable HTTP clients and service boundaries
- `python-pro-02`: concurrency and parallelism decisions
- `python-data-01`: Arrow, Parquet, and embedded DuckDB analytics
- `python-test-01`: test architecture, doubles, and generative testing
- `python-lang-01`: advanced typing and the Python data model
- `python-stats-01`: resampling, experiments, and causal boundaries
- `python-ml-01`: reproducible data and model delivery
- `python-svc-02`: service hardening and observability
- `python-perf-01`: measurement-first performance engineering

Follow each module's declared prerequisites rather than assuming this list must
be linear. See [professional paths](../docs/professional-paths.md) for direct
learner, guide, and solution links.

---

## Suggested rhythm
- 5 focused weekdays (learning + exercises), 1 lighter day for reading/recap, 1 day for mini-projects or catch-up.  
- Keep a daily journal: what you learned, 3 takeaways, 1 blocker.
- Pause at phase projects and repeat material as needed; project lessons often
  take more than one session.

## Resources & Tools
- Python 3.11–3.12 (3.12 recommended), Jupyter, pandas, NumPy,
  scikit-learn, matplotlib/Seaborn, PyTorch, Plotly/Altair, pytest, Ruff,
  mypy, Git, Docker, and MLflow.
- Use the repository companion guides first. Optional books and external
  documentation are enrichment, not offline prerequisites.

## Deliverables after the track
- Portfolio: 3 notebooks (EDA, ML pipeline, DL/NLP or time series), tests for utility modules, Dockerized model endpoint, project README and slides.

The track is practical breadth, not a replacement for the complete Python
language, statistics, security, or operations references. Demonstrate mastery
with runnable work and explanations rather than lesson completion alone.

---
