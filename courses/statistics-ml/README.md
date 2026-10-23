# Statistics and Machine Learning for Data Scientists End To End

This book develops the 1,005 named methods in the supplied 40-section outline into an end-to-end reference for data science decisions. Read sequentially for foundations, or use the topic manifest to find a method. Each chapter explains mechanisms, assumptions, appropriate uses, failure modes and interpretation, then connects them to complete Python demonstrations and answered interview discussions.

This is a tutorial and reference book. It contains no exams, problem sets or hidden solutions. The small examples explain mechanisms; their assertions check mathematical and implementation claims, not learner mastery. Advanced method descriptions are not claims that every research estimator has a production implementation in this repository.

## Running the worked examples

Open a chapter in the classroom reader, or read its Markdown file. Reading needs no Python packages. The examples use Python 3.11 or 3.12 and the repository's prepared scientific environment: NumPy, pandas, SciPy, scikit-learn and statsmodels. No dataset, pretrained model, API key or network connection is required after dependencies are installed. Examples construct tiny local fixtures and print interpretable results.

From the repository root, run this command in a terminal whose `python` resolves to the prepared environment. The command is identical in PowerShell, Command Prompt, Bash and zsh:

```text
python courses/statistics-ml/examples/chapter_01.py
```

Replace `01` with the chapter number. Optional ecosystems such as PyMC/Stan, XGBoost, NetworkX, lifelines, UMAP and specialized spatial, survey or reinforcement-learning packages are discussed only where relevant. They are not required by the examples and are never installed or imported automatically.

## Scope and provenance

[source-outline.md](source-outline.md) is an unmodified copy of the user-provided scope. [manifest.json](manifest.json) records its SHA-256 digest and chapter metadata. [coverage.json](coverage.json) maps each of its 1,005 bold method bullets to a stable `stat-SS-NN` anchor. These IDs follow the original section and bullet order, so similarly named methods in different contexts retain different IDs. Coverage means an explanatory treatment of the named method, not an unsupported claim that one toy calculation validates the entire method family.

The prose, numerical fixtures and programs are original teaching material. Chapter references link to primary papers, author-maintained books or official API documentation. External reading is optional. Interpret each demonstration within its stated assumptions and distinguish a worked calculation, an estimator's mathematical guarantee, and evidence that a real deployment is useful.

## Contents

1. [Problem Formulation and Statistical Reasoning](chapters/01-problem-formulation-and-statistical-reasoning.md)
2. [Mathematical Foundations](chapters/02-mathematical-foundations.md)
3. [Probability Fundamentals and Stochastic Processes](chapters/03-probability-fundamentals-and-stochastic-processes.md)
4. [Probability Distributions You Should Recognize](chapters/04-probability-distributions-you-should-recognize.md)
5. [Sampling, Surveys, and Data Collection](chapters/05-sampling-surveys-and-data-collection.md)
6. [Measurement, Exploratory Analysis, and Data Quality](chapters/06-measurement-exploratory-analysis-and-data-quality.md)
7. [Missing Data, Measurement Error, and Robust Statistics](chapters/07-missing-data-measurement-error-and-robust-statistics.md)
8. [Estimation and Statistical Inference](chapters/08-estimation-and-statistical-inference.md)
9. [Hypothesis Tests and Group Comparisons](chapters/09-hypothesis-tests-and-group-comparisons.md)
10. [Multiple Testing, Sequential Inference, and Selective Inference](chapters/10-multiple-testing-sequential-inference-and-selective-inference.md)
11. [Regression and Generalized Linear Models](chapters/11-regression-and-generalized-linear-models.md)
12. [Regression Diagnostics, Multilevel Models, and Longitudinal Analysis](chapters/12-regression-diagnostics-multilevel-models-and-longitudinal-analysis.md)
13. [Classical Experimental Design](chapters/13-classical-experimental-design.md)
14. [Online Experimentation and A/B Testing](chapters/14-online-experimentation-and-a-b-testing.md)
15. [Causal Inference Foundations](chapters/15-causal-inference-foundations.md)
16. [Quasi-Experiments and Causal Study Designs](chapters/16-quasi-experiments-and-causal-study-designs.md)
17. [Causal Estimation, Heterogeneous Effects, and Policy Learning](chapters/17-causal-estimation-heterogeneous-effects-and-policy-learning.md)
18. [Bayesian Statistics and Probabilistic Modeling](chapters/18-bayesian-statistics-and-probabilistic-modeling.md)
19. [Statistical Learning and Classical Supervised Models](chapters/19-statistical-learning-and-classical-supervised-models.md)
20. [Feature Engineering and Representation Learning](chapters/20-feature-engineering-and-representation-learning.md)
21. [Unsupervised Learning and Multivariate Analysis](chapters/21-unsupervised-learning-and-multivariate-analysis.md)
22. [Model Validation and Predictive Performance](chapters/22-model-validation-and-predictive-performance.md)
23. [Uncertainty Quantification and Distribution Shift](chapters/23-uncertainty-quantification-and-distribution-shift.md)
24. [Explainability, Fairness, and Model Robustness](chapters/24-explainability-fairness-and-model-robustness.md)
25. [Time-Series Foundations and Diagnostics](chapters/25-time-series-foundations-and-diagnostics.md)
26. [Classical Forecasting Methods](chapters/26-classical-forecasting-methods.md)
27. [Advanced Forecasting and Forecast Evaluation](chapters/27-advanced-forecasting-and-forecast-evaluation.md)
28. [Survival Analysis, Duration Models, and Reliability](chapters/28-survival-analysis-duration-models-and-reliability.md)
29. [Anomaly Detection, Changepoints, and Statistical Process Control](chapters/29-anomaly-detection-changepoints-and-statistical-process-control.md)
30. [Spatial and Spatiotemporal Statistics](chapters/30-spatial-and-spatiotemporal-statistics.md)
31. [Network and Graph Analysis](chapters/31-network-and-graph-analysis.md)
32. [Recommendation, Information Retrieval, and Ranking](chapters/32-recommendation-information-retrieval-and-ranking.md)
33. [Deep Learning, Language, and Generative Modeling](chapters/33-deep-learning-language-and-generative-modeling.md)
34. [Generative AI and Language-Model Evaluation](chapters/34-generative-ai-and-language-model-evaluation.md)
35. [Bandits, Reinforcement Learning, and Adaptive Decisions](chapters/35-bandits-reinforcement-learning-and-adaptive-decisions.md)
36. [Optimization and Operations Research](chapters/36-optimization-and-operations-research.md)
37. [Simulation and Computational Statistics](chapters/37-simulation-and-computational-statistics.md)
38. [Product, Customer, Marketing, and Business Analytics](chapters/38-product-customer-marketing-and-business-analytics.md)
39. [Research Synthesis and Specialized Statistical Methodologies](chapters/39-research-synthesis-and-specialized-statistical-methodologies.md)
40. [Production Methodology, Governance, and Senior Scientific Judgment](chapters/40-production-methodology-governance-and-senior-scientific-judgment.md)
